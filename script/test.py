import pandas as pd
import json
import os
from my_functions import *

dict_gare = json.load(open('dizionario_gare.json'))

anno = '2024'
ambiente = 'P'
sesso = 'M'
cat = 'X'
gara = '80m'
tip_estr = '1'
vento = '2'
regione = '0'
naz = '2'
lim = '0'
societa = ''

with open('log.txt', 'w') as f_log:
    df = get_data_FIDAL(anno, ambiente, sesso, cat, dict_gare[gara]['codice'], tip_estr, vento, regione, naz, lim, societa, f_log)
    df = format_data_FIDAL(df, gara, ambiente, f_log)
    folder = 'test/'+ dict_gare[gara]['tipo'] + '/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    file = folder + gara.replace(' ', '_') + '_' + anno + '.csv'
    if df is not None:
        df.to_csv(file, index=False)
    
