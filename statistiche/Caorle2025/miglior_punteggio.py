from script.config import DB_CONFIG
from sqlalchemy import create_engine, text
import pandas as pd

# Risultati
def get_sqlalchemy_connection_string():
    """Generates the connection string for SQLAlchemy."""
    return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"


def get_db_engine():
    """Create and return SQLAlchemy engine."""
    connection_string = get_sqlalchemy_connection_string()
    return create_engine(connection_string)

with get_db_engine().connect() as conn:
    query = text("""
                 SELECT * FROM results
                 WHERE luogo LIKE 'Caorle%'
                 AND data BETWEEN DATE '2025-08-02' AND DATE '2025-08-03'
                 """)
    df = pd.read_sql(query, conn)

df_M = df[df['sesso'] == 'M']
df_F = df[df['sesso'] == 'F']

# Punteggi
import json

def time_to_seconds(str_time):
    parts = str_time.strip().split(':')
    try:
        parts = [float(p) for p in parts]
    except Exception:
        # If not split by colons, assume simple seconds format
        return str_time
    if len(parts) == 3:  # HH:MM:SS.ss
        return f"{parts[0]*3600 + parts[1]*60 + parts[2]:.2f}"
    elif len(parts) == 2:  # MM:SS.ss
        return f"{parts[0]*60 + parts[1]:.2f}"
    elif len(parts) == 1:
        return f"{parts[0]:.2f}"
    else:
        raise ValueError(f"Invalid time format: {str_time}")

def convert_keys_to_seconds(score_M):
    new_score_M = {}
    for disciplina, results in score_M.items():
        new_results = {}
        for key, value in results.items():
            try:
                sec = time_to_seconds(key)
                new_results[sec] = value
            except Exception as e:
                print(f"Skipping key {key}: {e}")
        new_score_M[disciplina] = new_results
    return new_score_M

# Use it:

score_M = json.load(open("statistiche/WA-Scoring-tables/2025_men_points_lookup.json"))
score_M = convert_keys_to_seconds(score_M)
df_to_json_key_M = json.load(open("statistiche/WA-Scoring-tables/discipline_dict_men.json"))

score_W = json.load(open("statistiche/WA-Scoring-tables/2025_women_points_lookup.json"))
score_W = convert_keys_to_seconds(score_W)
df_to_json_key_F = json.load(open("statistiche/WA-Scoring-tables/discipline_dict_women.json"))

def get_score(row):
    if row['sesso'] == 'M':
        disciplina_key = df_to_json_key_M[row['disciplina']]
        score_dict = score_M
    else:
        disciplina_key = df_to_json_key_F[row['disciplina']]
        score_dict = score_W

    prestazione = round(float(row['prestazione']), 2)

    i = 0
    while i < 200:
        try:
            score = score_dict[disciplina_key][f"{prestazione:.2f}"]
            i = 300
        except:
            prestazione += 0.01
            i += 1
    
    if i == 200:
        print(disciplina_key, prestazione)
        exit()

    return score


df['punteggio-WA'] = df.apply(get_score, axis=1)
df = df.sort_values(by='punteggio-WA', ascending=False).reset_index(drop=True)
df.index += 1
to_print = df[['punteggio-WA', 'prestazione', 'vento', 'disciplina', 'atleta', 'categoria', 'società']]
to_print.to_csv('statistiche/Caorle2025/risultati_per_punteggioWA.csv')
print(to_print)




