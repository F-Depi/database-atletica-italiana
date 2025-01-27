import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SMALL_SIZE = 13
MEDIUM_SIZE = 18
BIGGER_SIZE = 18

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize


def eta_atleta(df_row):
    giorno_gara = int(df_row['data'][:4])
    anno_nascita = str(df_row['anno'])
    if len(anno_nascita) < 4:
        return -1

    anno_nascita = int(anno_nascita[:4])
    return giorno_gara - anno_nascita


def istogramma_cat():
    data = pd.read_csv('60m_2025-01-24.csv')

    dataM = data[data['categoria'].str.contains('M', na=False)]
    dataF = data[data['categoria'].str.contains('F', na=False)]

    ## Tolgo le righe con prestazione maggiore di 12 secondi
    dataM = dataM[dataM['prestazione'] < 12]
    dataF = dataF[dataF['prestazione'] < 12]

    fig, ax = plt.subplots(2, 3)
    fig.suptitle('Distribuzione dei risultati nei 60m piani indoor')
    fig.tight_layout()
    ax = ax.flatten()
    ax[0].hist(dataM['prestazione'], bins=50, alpha=0.5, label='Uomini, tot ' + str(len(dataM['prestazione'])))
    ax[0].hist(dataF['prestazione'], bins=50, alpha=0.5, label='Donne, tot ' + str(len(dataF['prestazione'])))
    #ax[0].axvline(np.mean(dataM['prestazione']))
    #ax[0].axvline(np.mean(dataF['prestazione']))
    ax[0].set_title('Tutte le categorie')
    ax[0].legend()

    ## Ora vediamo un plot per ogni categoria
    ii = 1
    categorie = ['Cadetti', 'Allievi', 'Junior', 'Promesse', 'Senior U35']
    for cat in ['C', 'A', 'J', 'P', 'S']:
        tM = dataM[dataM['categoria'] == cat+'M']['prestazione']
        tF = dataF[dataF['categoria'] == cat+'F']['prestazione']
        ax[ii].hist(tM, bins=50, alpha=0.5, label='Uomini, tot ' + str(len(tM)))
        ax[ii].hist(tF, bins=50, alpha=0.5, label='Donne, tot ' + str(len(tF)))
        #ax[ii].axvline(np.mean(tM))
        #ax[ii].axvline(np.mean(tF))
        ax[ii].set_title('Categoria ' + categorie[ii-1])
        ax[ii].legend()
        ii += 1

    plt.show()


def andamento_partecipazione_cat():
    data = pd.read_csv('60m_2025-01-24.csv')
    
    # Per comodità aggiungiamo una colonna con l'età dell'atleta
    anni_atleta = data.apply(eta_atleta, axis=1)
    data['anni_atleta'] = anni_atleta

    dataM = data[data['categoria'].str.contains('M', na=False)]
    dataF = data[data['categoria'].str.contains('F', na=False)]

    # Numero di risultati per categoria
    anni = range(14,35)
    N_ris_M = np.zeros(len(anni))
    N_ris_F = np.zeros(len(anni))

    ii = 0
    for eta in anni:
        N_ris_M[ii] = len(dataM[dataM['anni_atleta'] == eta])
        N_ris_F[ii] = len(dataF[dataF['anni_atleta'] == eta])
        ii += 1

    plt.figure()
    plt.plot(anni, N_ris_M, linestyle=' ', marker='o', label='Uomini')
    plt.plot(anni, N_ris_F, linestyle=' ', marker='o', label='Donne')
    plt.xlabel('Età atleta [anni]')
    plt.ylabel('# risultati')
    plt.title('Andamento del numero dei risultati nei 60m piani indoor con l\'età dei partecipanti')
    plt.legend()
    tiks = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 27, 29, 31, 33]
    lab_tiks = ['C1','C2','A1','A2','J1', 'J2', 'P1', 'P2', 'P3', 23, 25, 27, 29, 31, 33]
    plt.xticks(tiks, lab_tiks)
    plt.tight_layout()
    plt.show()

## Istogramma con distribuzione dei tempi per le diverse categorie
#istogramma_cat()

## Andamento della partecipazione negli anni per le categorie
andamento_partecipazione_cat()
