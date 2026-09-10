import os
import pandas as pd
import re

LATEX_SPECIAL_CHARS = {
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
_LATEX_PATTERN = re.compile("|".join(re.escape(k) for k in LATEX_SPECIAL_CHARS))


def escape_latex(text):
    if not isinstance(text, str):
        return text
    return _LATEX_PATTERN.sub(lambda m: LATEX_SPECIAL_CHARS[m.group()], text)


regioni = pd.read_csv("liste/lista_regioni.csv", dtype="str", keep_default_na=False)
province = pd.read_csv("liste/lista_province.csv", dtype="str", keep_default_na=False)

FIGURE_DIR_REGIONI = "../figures/regioni"
FIGURE_DIR_PROVINCE = "../figures/province"

# Path assoluti/relativi usati SOLO per il controllo os.path.exists.
# Devono corrispondere alla posizione reale dei file rispetto alla working directory
# dello script (non a quella del .tex, che è relativa a report_regioni/).
CHECK_DIR_REGIONI = "figures/regioni"
CHECK_DIR_PROVINCE = "figures/province"

SECTION_TEMPLATE = r"""\clearpage\section{%s}
\begin{figure}[h!]
    \centering
    \includegraphics[width=\textwidth]{%s/%s.pdf}
\end{figure}
"""

SUBSECTION_TEMPLATE = r"""\clearpage\subsection{%s}
\begin{figure}[h!]
    \centering
    \includegraphics[width=\textwidth]{%s/%s.pdf}
\end{figure}
"""

with open("report_regioni/figure.tex", "w") as f:
    for _, reg_row in regioni.iterrows():
        cod_regione = reg_row["COD"]
        nome_regione = reg_row["Regione"]
        nome_regione_disp = escape_latex(nome_regione)

        pdf_regione = os.path.join(CHECK_DIR_REGIONI, f"{cod_regione}.pdf")
        if not os.path.exists(pdf_regione):
            print(
                f"[ATTENZIONE] Grafico mancante per regione {cod_regione} ({nome_regione}): {pdf_regione}"
            )
        else:
            f.write(
                SECTION_TEMPLATE % (nome_regione_disp, FIGURE_DIR_REGIONI, cod_regione)
            )
            f.write("\n")

        # Tutte le province di questa regione (match sul COD)
        prov_regione = province[province["Regione"] == cod_regione]

        # Trentino e Alto-Adige sono considerate due regioni separate e hanno
        # quindi una sola provincia (come in Valle d'Aosta)
        if len(prov_regione) == 1:
            continue

        for _, prov_row in prov_regione.iterrows():
            cod_provincia = prov_row["COD"]
            nome_provincia_disp = escape_latex(prov_row["Provincia"])

            pdf_provincia = os.path.join(CHECK_DIR_PROVINCE, f"{cod_provincia}.pdf")
            if not os.path.exists(pdf_provincia):
                print(
                    f"[ATTENZIONE] Grafico mancante per provincia {cod_provincia} ({prov_row['Provincia']}): {pdf_provincia}"
                )
                continue

            f.write(
                SUBSECTION_TEMPLATE
                % (nome_provincia_disp, FIGURE_DIR_PROVINCE, cod_provincia)
            )
            f.write("\n")
