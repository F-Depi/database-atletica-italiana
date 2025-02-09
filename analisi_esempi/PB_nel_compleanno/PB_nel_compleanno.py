from operator import index
import json
import pandas as pd
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../'))
import sys
sys.path.append(os.path.abspath(PROJECT_ROOT + '/script/'))
from my_functions import get_data_nascita_FIDAL, get_file_database


col_dtype = json.load(open('colonne_dtype.json'))

'''
## Per prima cosa dobbiamo aprire il profilo fidal di ogni atleta che ha fatto
## i 1500m per prendere la data esatta di nascita (il database ha solo l'anno)

ambiente = 'P'
gara = '1500m'

df = get_file_database(ambiente, gara)
df = df[df['prestazione'] < 233.48]

df = df.sort_values(by=['link_atleta'])

# Vettore booleano per lasciare solo 1 risultato per ogni persona (.shift() restituisce False per la prima riga)
mask = df['link_atleta'] != df['link_atleta'].shift()
mask.iloc[0] = True

df_atleti = df[mask]
df_nascita = df_atleti.apply(lambda row: get_data_nascita_FIDAL(row['link_atleta'], row['anno']), axis=1)
df_atleti['anno'] = df_nascita

for link_atleta, nascita in zip(df_atleti['link_atleta'], df_atleti['anno']):
    #mask2 = df['link_atleta'] == link_atleta
    #df.loc[mask2, 'nascita'] = nascita
    for ii, row in df.iterrows():
        if df.loc[ii, 'link_atleta'] == link_atleta:
            df.loc[ii, 'anno'] = nascita

df.to_csv('test.csv', index=False)
'''

## Ora possiamo fare la statistica
df2 = pd.read_csv('1500m_con_data_nascita_completa.csv', dtype=col_dtype)
df_null = df2[df2['anno'] == '']
df2 = df2[df2['anno'].str[-5:] == df2['data'].str[-5:]]
df2 = pd.concat([df_null, df2])
df2 = df2.sort_values('prestazione').reset_index(drop=True)
print(df2)
df2.to_csv('caro_gluis.csv', index=False)



