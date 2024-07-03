import pandas as pd
import os
from my_functions import *

'''
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
            
            gara = file[:-20]
            if 'cronometraggio' in df.columns:
                df_typo = df[df['cronometraggio'] == '2.0']
                df_typo.insert(0, 'gara', gara)
                df_typo.to_csv(log_file, sep=',', mode='a',index=False, header=write_header)
                write_header = False
'''

with open('log', 'w') as f_log:
    file = '../database/outdoor/Marcia/Marcia_10km_2005_2024-06-29.csv'
    df = pd.read_csv(file, sep=',', header=0, dtype=str)
    df['prestazione'] = pd.to_numeric(df['prestazione'])
    df['cronometraggio'] = pd.to_numeric(df['cronometraggio'])
    mask = df['cronometraggio'] == 3
    print(df[mask])
    df[['prestazione', 'cronometraggio']] = df.apply(lambda row: conversione_manuale_elettrico(row['tempo'], f_log), axis=1, result_type='expand')
    print(df[mask])
