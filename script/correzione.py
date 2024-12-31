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


ambiente = 'P'
gara = '1500m'

df = get_file_database(ambiente, gara)
df = df.sort_values(by=['link_atleta'])

# Vettore booleano per lasciare solo 1 risultato per ogni persona (.shift() restituisce False per la prima riga)
mask = df['link_atleta'] != df['link_atleta'].shift()
mask.iloc[0] = True

df = df[mask]

### Ora dividiamo il df in 8 parti, una per ogni thread, forse
### non finito###
#len_per_thread = len(df) // 8
#num_thread = int(sys.argv[1])
#if num_thread > 8 or num_thread < 1:
#    print('L\'argomento deve essere 1, ..., 8')
#    exit()
#start_point = (num_thread - 1) * len_per_thread
#end_point = num_thread * len_per_thread
#
#df = df[start_point:end_point]
#
#t_0 = time.time()
#date_nascita = df.apply(lambda row: get_data_nascita_FIDAL(row['link_atleta'], row['anno']), axis=1)
#df['nascita'] = date_nascita
#df.to_csv('test.csv', index=False)
#t_1 = time.time()
#print(t_1 - t_0)
