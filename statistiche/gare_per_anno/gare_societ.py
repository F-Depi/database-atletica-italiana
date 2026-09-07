import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "script"))
from my_functions import *


def genera_grafico(COD_SOCIETA):
    """
    Query il DB per gli atleti di una società e plotta anno vs numero di gare.
    Grafico sinistro: totale società, totale indoor, totale outdoor.
    Grafico destro: totale per categoria.
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

    tot_categorie = (
        df.groupby(["categoria_base", "year"])["n"]
        .sum()
        .reset_index()
    )

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 6), sharey=False)
    fig.suptitle(f"{nome_societa} ({COD_SOCIETA})", fontsize=16, fontweight="bold")

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
    ax_left.legend(fontsize=8)

    # --- Grafico destro ---
    categorie = sorted(tot_categorie["categoria_base"].unique())
    cmap = cm.get_cmap("tab20", max(len(categorie), 1))

    for i, cat in enumerate(categorie):
        sub = tot_categorie[tot_categorie["categoria_base"] == cat].sort_values("year")
        ax_right.plot(
            sub["year"], sub["n"],
            marker="o", markersize=5, linewidth=1.5,
            color=cmap(i), label=cat,
        )

    ax_right.set_xlabel("Anno")
    ax_right.set_ylabel("Numero di gare")
    ax_right.set_title(f"Totale per categoria")
    ax_right.grid(alpha=0.3)
    ax_right.set_xticks(anni_tutti)
    ax_right.tick_params(axis="x", rotation=45)
    ax_right.yaxis.set_major_locator(plt.MaxNLocator(nbins=15))
    ax_right.legend(fontsize=8, ncol=2)

    plt.tight_layout()
    plt.savefig(f"gare_per_anno_societa_{COD_SOCIETA}.png", dpi=300)
    plt.show()


for cod in ["BL012", "TN524", "BL009", "BL008", "VI626", "BS181", "TV406", "TV409", "TV354", "TN109", "TN101", "BZ066"]:
    genera_grafico(cod)
    exit()
