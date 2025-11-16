# Dashboard Profissional Power BI Style – Versão Final (v8)
# Autor: Luiz José Sousa Cunha

import os
import io
import base64
import socket
import pandas as pd
import plotly.express as px
from datetime import datetime
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

PROJECT_NAME = "Dashboard"
os.makedirs("planilha", exist_ok=True)

def encontrar_porta_livre(porta_inicial=8050):
    porta = porta_inicial
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", porta))
                return porta
            except OSError:
                porta += 1

def detectar_colunas(df):
    col_num = df.select_dtypes(include="number").columns.tolist()
    col_cat = df.select_dtypes(exclude="number").columns.tolist()
    date_cols = []
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            date_cols.append(c)
        else:
            try:
                parsed = pd.to_datetime(df[c], errors="coerce")
                if parsed.notna().sum() > 0.5 * len(parsed):
                    date_cols.append(c)
                    df[c] = parsed
            except Exception:
                pass
    return col_cat, col_num, date_cols, df

def build_kpis_and_figs(df, cat_col=None, num_col=None, date_col=None,
                        cat_multi=None, val_range=None,
                        start_date=None, end_date=None):
    dff = df.copy()
    if cat_multi and cat_col in dff.columns:
        dff = dff[dff[cat_col].astype(str).isin([str(x) for x in cat_multi])]
    if date_col in dff.columns:
        dff[date_col] = pd.to_datetime(dff[date_col], errors="coerce")
        if start_date and end_date:
            mask = (dff[date_col] >= pd.to_datetime(start_date)) & (dff[date_col] <= pd.to_datetime(end_date))
            dff = dff.loc[mask]
    if val_range and num_col in dff.columns:
        lo, hi = val_range
        dff = dff[(dff[num_col] >= lo) & (dff[num_col] <= hi)]

    kpi_cards = []
    if num_col in dff.columns:
        total = dff[num_col].sum()
        media = dff[num_col].mean()
        crescimento = (dff[num_col].pct_change().mean() or 0) * 100
        kpi_cards = [
            {"icon": "💰", "title": "Total", "value": f"{total:,.2f}", "color": "#1ABC9C"},
            {"icon": "📊", "title": "Média", "value": f"{media:,.2f}", "color": "#17A589"},
            {"icon": "📈", "title": "Crescimento", "value": f"{crescimento:.2f}%", "color": "#28B463"}
        ]
    else:
        kpi_cards = [{"icon": "🧾", "title": "Registros", "value": str(len(dff)), "color": "#117A65"}]

    if date_col in dff.columns and num_col in dff.columns:
        fig_area = px.area(dff, x=date_col, y=num_col, title="Tendência Temporal")
    else:
        fig_area = px.area(dff.reset_index(), x="index", y=num_col or dff.columns[0], title="Tendência")

    if cat_col in dff.columns and num_col in dff.columns:
        fig_bar = px.bar(dff.groupby(cat_col)[num_col].sum().reset_index(),
                         x=cat_col, y=num_col, title=f"Comparativo por {cat_col}")
        fig_pie = px.pie(dff.groupby(cat_col)[num_col].sum().reset_index(),
                         names=cat_col, values=num_col, title="Distribuição (%)")
    else:
        fig_bar = px.histogram(dff, x=num_col or dff.columns[0], title="Histograma")
        fig_pie = px.pie(dff, names=dff.columns[0], title="Distribuição")

    fig_hist = px.histogram(dff, x=num_col or dff.columns[0], nbins=30, title="Distribuição de Valores")
    for f in [fig_area, fig_bar, fig_pie, fig_hist]:
        f.update_layout(template="plotly_white", title_x=0.5, height=400)
    return kpi_cards, fig_area, fig_bar, fig_pie, fig_hist

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
server = app.server

app.layout = dbc.Container([
    html.H1(PROJECT_NAME, className="titulo"),
    html.Div("Dashboard profissional interativo baseado em planilhas Excel.", className="subtitulo"),
    html.Div([dcc.Upload(id="upload-data",
        children=html.Div(["📁 Arraste ou ", html.A("selecione um arquivo Excel (.xlsx)")]),
        className="upload-box")]),
    html.Div([
        dcc.Dropdown(id="sheet-dropdown", placeholder="Selecione a aba"),
        dcc.Dropdown(id="cat-dropdown", placeholder="Coluna categórica"),
        dcc.Dropdown(id="num-dropdown", placeholder="Coluna numérica"),
        dcc.Dropdown(id="date-dropdown", placeholder="Coluna de data (opcional)"),
        dcc.Dropdown(id="cat-multi", multi=True, placeholder="Categorias (multi)"),
        dcc.RangeSlider(id="value-range", min=0, max=1, value=[0, 1], marks={0: "0", 1: "1"}),
        html.Div(id="date-range-container")
    ], className="filtros"),
    html.Div(id="kpi-row", className="kpi-container"),
    html.Div([
        dcc.Graph(id="area-chart"),
        dcc.Graph(id="bar-chart"),
        dcc.Graph(id="pie-chart"),
        dcc.Graph(id="hist-chart")
    ], className="graficos"),
    dcc.Store(id="store-sheets")
], fluid=True)

@app.callback(
    Output("store-sheets", "data"),
    Output("sheet-dropdown", "options"),
    Output("sheet-dropdown", "value"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True
)
def handle_upload(contents, filename):
    if not contents:
        raise PreventUpdate
    _, b64 = contents.split(",", 1)
    data = base64.b64decode(b64)
    xls = pd.ExcelFile(io.BytesIO(data))
    sheets = {s: xls.parse(s).to_json(date_format="iso", orient="split") for s in xls.sheet_names}
    return sheets, [{"label": s, "value": s} for s in xls.sheet_names], xls.sheet_names[0]

if __name__ == "__main__":
    port = encontrar_porta_livre(8050)
    print(f"✅ {PROJECT_NAME} rodando na porta {port}")
    print(f"🌐 Acesse: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
