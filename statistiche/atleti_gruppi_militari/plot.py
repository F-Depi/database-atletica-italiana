#import pandas as pd
#import matplotlib.pyplot as plt
#
#data = pd.read_csv("cambio_società.csv")
#
#data["data_primo_risultato_nuova_società"] = pd.to_datetime(
#    data["data_primo_risultato_nuova_società"]
#)
#
#plt.figure(figsize=(10,5))
#plt.scatter(
#    data["data_primo_risultato_nuova_società"],
#    data["età_al_cambio"],
#    alpha=0.6
#)
#
#plt.xlabel("Data ingresso nuova società")
#plt.ylabel("Età al cambio")
#plt.grid(alpha=0.3)
#plt.tight_layout()
#plt.show()


""" Genrate an interactive pdf """
import pandas as pd
import plotly.express as px

# ── Load data ──────────────────────────────────────────────────────────────
data = pd.read_csv("cambio_società.csv")
data["data_primo_risultato_nuova_società"] = pd.to_datetime(
    data["data_primo_risultato_nuova_società"]
)

# ── Build figure with clickable links via customdata ───────────────────────
fig = px.scatter(
    data,
    x="data_primo_risultato_nuova_società",
    y="età_al_cambio",
    hover_name="atleta",
    title="Cambio Società – Età al cambio per data",
    custom_data=["link_atleta"],
)

# Open the athlete's URL when a point is clicked
fig.update_traces(
    marker=dict(size=8, opacity=0.8),
)

fig.update_layout(
    clickmode="event",
)

# Embed JS so clicking a point opens the link
click_js = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    var plot = document.querySelector(".plotly-graph-div");
    plot.on("plotly_click", function(data) {
        var url = data.points[0].customdata[0];
        if (url) window.open(url, "_blank");
    });
});
</script>
"""

html_content = fig.to_html(full_html=True, include_plotlyjs=True)
html_content = html_content.replace("</body>", click_js + "\n</body>")

output_path = "cambio_società.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Saved: {output_path}")
