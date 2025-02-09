import os
import pandas as pd
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../'))
import sys
sys.path.append(os.path.abspath(PROJECT_ROOT + '/script/'))
from my_functions import get_file_database, best_by_atleta


## 60HS indoor
ambiente = 'I'
gara = '60Hs_h106-9.14'
data_I = get_file_database(ambiente, gara, PROJECT_ROOT)
data_I = data_I[data_I['data'].str[:4] == '2025']
data_I = best_by_atleta(data_I)

## Hanno il minimo
data_qual_I = data_I[data_I['prestazione'] <= 8.30]
#print(data_qual_I)

## 110HS Outdoor
ambiente = 'P'
gara = '110Hs_h106-9.14'
data_P = get_file_database(ambiente, gara, PROJECT_ROOT)
data_P = data_P[data_P['data'].str[:4] == '2024']
data_P = data_P[data_P['vento'] != '']
data_P = data_P[data_P['vento'].astype(float) <= 2]
data_P = best_by_atleta(data_P)

## Hanno il minimo
data_qual_O = data_P[data_P['prestazione'] <= 14.40]
#print(data_qual_O)

## Merge dei qualificati
data_qual_I.insert(0, 'disciplina', '60hs')
data_qual_O.insert(0, 'disciplina', '110hs')
data_qual = pd.concat([data_qual_O, data_qual_I])
data_qual = best_by_atleta(data_qual)
#print(data_qual)

data_qual.to_csv(PROJECT_ROOT + '/analisi_esempi/atleti_con_minimo/HS_qual.csv', index=None)
