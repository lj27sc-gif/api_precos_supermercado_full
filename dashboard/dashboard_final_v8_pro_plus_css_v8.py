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

# ---------------- CONFIG ----------------
PROJECT_NAME = "Dashboard"
os.makedirs("planilha", exist_ok=True)


# ---------------- FUNÇÕES DE APOIO ----------------
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
        try:
            dff = dff[(pd.to_numeric(dff[num_col], errors="coerce") >= float(lo)) & (pd.to_numeric(dff[num_col], errors="coerce") <= float(hi))]
        except Exception:
            pass

    kpi_cards = []
    if num_col in dff.columns:
        total = pd.to_numeric(dff[num_col], errors="coerce").sum()
        media = pd.to_numeric(dff[num_col], errors="coerce").mean()
        crescimento = 0
        if date_col in dff.columns and start_date and end_date:
            try:
                start = pd.to_datetime(start_date)
                end = pd.to_datetime(end_date)
                period_len = (end - start) + pd.Timedelta(days=1)
                prev_end = start - pd.Timedelta(days=1)
                prev_start = prev_end - period_len + pd.Timedelta(days=1)
                prev_mask = (pd.to_datetime(df[date_col], errors="coerce") >= prev_start) & (pd.to_datetime(df[date_col], errors="coerce") <= prev_end)
                prev_val = pd.to_numeric(df.loc[prev_mask, num_col], errors="coerce").sum()
                curr_val = pd.to_numeric(dff[num_col], errors="coerce").sum()
                if prev_val and prev_val != 0:
                    crescimento = (curr_val - prev_val) / abs(prev_val) * 100
                else:
                    crescimento = None
            except Exception:
                crescimento = None
        kpi_cards = [
            {"icon": "💰", "title": "Total", "value": f"{total:,.2f}", "color": "#1ABC9C"},
            {"icon": "📊", "title": "Média", "value": f"{media:,.2f}" if media is not None else "N/A", "color": "#17A589"},
            {"icon": "📈", "title": "Crescimento", "value": f"{crescimento:.2f}%" if isinstance(crescimento, (int, float)) else "N/A", "color": "#28B463"}
        ]
    else:
        kpi_cards = [{"icon": "🧾", "title": "Registros", "value": str(len(dff)), "color": "#117A65"}]

    # Gráficos
    if date_col in dff.columns and num_col in dff.columns:
        try:
            fig_area = px.area(dff.sort_values(by=date_col), x=date_col, y=num_col, title="Tendência Temporal")
        except Exception:
            fig_area = px.area(dff.reset_index(), x="index", y=num_col or dff.columns[0], title="Tendência Temporal")
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


# ---------------- APP ----------------
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
server = app.server

app.title = PROJECT_NAME
FONT_LINK = "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap"

app.layout = dbc.Container([
    html.Link(href=FONT_LINK, rel="stylesheet"),
    html.H1(PROJECT_NAME, className="titulo"),
    html.Div("Dashboard profissional interativo baseado em planilhas Excel.", className="subtitulo"),
    html.Hr(),

    dbc.Row([
        dbc.Col(dcc.Upload(id="upload-data",
                           children=html.Div(["📁 Arraste ou ", html.A("selecione um arquivo Excel (.xlsx)")]),
                           style={"width":"100%","height":"60px","lineHeight":"60px","borderWidth":"2px","borderStyle":"dashed",
                                  "borderColor":"#117A65","borderRadius":"10px","textAlign":"center","backgroundColor":"#F8F9F9",
                                  "fontSize":"16px","fontWeight":"600","color":"#145A32"}), md=12)
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(dcc.Dropdown(id="sheet-dropdown", placeholder="Selecione a aba"), md=3),
        dbc.Col(dcc.Dropdown(id="cat-dropdown", placeholder="Coluna categórica"), md=3),
        dbc.Col(dcc.Dropdown(id="num-dropdown", placeholder="Coluna numérica"), md=3),
        dbc.Col(dcc.Dropdown(id="date-dropdown", placeholder="Coluna de data (opcional)"), md=3),
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(dcc.Dropdown(id="cat-multi", multi=True, placeholder="Categorias (multi)"), md=4),
        dbc.Col(dcc.RangeSlider(
            id="value-range",
            tooltip={"placement": "bottom"},
            min=0,
            max=1,
            value=[0, 1],
            marks={0: "0", 1: "1"}
        ), md=6),
        dbc.Col(html.Div(id="date-range-container"), md=2)
    ]),
    html.Br(),

    dbc.Row(id="kpi-row", className="mb-4"),

    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id="area-chart")), md=6),
        dbc.Col(dbc.Card(dcc.Graph(id="bar-chart")), md=6),
    ]),
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id="pie-chart")), md=4),
        dbc.Col(dbc.Card(dcc.Graph(id="hist-chart")), md=8),
    ]),

    dcc.Store(id="store-sheets")
], fluid=True)


