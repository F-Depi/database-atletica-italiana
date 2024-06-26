import requests
from bs4 import BeautifulSoup
import pandas as pd


## Scarica una pagina e mette i dati in un DataFrame
def get_data_FIDAL(anno, tipo_att, sesso, cat, gara, tip_estr, vento, regione, naz, limite, societa):
    
    cat = cat[0] + sesso + cat[1:]

    url_FIDAL = 'https://www.fidal.it/graduatorie.php?anno='+anno+'&tipo_attivita='+tipo_att+'&sesso='+sesso+'&categoria='+cat+'&gara='+gara+'&tipologia_estrazione='+tip_estr+'&vento='+vento+'&regione='+regione+'&nazionalita='+naz+'&limite='+limite+'&societa='+societa+'&submit=Invia'

    print(url_FIDAL)

    # Scarico la pagina
    page = requests.get(url_FIDAL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    # Rimuovo la riga con i nomi delle colonne
    data_row = soup.find_all('tr')[1:]
    
    # Rimuovo le righe (una ogni 10 prestazioni) che contengono il numero di prestazioni (10, 20, 30, ...)
    # Ho quindi che la riga 11, 22, 33, ... contengono il numero di prestazioni e vanno rimosse
    data_row = [row for i, row in enumerate(data_row) if (i+1) % 11 != 0]

    if len(data_row) == 0:
        print('Nessun dato trovato')
        return pd.DataFrame()

    if 'colspan="8"' in str(data_row[-1]):
        data_row = data_row[:-1]
    
    # La tabella ha sempre le stesse 8 colonne, quindi mi fido a creare il data frame e mettere dentro i dari di data_row uno alla volta. Aggiungo 2 colonne per i link
    df_data = pd.DataFrame(index = range(len(data_row)), columns=['Prestazione', 'Vento', 'Atleta', 'Anno', 'Società', 'Posizione', 'Luogo', 'Data', 'Link Atleta', 'Link Società', 'Categoria'])

    for i, row in enumerate(data_row):
    
        j = 0
        for cell in row.find_all('td'):
            cell = cell.text.strip()
            if j == 3: cell = check_anno(cell, i)
            if j == 7: cell = check_data(cell, anno, i)
            df_data.iat[i, j] = cell
            j += 1
    
        data_a = row.find_all('a')
        if len(data_a) > 1:
            df_data.iat[i, j] = data_a[0].get('href')
            df_data.iat[i, j+1] = data_a[1].get('href')
        df_data.iat[i, j+2] = assegna_categoria(df_data.at[i, 'Anno'], df_data.at[i, 'Data'], sesso, cat)

    df_data = df_data[['Prestazione', 'Vento', 'Atleta', 'Anno', 'Categoria', 'Società', 'Posizione', 'Luogo', 'Data', 'Link Atleta', 'Link Società']]

    return df_data


## Alla Fidal non piace scrive l'anno con 4 cifre, quindi scrivono solo le ultime due. Questa funzione aggiunge il 19 o il 20 davanti.
def check_anno(cell, i):
    if cell == '':
        print('Anno non disponibile in riga', i)
        return cell
    else:
        anno = int(cell)
        if anno > 24:
            return str(1900 + anno)
        else:
            return str(2000 + anno)


## Alla Fidal non piace scrivere la data in formato standard, quindi la scrivono in modo strano e senza l'anno. Questa funzione la mette in formato standard.
def check_data(cell, anno, i):
    if cell == '':
        print('Data non disponibile in riga', i)
        return cell
    else:
        data = cell.split('/')
        return anno + '-' + data[1] + '-' + data[0]


## 
def assegna_categoria(anno_atleta, data_prestazione, sesso, categoria):
    if anno_atleta == '': return categoria
    if data_prestazione == '': return categoria
    eta = int(data_prestazione[:4]) - int(anno_atleta)
    if eta < 6:
        print('Atleta troppo giovane, età:', eta)
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



















