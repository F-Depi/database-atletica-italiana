import pandas as pd
import json
from my_functions import *


anno = '2024'
tipo_att = 'P'
sesso = 'M'
cat = 'X'
gara = '110 Hs h106-9.14'
tip_estr = '1'
vento = '2'
regione = '0'
naz = '2'
lim = '5'
societa = ''

with open('dizionario_gare.json') as f:
    dict_gare = json.load(f)

for gara in dict_gare:
    print(gara)

exit()

file = 'test.csv'

df = get_data_FIDAL(anno, tipo_att, sesso, cat, gara, tip_estr, vento, regione, naz, lim, societa)
df.to_csv(file, index=False)
