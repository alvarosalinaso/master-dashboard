"""Master Dashboard — Todos los proyectos de Álvaro Salinas."""

import json
import sqlite3
from pathlib import Path

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

app = dash.Dash(
    __name__,
    title="Álvaro Salinas — Data Portfolio",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

COLORS = {
    "bg": "#0a0a1a",
    "card": "#12122a",
    "border": "#2a2a4a",
    "accent": "#e94560",
    "gold": "#FFD700",
    "text": "#e0e0e0",
    "muted": "#8892b0",
    "green": "#00d2d3",
    "blue": "#54a0ff",
}


def _tab_style():
    return {
        "style": {
            "backgroundColor": COLORS["card"],
            "color": COLORS["text"],
            "border": "none",
        },
        "selected_style": {
            "backgroundColor": COLORS["accent"],
            "color": "white",
            "border": "none",
        },
    }


# ── Data loading ──────────────────────────────────────────────────────────────

BASE = Path(__file__).parent.parent

WC_DB = BASE / "worldcup-2026" / "data" / "worldcup.db"
GAMES_CSV = BASE / "chilean-videogames-analysis" / "data" / "processed" / "games.csv"
SPEECHES_CSV = BASE / "geopolitica-textual-nlp" / "data" / "processed" / "speeches.csv"
CENSUS_CSV = BASE / "chile-geografia-historica" / "data" / "processed" / "census.csv"
EVENTS_CSV = BASE / "chile-geografia-historica" / "data" / "processed" / "events.csv"
PRESIDENTS_CSV = BASE / "chile-geografia-historica" / "data" / "processed" / "presidents.csv"
CAJAS_CSV = BASE / "cajas-alimentacion" / "data" / "raw" / "coordinates.csv"
SANIT_CSV = BASE / "sanitizacion-santiago" / "data" / "raw" / "sanitization_points.csv"


def load_data():
    data = {}
    if WC_DB.exists():
        conn = sqlite3.connect(str(WC_DB))
        data["wc_matches"] = pd.read_sql("SELECT * FROM matches", conn)
        data["wc_teams"] = pd.read_sql("SELECT * FROM teams", conn)
        conn.close()
    if GAMES_CSV.exists():
        data["games"] = pd.read_csv(GAMES_CSV)
    if SPEECHES_CSV.exists():
        data["speeches"] = pd.read_csv(SPEECHES_CSV)
    if CENSUS_CSV.exists():
        data["census"] = pd.read_csv(CENSUS_CSV)
    if EVENTS_CSV.exists():
        data["events"] = pd.read_csv(EVENTS_CSV)
    if PRESIDENTS_CSV.exists():
        data["presidents"] = pd.read_csv(PRESIDENTS_CSV)
    if CAJAS_CSV.exists():
        data["cajas"] = pd.read_csv(CAJAS_CSV)
    if SANIT_CSV.exists():
        data["sanit"] = pd.read_csv(SANIT_CSV)
    return data


DATA = load_data()

# ── Layout ────────────────────────────────────────────────────────────────────

app.layout = html.Div(
    style={
        "backgroundColor": COLORS["bg"],
        "minHeight": "100vh",
        "fontFamily": "'Segoe UI', system-ui, sans-serif",
        "color": COLORS["text"],
    },
    children=[
        html.Div(
            style={
                "background": "linear-gradient(135deg, #0d1b2a 0%, #1a1a3e 50%, #162447 100%)",
                "padding": "40px 20px",
                "textAlign": "center",
                "borderBottom": f"3px solid {COLORS['accent']}",
            },
            children=[
                html.H1(
                    "Álvaro Salinas Ortiz",
                    style={"fontSize": "2.5rem", "fontWeight": "800", "color": COLORS["gold"], "margin": "0"},
                ),
                html.P(
                    "Data Analyst — Python · SQL · NLP · Dashboards",
                    style={"color": COLORS["muted"], "marginTop": "8px", "fontSize": "1.1rem"},
                ),
            ],
        ),
        dcc.Tabs(
            id="tabs",
            value="overview",
            style={"backgroundColor": COLORS["card"], "borderBottom": f"1px solid {COLORS['border']}"},
            children=[
                dcc.Tab(label="Resumen", value="overview", **_tab_style()),
                dcc.Tab(label="World Cup 2026", value="worldcup", **_tab_style()),
                dcc.Tab(label="Videojuegos Chile", value="games", **_tab_style()),
                dcc.Tab(label="Discurso NLP", value="nlp", **_tab_style()),
                dcc.Tab(label="Geografía Chile", value="geo", **_tab_style()),
                dcc.Tab(label="Cajas Alimentación", value="cajas", **_tab_style()),
                dcc.Tab(label="Sanitización Santiago", value="sanit", **_tab_style()),
            ],
        ),
        html.Div(id="tab-content", style={"maxWidth": "1200px", "margin": "0 auto", "padding": "30px 20px"}),
    ],
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def card(title, children, color=COLORS["card"]):
    child_list = children if isinstance(children, list) else [children]
    return html.Div(
        style={
            "backgroundColor": color, "borderRadius": "12px", "padding": "25px",
            "marginBottom": "25px", "border": f"1px solid {COLORS['border']}",
            "boxShadow": "0 4px 20px rgba(0,0,0,0.3)",
        },
        children=[
            html.H3(title, style={"color": COLORS["gold"], "fontSize": "1.3rem", "marginBottom": "15px", "paddingBottom": "10px", "borderBottom": f"2px solid {COLORS['border']}"}),
        ] + child_list,
    )


def stat_row(stats):
    return html.Div(
        style={"display": "flex", "gap": "15px", "flexWrap": "wrap", "marginBottom": "25px"},
        children=[
            html.Div(
                style={
                    "flex": "1", "minWidth": "140px",
                    "background": "linear-gradient(135deg, #16213e, #0f3460)",
                    "borderRadius": "10px", "padding": "20px", "textAlign": "center",
                    "border": f"1px solid {COLORS['border']}",
                },
                children=[
                    html.Div(str(val), style={"fontSize": "2rem", "fontWeight": "800", "color": COLORS["gold"]}),
                    html.Div(label, style={"fontSize": "0.85rem", "color": COLORS["muted"], "marginTop": "4px"}),
                ],
            )
            for val, label in stats
        ],
    )


# ── Tab callback ──────────────────────────────────────────────────────────────


@callback(Output("tab-content", "children"), Input("tabs", "value"))
def render_tab(tab):
    funcs = {
        "overview": overview_tab,
        "worldcup": worldcup_tab,
        "games": games_tab,
        "nlp": nlp_tab,
        "geo": geo_tab,
        "cajas": cajas_tab,
        "sanit": sanit_tab,
    }
    return funcs.get(tab, overview_tab)()


# ── Tabs ──────────────────────────────────────────────────────────────────────


def overview_tab():
    projects = [
        {"name": "World Cup 2026", "desc": "Dashboard comparativo de Mundiales", "icon": "⚽", "color": COLORS["green"]},
        {"name": "Videojuegos Chile", "desc": "ETL + clustering de 150 juegos", "icon": "🎮", "color": COLORS["blue"]},
        {"name": "Discurso NLP", "desc": "NER + sentimiento presidencial", "icon": "📜", "color": COLORS["accent"]},
        {"name": "Geografía Chile", "desc": "Censos + eventos + presidentes", "icon": "🗺️", "color": "#9b59b6"},
        {"name": "Cajas Alimentación", "desc": "80,595 puntos de entrega", "icon": "📦", "color": COLORS["gold"]},
        {"name": "Sanitización Santiago", "desc": "87 puntos de sanitización comunal", "icon": "🧹", "color": "#e74c3c"},
    ]
    return html.Div([
        stat_row([("7", "Proyectos"), ("80,595", "Puntos georeferenciados"), ("150+", "Juegos analizados"), ("16", "Discursos NLP"), ("87", "Puntos sanitización")]),
        card("Proyectos Destacados", html.Div([
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "15px"},
                children=[
                    html.Div(
                        style={"backgroundColor": COLORS["bg"], "borderRadius": "10px", "padding": "20px", "border": f"1px solid {p['color']}"},
                        children=[
                            html.Div(p["icon"], style={"fontSize": "2rem", "marginBottom": "10px"}),
                            html.Div(p["name"], style={"fontWeight": "700", "color": p["color"]}),
                            html.Div(p["desc"], style={"fontSize": "0.85rem", "color": COLORS["muted"], "marginTop": "5px"}),
                        ],
                    )
                    for p in projects
                ],
            )
        ])),
    ])


