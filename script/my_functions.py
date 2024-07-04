import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
import json
import re

## Scarica una pagina e mette i dati in un DataFrame del tipo 'tempo', 'vento', 'atleta', 'anno', 'categoria', 'società', 'posizione', 'luogo', 'data', 'link_atleta', 'link_società'
def get_data_FIDAL(anno, ambiente, sesso, cat, gara, tip_estr, vento, regione, naz, limite, societa, f_log):
    
    cat = cat[0] + sesso + cat[1:]

    url_FIDAL = 'https://www.fidal.it/graduatorie.php?anno='+anno+'&tipo_attivita='+ambiente+'&sesso='+sesso+'&categoria='+cat+'&gara='+gara+'&tipologia_estrazione='+tip_estr+'&vento='+vento+'&regione='+regione+'&nazionalita='+naz+'&limite='+limite+'&societa='+societa+'&submit=Invia'

    print(url_FIDAL, file=f_log)

    # Scarico la pagina
    page = requests.get(url_FIDAL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    # Rimuovo la riga con i nomi delle colonne
    data_row = soup.find_all('tr')[1:]
    
    # Rimuovo le righe (una ogni 10 prestazioni) che contengono il numero di prestazioni (10, 20, 30, ...)
    # Ho quindi che la riga 11, 22, 33, ... contengono il numero di prestazioni e vanno rimosse
    data_row = [row for i, row in enumerate(data_row) if (i+1) % 11 != 0]

    if len(data_row) == 0:
        print('Nessun dato trovato', file=f_log)
        return pd.DataFrame()

    if 'colspan="8"' in str(data_row[-1]):
        data_row = data_row[:-1]
    
    # La tabella ha sempre le stesse 8 colonne, quindi mi fido a creare il data frame e mettere dentro i dari di data_row uno alla volta. Aggiungo 2 colonne per i link
    df_data = pd.DataFrame(index = range(len(data_row)), columns=['tempo', 'vento', 'atleta', 'anno', 'società', 'posizione', 'luogo', 'data', 'link_atleta', 'link_società', 'categoria'])

    for i, row in enumerate(data_row):
    
        j = 0
        # Inserimento di tempo, vento, atleta, anno, società, posizione, luogo, data
        for cell in row.find_all('td'):
            cell = cell.text.strip()
            if j == 3: cell = check_anno(cell, i, f_log)
            if j == 7: cell = check_data(cell, anno, i, f_log)
            df_data.iat[i, j] = cell
            j += 1
    
        # Inserimento di link_atleta, link_società, categoria, prestazione, cronometraggio
        data_a = row.find_all('a')
        if len(data_a) > 1:
            df_data.at[i, 'link_atleta'] = data_a[0].get('href')
            df_data.at[i, 'link_società'] = data_a[1].get('href')
        df_data.at[i, 'categoria'] = assegna_categoria(df_data.at[i, 'anno'], df_data.at[i, 'data'], sesso, cat, f_log)

    df_data = df_data[['tempo', 'vento', 'atleta', 'anno', 'categoria', 'società', 'posizione', 'luogo', 'data', 'link_atleta', 'link_società']]

    return df_data


## Formatta i dati scaricati dalla FIDAL con la funzione get_data_FIDAL()
def format_data_FIDAL(df, gara, ambiente, f_log) -> pd.DataFrame:

    if len(df) == 0:
        print('Nessun dato da formattare', file=f_log)
        return pd.DataFrame()

    dict_gare = json.load(open('dizionario_gare.json'))
    if gara not in dict_gare:
        print('Gara non presente nel dizionario: ' + gara + '. Le gare sono:\n', file=f_log)
        for key in dict_gare.keys():
            print(key)
        return pd.DataFrame()

    if ambiente not in ['I', 'P', 'S']:
        print('Ambiente non valido: ' + ambiente + '. I possibili valori sono I (indoor), P (pista), S (strada)', file=f_log)
        return pd.DataFrame()

    # A questo punto in base al tipo di gara formatto i dati
    classifica_gara = dict_gare[gara]['classifica']

    vento = dict_gare[gara]['vento']
    if ambiente == 'I': vento = 'no'

    # Salti, lanci e 24h di corsa sono gare in cui la classifica è data dalla misura.
    if classifica_gara == 'distanza':
        df = df.rename(columns={'tempo': 'prestazione'})
        if vento == 'no':
            del df['vento']
        return df

    # Le gare di corsa hanno come prestazione un tempo, che va anche convertito in base al cronometraggio
    if classifica_gara == 'tempo':
        #df['prestazione'], df['cronometraggio'] = zip(*df['tempo'].map(conversione_manuale_elettrico)
        df[['prestazione', 'cronometraggio']] = df.apply(lambda row: conversione_manuale_elettrico(row['tempo'], f_log), axis=1, result_type='expand')
        df = df[['prestazione', 'vento', 'tempo', 'cronometraggio', 'atleta', 'anno', 'categoria', 'società', 'posizione', 'luogo', 'data', 'link_atleta', 'link_società']]
        if vento == 'no':
            del df['vento']
        return df

    print('Tipo di gara non riconosciuto. classifica_gara:', classifica_gara, file=f_log)
    return pd.DataFrame()


## Alla Fidal non piace scrive l'anno con 4 cifre, quindi scrivono solo le ultime due. Questa funzione aggiunge il 19 o il 20 davanti.
def check_anno(cell, i, f_log) -> str:
    if cell == '':
        print('Anno non disponibile in riga', i, file=f_log)
        return cell
    else:
        anno = int(cell)
        if anno > 24:
            return str(1900 + anno)
        else:
            return str(2000 + anno)


## Alla Fidal non piace scrivere la data in formato standard, quindi la scrivono in modo strano e senza l'anno. Questa funzione la mette in formato standard.
def check_data(cell, anno, i, f_log) -> str:
    if cell == '':
        print('Data non disponibile in riga', i, file=f_log)
        return cell
    else:
        data = cell.split('/')
        return anno + '-' + data[1] + '-' + data[0]


## Calcola l'età dell'atleta per assegnare la categoria
def assegna_categoria(anno_atleta, data_prestazione, sesso, categoria, f_log) -> str:
    if anno_atleta == '': return categoria
    if data_prestazione == '': return categoria
    eta = int(data_prestazione[:4]) - int(anno_atleta)
    if eta < 6:
        print('Atleta troppo giovane, età:', eta, file=f_log)
        return ''
    elif eta < 12: return 'E' + sesso
    elif eta < 14: return 'R' + sesso
    elif eta < 16: return 'C' + sesso
    elif eta < 18: return 'A' + sesso
    elif eta < 20: return 'J' + sesso
    elif eta < 23: return 'P' + sesso
    elif eta > 34:
        eta = (eta // 5) * 5
        return 'S' + sesso + str(eta)
    else: return 'S' + sesso


## Converte i tempi manuali in tempi elettrici. Se è una misura (lanci o salti, queste hanno sempre 2 cifre decimali quindi non dovrebbe toccarle)
def conversione_manuale_elettrico(tempo, f_log) -> tuple[float, str]:
    ## Restituisce il tempo convertito e un codice (e, m, x) se il tempo è elettrico, manuale o sconosciuto

    # Se non è un tempo
    if '.' not in tempo and ':' not in tempo:
        print('Questo tempo non ha né punto decimale né \':\': ' + tempo, file=f_log)
        return -1, 'x'

    # Se hanno usato la notazione 1h23:45.67
    if 'h' in tempo:
        tempo = tempo.replace('h', ':')

    # Se non è un tempo misurato solo in muti (gare su strada), per correttezza aggiungo anche qui 0.25 secondi
    if '.' not in tempo:
        hh_mm_SS = tempo.split(':')
        if len(hh_mm_SS) == 2:
            mm_SS = int(hh_mm_SS[0]) * 60 + int(hh_mm_SS[1]) + 0.25
            return mm_SS, 'm'
        elif len(hh_mm_SS) == 3:
            hh_mm_SS = int(hh_mm_SS[0]) * 3600 + int(hh_mm_SS[1]) * 60 + int(hh_mm_SS[2]) + 0.25
            return hh_mm_SS, 'm'
        else:
            print('Questo tempo ha troppi \':\': ' + tempo, file=f_log)

    # Se il tempo contiene un '.' allora ha anche i decimali
    # Prima controlliamo che non ce ne siano troppi
    if len(tempo.split('.')) == 3:
        print('Questo tempo ha 3 punti decimali: ' + tempo + '. Immagino il 1° punto sia per i minuti', file=f_log)
        hh_mm_SS = tempo.split('.')
        mm_SS = int(hh_mm_SS[0]) * 60 + int(hh_mm_SS[1]) + int(hh_mm_SS[2]) / 100
        return mm_SS, 'x'

    if len(tempo.split('.')) > 3:
        print('Questo tempo ha più di 2 punti decimali: ' + tempo, file=f_log)
        return -1, 'x'

    # Se è un tempo sopra il minuto
    hh_mm_in_seconds = 0
    if ':' in tempo:
        hh_mm_SS = tempo.split(':')
        if len(hh_mm_SS) == 2:
            hh_mm_in_seconds = int(hh_mm_SS[0]) * 60
            tempo = hh_mm_SS[1]
        elif len(hh_mm_SS) == 3:
            hh_mm_in_seconds = int(hh_mm_SS[0]) * 3600 + int(hh_mm_SS[1]) * 60
            tempo = hh_mm_SS[2]
        elif len(hh_mm_SS) > 3:
            print('Questo tempo ha più di due \':\' ' + tempo, file=f_log)
            return -1, 'x'

    # Conversione da possibile tempo manuale a tempo elettrico (+0.25 secondi)
    if len(tempo.split('.')[-1]) == 1: return hh_mm_in_seconds + float(tempo) + 0.25, 'm'
    elif len(tempo.split('.')[-1]) == 2: return hh_mm_in_seconds + float(tempo), 'e'
    elif len(tempo.split('.')[-1]) == 3:
        print('Questo tempo ha più di due cifre dopo il punto decimale: ' + tempo, file=f_log)
        # la fidal arrotonda i millesimi per super eccesso, quindi 10.231 diventa 10.24. Solo 10.230 rimane 10.23
        tempo = math.ceil(float(tempo) * 100) / 100
        return hh_mm_in_seconds + tempo, 'e'
    else:
        print('Questo tempo ha più di 3 cifre decimali: ' + tempo, file=f_log)
        return -1, 'x'


## Controlla l'ultimo aggiornamento delle graduatorie
def ultimo_aggiornamento_FIDAL(f_log) -> str:
    url_FIDAL = 'https://www.fidal.it/graduatorie.php'
    page = requests.get(url_FIDAL)
    data = re.search(r'aggiornati dal 2005 al \d{2}-\d{2}-\d{4}', page.text)
    if data:
        data = data.group()[-10:]
        data = data.split('-')
        return data[2] + '-' + data[1] + '-' + data[0]
    else:
        print('Nessuna data trovata', file=f_log)
        return ''













