import pandas as pd
import json
from my_functions import *
import os

'''
Script per aggiornare automaticamente il database con i dati nuovi delle graduatorie.
NON FINITO
'''

f_log = open('log', 'w')
dict_gare = json.load(open('dizionario_gare.json'))
col_dtype = json.load(open('colonne_dtype.json'))
folder = '../database/outdoor/'

last_server_update = ultimo_aggiornamento_FIDAL(f_log)
last_local_update = os.listdir(folder + 'Corse Piane/')[0][-14:-4]
print('Last server update:\t' + last_server_update)
print('Last local update:\t' + last_local_update)

if last_server_update == last_local_update:
    print('Database già aggiornato')
    exit()

print('Aggiornamento in corso...')

# L'aggiornamento verrà fatto scaricando tutti i dati dell'anno in corso (e di quelli mancanti)
years = range(int(last_local_update[:4]), int(last_server_update[:4]) + 1)

for sub_folder in os.listdir(folder):
    if sub_folder.endswith('.csv'):
        continue
    sub_folder = folder + sub_folder + '/'

    for file in os.listdir(sub_folder):
        # evito file di errori e di discipline sconosciute
        non_sono_risultati = not(file.endswith('.csv') and file[:3] != 'Sco')
        if non_sono_risultati:
            continue

        gara = file[:-20]
        print(gara)
        cod = dict_gare[gara]['codice']

        df_new = pd.DataFrame()
        for year in years:
            for cat in ['E', 'C', 'X']:
                for sesso in ['M', 'F']:
                    df = get_data_FIDAL(str(year), 'P', sesso, cat, cod, '1', '2', '0', '2', '0', '', f_log)
                    df_new = pd.concat([df_new, df])
        print(df_new)
        print('-'*90)

