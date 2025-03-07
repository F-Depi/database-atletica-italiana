import os
import pandas as pd
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../'))
import sys
sys.path.append(os.path.abspath(PROJECT_ROOT + '/script/'))
from my_functions import get_file_database, best_by_atleta


def qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P):
    ambiente = 'I'
    data_qual = pd.DataFrame(columns=['disciplina', 'tempo', 'vento', 'atleta', 'anno', 'società', 'posizione', 'luogo', 'data', 'link_atleta', 'link_società', 'categoria'])
    for gara, min in zip(gara_I, min_I):
        data_I = get_file_database(ambiente, gara)
        data_I = data_I[data_I['categoria'].str.contains(sesso, na=False)]
        data_I = data_I[data_I['data'].str[:4] == '2025']
        data_I = best_by_atleta(data_I)

        ## Hanno il minimo
        data_I = data_I[data_I['prestazione'] <= min]
        data_I['disciplina'] = gara + ' (I)'
        data_qual = pd.concat([data_qual, data_I])
        #print(data_qual_I)

    ## 110HS Outdoor
    ambiente = 'P'
    for gara, min in zip(gara_P, min_P):
        data_P = get_file_database(ambiente, gara)
        data_P = data_P[data_P['categoria'].str.contains(sesso, na=False)]
        data_P = data_P[data_P['data'].str[:4] == '2024']
        if 'vento' in data_P.columns:
            data_P = data_P[data_P['vento'] != '']
            data_P = data_P[data_P['vento'].astype(float) <= 2]
        data_P = best_by_atleta(data_P)

        ## Hanno il minimo
        data_P = data_P[data_P['prestazione'] <= min]
        data_P['disciplina'] = gara + ' (P)'
        data_qual = pd.concat([data_qual, data_P])
        #print(data_qual_O)

    ## Merge dei qualificati
    data_qual = best_by_atleta(data_qual)
    #print(data_qual)

    data_qual.to_csv(f'{sesso}_{gara_I[0]}.csv', index=None)


sesso = 'M'
# 60HS 
gara_I = ['60Hs_h106-9.14']
gara_P = ['110Hs_h106-9.14']
min_I = [8.30]
min_P = [14.40]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)

# 60m
gara_I = ['60m', '50m']
gara_P = ['100m']
min_I = [6.80, 5.90]
min_P = [10.30]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)

# 200m
gara_I = ['400m']
gara_P = ['400m']
min_I = [48.05]
min_P = [47.05]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)

# 800m
gara_I = ['800m']
gara_P = ['800m']
min_I = [110.80]
min_P = [108]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)

# 1500m
gara_I = ['1500m']
gara_P = ['1500m']
min_I = [226.20]
min_P = [222]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)

# 3000m
gara_I = ['3000m']
gara_P = ['3000m']
min_I = [489]
min_P = [484]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)


sesso = 'F'
# 60HS 
gara_I = ['60Hs_h84-8.50']
gara_P = ['100Hs_h84-8.50']
min_I = [8.55]
min_P = [13.80]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)

# 60m
gara_I = ['60m', '50m']
gara_P = ['100m']
min_I = [7.54, 6.54]
min_P = [11.70]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)

# 200m
gara_I = ['400m']
gara_P = ['400m']
min_I = [54.50]
min_P = [53.30]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)

# 800m
gara_I = ['800m']
gara_P = ['800m']
min_I = [126.50]
min_P = [124]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)

# 1500m
gara_I = ['1500m']
gara_P = ['1500m']
min_I = [263]
min_P = [251]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)

# 3000m
gara_I = ['3000m']
gara_P = ['3000m']
min_I = [570]
min_P = [560]
qualificati_indoor25(sesso, gara_I, gara_P, min_I, min_P)
