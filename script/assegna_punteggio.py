from my_functions import get_file_database
import pandas as pd
import json
import os

"""
Assegna i punteggi World Athletics a un file CSV di risultati
Non è mai stato implementato perché la fidal non li usa.
Le tabelle sono inoltre state aggiornate a inizio 2025, qui ci sono quelle vecchie.
"""
def trova_punti(tabelle, prop_gare, ambiente, sesso, gara, mark):

    ## Questa serve per capire se dobbiamo cercare il punteggio approssimando
    ## sopra o sotto il valore della prestazione
    tipo_classifica = prop_gare[gara]["classifica"]
    if tipo_classifica == "tempo": foo = True
    else: foo = False

    if "M" in sesso: sesso = "men"
    if "F" in sesso: sesso = "women"
    if ambiente == "I": ambiente = "indoor"
    if ambiente == "P": ambiente = "outdoor"

    ## Sistemo le discripanze tra i nomi delle gare
    if gara == "1miglio": gara = "mile"
    if gara == "2miglia": gara = "2 Miles"
    if gara == "10000m": gara = "10,000m"
    if gara == "disco_1kg": gara = "DT"
    if gara == "disco_2kg": gara = "DT"
    if gara == "martello_4kg": gara = "HT"
    if gara == "martello_7kg": gara = "HT"
    if gara == "peso_4kg": gara = "SP"
    if gara == "peso_7kg": gara = "SP"
    if gara == "giavellotto_600g": gara = "JT"
    if gara == "giavellotto_800g": gara = "JT"
    if gara == "Marcia_10000m": gara = "10,000mW"
    if gara == "Marcia_20000m": gara = "20,000mW"
    if gara == "Marcia_5000m": gara = "5000mW"
    if gara == "Marcia_3000m": gara = "3000mW"
    if gara == "Marcia_10km": gara = "10kmW"
    if gara == "Marcia_20km": gara = "20kmW"
    if gara == "Marcia_50km": gara = "50kmW"
    if gara == "60Hs_h84-8.50": gara = "60mH"
    if gara == "60Hs_h106-9.14": gara = "60mH"
    if gara == "100Hs_h84-8.50": gara = "100mH"
    if gara == "110Hs_h106-9.14": gara = "110mH"
    if gara == "100Hs_h84-8.50": gara = "100mH"
    if gara == "400Hs_h76": gara = "400mH"
    if gara == "400Hs_h91": gara = "400mH"
    if gara == "asta": gara = "PV"
    if gara == "triplo": gara = "TJ"
    if gara == "alto": gara = "HJ"
    if gara == "lungo": gara = "LJ"
    if gara == "3000st_h76": gara = "3000mSC"
    if gara == "3000st_h91": gara = "3000mSC"

    if foo == True:
        for record in tabelle:
            if (record["category"] == ambiente and
                record["gender"] == sesso and
                record["event"] == gara):
                if (record["mark"] >= mark):
                    return record["points"]
    else:
        for record in tabelle:
            if (record["category"] == ambiente and
                record["gender"] == sesso and
                record["event"] == gara):
                if (record["mark"] <= mark):
                    return record["points"]
    print(f'Punteggio non trovato per "category":"{ambiente}","gender":"{sesso}","event":"{gara}","mark":{mark}')
    return None  # Return None if no match is found


societa = 'BL012'
tabelle = json.load(open('../database/iaaf.json'), )
dict_gare = json.load(open('dizionario_gare.json'))

for ambiente in ['I', 'P']:
    if ambiente == 'I':
        folder = '../database/indoor/'
    elif ambiente == 'P':
        folder = '../database/outdoor/'
    else: exit()

    for sub_folder in os.listdir(folder):
        if sub_folder.endswith('.csv'): continue

        sub_folder = folder + sub_folder + '/'

        for file in os.listdir(sub_folder):

            # evito i file di errori e di discipline sconosciute
            sono_risultati = file.endswith('.csv') and file[:3] != 'Sco'
            if not sono_risultati: continue

            print('Aggiorno ' + sub_folder + file)

            gara = file[:-15]

            ## Carico il database e filtro per società
            df = get_file_database(ambiente, gara)
            cond1 = df['link_società'].str[-5:] == societa
            df = df[cond1]

            if df.empty: continue

            ## Assegno i punteggi
            punteggio_col = df.apply(lambda row: trova_punti(tabelle, dict_gare, ambiente, row['categoria'], gara, row['prestazione']), axis=1)
            df.insert(0, "punteggio", punteggio_col)
            
            df = df.sort_values(by=['punteggio'], ascending=False)

            path = f'{sub_folder.replace('database', 'database_ANA')}{gara}.csv'
            df.to_csv(path, index=False)

