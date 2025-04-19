import pandas as pd
import json
from my_functions import *
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

'''
Script per aggiornare automaticamente il database con i dati nuovi delle graduatorie.
Il database viene aggiornato guardando l'ultimo anno presente. Tutti i dati di quell'anno vengono cancellati e riscaricati.
Se l'ultimo anno presente non era quello in corso, vengono scaricati anche gli anni successivi.
Aggiorno a chunk di 1 anno intero perché:
    - è più semplice
    - alcuni risultati potrebbero essere stati fatti riconoscere a posteriori (es. prestazioni ottenute all'estero)

NOTA: vengono aggiornate solo le gare che hanno un file di risultati già presente nel database.
'''

f_log = open('log', 'w')
dict_gare = json.load(open('script/dizionario_gare.json'))
col_dtype = json.load(open('script/colonne_dtype.json'))

last_server_update = ultimo_aggiornamento_FIDAL(f_log)
print('Last server update:\t' + last_server_update)

last_database_update = ultimo_aggiornamento_database()
if last_database_update:
    print('Last database update:\t' + last_database_update)

## Diamo il via alla giungla di nesting
for ambiente in ['I', 'P']:
    if ambiente == 'I':
        folder = './database/indoor/'
    elif ambiente == 'P':
        folder = './database/outdoor/'
    else: exit()

    for sub_folder in os.listdir(folder):
        if sub_folder.endswith('.csv'): continue

        sub_folder = folder + sub_folder + '/'

        for file in os.listdir(sub_folder):

            # evito i file di errori e di discipline sconosciute
            sono_risultati = file.endswith('.csv') and file[:3] != 'Sco'
            if not sono_risultati: continue

            last_local_update = file[-14:-4]
            if last_local_update == last_server_update:
                print(sub_folder + file + ' è già aggiornato')
                continue

            print('Aggiorno ' + sub_folder + file)

            # L'aggiornamento verrà fatto scaricando tutti i dati dell'anno in corso (e di quelli mancanti)
            years = range(int(last_local_update[:4]), int(last_server_update[:4]) + 1)

            gara = file[:-15]
            cod = dict_gare[gara]['codice']

            df_new = pd.DataFrame()
            for year in years:
                for cat in ['E', 'C', 'X']:
                    for sesso in ['M', 'F']:
                        df = get_data_FIDAL(str(year), ambiente, sesso, cat, cod, '1', '2', '0', '2', '0', '', f_log)
                        df_new = pd.concat([df_new, df])

            # Formattazione dei dati
            df_new = format_data_FIDAL(df_new, gara, ambiente, f_log)

            # Carico il vecchio database
            df_old = pd.read_csv(sub_folder + file, dtype=col_dtype)

            # Tolgo i risultati dell'ultimo anno perchè li ho appena riscaricati più aggiornati
            df_old = df_old[df_old['data'].str[:4] != last_local_update[:4]]

            df = pd.concat([df_old, df_new])
            df = df.reset_index(drop=True)

            df.to_csv(sub_folder + gara + '_' + last_server_update + '.csv', index=False)
            os.remove(sub_folder + file)


        print('-'*90)

