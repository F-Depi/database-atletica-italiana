import logging

import pandas as pd
from sqlalchemy import text

from my_functions import *

"""
Script per aggiornare automaticamente il database con i dati nuovi delle
graduatorie.
Il database viene aggiornato guardando l'ultimo anno presente. Tutti i dati di
quell'anno vengono cancellati e riscaricati.
Se l'ultimo anno presente non era quello in corso, vengono scaricati anche gli
anni successivi.
Aggiorno a chunk di 1 anno intero perché:
    - è più semplice
    - alcuni risultati potrebbero essere stati fatti riconoscere a posteriori
      (es. prestazioni ottenute all'estero)

Log:
    - status.log        -> avanzamento (INFO/WARNING)
    - error.log         -> errori con traceback
    - visited_links.log -> link visitati (scritto da my_functions via f_log)
"""

tieni_correzioni_manuali = False
force_update = False
last_server_update = ultimo_aggiornamento_FIDAL()

DEDUP_COLS = [
    "atleta", "anno", "categoria", "società", "posizione",
    "luogo", "data", "link_atleta", "link_società",
]

REFRESH_ATLETI_SQL = [
    "TRUNCATE atleti",
    """
    INSERT INTO atleti
    WITH latest_info AS (
        SELECT
            link_atleta, atleta, categoria, società, anno,
            ROW_NUMBER() OVER (PARTITION BY link_atleta ORDER BY data DESC) AS rn
        FROM results
    )
    SELECT link_atleta, atleta, categoria, società, anno
    FROM latest_info
    WHERE rn = 1
    """,
]

log = logging.getLogger("aggiornamento")


def setup_logging():
    """status.log: messaggi sotto ERROR. error.log: solo errori (con traceback)."""
    log.setLevel(logging.INFO)
    log.handlers.clear()

    status = logging.FileHandler("status.log", mode="w", encoding="utf-8")
    status.setLevel(logging.INFO)
    status.addFilter(lambda r: r.levelno < logging.ERROR)
    status.setFormatter(logging.Formatter("%(message)s"))

    error = logging.FileHandler("error.log", mode="w", encoding="utf-8")
    error.setLevel(logging.ERROR)
    error.setFormatter(logging.Formatter("%(asctime)s %(message)s"))

    log.addHandler(status)
    log.addHandler(error)


def scarica_dati(codice, ambiente, years, regioni, f_log):
    """Scarica tutte le graduatorie (nazionali e regionali) per gli anni dati."""
    frames = []
    for year in years:
        for cat in ["C", "X"]:
            for sesso in ["M", "F"]:
                frames.append(get_data_FIDAL(
                    str(year), ambiente, sesso, cat, codice,
                    "1", "2", "0", "2", "0", "", f_log,
                ))

        # Le graduatorie ragazzi esistono solo regionalmente
        for sesso in ["M", "F"]:
            for reg in regioni:
                frames.append(get_data_FIDAL(
                    str(year), ambiente, sesso, "R", codice,
                    "1", "2", reg, "2", "0", "", f_log,
                ))

    return pd.concat(frames) if frames else pd.DataFrame()


def unisci_correzioni_manuali(df_new, conn, where_clause, params):
    """
    Aggiunge i risultati nuovi tenendo le correzioni manuali già nel DB.
    Deduplico senza guardare il tempo (che è quello con l'errore) tenendo la
    prima copia, ovvero la versione già corretta nel mio DB.
    """
    df_old = pd.read_sql(text(f"SELECT * FROM results {where_clause}"), conn, params=params)
    df = pd.concat([df_old, df_new]).drop_duplicates(subset=DEDUP_COLS, keep="first")
    return df.reset_index(drop=True)