# ---------------- CALLBACKS ----------------
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
    try:
        _, b64 = contents.split(",", 1)
        data = base64.b64decode(b64)
        xls = pd.ExcelFile(io.BytesIO(data))
        sheets = {s: xls.parse(s).to_json(date_format="iso", orient="split") for s in xls.sheet_names}
        return sheets, [{"label": s, "value": s} for s in xls.sheet_names], xls.sheet_names[0]
    except Exception as e:
        print(e)
        raise PreventUpdate


@app.callback(
    Output("cat-dropdown","options"),
    Output("num-dropdown","options"),
    Output("date-dropdown","options"),
    Output("cat-multi","options"),
    Output("value-range","min"),
    Output("value-range","max"),
    Output("value-range","value"),
    Output("value-range","marks"),
    Input("sheet-dropdown","value"),
    State("store-sheets","data")
)
def on_sheet_select(sheet, sheets):
    if not sheet or not sheets:
        raise PreventUpdate
    df = pd.read_json(sheets[sheet], orient="split")
    col_cat, col_num, date_cols, df = detectar_colunas(df)

    cat_opts = [{"label": c, "value": c} for c in col_cat]
    num_opts = [{"label": c, "value": c} for c in col_num]
    date_opts = [{"label": c, "value": c} for c in date_cols]

    multi_opts = []
    if col_cat:
        vals = df[col_cat[0]].dropna().astype(str).unique().tolist()
        multi_opts = [{"label": v, "value": v} for v in vals]

    if col_num:
        v = df[col_num[0]].dropna()
        if not v.empty:
            vmin, vmax = float(v.min()), float(v.max())
            return (
                cat_opts, num_opts, date_opts, multi_opts,
                vmin, vmax, [vmin, vmax],
                {vmin: str(round(vmin, 2)), vmax: str(round(vmax, 2))}
            )
    return (
        cat_opts, num_opts, date_opts, multi_opts,
        0.0, 1.0, [0.0, 1.0], {0.0: "0", 1.0: "1"}
    )


@app.callback(
    Output("date-range-container","children"),
    Input("date-dropdown","value"),
    State("sheet-dropdown","value"),
    State("store-sheets","data")
)
def show_datepicker(date_col, sheet, sheets):
    if not date_col or not sheet or not sheets:
        return html.Div()
    df = pd.read_json(sheets[sheet], orient="split")
    if date_col not in df.columns:
        return html.Div()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    min_d, max_d = df[date_col].min(), df[date_col].max()
    if pd.isna(min_d) or pd.isna(max_d):
        return html.Div()
    picker = dcc.DatePickerRange(
        id="date-range",
        start_date=min_d.date(),
        end_date=max_d.date(),
        min_date_allowed=min_d.date(),
        max_date_allowed=max_d.date(),
        display_format="YYYY-MM-DD"
    )
    return html.Div([html.Label("Intervalo de datas:"), picker])


@app.callback(
    Output("kpi-row", "children"),
    Output("area-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("pie-chart", "figure"),
    Output("hist-chart", "figure"),
    Input("sheet-dropdown", "value"),
    Input("cat-dropdown", "value"),
    Input("num-dropdown", "value"),
    Input("cat-multi", "value"),
    Input("value-range", "value"),
    Input("date-dropdown", "value"),
    State("store-sheets", "data"),
    State("date-range-container", "children")
)
def update_dashboard(sheet, cat_col, num_col, cat_multi, val_range, date_col, sheets, date_range_child):
    start_date, end_date = None, None
    if isinstance(date_range_child, dict):
        try:
            children = date_range_child.get("props", {}).get("children", [])
            for c in children:
                if isinstance(c, dict) and c.get("type") == "DatePickerRange":
                    props = c.get("props", {})
                    start_date = props.get("start_date")
                    end_date = props.get("end_date")
        except Exception:
            pass

    if not sheet or not sheets:
        raise PreventUpdate

    df = pd.read_json(sheets[sheet], orient="split")
    kpis, fig_area, fig_bar, fig_pie, fig_hist = build_kpis_and_figs(
        df, cat_col, num_col, date_col, cat_multi, val_range, start_date, end_date
    )

    cards = []
    for kpi in kpis:
        card = html.Div([
            html.Div(kpi["icon"], className="kpi-icon"),
            html.Div(kpi["title"], className="kpi-title"),
            html.Div(kpi["value"], className="kpi-value", style={"color": kpi["color"]})
        ], className="kpi-card")
        cards.append(card)

    return cards, fig_area, fig_bar, fig_pie, fig_hist


# ---------------- RUN ----------------
if __name__ == '__main__':
    port = encontrar_porta_livre(8050)
    print(f"✅ {PROJECT_NAME} rodando na porta {port}")
    print(f"🌐 Acesse: http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
