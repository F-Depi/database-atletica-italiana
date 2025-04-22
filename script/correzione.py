import pandas as pd
import os
import sys
import json
from my_functions import *
import time

def trova_errori():
    ''' Trova gli errori e li aggiunge al file di log '''
    folder = '../database-atletica-csv/outdoor/'
    log_file = folder + 'errori_post_deduplication.csv'
    write_header = True

    for sub_folder in os.listdir(folder):
        if sub_folder.endswith('.csv'):
            continue
        sub_folder = sub_folder + '/'

        for file in os.listdir(folder + sub_folder):
            if file.endswith('.csv'):
                print(file)

                df = pd.read_csv(folder + sub_folder + file, sep=',', header=0, dtype=str)

                gara = file[:-15]
                #if 'cronometraggio' in df.columns:
                #    df_typo = df[df['cronometraggio'] == 'x']
                #    df_typo.insert(0, 'gara', gara)
                #    df_typo.to_csv(log_file, sep=',', mode='a',index=False, header=write_header)
                #    write_header = False

                if 'vento' in df.columns:
                    indexes = []
                    for i, row in df.iterrows():
                        try:
                            _ = float(row['vento'])
                        except ValueError:
                            indexes.append(i)
                    df_err = df.iloc[indexes]
                    df_err.insert(0, 'gara', gara)
                    df_err.to_csv(log_file, sep=',', mode='a',index=False, header=write_header)
                    write_header = False


def cambia_struttura():
    ''' Cambiamo alcune cose sulla strutta del database '''
    dict_gare = json.load(open('dizionario_gare.json'))
    col_dtype = json.load(open('colonne_dtype.json'))

    folder = '../database/indoor/Siepi/'
    for file in os.listdir(folder):

        gara = file[:-20]
        print(gara)
        f_log = open('log', 'w')
        df = pd.read_csv(folder + file, sep=',', header=0, dtype=col_dtype)
        print(df)

        df[['prestazione', 'cronometraggio']] = df.apply(lambda row: conversione_manuale_elettrico(row['tempo'], f_log), axis=1, result_type='expand')
        df['prestazione'] = df['prestazione'].round(2)
        df.to_csv(folder + file, sep=',', index=False)

        print('-'*90)


def deduplicate_db():
    '''Deduplichiamo il database perché ho capito che le righe DEVONO essere uniche
    grazie alla colonna posizione che distrugge l'ultima possibile molteplicità '''

    col_dtype = json.load(open('script/colonne_dtype.json'))
    ## Diamo il via alla giungla di nesting
    for ambiente in ['indoor', 'outdoor']:
        folder = f'database/{ambiente}/'

        for sub_folder in os.listdir(folder):
            if sub_folder.endswith('.csv'): continue

            sub_folder = folder + sub_folder + '/'

            for file in os.listdir(sub_folder):

                # evito i file di errori e di discipline sconosciute
                sono_risultati = file.endswith('.csv') and file[:3] != 'Sco'
                if not sono_risultati: continue

                print('Aggiorno ' + sub_folder + file)
                
                # Carico il file
                try:
                    df = pd.read_csv(sub_folder + file, dtype=col_dtype)
                    df = df.drop_duplicates()
                    df = df.sort_values(by='data')
                    df = df.reset_index(drop=True)
                    df.to_csv(sub_folder + file, index=False)
                except Exception as e:
                    print(f"Errore durante la lettura del file {file}: {e}")
                    continue


#trova_errori()

with open('log', 'w') as f_log:

    col_dtype = json.load(open('script/colonne_dtype.json'))
    filename = '../database-atletica-csv/outdoor/Ostacoli/foo.csv'
    df = pd.read_csv(filename, dtype=col_dtype)
    df = format_data_FIDAL(df, '60Hs_h60-7.50', 'P', f_log=f_log)
    print(df[df['cronometraggio'] == 'e'])
    df.to_csv('foo.csv', index=False)
