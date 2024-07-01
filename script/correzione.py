import pandas as pd
import os

folder = '../database/outdoor/'
write_header = True

for sub_folder in os.listdir(folder):
    if sub_folder.endswith('.txt'):
        continue
    sub_folder = sub_folder + '/'

    for file in os.listdir(folder + sub_folder):
        if file.endswith('.csv'):
            print(file)

            df = pd.read_csv(folder + sub_folder + file, sep=',', header=0, dtype=str)
            
            gara = file[:-20]
            if 'cronometraggio' in df.columns:
                df_typo = df[df['cronometraggio'] == '2.0']
                df_typo.insert(0, 'gara', gara)
                df_typo.to_csv(log_file, sep=',', mode='a',index=False, header=write_header)
                write_header = False


