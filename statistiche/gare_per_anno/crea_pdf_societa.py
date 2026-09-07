"""
Combina i PNG generati da genera_grafico(cod, save=True) in un unico PDF
usando LaTeX come motore di composizione: genera un file .tex con un
indice (\\tableofcontents) navigabile e una pagina per società, poi lo
compila con pdflatex. Non modifica genera_grafico.

Richiede una distribuzione LaTeX installata (es. TeX Live / MiKTeX) con
pdflatex disponibile nel PATH.

Presuppone che i file siano salvati con il pattern:
    gare_per_anno_societa_{COD_SOCIETA}.pdf
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
CODICI = ["BL012", "TN524", "BL009", "BL008", "VI626", "BS181", "TV406", "TV409",
           "TV354", "TN109", "TN101", "BZ066"]
#with open('lista_societa_250.txt', 'r') as file:
#    CODICI = [line.strip() for line in file]


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
#OUTPUT_PDF = "Gare_per_anno_tutte_societa.pdf"
OUTPUT_PDF = "Gare_per_anno_societa_note.pdf"

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
        r"\usepackage[margin=1.5cm,landscape]{geometry}",
        r"\usepackage{graphicx}",
        r"\usepackage{tocloft}",
        r"\setlength{\cftsecnumwidth}{3em}",
        r"\usepackage{hyperref}",
        r"\hypersetup{colorlinks=true, linkcolor=blue, bookmarksopen=true}",
        r"\begin{document}",
        r"\begin{titlepage}",
        r"\centering",
        r"\vspace*{3cm}",
        r"{\Huge\bfseries %s\par}" % _escape_latex(TITOLO_COPERTINA),
        r"\vspace{1cm}",
        r"{\Large %s\par}" % _escape_latex(SOTTOTITOLO_COPERTINA),
        r"\vspace{0.5cm}",
        r"{\large %s\par}" % _data_italiana(),
        r"\end{titlepage}",
        
        # ===== ABSTRACT STRETTO E CENTRATO =====
        r"\clearpage",
        r"\begin{center}",
        r"\begin{minipage}{0.6\textwidth}",
        r"\begin{abstract}",
        r"Le seguenti pagine riportano il numero totale dei risultati gara conseguiti di anno in anno (dal 2005 a oggi) dagli atleti di una società. Il grafico a sinistra mostra i risultati totali della società e gli andamenti dei soli risultati indoor, outdoor, maschili e femminili. Il grafico a destra divide invece i risultati per categorie.",
        r"\par\vspace{0.3cm}",
        r"Sono incluse solo le società che al 4 di settembre hanno più di 250 risultati nel 2026.",
        r"\par\vspace{0.3cm}",
        r"Database di \url{https://atletica.mooo.com}",
        r"Fonte dati: \url{https://www.fidal.it/}",
        r"\par\vspace{0.3cm}",
        r"Aggiornato al %s." % _data_italiana(),
        r"\end{abstract}",
        r"\end{minipage}",
        r"\end{center}",
        # ===== FINE ABSTRACT =====
        
        r"\clearpage",
        r"\tableofcontents",
        r"\clearpage",
    ]

    for cod in codici_trovati:
        etichetta = _escape_latex(_etichetta(cod))
        percorso_grafico = os.path.join(path_immagini, f"gare_per_anno_societa_{cod}.pdf")

        righe.append(r"\clearpage")
        righe.append(r"\section{%s}" % etichetta)
        righe.append(r"\begin{center}")
        righe.append(r"\includegraphics[width=\textwidth, height=0.85\textheight, keepaspectratio]{%s}" % percorso_grafico.replace("\\", "/"))
        righe.append(r"\end{center}")

    righe.append(r"\end{document}")

    with open(path_tex, "w", encoding="utf-8") as f:
        f.write("\n".join(righe))


def combina_grafico_in_pdf(codici, cartella_grafico=CARTELLA_PNG, output_pdf=OUTPUT_PDF):
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
        path_grafico = os.path.join(cartella_grafico, f"gare_per_anno_societa_{cod}.pdf")
        if os.path.exists(path_grafico):
            codici_trovati.append(cod)
        else:
            mancanti.append(path_grafico)

    if mancanti:
        print("Attenzione, questi file non sono stati trovati e verranno saltati:")
        for m in mancanti:
            print(f"  - {m}")

    if not codici_trovati:
        print("Nessuna immagine trovata: PDF non creato.")
        return

    cartella_grafico_assoluta = os.path.abspath(cartella_grafico)

    with tempfile.TemporaryDirectory() as tmp:
        path_tex = os.path.join(tmp, "documento.tex")
        _crea_tex(codici_trovati, cartella_grafico_assoluta, path_tex)

        # 3 compilazioni bastano e avanzano per popolare indice/segnalibri.
        # Nota: il numero di compilazioni NON incide sulla sovrapposizione
        # numero/titolo nell'indice, che è un problema di larghezza fissa
        # (vedi \cftsecnumwidth sopra), non di riferimenti da risolvere.
        for _ in range(3):
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
    combina_grafico_in_pdf(CODICI)
