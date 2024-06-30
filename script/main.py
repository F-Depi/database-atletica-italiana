import json
import os
from my_functions import get_data_FIDAL, ultimo_aggiornamento_FIDAL

'''
Questo script scarica tutte le graduatorie outdoor di tutte le categorie e tutti gli anni
L'ho fatto andare una volta e ci ha messo tipo 3 ore per scaricare tutto
(si potrebbe tranquillamente parallelizzare perché la limitazione è il tempo di risposta del server FIDAL,
ma è uno script che basta runnare 1 volta e poi non serve più)
Per aggiornare il database si usa il file 'aggiorna_database.py'
'''

data_agg = ultimo_aggiornamento_FIDAL()

#anno = '2024'
ambiente = 'P'
#sesso = 'M'
#cat = 'C'
#gara = '100m'
tip_estr = '1'
vento = '2'
regione = '0'
naz = '2'
lim = '0'
societa = ''

dict_gare = json.load(open('dizionario_gare.json'))

for gara in dict_gare.keys():
    print('-'*90)
    print(gara)
    
    cod_gara = dict_gare[gara]['codice']
    tipo_gara = dict_gare[gara]['tipo']
    
    folder = '../database/outdoor/' + tipo_gara + '/'
    if not os.path.exists(folder): os.makedirs(folder)
    file = folder + gara.replace(' ','_') + '_2005_' + data_agg + '.csv'
    
    write_header = True
    for anno in range(2005, 2025):
        anno = str(anno)
        for cat in ['E', 'R', 'C', 'X']:
            for sesso in ['M', 'F']:
    
                print(anno, cat, sesso)
    
                df = get_data_FIDAL(anno, ambiente, sesso, cat, cod_gara, tip_estr, vento, regione, naz, lim, societa)
                df.to_csv(file, index=False, mode='a', header=write_header)
                write_header = False
    
    
    
