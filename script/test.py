import sys
import os

from numpy import broadcast_arrays
from my_functions import *

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

'''
dict_gare = json.load(open('script/dizionario_gare.json'))

anno = '2024'
ambiente = 'P'
sesso = 'M'
cat = 'X'
gara = '80m'
tip_estr = '1'
vento = '2'
regione = '0'
naz = '2'
lim = '0'
societa = ''

with open('log.txt', 'w') as f_log:
    df = get_data_FIDAL(anno, ambiente, sesso, cat, dict_gare[gara]['codice'], tip_estr, vento, regione, naz, lim, societa, f_log)
    df = format_data_FIDAL(df, gara, ambiente, f_log)
    folder = 'test/'+ dict_gare[gara]['tipo'] + '/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    file = folder + gara.replace(' ', '_') + '_' + anno + '.csv'
    if df is not None:
        df.to_csv(file, index=False)
'''

# Make pandas show full strings
pd.set_option('display.max_colwidth', None)  # or a large number
pd.set_option('display.max_columns', None)   # show all columns
pd.set_option('display.max_rows', None)      # show all rows

gara = 'lungo'
df = get_file_database('P', gara)
print('Results '+gara+':\t\t\t', len(df))

## Print the first duplicate that appears
df = df[(df['categoria'] != 'RM')]
df = df[(df['categoria'] != 'RF')]
df = df[(df['categoria'] != 'EM')]
df = df[(df['categoria'] != 'EF')]
duplicate_rows = df[df.duplicated()]
for _, r in duplicate_rows.iterrows():
    print(f'{r['prestazione']} \t {r['link_atleta']} \t {r['luogo']} {r['data']}')




cat = 'C'
df_E = df[(df['categoria'] == cat + 'M') | (df['categoria'] == cat + 'F')]
tot = len(df_E)
print(f'Total results ('+cat+'):\t\t', tot)
#print('Expected unique (tot/3)\t\t', tot / 3)
print('Expected unique (tot/2)\t\t', tot / 2)
df_E = df_E.drop_duplicates()
unique = len(df_E)
print('Unique results:\t\t\t', unique)

legit_duplicates = (tot - 3 * len(df_E)) / 3
#print('\nEstimated legit duplicates:\t', tot/3 - len(df_E))

#prev_year = 2000
#for i, row in df.iterrows():
#    year = int(row['data'][:4])
#    if prev_year > year:
#        print(i)
#        break
#
#    prev_year = year
#
#df_half = df[:i]
#df_half_E = df_half[(df_half['categoria'] == cat + 'M') | (df_half['categoria'] == cat + 'F')]
#first_E_scraped = len(df_half_E)
#print('Unici + duplicati legittimi:', first_E_scraped)
#print('Expected tot from those: ', 3 * (first_E_scraped + legit_duplicates))

## Weird deduplication where we keep a duplicate if it appears within 10 rows
#prev_rows = df.iloc[:10]
#already_seen = set()
#for i, row in df.iterrows():
#    if i < 9:                                                       #pyright: ignore
#        continue
#    if row['prestazione'] in already_seen:
        