def worldcup_tab():
    if "wc_matches" not in DATA:
        return card("World Cup 2026", html.P("Data not available"))
    df = DATA["wc_matches"]
    fig = px.histogram(df, x="home_score", nbins=10, title="Distribución de Goles")
    fig.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], height=400)
    return html.Div([
        stat_row([(str(len(df)), "Partidos"), (str(df["home_score"].sum() + df["away_score"].sum()), "Goles")]),
        card("Análisis de Goles", dcc.Graph(figure=fig)),
    ])


def games_tab():
    if "games" not in DATA:
        return card("Videojuegos", html.P("Data not available"))
    df = DATA["games"]
    fig = px.pie(df, names="source", title="Distribución por Plataforma")
    fig.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], height=400)
    return html.Div([
        stat_row([(str(len(df)), "Juegos"), (str(df["source"].nunique()), "Plataformas")]),
        card("Plataformas", dcc.Graph(figure=fig)),
    ])


def nlp_tab():
    if "speeches" not in DATA:
        return card("NLP", html.P("Data not available"))
    df = DATA["speeches"]
    fig = px.scatter(df, x="year", y="speaker", title="Discursos Presidenciales")
    fig.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], height=500)
    return html.Div([
        stat_row([(str(len(df)), "Discursos"), (str(df["year"].min()) + "-" + str(df["year"].max()), "Período")]),
        card("Línea de Tiempo", dcc.Graph(figure=fig)),
    ])


