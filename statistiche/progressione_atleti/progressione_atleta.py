from script.my_functions import get_db_engine
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import text

SMALL_SIZE = 13
MEDIUM_SIZE = 18
BIGGER_SIZE = 18

plt.rc('font', size=SMALL_SIZE)
plt.rc('axes', titlesize=BIGGER_SIZE)
plt.rc('axes', labelsize=MEDIUM_SIZE)
plt.rc('xtick', labelsize=SMALL_SIZE)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('legend', fontsize=MEDIUM_SIZE)


def due_discipline_atleta(link_atleta, discipline, SB, y_lim, conn, save=False):
    disc = tuple(discipline)

# Query per 100m ostacoli
    query = text(f"""SELECT * FROM results
        WHERE disciplina in {disc}
        AND link_atleta = '{link_atleta}'
        AND categoria not LIKE 'E%'
        AND categoria not LIKE 'R%'
        """)
    df = pd.read_sql_query(query, conn)
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
    df['anno'] = df['data'].dt.year


    data0 = df[df['disciplina'] == discipline[0]][['data', 'prestazione']]
    data1 = df[df['disciplina'] == discipline[1]][['data', 'prestazione']]

    data0_SB = (df[df['disciplina'] == discipline[0]]
             .loc[df[df['disciplina'] == discipline[0]].groupby('anno')['prestazione'].idxmin()]
             [['data', 'prestazione']])
    data1_SB = (df[df['disciplina'] == discipline[1]]
             .loc[df[df['disciplina'] == discipline[1]].groupby('anno')['prestazione'].idxmin()]
             [['data', 'prestazione']])

    plt.figure(figsize=(12, 7))
    if not SB:
        plt.plot(data0['data'], data0['prestazione'], 'o', label=discipline[0].replace('_', ' ').title())
        plt.plot(data1['data'], data1['prestazione'], 'o', label=discipline[1].replace('_', ' ').title())
    plt.plot(data0_SB['data'], data0_SB['prestazione'], 's-', label=discipline[0].replace('_', ' ').title() + ' SB')
    plt.plot(data1_SB['data'], data1_SB['prestazione'], 's-', label=discipline[1].replace('_', ' ').title() + ' SB')
    plt.ylim(y_lim)

    plt.xlabel('Data')
    plt.ylabel('Tempo [s]')
    plt.title(f'Progressione di {df['atleta'].iloc[0]} in {", ".join(discipline)}')


    ax = plt.gca()

    dict_xlabel = df.groupby('anno')['categoria'].first().to_dict()
    ax.set_xticks([pd.Timestamp(f'{a}-01-01') for a in dict_xlabel.keys()])
    ax.set_xticklabels([f"{a}\n{c}" for a, c in dict_xlabel.items()])

    plt.grid()
    plt.legend()
    plt.tight_layout()
    if save:
        plt.savefig(f'statistiche/progressione_atleti/progressione_{df["atleta"].iloc[0].replace(" ", "_")}_{"_".join(discipline)}.png', dpi=400)
    else:
        plt.show()


conn = get_db_engine().connect()

""" Donne """
#link_atleti = ['https://www.fidal.it/atleta/CARMASSI-Giada/eayRk5SjbmY%3D',
#              'https://www.fidal.it/atleta/BESANA-Veronica/dquRkpmfamM%3D',
#              'https://www.fidal.it/atleta/BOGLIOLO-Luminosa/dayRkpKga2g%3D',
#              'https://www.fidal.it/atleta/DI-LAZZARO-Elisa-maria/eauRkpuiaWQ%3D',
#              'https://www.fidal.it/atleta/WEGIERSKA-Angelika-elzbieta/eayRk5amaWs%3D',
#              'https://www.fidal.it/atleta/RICCARDI-Giulia/d6iRk5SoaGU%3D']
#
#
#discipline = ['100m', '100Hs_h84-8.50']
#SB = False
#y_lim = (11.0, 16.0)
#
#for link in link_atleti:
#    due_discipline_atleta(link, discipline, SB, y_lim, conn, save=True)


""" Uomini """
link_atleti = ['https://www.fidal.it/atleta/SIMONELLI-Lorenzo-ndele/f6yRkpqnbGg%3D',
               'https://www.fidal.it/atleta/DAL-MOLIN-Paolo/dK6RlJmlaGQ%3D',
               'https://www.fidal.it/atleta/PERINI-Lorenzo/drKRkpSncWk%3D',
               'https://www.fidal.it/atleta/GIACALONE-Nicolo-/f6yRkpama2w%3D',
               'https://www.fidal.it/atleta/GHEDINA-Vittorio/eKmRlJagbGY%3D',
               'https://www.fidal.it/atleta/DE-PAOLI-Federico/eKmRlJmfcWs%3D']

discipline = ['60m', '60Hs_h106-9.14']
SB = False
y_lim = (6.5, 9.0)

#discipline = ['100m', '110Hs_h106-9.14']
#SB = False
#y_lim = (10.0, 16.0)

for link in link_atleti:
    due_discipline_atleta(link, discipline, SB, y_lim, conn, save=True)
