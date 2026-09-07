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



def genera_grafico(COD_SOCIETA, save=False):
    """
    Query il DB per gli atleti di una società e plotta anno vs numero di gare.
    Grafico sinistro: totale società, totale indoor, totale outdoor.
    Grafico destro: totale per categoria (S35-S95 raggruppate in "Master", categoria E esclusa).
    """

    conn = get_db_engine().connect()

    QUERY = """
        SELECT categoria,
               sesso,
               cod_società,
               EXTRACT(YEAR FROM data)::int AS year,
               ambiente,
               COUNT(*) AS n
        FROM results
        WHERE cod_società = %(cod)s
        GROUP BY categoria, sesso, cod_società, year, ambiente
        ORDER BY categoria, year, ambiente;
    """

    df = pd.read_sql(QUERY, conn, params={"cod": COD_SOCIETA})
    anni_tutti = sorted(df["year"].unique())

    NOME_QUERY = """
        SELECT società
        FROM results
        WHERE cod_società = %(cod)s
        ORDER BY data DESC
        LIMIT 1;
    """
    nome_societa_row = pd.read_sql(NOME_QUERY, conn, params={"cod": COD_SOCIETA})
    nome_societa = (
        nome_societa_row["società"].iloc[0]
        if not nome_societa_row.empty
        else COD_SOCIETA.upper()
    )

    # --- Dati per il grafico di sinistra: totale / indoor / outdoor / uomini / donne ---
    tot_societa = df.groupby("year")["n"].sum().reset_index()
    tot_indoor = df[df["ambiente"] == "I"].groupby("year")["n"].sum().reset_index()
    tot_outdoor = df[df["ambiente"] == "P"].groupby("year")["n"].sum().reset_index()
    tot_uomini = df[df["sesso"] == "M"].groupby("year")["n"].sum().reset_index()
    tot_donne = df[df["sesso"] == "F"].groupby("year")["n"].sum().reset_index()

    # --- Dati per il grafico di destra: totale per categoria, sommando i due sessi ---
    # Il secondo carattere della categoria è sempre M o F (es. "SM35" / "SF35"):
    # lo rimuoviamo per ottenere una categoria "neutra" su cui sommare uomini e donne.
    df["categoria_base"] = df["categoria"].str[0] + df["categoria"].str[2:]

    # Rimuove la categoria "E"
    df = df[df["categoria_base"] != "E"]

    # Raggruppa tutte le categorie Master (S35, S40, ..., S95) in un'unica voce "Master"
    df["categoria_base"] = df["categoria_base"].fillna("").apply(
        lambda c: "Master" if re.match(r"^S\d{2}$", c) else c
    )

    tot_categorie = (
        df.groupby(["categoria_base", "year"])["n"]
        .sum()
        .reset_index()
    )

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 9), sharey=False)
    fig.suptitle(f"{nome_societa} ({COD_SOCIETA})", fontweight="bold")

    # --- Grafico sinistro ---
    ax_left.plot(
        tot_societa["year"], tot_societa["n"],
        marker="o", markersize=7, linewidth=3, color="black",
        label=f"Totale", zorder=10,
    )
    ax_left.plot(
        tot_indoor["year"], tot_indoor["n"],
        marker="s", markersize=5, linewidth=1.5, color="tab:blue",
        label="Indoor",
    )
    ax_left.plot(
        tot_outdoor["year"], tot_outdoor["n"],
        marker="o", markersize=5, linewidth=1.5, color="tab:orange",
        label="Outdoor",
    )
    ax_left.plot(
        tot_uomini["year"], tot_uomini["n"],
        marker="^", markersize=5, linewidth=1.5, color="tab:green",
        label="Uomini",
    )
    ax_left.plot(
        tot_donne["year"], tot_donne["n"],
        marker="v", markersize=5, linewidth=1.5, color="tab:red",
        label="Donne",
    )
    ax_left.set_xlabel("Anno")
    ax_left.set_ylabel("Numero di gare")
    ax_left.set_title(f"Totale Risultati Per Anno")
    ax_left.grid(alpha=0.3)
    ax_left.set_xticks(anni_tutti)
    ax_left.tick_params(axis="x", rotation=45)
    ax_left.yaxis.set_major_locator(plt.MaxNLocator(nbins=15))
    ax_left.legend()

    # --- Grafico destro ---
    ordine_categorie = ["R", "C", "A", "J", "P", "S", "Master"]
    cmap = ["#3776AB", "#FFD43B", "#2CA02C", "#D62728", "#9467BD", "#FF7F0E", 
            "#17BECF", "#E377C2", "#8C564B", "#7F7F7F"]
    def chiave_ordinamento(cat):
        if cat in ordine_categorie:
            return (0, ordine_categorie.index(cat))
        return (1, cat)  # eventuali categorie non previste vanno in fondo, in ordine alfabetico

    categorie = sorted(tot_categorie["categoria_base"].unique(), key=chiave_ordinamento)

    for i, cat in enumerate(categorie):
        sub = tot_categorie[tot_categorie["categoria_base"] == cat].sort_values("year")
        ax_right.plot(
            sub["year"], sub["n"],
            marker="o", markersize=5, linewidth=1.5,
            color=cmap[i], label=cat,
        )

    ax_right.set_xlabel("Anno")
    ax_right.set_ylabel("Numero di gare")
    ax_right.set_title(f"Totale per categoria")
    ax_right.grid(alpha=0.3)
    ax_right.set_xticks(anni_tutti)
    ax_right.tick_params(axis="x", rotation=45)
    ax_right.yaxis.set_major_locator(plt.MaxNLocator(nbins=15))
    ax_right.legend()

    plt.tight_layout()
    if save:
        plt.savefig(f"figures/gare_per_anno_societa_{COD_SOCIETA}.png", dpi=150)
    else:
        plt.show()
    plt.close()

cods = ["BL012", "TN524", "BL009", "BL008", "VI626", "BS181", "TV406", "TV409", "TV354", "TN109", "TN101", "BZ066"]

with open('lista_società.txt', 'r') as file:
    cod = [line.strip() for line in file]

for ii in range(len(cod)):
    print(f"{ii}/{len(cod)}: {cod[ii]}")
    #genera_grafico(cod[ii], save=True)
genera_grafico("BL009", True)
