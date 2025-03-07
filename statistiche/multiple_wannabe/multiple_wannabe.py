import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../'))
import sys
sys.path.append(os.path.abspath(PROJECT_ROOT + '/script/'))
from my_functions import get_file_database, best_by_atleta

from functools import reduce


def iaaf_score(prestazione, tipo, abc):
    ## tipo = ['corsa', 'salto', 'lancio']
    a = abc[0]
    b = abc[1]
    c = abc[2]

    if tipo == 'corsa':
        foo = b - prestazione
        if foo < 0: return 0
        return np.floor(a * foo**c)

    elif tipo == 'salto':
        foo = 100 * prestazione - b
        if foo < 0: return 0
        return np.floor(a * foo**c)

    elif tipo == 'lancio':
        foo = prestazione - b
        if foo < 0: return 0
        return np.floor(a * foo**c)
    else:
        print('tipo non riconosciuto, tipo = [corsa, salto, lancio]')
        exit()


def get_dati(gara, tipo, sesso, abc, vento='y'):
    data = get_file_database('P', gara)                         # risultati outdoor

    if vento == 'y':
        data = data[data['vento'] != '']                          # e filtro 
        data = data[data['vento'].astype(float) <= 2]             # il vento

    if tipo == 'salto' or tipo == 'lancio':
        data = pd.concat([get_file_database('I', gara), data])    # indoor

    data = data[data['categoria'].str.contains(sesso, na=False)]

    if tipo == 'corsa':
        data = best_by_atleta(data, 'tempo').reset_index(drop=True)
    else:
        data = best_by_atleta(data, 'misura').reset_index(drop=True)
    
    ## Assegnamo il punteggio IAAF delle multiple
    data['punti'] = data['prestazione'].apply(iaaf_score, args=(tipo, abc, ))

    return data


def merge_results(dfs, gare):
    common_names = set(dfs[0]['link_atleta'])
    for df in dfs[1:]:
        common_names &= set(df['link_atleta'])

    filtered_dfs = []
    for i, df in enumerate(dfs):
        df_filt = df[df['link_atleta'].isin(common_names)][['prestazione', 'punti', 'atleta', 'link_atleta']]
        df_filt = df_filt.rename(columns={'prestazione': gare[i], 'punti': gare[i]+' p'})
        filtered_dfs.append(df_filt)


    result = reduce(lambda left, right: pd.merge(left, right, on=['atleta', 'link_atleta']), filtered_dfs)
    punti_columns = [g + ' p' for g in gare]  # List of all 'punti' columns
    result['punti TOT'] = result[punti_columns].sum(axis=1)
    result = result.sort_values(by=['punti TOT'], ascending=False)
    column_order = ['punti TOT'] + [col for g in gare for col in (g, g + ' p')] + ['atleta', 'link_atleta']
    result = result[column_order].reset_index(drop=True)
    result.index += 1 
    result.to_csv('risultati.csv')


## Stat Request: la Giulia deve comparire prima
sesso = 'F'
gara1 = 'lungo'
tipo1 = 'salto'
abc1 = [0.188807, 210, 1.41]

gara2 = '200m'
tipo2 = 'corsa'
abc2 = [4.99087, 42.5, 1.81]

gara3 = '100Hs_h84-8.50'
tipo3 = 'corsa'
abc3 = [9.23076, 26.7, 1.835]

gara4 = 'asta'
tipo4 = 'salto'
abc4 = [0.44125, 100, 1.35]


gara5 = 'giavellotto_600g'
tipo5 = 'lancio'
abc5 = [15.9803, 3.8, 1.04]

abc_peso = [56.0211, 1.5, 1.05]


data1 = get_dati(gara1, tipo1, sesso, abc1)
data2 = get_dati(gara2, tipo2, sesso, abc2)
data3 = get_dati(gara3, tipo3, sesso, abc3)
data4 = get_dati(gara4, tipo4, sesso, abc4, vento='n')
data5 = get_dati(gara5, tipo5, sesso, abc5, vento='n')


merge_results([data1, data2, data3, data4, data5], [gara1, gara2, gara3, gara4, gara5])


exit()
common_names = set(data1['link_atleta']) & set(data2['link_atleta']) & set(data3['link_atleta'])

data1_filt = data1[data1['link_atleta'].isin(common_names)][['prestazione', 'punti', 'link_atleta']]
data1_filt = data1_filt.rename(columns={'prestazione': gara1, 'punti': gara1+' p'})
data2_filt = data2[data2['link_atleta'].isin(common_names)][['prestazione', 'punti', 'link_atleta']]
data2_filt = data2_filt.rename(columns={'prestazione': gara2, 'punti': gara2+' p'})
data3_filt = data3[data3['link_atleta'].isin(common_names)][['prestazione', 'punti', 'atleta', 'link_atleta']]
data3_filt = data3_filt.rename(columns={'prestazione': gara3, 'punti': gara3+' p'})

result = data1_filt.merge(data2_filt, on='link_atleta').merge(data3_filt, on='link_atleta')
result['punti TOT'] = result[gara1+' p'] + result[gara2+' p'] + result[gara3+' p']
result = result.sort_values(by=['punti TOT'], ascending=False)
result = result[['punti TOT', gara1, gara1+' p', gara2, gara2+' p', gara3, gara3+' p', 'atleta', 'link_atleta']].reset_index(drop=True)
result.index += 1 
result.to_csv('risultati.csv')






























exit()
data1['gara'] = gara1
data2['gara'] = gara2
data3['gara'] = gara3

## Unisco i dataframe, creo un raggruppamento per atleta e seleziono solo gli
## atleti con 3 risultati
data = pd.concat([data1, data2, data3])
data_grouped = data.groupby('link_atleta') 
data = data[data_grouped['link_atleta'].transform('count') >= 3]

data_TOT = pd.DataFrame(index = range(len(data_grouped)), columns=['punti TOT', gara1, gara2, gara3, 'atleta', 'link_atleta']) # ignore
for _, df_atleta in data_grouped:
    data_TOT['punti_TOT'] = sum(df_atleta['punti'])
    data_TOT[gara1] = df_atleta[df_atleta['gara'] == gara1]['prestazione']
    data_TOT[gara2] = df_atleta[df_atleta['gara'] == gara2]['prestazione']
    data_TOT[gara3] = df_atleta[df_atleta['gara'] == gara3]['prestazione']
    data_TOT['atleta'] = df_atleta['atleta'].iloc[0]
    data_TOT['link_atleta'] = df_atleta['link_atleta'].iloc[0]

print(data_TOT)

