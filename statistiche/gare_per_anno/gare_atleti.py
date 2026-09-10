"""
Query il DB per N atleti e plotta anno vs numero di gare.
Marker: indoor = quadrato, outdoor = cerchio.
Colore: diverso per ogni atleta.
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "script"))
from my_functions import *

conn = get_db_engine().connect()

ATLETI = {
    "Federico": "https://www.fidal.it/atleta/DE-PAOLI-Federico/eKmRlJmfcWs%3D",
    # "Giulia": "https://www.fidal.it/atleta/RICCARDI-Giulia/d6iRk5SoaGU%3D",
    "Diana": "https://www.fidal.it/atleta/CARNIEL-Diana/eaqRk5OkcWY%3D",
    "Giuliano": "https://www.fidal.it/atleta/FERRARI-Giuliano/d6iRlJOibGs%3D",
    "Alessandro": "https://www.fidal.it/atleta/PEDROTTI-Alessandro/d6iRlJSla2Q%3D",
}

QUERY = """
    SELECT EXTRACT(YEAR FROM data)::int AS year, ambiente, COUNT(*) AS n
    FROM results
    WHERE link_atleta = %(link)s
    GROUP BY year, ambiente
    ORDER BY year, ambiente;
"""


plt.figure(figsize=(10, 6))
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

for i, (nome, link) in enumerate(ATLETI.items()):
    df = pd.read_sql(QUERY, conn, params={"link": link})
    indoor = df[df["ambiente"] == "I"]
    outdoor = df[df["ambiente"] == "P"]
    tot = pd.concat([indoor, outdoor]).groupby("year")["n"].sum().reset_index()

    color = colors[i % len(colors)]

    # plt.plot(indoor["year"], indoor["n"], marker="s", linestyle="", color=color,
    #         label=f"{nome} (I)")
    # plt.plot(outdoor["year"], outdoor["n"], marker="o", linestyle="", color=color,
    #         label=f"{nome} (P)")
    plt.plot(tot["year"], tot["n"], marker="o", color=color, label=f"{nome}")

plt.xlabel("Anno")
plt.ylabel("Numero di gare")
plt.title("Numero di gare all'anno, per atleta")
plt.grid()
plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
plt.gca().yaxis.set_major_locator(plt.MaxNLocator(nbins=15))
plt.legend()
plt.tight_layout()
plt.savefig("figures/gare_per_anno_atleti.png", dpi=300)
plt.show()
