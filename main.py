import pandas as pd
from my_functions import *

#anno = '2024'
tipo_att = 'P'
sesso = 'M'
#cat = 'C'
cod_gara = 'S6'
gara = '2000st-h84'
tip_estr = '1'
vento = '2'
regione = '0'
naz = '2'
lim = '0'
societa = ''

file = 'database/outdoor/'+gara+'_2005_2024-06-25.csv'

# Write the header

with open(file, 'w') as f:
    f.write('prestazione,vento,tempo,cronometraggio,atleta,anno,categoria,società,posizione,luogo,data,link_atleta,link_società\n')

for anno in range(2005, 2025):
    anno = str(anno)
    for cat in ['E', 'R', 'C', 'X']:
        for sesso in ['M', 'F']:

            print(anno, cat, sesso)

            df = get_data_FIDAL(anno, tipo_att, sesso, cat, cod_gara, tip_estr, vento, regione, naz, lim, societa)
            df.to_csv(file, index=False, mode='a', header=False)



