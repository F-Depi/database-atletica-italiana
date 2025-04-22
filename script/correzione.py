import pandas as pd
import os
import sys
import json
from my_functions import *
import time

''' Trova gli errori e li aggiunge al file di log
folder = '../database/outdoor/'
log_file = folder + 'errori_now.csv'
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
            if 'cronometraggio' in df.columns:
                df_typo = df[df['cronometraggio'] == 'x']
                df_typo.insert(0, 'gara', gara)
                df_typo.to_csv(log_file, sep=',', mode='a',index=False, header=write_header)
                write_header = False
'''



''' Cambiamo alcune cose sulla strutta del database
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
'''


'''Aggiunge le date di nascita complete'''
#ambiente = 'P'
#gara = '1500m'
#
#df = get_file_database(ambiente, gara)
#df = df.sort_values(by=['link_atleta'])
#
## Vettore booleano per lasciare solo 1 risultato per ogni persona (.shift() restituisce False per la prima riga)
#mask = df['link_atleta'] != df['link_atleta'].shift()
#mask.iloc[0] = True
#
#df = df[mask]


'''Deduplichiamo il database perché ho capito che le righe DEVONO essere uniche
grazie alla colonna posizione che distrugge l'ultima possibile molteplicità'''

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

