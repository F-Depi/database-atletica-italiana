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

def escape_latex(text):
    if not isinstance(text, str):
        return text
    # Backslash must be handled first to avoid double-escaping
    pattern = re.compile("|".join(re.escape(k) for k in LATEX_SPECIAL_CHARS))
    return pattern.sub(lambda m: LATEX_SPECIAL_CHARS[m.group()], text)


societa = pd.read_csv("liste/lista_societa_250.csv", dtype="str", keep_default_na=False)

with open("report_societa/figure.tex", "w") as f:
    for ii, row in societa.iterrows():
        COD = escape_latex(row["COD"])
        nome = escape_latex(row["Società"])
        TEMPLATE = r"""\clearpage\section{%s: %s}
\begin{figure}[h!]
    \includegraphics[width=\textwidth]{../figures/societa/%s.pdf}
\end{figure}
""" % (COD, nome, COD)
        f.write(TEMPLATE + "\n")