def pulisci(df, disciplina, ambiente, f_log):
    """Controlli, filtri e colonne derivate prima del salvataggio."""
    check_errori(df, disciplina, f_log)

    if "cronometraggio" in df.columns:
        df = df[df["cronometraggio"] != "x"]
    df = df[df["prestazione"] > 0]
    df = df.drop(columns=["id"], errors="ignore")

    df = df.copy()
    df["disciplina"] = disciplina
    df["ambiente"] = ambiente
    df["sesso"] = df["categoria"].str[1]
    df["cod_società"] = df["link_società"].str[-5:]
    return df


def aggiorna_ambiente(conn, riga, ambiente, regioni, f_log):
    """Aggiorna una singola coppia disciplina/ambiente."""
    disciplina = riga["disciplina"]
    ult_agg = riga["ultimo_aggiornamento"].strftime("%Y-%m-%d")
    years = range(int(ult_agg[:4]), int(last_server_update[:4]) + 1)

    log.info("Aggiorno %s %s", disciplina, ambiente)

    df_new = scarica_dati(riga["codice"], ambiente, years, regioni, f_log)
    if df_new.empty:
        log.info("Nessun dato trovato per %s %s", disciplina, ambiente)
        return

    df_new = format_data_FIDAL(df_new, disciplina, ambiente, f_log).drop_duplicates()

    where_clause = """WHERE disciplina = :disciplina
                      AND data >= :data_inizio
                      AND ambiente = :ambiente"""
    params = {
        "disciplina": disciplina,
        "data_inizio": f"{years[0]}-01-01",
        "ambiente": ambiente,
    }

    # Altrimenti ignoro i risultati già presenti perché li ho appena riscaricati
    # più aggiornati (utile se la FIDAL corregge errori a posteriori)
    if tieni_correzioni_manuali:
        df = unisci_correzioni_manuali(df_new, conn, where_clause, params)
    else:
        df = df_new

    df = pulisci(df, disciplina, ambiente, f_log)

    conn.execute(text(f"DELETE FROM results {where_clause}"), params)
    df.to_sql("results", conn, if_exists="append", index=False,
              method="multi", chunksize=1000)
    conn.commit()


def aggiorna_disciplina(conn, riga, regioni, f_log):
    for ambiente in ["I", "P"]:
        aggiorna_ambiente(conn, riga, ambiente, regioni, f_log)

    conn.execute(
        text("UPDATE discipline SET ultimo_aggiornamento = CURRENT_TIMESTAMP "
             "WHERE disciplina = :d"),
        {"d": riga["disciplina"]},
    )
    conn.commit()


def refresh_tabelle_derivate(conn):
    for stmt in REFRESH_ATLETI_SQL:
        conn.execute(text(stmt))
    conn.commit()
    log.info("✅ atleti table refreshed successfully.")

    # Vista materializzata usata per velocizzare la ricerca sul sito
    conn.execute(text("REFRESH MATERIALIZED VIEW societa"))
    conn.commit()


def main():
    setup_logging()

    with open("visited_links.log", "w", buffering=1) as f_log, \
         get_db_engine().connect() as conn:

        df_discipline = pd.read_sql("SELECT * FROM discipline", conn)
        regioni = {row.regione: row.province
                   for row in conn.execute(text("SELECT * FROM regioni_province"))}

        updated_something = False

        for _, riga in df_discipline.iterrows():
            disciplina = riga["disciplina"]
            ult_agg = riga["ultimo_aggiornamento"].strftime("%Y-%m-%d")

            if ult_agg >= last_server_update and not force_update:
                log.info("%s è già aggiornata", disciplina)
                continue

            updated_something = True
            try:
                aggiorna_disciplina(conn, riga, regioni, f_log)
            except Exception:
                conn.rollback()  # altrimenti la transazione resta abortita
                log.exception("======== Error during the update of %s ==========", disciplina)
                log.warning("There was an error, go look at error.log")

            log.info("-" * 90)

        if updated_something:
            refresh_tabelle_derivate(conn)

        log.info("updated_something: %s", updated_something)


if __name__ == "__main__":
    main()
