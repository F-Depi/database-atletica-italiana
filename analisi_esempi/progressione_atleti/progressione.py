import os
import pandas as pd
import matplotlib.pyplot as plt
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../'))
import sys
sys.path.append(os.path.abspath(PROJECT_ROOT + '/script/'))
from my_functions import get_file_database, best_by_atleta

## Progressione nei 110 Hs
ambiente = 'P'
gara = '110Hs_h106-9.14'
ascend = True   # è una corsa quindi ordine crescente di risultato
vento = 'y'     # Serve per poter decidere se escludere le gare ventose
data = get_file_database(ambiente, gara)    # dati dal database
if vento == 'y':
    data = data[data['vento'] != '']                
    data = data[data['vento'].astype(float) <= 2]   

## Voglio prendere solo la miglior gara dell'anno quindi creo una colonna con 
## solo l'anno della gara per aiutarmi nel sorting
data['anno_gara'] = data['data'].str[:4]
data = data.sort_values(by=['link_atleta', 'anno_gara', 'prestazione'],
                        ascending=[True, True, ascend])
data = data.drop_duplicates(subset=['link_atleta', 'anno_gara'], keep='first')
print(len(data))


## Teniamo solo gli atleti con 3 o più anni di gare
data = data[data.groupby('link_atleta')['link_atleta'].transform('count') >= 3]
print(len(data))

## Teniamo solo gli atleti scesi sotto i 15 secondi
data = data.groupby('link_atleta').filter(lambda group: group['prestazione'].min() < 14)
print(len(data))


## Raggruppiamo i risultati per atleta prima di plottarli
data_grouped = data.groupby('link_atleta')
N = len(data_grouped)
print(N)

markers = ['o', '^', 's', 'x']
ii = 0
jj = 0

plt.figure(figsize = (16, 9))
for name, group in data_grouped:
    if jj > (ii + 1) * N // len(markers): ii += 1
    plt.plot(group['anno_gara'].astype(int), group['prestazione'].astype(float),
             linestyle='-', marker=markers[ii], label = group['atleta'].iloc[0])
    jj += 1

tiks = [2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023, 2025]
lab_tiks = ['2007', '2009', '2011', '2013', '2015', '2017', '2019', '2021', '2023', '2025']
plt.xticks(tiks, lab_tiks)
plt.legend(ncol=4)
plt.xlabel('anno')
plt.ylabel('tempo [s]')
plt.title('Atleti italiani attivi per almeno 3 anni scesi sotto i 14 secondi')
plt.tight_layout()
plt.savefig('progressione_sub_14.pdf')
plt.show()

