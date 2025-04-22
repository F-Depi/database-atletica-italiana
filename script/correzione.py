import pandas as pd
import os
import sys
import json
from my_functions import *
import time

def trova_errori():
    ''' Trova gli errori e li aggiunge al file di log '''
    folder = '../database-atletica-csv/indoor/'
    log_file = folder + 'errori_post_deduplicazione.csv'
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


"""Sistemiamo il centesimo in più nella prestazione dei tempi manuali"""
def togli_centesimo():
    ''' Trova gli errori e li aggiunge al file di log '''
    folder = '../database-atletica-csv/indoor/'

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
                    df['prestazione'] = df['prestazione'].astype(float)
                    ###df.loc[df['cronometraggio'] == 'm', 'prestazione'] -= 0.01 # Ok ha funzionato ora non serve mai più
                    ## Round to 2 decimal places
                    df['prestazione'] = df['prestazione'].round(2)
                    df.to_csv(folder + sub_folder + file, sep=',', index=False, header=True)


#trova_errori()
togli_centesimo()
