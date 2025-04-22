import os
import sys
import json
import psycopg2
import pandas as pd
from sqlalchemy import create_engine, text

'''
Aggiorna il database postreSQL del PC, consigurato in config.py, con i dati
di database.
create_tables() è stata runnata solo la prima volta per creare la tabella.
import_data() può rigenerare completamente il database oppure aggiornare solo
i dati dell'anno in corso.
'''

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG


## Permette di aprire un file del database di csv con pandas
def get_file_database(ambiente, gara) -> pd.DataFrame | None:

    if ambiente == 'I':
        foldername = '../database-atletica-csv/indoor/'
    elif ambiente == 'P':
        foldername = '../database-atletica-csv/outdoor/'
    else:
        print('\nGli ambienti possibili sono: \'I\', \'P\'\n')
        exit()

    filename = ''
    for subfolder in os.listdir(foldername):
        if subfolder[-3:] == 'csv':continue
        for file in os.listdir(foldername + subfolder):
            if file[:-15] == gara:
                filename = foldername + subfolder + '/' +  file
                break
    if filename == '':
        print(f'\nWARNING: Gara {gara} non trovata in {foldername}\n')
        return None


    col_dtype = json.load(open('script/colonne_dtype.json'))
    df = pd.read_csv(filename, dtype=col_dtype)

    return df


def get_sqlalchemy_connection_string():
    return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"


def create_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Drop existing table and all its indexes
        cur.execute("DROP TABLE IF EXISTS results CASCADE")
        
        # Create table and indexes
        cur.execute("""
            CREATE TABLE results (
                id SERIAL PRIMARY KEY,
                prestazione FLOAT,
                vento VARCHAR(10),
                tempo VARCHAR(20),
                cronometraggio VARCHAR(20),
                atleta VARCHAR(100),
                anno VARCHAR(4),
                categoria VARCHAR(20),
                società VARCHAR(100),
                posizione VARCHAR(10),
                luogo VARCHAR(100),
                data DATE,
                link_atleta VARCHAR(200),
                link_società VARCHAR(200),
                disciplina VARCHAR(50),
                ambiente CHAR(1),
                sesso CHAR(1),
                cod_società CHAR(5)
            );
            
            CREATE INDEX idx_prestazione ON results(prestazione);
            CREATE INDEX idx_disciplina ON results(disciplina);
        """)
        
        conn.commit()
        print("Table and indexes created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        
    finally:
        cur.close()
        conn.close()


# Importa i dati dai csv al database postgreSQL di cui è salvata la
# configurazione in config.py.
# update=False sovraiscrive tutto
# update=True cancella dal database SQL i dati dell'anno in corso e copia li
# riscrive copiandoli dal csv
def import_data(update=False):
    # Create SQLAlchemy engine
    engine = create_engine(get_sqlalchemy_connection_string())
    current_year = pd.Timestamp.now().year

    if update:
        # Delete all current year results
        with engine.connect() as conn:
                conn.execute(
                    text(f"DELETE FROM results WHERE EXTRACT(YEAR FROM data) = {current_year}")
                )
                conn.commit()
                print(f"Deleted existing {current_year} records")
    
    # Load disciplines
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
              'script', 'dizionario_gare.json')) as f:
        disciplines = json.load(f)
    
    try:
        for discipline in disciplines:
            for ambiente in ['I', 'P']:
                print(f"Processing {discipline} - {ambiente}")
                df = get_file_database(ambiente, discipline)
                if df is not None:
                    # Import df to PostgreSQL
                    df['disciplina'] = discipline
                    df['ambiente'] = ambiente
                    df['sesso'] = df['categoria'].str[1]
                    df['cod_società'] = df['link_società'].str[-5:]
                    
                    # Convert data column to datetime if it exists
                    if 'data' in df.columns:
                        df['data'] = pd.to_datetime(df['data'])
                    
                    if update:
                        df = df[df['data'].dt.year == int(current_year)]
                    
                    # Use SQLAlchemy to write to database
                    df.to_sql('results', 
                             engine, 
                             if_exists='append', 
                             index=False,
                             method='multi',
                             chunksize=1000)
                    
                    print(f"Imported {len(df)} rows for {discipline} - {ambiente}")
    
    except Exception as e:
        print(f"Error during import: {e}")
    
    finally:
        engine.dispose()



if __name__ == "__main__":
    #create_tables()
    import_data(update=True)
