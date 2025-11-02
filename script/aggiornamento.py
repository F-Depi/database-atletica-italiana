import pandas as pd
from my_functions import *


'''
Script per aggiornare automaticamente il database con i dati nuovi delle
graduatorie.
Il database viene aggiornato guardando l'ultimo anno presente. Tutti i dati di
quell'anno vengono cancellati e riscaricati.
Se l'ultimo anno presente non era quello in corso, vengono scaricati anche gli
anni successivi.
Aggiorno a chunk di 1 anno intero perché:
    - è più semplice
    - alcuni risultati potrebbero essere stati fatti riconoscere a posteriori
      (es. prestazioni ottenute all'estero)

NOTA: vengono aggiornate solo le gare che hanno un file di risultati già
presente nel database.
'''

tieni_correzioni_manuali = False
force_update = False

f_log = open('log.txt', 'w')
f_status = open('status.txt', 'w')

conn = get_db_engine().connect()
df_discipline = pd.read_sql("SELECT * FROM discipline", conn)
result = conn.execute(text("SELECT * FROM regioni_province"))
dict_reg_prov = {row.regione: row.province for row in result}


last_server_update = ultimo_aggiornamento_FIDAL()
print('Last server update:\t' + last_server_update, file=f_status)

last_database_update = ultimo_aggiornamento_database()
if last_database_update:
    print('Last database update:\t' + last_database_update, file=f_status)
f_status.flush()


updated_something = False

## Diamo il via alla giungla di nesting
for i, row in df_discipline.iterrows():
    disciplina = row['disciplina']
    ult_agg = row['ultimo_aggiornamento'].strftime("%Y-%m-%d")
    if ult_agg >= last_server_update and not force_update:
        print(f"{disciplina} è già aggiornata", file=f_status)
        f_status.flush()
        continue

    for ambiente in ['I', 'P']:

        print(f"Aggiorno {disciplina} {ambiente}", file=f_status)
        f_status.flush()
        updated_something = True

        # L'aggiornamento verrà fatto scaricando tutti i dati dell'anno in corso
        #(e di quelli mancanti)
        years = range(int(ult_agg[:4]), int(last_server_update[:4]) + 1)

        codice = row['codice']

        df_new = pd.DataFrame()
        for year in years:
            for cat in ['C', 'X']:
                for sesso in ['M', 'F']:
                    df = get_data_FIDAL(str(year), ambiente, sesso, cat, codice,
                                        '1', '2', '0', '2', '0', '', f_log)
                    df_new = pd.concat([df_new, df])

            # Le graduatorie ragazzi esistono solo regionalmente
            cat = 'R'
            for sesso in ['M', 'F']:
                for reg in dict_reg_prov.keys():
                    df = get_data_FIDAL(str(year), ambiente, sesso, cat, codice,
                                        '1', '2', reg, '2', '0', '', f_log)
                    df_new = pd.concat([df_new, df])

        if df_new.empty:
            print(f"Nessun dato trovato per {disciplina} {ambiente}", file=f_status)
            f_status.flush()
            continue

        # Formattazione dei dati
        df_new = format_data_FIDAL(df_new, disciplina, ambiente, f_log)
        df_new = df_new.drop_duplicates()

        # Carico il vecchio database
        where_clause = f"""WHERE disciplina = '{disciplina}'
                           AND data >= '{years[0]}-01-01'
                           AND ambiente = '{ambiente}'"""

        if tieni_correzioni_manuali:
        # L'obbiettivo è aggiungere i risultati nuovi, sapendo che abbiamo in
        # df_new anche risultati già presenti nel DB. L'attenzione particolare
        # sta nel fatto che ci sono risultati errati che nel DB ho corretto ma
        # che continuo a riscaricare errati. Voglio quindi deduplicare senza
        # guardare il tempo (che è quello che ha l'errore) tenendo la prima
        # copia, ovvero la versione già corretta nel mio DB.
            query1 = text(f"SELECT * FROM results {where_clause}")
            df_old = pd.read_sql(query1, conn)
            df = pd.concat([df_old, df_new])
            df = df.drop_duplicates(subset=['atleta', 'anno', 'categoria',
                                   'società', 'posizione', 'luogo', 'data',
                                   'link_atleta', 'link_società'], keep='first')
            df = df.reset_index(drop=True)

        else:
        # Ignoro i risultati che ci sono già perchè li ho appena riscaricati
        # più aggiornati. Ogni tanto mi tocca farlo se ci sono errori grossi
        # della fidal che passano inosservati dai miei filtri e che loro si
        # preoccupano di correggere dopo un po'
            df = df_new
        
        # Controllo automatico di (alcuni) possibili errori
        check_errori(df, disciplina, f_log)

        if 'cronometraggio' in df.columns:
            df = df[df['cronometraggio'] != 'x']
        df = df[df['prestazione'] > 0]
 
        if 'id' in df.columns:
            df = df.drop(columns=['id'])

        df['disciplina'] = disciplina
        df['ambiente'] = ambiente
        df['sesso'] = df['categoria'].str[1]
        df['cod_società'] = df['link_società'].str[-5:]

        conn.execute(text(f"DELETE FROM results {where_clause}"))
        df.to_sql('results',
                  conn,
                  if_exists='append',
                  index=False,
                  method='multi',
                  chunksize=1000)

        conn.commit()
    
    conn.execute(text(f"""UPDATE discipline
                      SET ultimo_aggiornamento = CURRENT_TIMESTAMP
                      WHERE disciplina = '{disciplina}'"""))
    conn.commit()


    print('-'*90, file=f_status)
    f_status.flush()


conn.close()
print(updated_something, file=f_status)
f_status.flush()
