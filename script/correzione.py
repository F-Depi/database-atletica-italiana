import pandas as pd
import os

folder = '../database/outdoor/'
for sub_folder in os.listdir(folder):

    sub_folder = sub_folder + '/'

    log_file = folder + sub_folder + 'errori.txt'
    with open(log_file, 'w') as f_log:

        write_header = True

        for file in os.listdir(folder + sub_folder):
            if file.endswith('.csv'):
                print(file)

                df = pd.read_csv(folder + sub_folder + file, sep=',', header=0, dtype=str)
                
                gara = file[:-20]
                if 'cronometraggio' in df.columns:
                    df_typo = df[df['cronometraggio'] == '2.0']
                    df_typo['gara'] = gara
                    df_typo.to_csv(folder + sub_folder + log_file, sep=',', mode='a',index=False, header=write_header)
                    write_header = False


