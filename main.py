import pandas as pd
from my_functions import *

#anno = '2024'
tipo_att = 'P'
sesso = 'M'
#cat = 'C'
gara = '03'
tip_estr = '1'
vento = '2'
regione = '0'
naz = '2'
lim = '0'
societa = ''

file = '100m_2005_2024-06-25.csv'

write_header = False 
for anno in range(2005, 2025):
    anno = str(anno)
    for cat in ['E', 'R']:
        for sesso in ['M', 'F']:

            print(anno, cat, sesso)

            df = get_data_FIDAL(anno, tipo_att, sesso, cat, gara, tip_estr, vento, regione, naz, lim, societa)
            df.to_csv(file, index=False, mode='a', header=write_header)
            write_header = False



