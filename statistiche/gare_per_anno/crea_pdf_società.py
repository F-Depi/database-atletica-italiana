"""
Combina i PNG generati da genera_grafico(cod, save=True) in un unico PDF
usando LaTeX come motore di composizione: genera un file .tex con un
indice (\\tableofcontents) navigabile e una pagina per società, poi lo
compila con pdflatex. Non modifica genera_grafico.

Richiede una distribuzione LaTeX installata (es. TeX Live / MiKTeX) con
pdflatex disponibile nel PATH.

Presuppone che i file siano salvati con il pattern:
    gare_per_anno_societa_{COD_SOCIETA}.png
nella cartella indicata da CARTELLA_PNG.
"""

import re
import datetime
import os
import shutil
import subprocess
import tempfile
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "script"))
from my_functions import *
import pandas as pd


_MESI_ITALIANI = [
    "", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
]


def _data_italiana():
    oggi = datetime.date.today()
    return f"{oggi.day} {_MESI_ITALIANI[oggi.month]} {oggi.year}"

# Stessa lista di codici usata nel ciclo di generazione; verrà ordinata.
with open('lista_società.txt', 'r') as file:
    CODICI = [line.strip() for line in file]

# Opzionale: mappa cod -> nome società da mostrare nell'indice.
# Se un codice non è presente qui, viene mostrato il codice stesso.
conn = get_db_engine().connect()
def get_nome_società(cod, conn):
    NOME_QUERY = """
        SELECT società
        FROM results
        WHERE cod_società = %(cod)s
        ORDER BY data DESC
        LIMIT 1;
    """
    nome_societa_row = pd.read_sql(NOME_QUERY, conn, params={"cod": cod})
    nome_societa = (
        nome_societa_row["società"].iloc[0]
        if not nome_societa_row.empty
        else cod.upper()
    )
    return nome_societa
NOMI_SOCIETA = {cod: get_nome_società(cod, conn) for cod in CODICI}

CARTELLA_PNG = "figures"  # cartella dove genera_grafico salva i PNG
OUTPUT_PDF = "gare_per_anno_tutte_le_societa.pdf"

TITOLO_COPERTINA = "Gare per Anno per Società"
SOTTOTITOLO_COPERTINA = "Report riepilogativo"

def _escape_latex(testo):
    sostituzioni = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }

    return re.sub(
        r'([&%$#_{}~^\\])',
        lambda m: sostituzioni[m.group(1)],
        testo
    )

def _etichetta(cod):
    return f"{cod}: {NOMI_SOCIETA.get(cod, cod)}"


def _crea_tex(codici_trovati, path_immagini, path_tex):
    righe = [
        r"\documentclass[a4paper,oneside]{article}",
        r"\usepackage[margin=1.5cm]{geometry}",
        r"\usepackage{graphicx}",
        r"\usepackage{hyperref}",
        r"\hypersetup{colorlinks=true, linkcolor=blue, bookmarksopen=true}",
        r"\begin{document}",
        r"\begin{titlepage}",
        r"\centering",
        r"\vspace*{5cm}",
        r"{\Huge\bfseries %s\par}" % _escape_latex(TITOLO_COPERTINA),
        r"\vspace{1cm}",
        r"{\Large %s\par}" % _escape_latex(SOTTOTITOLO_COPERTINA),
        r"\vspace{0.5cm}",
        r"{\large %s\par}" % _data_italiana(),
        r"\end{titlepage}",
        r"\tableofcontents",
        r"\clearpage",
    ]

    for cod in codici_trovati:
        etichetta = _escape_latex(_etichetta(cod))
        percorso_png = os.path.join(path_immagini, f"gare_per_anno_societa_{cod}.png")
        
        # Forza una nuova pagina pulita prima di ogni sezione
        righe.append(r"\clearpage")
        righe.append(r"\section{%s}" % etichetta)
        righe.append(r"\begin{center}")
        # Altezza ridotta a 0.88\textheight per evitare lo straripamento pagina con il titolo
        righe.append(r"\includegraphics[angle=90, height=0.88\textheight, width=\textwidth, keepaspectratio]{%s}" % percorso_png.replace("\\", "/"))
        righe.append(r"\end{center}")

    righe.append(r"\end{document}")

    with open(path_tex, "w", encoding="utf-8") as f:
        f.write("\n".join(righe))


def combina_png_in_pdf(codici, cartella_png=CARTELLA_PNG, output_pdf=OUTPUT_PDF):
    if shutil.which("pdflatex") is None:
        raise RuntimeError(
            "pdflatex non trovato nel PATH. Installa una distribuzione LaTeX "
            "(es. TeX Live su Linux/Mac, MiKTeX su Windows)."
        )

    # Ordina i codici alfabeticamente
    codici_ordinati = sorted(codici)

    codici_trovati = []
    mancanti = []
    for cod in codici_ordinati:
        path_png = os.path.join(cartella_png, f"gare_per_anno_societa_{cod}.png")
        if os.path.exists(path_png):
            codici_trovati.append(cod)
        else:
            mancanti.append(path_png)

    if mancanti:
        print("Attenzione, questi file non sono stati trovati e verranno saltati:")
        for m in mancanti:
            print(f"  - {m}")

    if not codici_trovati:
        print("Nessuna immagine trovata: PDF non creato.")
        return

    cartella_png_assoluta = os.path.abspath(cartella_png)

    with tempfile.TemporaryDirectory() as tmp:
        path_tex = os.path.join(tmp, "documento.tex")
        _crea_tex(codici_trovati, cartella_png_assoluta, path_tex)

        # pdflatex va eseguito due volte per popolare correttamente l'indice
        for _ in range(5):
            risultato = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "documento.tex"],
                cwd=tmp,
                capture_output=True,
                text=True,
            )
            if risultato.returncode != 0:
                print(risultato.stdout[-3000:])
                raise RuntimeError("Compilazione LaTeX fallita, vedi output sopra.")

        shutil.copy(os.path.join(tmp, "documento.pdf"), output_pdf)

    print(f"PDF creato: {output_pdf} (indice + {len(codici_trovati)} pagine grafici, ordinate)")


if __name__ == "__main__":
    combina_png_in_pdf(CODICI)
