import re
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "script"))
from my_functions import *


SMALL_SIZE = 14
MEDIUM_SIZE = 15
BIGGER_SIZE = 18

plt.rc('font', size=SMALL_SIZE)           # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)     # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)     # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)     # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize


def ottieni_dati(COD, area="società", filtro=''):
    """
    Query il DB per gli atleti di una società e plotta anno vs numero di gare.
    COD: codice società se area = società (es. BL012)
         sigla provincia se area = provincia (es. BL)
         sigle regione se area = regione (es. VEN)
    """
    OPZIONI_VALIDE = ["società", "provincia", "regione"]
    
    conn = get_db_engine().connect()

    if area == "società":
        QUERY = f"""
            SELECT
                categoria,
                sesso,
                cod_società,
                EXTRACT(YEAR FROM data)::int AS year,
                ambiente,
                COUNT(*) AS n
            FROM results
            WHERE cod_società = %(cod)s
              AND LEFT(categoria, 1) != 'E'
              {filtro}
            GROUP BY
                categoria,
                sesso,
                cod_società,
                EXTRACT(YEAR FROM data),
                ambiente;
        """
    
    elif area == "provincia":
        QUERY = f"""
            WITH r AS (
                    SELECT
                    categoria,
                    sesso,
                    LEFT(cod_società, 2) AS provincia,
                    EXTRACT(YEAR FROM data)::int AS year,
                    ambiente,
                    data
                    FROM results
                )
            SELECT
                categoria,
                sesso,
                provincia,
                year,
                ambiente,
                COUNT(*) AS n
            FROM r
            WHERE provincia = %(cod)s
              AND LEFT(categoria, 1) != 'E'
              {filtro}
            GROUP BY categoria, sesso, provincia, year, ambiente
        """

    elif area == "regione":
        QUERY = f"""
            WITH r AS (
                SELECT
                    categoria,
                    sesso,
                    LEFT(cod_società, 2) AS provincia,
                    EXTRACT(YEAR FROM data)::int AS year,
                    ambiente,
                    data
                FROM results
        )
        SELECT
            r.categoria,
            r.sesso,
            r.year,
            r.ambiente,
            COUNT(*) AS n
        FROM r
        JOIN regioni_province rp
            ON r.provincia = ANY(rp.province)
        WHERE rp.regione = %(cod)s
          AND LEFT(r.categoria, 1) != 'E'
          {filtro}
        GROUP BY r.categoria, r.sesso, r.year, r.ambiente
        """

    else:
        raise ValueError(f"'{area}' non valido. Scegli tra: {OPZIONI_VALIDE}")

    df = pd.read_sql(QUERY, conn, params={"cod": COD})
    if len(df) == 0:
        print(f"Nessun risultato per {COD}")
        return {}, []
    anni_tutti = sorted(df["year"].unique())

    # --- Dati per il grafico di sinistra: totale / indoor / outdoor / uomini / donne ---
    tot = df.groupby("year")["n"].sum().reset_index()
    tot_indoor = df[df["ambiente"] == "I"].groupby("year")["n"].sum().reset_index()
    tot_outdoor = df[df["ambiente"] == "P"].groupby("year")["n"].sum().reset_index()
    tot_uomini = df[df["sesso"] == "M"].groupby("year")["n"].sum().reset_index()
    tot_donne = df[df["sesso"] == "F"].groupby("year")["n"].sum().reset_index()

    # --- Dati per il grafico di destra: totale per categoria, sommando i due sessi ---
    # Il secondo carattere della categoria è sempre M o F (es. "SM35" / "SF35"):
    # lo rimuoviamo per ottenere una categoria "neutra" su cui sommare uomini e donne.
    df["categoria"] = df["categoria"].str[0] + df["categoria"].str[2:]

    # Raggruppa tutte le categorie Master (S35, S40, ..., S95) in un'unica voce "Master"
    df["categoria"] = df["categoria"].fillna("").apply(
        lambda c: "Master" if re.match(r"^S\d{2}$", c) else c
    )

    tot_categorie = (
            df.groupby(["categoria", "year"])["n"]
            .sum()
            .reset_index()
            )


    totale = {
        "totale": tot,
        "indoor": tot_indoor,
        "outdoor": tot_outdoor,
        "uomini": tot_uomini,
        "donne": tot_donne,
        **{
            categoria: tot_categorie[tot_categorie["categoria"] == categoria]
            for categoria in tot_categorie["categoria"].unique()
        }
    }

    totale.pop("X", None) # Categoria non identificata per risultati molto vecchi

    # Aggiungi 0 negli anni vuoti
    for k, v in totale.items():
        totale[k] = (v.set_index("year")["n"].reindex(anni_tutti, fill_value=0)
                     .rename_axis("year").reset_index())

    return totale, anni_tutti


