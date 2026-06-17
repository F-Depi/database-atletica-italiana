from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import webbrowser

data = pd.read_csv("cambio_società.csv")

data["data_primo_risultato_nuova_società"] = pd.to_datetime(
    data["data_primo_risultato_nuova_società"]
)

fig = px.scatter(
    data,
    x="data_primo_risultato_nuova_società",
    y="età_al_cambio",
    hover_name="atleta"
)

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id="graph", figure=fig)
])

@app.callback(
    Output("graph", "figure"),
    Input("graph", "clickData")
)
def open_link(clickData):
    if clickData:
        i = clickData["points"][0]["pointIndex"]
        url = data.iloc[i]["link_atleta"]
        webbrowser.open(url)
    return fig

app.run(debug=True)
