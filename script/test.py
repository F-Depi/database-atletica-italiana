import pandas as pd
import json
import os
from my_functions import *

dict_gare = json.load(open('dizionario_gare.json'))

for key in dict_gare.keys():
    print(key, dict_gare[key])
    
exit()

anno = '2024'
ambiente = 'P'
sesso = 'M'
cat = 'X'
#gara = '110Hs h106-9.14'
tip_estr = '1'
vento = '2'
regione = '0'
naz = '2'
lim = '0'
societa = ''

for gara in dict_gare.keys():

    df = get_data_FIDAL(anno, ambiente, sesso, cat, dict_gare[gara]['codice'], tip_estr, vento, regione, naz, lim, societa)
    df = format_data_FIDAL(df, gara, ambiente)
    folder = 'test/'+ dict_gare[gara]['tipo'] + '/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    file = folder + gara.replace(' ', '_') + '_' + anno + '.csv'
    if df is not None:
        df.to_csv(file, index=False)
