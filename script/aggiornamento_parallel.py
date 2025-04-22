import concurrent.futures
import pandas as pd
import json
import os
import threading
from my_functions import get_data_FIDAL, format_data_FIDAL, ultimo_aggiornamento_FIDAL

'''
Permette di fare quello che fa main.py ma in parallelo per tagliare sui tempi di risposta del server fidal.
ATTENZIONE che già con 100 richieste in simultanea la pagina fidal.it aveva smesso di rispondere.
Con 20 richieste in parallelo per scaricare esordienti e ragazzi ci ho messo una cosa come 5 ore.
2025-04-20 01:38 on this site nothing happened. Sito della fidal crashato dopo un paio d'ore di 100 richeste al secondo.
Ripartito solo la mattina quando è stato probabilmente riavviato manualmente. Scusa Mei.
'''

write_lock = threading.Lock()

def process_combination(args):
    anno, cat, sesso, reg, gara, ambiente, ambiente_folder, cod_gara, tipo_gara, data_agg, f_log_path = args
    from io import StringIO

    # Redirect log to in-memory buffer to avoid writing from multiple threads at once
    log_buffer = StringIO()
    print(anno, cat, sesso, reg, file=log_buffer)

    folder = f'database/{ambiente_folder}/{tipo_gara}/'
    os.makedirs(folder, exist_ok=True)
    file = folder + gara + '_' + data_agg + '.csv'

    try:
        df = get_data_FIDAL(anno, ambiente, sesso, cat, cod_gara, '1', '2', reg, '2', '0', '', log_buffer)
        df = format_data_FIDAL(df, gara, ambiente, f_log=log_buffer)
        if df is not None:
            with write_lock:
                write_header = not os.path.exists(file)
                df.to_csv(file, index=False, mode='a', header=write_header)
                df.to_csv(file, index=False, mode='a', header=not os.path.exists(file))
    except Exception as e:
        print(f"Error for {anno} {cat} {sesso} {reg}: {e}", file=log_buffer)

    # Write log buffer to actual log file
    with write_lock:  # also locking log write just to be extra safe
        with open(f_log_path, 'a') as f_log:
            f_log.write(log_buffer.getvalue())
    log_buffer.close()

# Prep common variables
dict_gare = json.load(open('script/dizionario_gare.json'))
dict_reg_prov = json.load(open('script/regioni_province.json'))
data_agg = ultimo_aggiornamento_FIDAL()

# Log file
f_log_path = 'nottata_I.log'
open(f_log_path, 'w').close()  # clear previous log

# Prepare arguments for parallel execution
tasks = []

#for ambiente, ambiente_folder in zip(['P', 'I'], ['outdoor', 'indoor']):

ambiente = 'I'
ambiente_folder = 'indoor'
for gara in dict_gare.keys():
    cod_gara = dict_gare[gara]['codice']
    tipo_gara = dict_gare[gara]['tipo']
    for anno in range(2005, pd.Timestamp.now().year):
        anno = str(anno)
        for cat in ['E', 'R']:
            for sesso in ['M', 'F']:
                for reg in dict_reg_prov.keys():
                    tasks.append((anno, cat, sesso, reg, gara, ambiente, ambiente_folder,
                                  cod_gara, tipo_gara, data_agg, f_log_path))

print(len(tasks))
# Run tasks in parallel (adjust max_workers as needed)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    list(executor.map(process_combination, tasks))

