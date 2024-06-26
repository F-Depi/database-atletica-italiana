import pandas as pd
from my_functions import *

anno = '2021'
tipo_att = 'P'
sesso = 'M'
cat = 'X'
gara = '03'
tip_estr = '1'
vento = '2'
regione = '0'
naz = '2'
lim = '5'
societa = ''

file = 'test.csv'

df = get_data_FIDAL(anno, tipo_att, sesso, cat, gara, tip_estr, vento, regione, naz, lim, societa)
df.to_csv(file, index=False)
