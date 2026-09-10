import pandas as pd
import re
import os

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

def escape_latex(text):
    if not isinstance(text, str):
        return text
    # Backslash must be handled first to avoid double-escaping
    pattern = re.compile("|".join(re.escape(k) for k in LATEX_SPECIAL_CHARS))
    return pattern.sub(lambda m: LATEX_SPECIAL_CHARS[m.group()], text)


LIM = "_250"
societa = pd.read_csv(f"liste/lista_societa{LIM}.csv", dtype="str", keep_default_na=False)
report = f"report_societa{LIM}/figure.tex"

with open(report, "w") as f:
    for ii, row in societa.iterrows():
        COD = escape_latex(row["COD"])
        nome = escape_latex(row["Società"])
        pdf_regione = os.path.join("figures/societa", f"{COD}.pdf")
        if not os.path.exists(pdf_regione):
            print(f"[ATTENZIONE] Grafico mancante per ({COD}): {nome}")
            continue

        TEMPLATE = r"""\clearpage\section{%s: %s}
\begin{figure}[h!]
    \includegraphics[width=\textwidth]{../figures/societa/%s.pdf}
\end{figure}
""" % (COD, nome, COD)
        f.write(TEMPLATE + "\n")
