import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../'))
import sys
sys.path.append(os.path.abspath(PROJECT_ROOT + '/script/'))
from my_functions import get_file_database, best_by_atleta



def progressione_atleti(ambiente, gara, ascend, lim, sesso=['M', 'F'], min_anni=3, vento=['y', 'n'], agg_indoor=['y','n'], save=['y', 'n']):
    ## sesso: ['M', 'F']
    ## ascend: [True, False] per distinguere corse da concorsi dove la classifica
    ##         si fa ordinando la prestazione al contrario
    ## lim: [float] prestazione minima/massima che deve avere un atleta in
    ##      carriera per essere considerato nel grafico
    ## min_anni: [int, default=3] numero minimo di anni in cui l'atleta deve
    ##           avere almeno un risultato valido per essere considerato
    ## vento: ['y', 'n', default='y'] se si vuole escludere i risultati ventosi
    ##        mettere 'y'. 'n' non filtrerà per escludere risultati senza vento
    ##        o con vento irregolare

    data = get_file_database(ambiente, gara)    # dati dal database
    if vento == 'y':
        data = data[data['vento'] != '']                
        data = data[data['vento'].astype(float) <= 2]   
    data = data[data['categoria'].str.contains(sesso, na=False)]

    if agg_indoor == 'y':
        data_I = get_file_database('I', gara)
        data_I = data_I[data_I['categoria'].str.contains(sesso, na=False)]
        data = pd.concat([data, data_I])    # dati dal database


    ## Voglio prendere solo la miglior gara dell'anno quindi creo una colonna con 
    ## solo l'anno della gara per aiutarmi nel sorting
    data['anno_gara'] = data['data'].str[:4]
    data = data.sort_values(by=['link_atleta', 'anno_gara', 'prestazione'],
                            ascending=[True, True, ascend])
    data = data.drop_duplicates(subset=['link_atleta', 'anno_gara'], keep='first')
    data_grouped = data.groupby('link_atleta') 
    print(f'{len(data_grouped)} atleti')


    ## Teniamo solo gli atleti con 'min_anni' o più anni di gare
    data = data[data_grouped['link_atleta'].transform('count') >= min_anni]
    data_grouped = data.groupby('link_atleta') 
    print(f'{len(data_grouped)} atleti attivi per {min_anni} o più anni')


    ## Teniamo solo gli atleti scesi sotto i 'lim' secondi
    if ascend == True:
        ## corse
        data = data_grouped.filter(lambda group: group['prestazione'].min() <= lim)
        data_grouped = data.groupby('link_atleta') 
        N = len(data_grouped)
        print(f'Di cui {N} scesi sotto i {lim} secondi')

    elif ascend == False:
        ## concorsi
        data = data_grouped.filter(lambda group: group['prestazione'].max() >= lim)
        data_grouped = data.groupby('link_atleta') 
        N = len(data_grouped)
        print(f'Di cui {N} arrivati sopra i {lim} metri')

    else:
        print('Ascend = {ascend}. Ascend può solo essere True (per corse) o False (per concorsi)')
        exit()


    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    markers = ['s', 'o', '^', '*', 'P', 'X', 'D', 'v', '<', '>']
    ii = 0
    ii_max = len(colors) # after this the cycle will go on but we go back to color 0
    jj_max = len(markers)
    if N > ii_max * jj_max:
        print(f'{jj_max} Markers non sono abbastanza, ne servono {N // ii_max+ 1}')
        exit()

    
    ## Plot
    plt.figure(figsize = (16, 9))
    for name, group in data_grouped:

        eta = group['anno_gara'].astype(int) - group['anno'].astype(int)
        plt.plot(eta, group['prestazione'].astype(float), linestyle='-',
                 marker=markers[ii // ii_max], markersize=10, color=colors[ii % ii_max],
                 label = group['atleta'].iloc[0])
        ii += 1

    ## Mother of god forgive me
    plt.plot(np.zeros(1) + eta.iloc[0], np.zeros([1, ii_max - N % ii_max])
             + group['prestazione'].astype(float).iloc[0], color='w', alpha=0, label=' ')


    eta = data['anno_gara'].astype(int) - data['anno'].astype(int)
    tiks = range(min(eta), max(eta) + 1)
    plt.xticks(tiks)
    plt.legend(ncols=N // ii_max + 1)
    plt.xlabel('Età [anni]')
    plt.ylabel('prestazione')
    plt.title(f'{gara}: atleti italiani attivi per almeno {min_anni} anni, arrivati a {lim}')
    plt.tight_layout()
    if save == 'y':
        plt.savefig(f'progressione_{gara}_{sesso}_lim_{lim}.pdf')
    plt.show()


## Progressione nei 110 Hs
ambiente = 'P'
gara = '110Hs_h106-9.14'
min_anni = 3
lim = 13.9
ascend = True

progressione_atleti(ambiente, gara, ascend, lim, sesso='M', min_anni=min_anni, vento='y', save='y')


## Progressione nei 100 Hs
ambiente = 'P'
gara = '100Hs_h84-8.50'
min_anni = 3
lim = 13.5
ascend = True 

progressione_atleti(ambiente, gara, ascend, lim, sesso='F', min_anni=min_anni, vento='y', save='y')


## Progressione nei 100m
ambiente = 'P'
gara = '100m'
min_anni = 3
lim = 11.5
ascend = True  

progressione_atleti(ambiente, gara, ascend, lim, sesso='F', min_anni=min_anni, vento='y', save='y')


## Progressione nel triplo
ambiente = 'P'
gara = 'triplo'
min_anni = 3
lim = 13.5
ascend = False  

progressione_atleti(ambiente, gara, ascend, lim, sesso='F', min_anni=min_anni, vento='y', agg_indoor='y', save='y')


## Progressione nel lungo
ambiente = 'P'
gara = 'lungo'
min_anni = 3
lim = 6.35
ascend = False  

progressione_atleti(ambiente, gara, ascend, lim, sesso='F', min_anni=min_anni, vento='y', agg_indoor='y', save='y')
