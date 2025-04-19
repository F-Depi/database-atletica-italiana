import json
import os
import pandas as pd
from my_functions import get_data_FIDAL, format_data_FIDAL, ultimo_aggiornamento_FIDAL

'''
Questo script scarica tutte le graduatorie outdoor di tutte le categorie e tutti gli anni.
L'ho fatto andare una volta e ci ha messo tipo 3 ore per scaricare tutto (si potrebbe tranquillamente parallelizzare
perché la limitazione è il tempo di risposta del server FIDAL, ma è uno script che basta runnare 1 volta e poi non serve
più).
Per aggiornare il database si usa il file 'aggiorna_database.py'
'''

with open('nottata.log', 'w') as f_log:

    data_agg = ultimo_aggiornamento_FIDAL(f_log)

    #anno = '2024'
    #sesso = 'M'
    #cat = 'C'
    #gara = '100m'
    tip_estr = '1'
    vento = '2'
    regione = '0'
    naz = '2'
    lim = '0'
    societa = ''

    dict_gare = json.load(open('script/dizionario_gare.json'))
    dict_reg_prov = json.load(open('script/regioni_province.json'))

    for ambiente, ambiente_folder in zip(['P', 'I'], ['outdoor', 'indoor']):
        for gara in dict_gare.keys():
            print('-'*90, file=f_log)
            print(gara, file=f_log)
            
            cod_gara = dict_gare[gara]['codice']
            tipo_gara = dict_gare[gara]['tipo']
            
            folder = f'database/{ambiente_folder}/{tipo_gara}/'
            if not os.path.exists(folder): os.makedirs(folder)
            file = folder + gara + '_' + data_agg + '.csv'
            
            write_header = True
            for anno in range(2005, pd.Timestamp.now().year):
                anno = str(anno)
                #for cat in ['C', 'X']:
                #    for sesso in ['M', 'F']:
            
                #        regione = 0
                #        print(anno, cat, sesso, regione, file=f_log)
            
                #        df = get_data_FIDAL(anno, ambiente, sesso, cat, cod_gara, tip_estr, vento, regione, naz, lim, societa, f_log)
                #        df = format_data_FIDAL(df, gara, ambiente, f_log) 
                #        if df is not None:
                #            df.to_csv(file, index=False, mode='a', header=write_header)
                #            write_header = False

                for cat in ['E', 'R']:
                    for sesso in ['M', 'F']:
                        for reg in dict_reg_prov.keys():

                            regione = reg
                            print(anno, cat, sesso, reg, file=f_log)

                            df = get_data_FIDAL(anno, ambiente, sesso, cat, cod_gara, tip_estr, vento, regione, naz, lim, societa, f_log)
                            df = format_data_FIDAL(df, gara, ambiente, f_log) 
                            if df is not None:
                                df.to_csv(file, index=False, mode='a', header=write_header)
                                write_header = False