def geo_tab():
    if "census" not in DATA:
        return card("Geografía", html.P("Data not available"))
    df = DATA["census"]
    fig = px.line(df, x="census_year", y="population", color="region", title="Población por Región")
    fig.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], height=600)
    return html.Div([
        stat_row([(str(df["region"].nunique()), "Regiones"), (str(df["census_year"].min()) + "-" + str(df["census_year"].max()), "Censos")]),
        card("Evolución Demográfica", dcc.Graph(figure=fig)),
    ])


def cajas_tab():
    if "cajas" not in DATA:
        return card("Cajas Alimentación", html.P("Data not available"))
    df = DATA["cajas"]
    fig = px.density_mapbox(
        df, lat="lat", lon="lon", radius=8,
        center={"lat": -33.45, "lon": -70.66}, zoom=11,
        mapbox_style="carto-positron",
        title="Puntos de Entrega — Cajas de Alimentación",
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], height=600)
    return html.Div([
        stat_row([(str(len(df)), "Puntos de entrega")]),
        card("Mapa de Entregas", dcc.Graph(figure=fig)),
    ])


def sanit_tab():
    if "sanit" not in DATA:
        return card("Sanitización Santiago", html.P("Data not available"))
    df = DATA["sanit"]
    tipo_counts = df["type"].value_counts()
    fig_map = px.scatter_mapbox(
        df, lat="lat", lon="lon", color="type",
        hover_name="name", hover_data=["description", "type"],
        center={"lat": -33.45, "lon": -70.66}, zoom=12,
        mapbox_style="carto-positron",
        title="Puntos de Sanitización — Comuna de Santiago",
        color_discrete_map={"Cité": "#e74c3c", "Pasaje": "#3498db", "Edificio": "#2ecc71", "Domicilio": "#f39c12", "Calle": "#9b59b6", "Otro": "#95a5a6"},
    )
    fig_map.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], height=600)
    fig_bar = px.bar(x=tipo_counts.index, y=tipo_counts.values, title="Ubicaciones por Tipo", labels={"x": "Tipo", "y": "Cantidad"}, color=tipo_counts.index, color_discrete_map={"Cité": "#e74c3c", "Pasaje": "#3498db", "Edificio": "#2ecc71", "Domicilio": "#f39c12", "Calle": "#9b59b6", "Otro": "#95a5a6"})
    fig_bar.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], height=400, showlegend=False)
    return html.Div([
        stat_row([(str(len(df)), "Puntos de sanitización"), (str(df["type"].nunique()), "Categorías")]),
        card("Mapa de Sanitización", dcc.Graph(figure=fig_map)),
        card("Distribución por Tipo", dcc.Graph(figure=fig_bar)),
    ])


if __name__ == "__main__":
    app.run(debug=False, port=8050)