def genera_grafico(title, totale, anni, coeff, fname=''):
    """
    Grafico sinistro: totale società, totale indoor, totale outdoor.
    Grafico destro: totale per categoria (S35-S95 raggruppate in "Master", categoria E esclusa).
    """

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 9), sharey=False)
    fig.suptitle(title, fontweight="bold")

    # --- Grafico sinistro ---
    keys = ["indoor", "outdoor", "uomini", "donne", "totale"]
    c = ["tab:blue", "tab:orange", "tab:green", "tab:red", "black"]
    m = ["<", ">", "^", "v", "s"]

    for i, k in enumerate(keys):
        last = (i == len(keys) - 1)
        years = totale[k]["year"].array
        n = totale[k]["n"].array

        # Andamento
        ax_left.plot(years[:-1], n[:-1],
                     marker=m[i],c=c[i], label=k.title(),
                     markersize=7 if last else 5,
                     linewidth=3 if last else 1.5)

        # Ulitimo anno
        #ax_left.plot(years[-1], n[-1],
        #             marker=m[i],c=c[i], label=k.title(),
        #             markersize=7 if last else 5,
        #             linewidth=3 if last else 1.5)

        # Predizione sull'ulitimo anno
        ax_left.plot(years[-2:], [n[-2], n[-1] * coeff[k]],
                     c=c[i], alpha=0.8, linestyle="--",
                     markersize=7 if last else 5,
                     linewidth=3 if last else 1.5,
                     label="Previsione" if last else "")

    ax_left.set_xlabel("Anno")
    ax_left.set_ylabel("Numero di gare")
    ax_left.set_title(f"Totale Risultati Per Anno")
    ax_left.grid(alpha=0.3)
    ax_left.set_xticks(anni)
    ax_left.tick_params(axis="x", rotation=45)
    ax_left.yaxis.set_major_locator(plt.MaxNLocator(nbins=15))
    ax_left.legend(loc="upper left")

    # --- Grafico destro ---
    categorie = totale.keys()
    dict_cat = {"R": "Rag", "C": "Cad", "A": "All", "J": "Jun", "P": "Pro", "S": "Sen", "Master": "Master"}
    c = ["#3776AB", "#FFD43B", "#2CA02C", "#D62728", "#9467BD", "#FF7F0E", "#17BECF", "#E377C2"]
    m = ["<", ">", "^", "v", "s", "o", "P"]

    for i, cat in enumerate(dict_cat.keys()):
        if cat not in categorie: continue
        years = totale[cat]["year"].array
        n = totale[cat]["n"].array

        # Andamento
        ax_right.plot(years[:-1], n[:-1], marker=m[i], markersize=5,
                      linewidth=1.5, c=c[i], label=dict_cat[cat])

        # Ultimo anno
        #ax_right.plot(years[-1], n[-1], marker=m[i], markersize=5,
        #              c=c[i], label=dict_cat[cat])

        # Predizione sull'ulitimo anno
        ax_right.plot(years[-2:], [n[-2], n[-1] * coeff[cat]],
                      linestyle="--", linewidth=1.5, c=c[i])

    ax_right.set_xlabel("Anno")
    ax_right.set_title(f"Totale per categoria")
    ax_right.grid(alpha=0.3)
    ax_right.set_xticks(anni)
    ax_right.tick_params(axis="x", rotation=45)
    ax_right.yaxis.set_major_locator(plt.MaxNLocator(nbins=15))
    ax_right.legend(loc="upper left")

    plt.tight_layout()
    if fname != '':
        plt.savefig(f"figures/{fname}.pdf", format="pdf")
    else:
        plt.show()
    plt.close()


def ottieni_dati_con_predizioni(COD, area, mese_giorno):

    totale, anni = ottieni_dati(COD, area)
    if len(anni) == 0:
        return totale, anni, 0
    filtro = f"AND TO_CHAR(data, 'MM-DD') < '{mese_giorno}'"
    if area == "regione":
        filtro = filtro.replace("data", "r.data")
    totale_red, _ = ottieni_dati(COD, area, filtro=filtro)

    coeff = {}
    avg_numb = 3 if len(anni) >= 3 else len(anni)
    for key in totale:
        if key not in totale_red \
        or (totale[key].iloc[-avg_numb:] < 5).any().any():
            coeff[key] = 1
            continue

        merged = totale[key][["year", "n"]].merge(
        totale_red[key][["year", "n"]], on="year", suffixes=("", "_red")
        )
        coeff[key] = (merged["n"] / merged["n_red"]).iloc[-avg_numb:].mean()

    return totale, anni, coeff




""" Province """
province = pd.read_csv("liste/lista_province.csv", dtype="str", keep_default_na=False)
for ii, row in province.iterrows():
    COD = row["COD"]
    print(f"{ii+1}/{len(province)} ({COD})")

    totale, anni, coeff = ottieni_dati_con_predizioni(COD, "provincia", '09-08')
    if len(anni) == 0: 
        continue

    genera_grafico(f"{row["Provincia"]} ({COD})", totale, anni, coeff, fname=f"province/{COD}")


""" Regioni """
regioni = pd.read_csv("liste/lista_regioni.csv", dtype="str", keep_default_na=False)
for ii, row in regioni.iterrows():
    COD = row["COD"]
    print(f"{ii + 1}/{len(regioni)} ({COD})")

    totale, anni, coeff = ottieni_dati_con_predizioni(COD, "regione", '09-08')
    if len(anni) == 0: 
        continue

    genera_grafico(row["Regione"], totale, anni, coeff, fname=f"regioni/{COD}")


""" Società """
societa = pd.read_csv("liste/lista_societa_250.csv", dtype="str", keep_default_na=False)
for ii, row in societa.iterrows():
    COD = row["COD"]
    print(f"{ii + 1}/{len(societa)} ({COD})")

    totale, anni, coeff = ottieni_dati_con_predizioni(COD, "società", '09-08')
    if len(anni) == 0: 
        continue

    genera_grafico(f"{COD}: {row["Società"]}", totale, anni, coeff, fname=f"societa/{COD}")
