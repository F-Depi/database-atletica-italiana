import pandas as pd
import math
from my_functions import conversione_manuale_elettrico

file = 'database/80m_2005_2024-06-25.csv'
file_out = 'database/outdoor/80m_2005_2024-06-25.csv'
df = pd.read_csv(file, sep=',', header=0, dtype=str)
df = df.rename(columns={'Prestazione': 'tempo', 'Vento': 'vento', 'Atleta': 'atleta', 'Anno': 'anno', 'Categoria': 'categoria', 'Società': 'società', 'Posizione': 'posizione', 'Luogo': 'luogo', 'Data': 'data', 'Link Atleta': 'link_atleta', 'Link Società': 'link_società'})

df['prestazione'], df['cronometraggio'] = zip(*df.apply(conversione_manuale_elettrico, axis=1))
df = df[['prestazione', 'vento', 'tempo', 'cronometraggio', 'atleta', 'anno', 'categoria', 'società', 'posizione', 'luogo', 'data', 'link_atleta', 'link_società']]
df = df.sort_values(by=['prestazione', 'cronometraggio'], ascending=[True, True])

df.to_csv(file_out , sep=',', index=False)
