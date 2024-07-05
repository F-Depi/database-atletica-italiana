import pandas as pd
import os
import json
from my_functions import *

''' Trova gli errori e li aggiunge al file di log '''
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

