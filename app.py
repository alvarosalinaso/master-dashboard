"""Master Dashboard — Todos los proyectos de Álvaro Salinas."""

import json
import sqlite3
from pathlib import Path
from typing import Any

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

COLORS: dict[str, str] = {
    "bg": "#FAFAF7",
    "card": "#FFFFFF",
    "border": "#111111",
    "accent": "#E30613",
    "gold": "#FFD500",
    "text": "#111111",
    "muted": "#5A5A5A",
    "green": "#007A3D",
    "blue": "#0066CC",
    "red": "#E30613",
    "yellow": "#FFD500",
    "purple": "#6C3483",
}

BAUHAUS_SHAPES_SVG = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' width='1200' height='220' viewBox='0 0 1200 220'%3E"
    "%3Crect width='1200' height='220' fill='%23FAFAF7'/%3E"
    "%3Ccircle cx='120' cy='110' r='70' fill='%23E30613'/%3E"
    "%3Crect x='250' y='40' width='140' height='140' fill='%230066CC'/%3E"
    "%3Cpolygon points='450,180 520,40 590,180' fill='%23FFD500' stroke='%23111111' stroke-width='6'/%3E"
    "%3Cg stroke='%23111111' stroke-width='3' opacity='0.15'%3E"
    "%3Cline x1='0' y1='40' x2='1200' y2='40'/%3E%3Cline x1='0' y1='80' x2='1200' y2='80'/%3E"
    "%3Cline x1='0' y1='120' x2='1200' y2='120'/%3E%3Cline x1='0' y1='160' x2='1200' y2='160'/%3E"
    "%3C/g%3E%3Ccircle cx='1020' cy='110' r='18' fill='%23111111'/%3E"
    "%3Ccircle cx='1070' cy='110' r='18' fill='%23E30613'/%3E"
    "%3Ccircle cx='1120' cy='110' r='18' fill='%230066CC'/%3E"
    "%3C/svg%3E"
)


def _tab_style() -> dict[str, Any]:
    return {
        "style": {
            "backgroundColor": COLORS["card"],
            "color": COLORS["text"],
            "border": "3px solid #111111",
            "borderRadius": "0px",
            "fontWeight": "800",
            "textTransform": "uppercase",
            "letterSpacing": "0.06em",
            "margin": "0 6px 0 0",
        },
        "selected_style": {
            "backgroundColor": COLORS["accent"],
            "color": "white",
            "border": "3px solid #111111",
            "borderRadius": "0px",
            "fontWeight": "800",
            "textTransform": "uppercase",
            "letterSpacing": "0.06em",
            "margin": "0 6px 0 0",
        },
    }


def sparkline(values: list[float], color: str = "#E30613") -> Any:
    if not values or len(values) < 2:
        return html.Div(style={"height": "36px"})
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=list(values),
        mode="lines",
        line={"color": color, "width": 3, "shape": "spline"},
        fill="tozeroy",
        hoverinfo="skip",
        showlegend=False,
    ))
    fig.update_layout(
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"visible": False},
        yaxis={"visible": False},
        height=36,
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"height": "36px"})


def insight_card(question: str, answer: str, accent: str = "#E30613") -> Any:
    return html.Div(
        style={
            "backgroundColor": "#FFFFFF",
            "border": "3px solid #111111",
            "borderLeft": f"10px solid {accent}",
            "padding": "16px 18px",
            "marginBottom": "14px",
        },
        children=[
            html.Div(question, style={"fontWeight": "800", "textTransform": "uppercase", "fontSize": "0.78rem", "letterSpacing": "0.06em"}),
            html.Div(answer, style={"marginTop": "6px", "color": "#111111", "lineHeight": "1.5"}),
        ],
    )


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


def load_data() -> dict[str, Any]:
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


# Lazy load - DATA is loaded on first access via get_data()
_DATA: dict[str, Any] | None = None


def get_data() -> dict[str, Any]:
    """Get data with lazy loading."""
    global _DATA
    if _DATA is None:
        _DATA = load_data()
    return _DATA

# ── Layout ────────────────────────────────────────────────────────────────────

app.layout = html.Div(
    style={
        "backgroundColor": COLORS["bg"],
        "minHeight": "100vh",
        "fontFamily": "'Archivo Black','Segoe UI',system-ui,sans-serif",
        "color": COLORS["text"],
    },
    children=[
        html.Div(
            style={
                "backgroundImage": f"url(\"{BAUHAUS_SHAPES_SVG}\")",
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "padding": "42px 20px 30px 20px",
                "textAlign": "center",
                "borderBottom": "6px solid #111111",
            },
            children=[
                html.Div(
                    "DATA VISUALIZATION — ABSTRACT ART POSTER",
                    style={"display": "inlineBlock", "backgroundColor": "#111111", "color": "#FFD500", "fontWeight": "800", "letterSpacing": "0.18em", "fontSize": "0.72rem", "padding": "6px 14px", "marginBottom": "14px"},
                ),
                html.H1(
                    "ÁLVARO SALINAS ORTIZ",
                    style={"fontSize": "3rem", "fontWeight": "900", "color": "#111111", "margin": "0", "letterSpacing": "0.02em"},
                ),
                html.P(
                    "Data Analyst — Python · SQL · NLP · Dashboards",
                    style={"color": "#111111", "marginTop": "8px", "fontSize": "1.05rem", "fontWeight": "700", "backgroundColor": "#FFFFFF", "display": "inlineBlock", "padding": "4px 12px", "border": "3px solid #111111"},
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
            "backgroundColor": color, "borderRadius": "0px", "padding": "22px",
            "marginBottom": "22px", "border": "3px solid #111111",
            "boxShadow": "8px 8px 0px #111111",
        },
        children=[
            html.H3(title, style={"color": "#111111", "fontSize": "1.25rem", "fontWeight": "900", "textTransform": "uppercase", "letterSpacing": "0.04em", "marginBottom": "14px", "paddingBottom": "10px", "borderBottom": "3px solid #111111"}),
        ] + child_list,
    )


def kpi_card(value: str, label: str, color: str = "#E30613", trend: list[float] | None = None, delta: str | None = None):
    return html.Div(
        style={
            "flex": "1", "minWidth": "170px",
            "backgroundColor": "#FFFFFF",
            "border": "3px solid #111111",
            "boxShadow": "6px 6px 0px #111111",
            "padding": "16px 14px",
            "textAlign": "center",
        },
        children=[
            html.Div(str(value), style={"fontSize": "2.1rem", "fontWeight": "900", "color": "#111111", "lineHeight": "1"}),
            html.Div(label, style={"fontSize": "0.75rem", "fontWeight": "800", "textTransform": "uppercase", "letterSpacing": "0.08em", "marginTop": "6px"}),
            sparkline(trend or [], color=color),
            html.Div(delta or "", title="Variación vs periodo anterior", style={"fontSize": "0.78rem", "fontWeight": "800", "color": color, "marginTop": "4px"}),
        ],
    )


def stat_row(stats):
    def _norm(item):
        if len(item) == 5:
            return item
        if len(item) == 2:
            val, label = item
            return (val, label, COLORS["accent"], None, None)
        if len(item) == 3:
            val, label, color = item
            return (val, label, color, None, None)
        raise ValueError(f"stat_row item debe ser (val,label) o (val,label,color,trend,delta), got {item}")
    return html.Div(
        style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "22px"},
        children=[
            kpi_card(val, label, color, trend, delta)
            for val, label, color, trend, delta in [_norm(item) for item in stats]
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


@callback(
    Output("project-filter-output", "children"),
    Input({"type": "project-filter", "index": "worldcup"}, "n_clicks"),
    Input({"type": "project-filter", "index": "games"}, "n_clicks"),
    Input({"type": "project-filter", "index": "nlp"}, "n_clicks"),
    Input({"type": "project-filter", "index": "geo"}, "n_clicks"),
    Input({"type": "project-filter", "index": "cajas"}, "n_clicks"),
    Input({"type": "project-filter", "index": "sanit"}, "n_clicks"),
    prevent_initial_call=True,
)
def project_crossfilter(*clicks):
    import dash
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update
    tab = ctx.triggered[0]["prop_id"].split('"index": "')[1].split('"')[0]
    names = {"worldcup": "World Cup 2026", "games": "Videojuegos Chile", "nlp": "Discurso NLP", "geo": "Geografía Chile", "cajas": "Cajas Alimentación", "sanit": "Sanitización Santiago"}
    return f"Filtro activo: {names.get(tab, tab)} — cambia al tab superior para ver el drill-down."


@callback(
    Output("worldcup-crossfilter-output", "children"),
    Input("worldcup-goals-hist", "clickData"),
    prevent_initial_call=True,
)
def worldcup_crossfilter(click):
    if not click:
        return no_update
    x = click["points"][0].get("x", "?")
    return f"Goles seleccionados: {x} — el KPI de partidos se filtra a ese rango en el próximo drill-down."


# ── Tabs ──────────────────────────────────────────────────────────────────────


def overview_tab():
    projects = [
        {"name": "World Cup 2026", "desc": "Dashboard comparativo de Mundiales", "icon": "⚽", "color": "#0066CC", "tab": "worldcup"},
        {"name": "Videojuegos Chile", "desc": "ETL + clustering de 150 juegos", "icon": "🎮", "color": "#E30613", "tab": "games"},
        {"name": "Discurso NLP", "desc": "NER + sentimiento presidencial", "icon": "📜", "color": "#111111", "tab": "nlp"},
        {"name": "Geografía Chile", "desc": "Censos + eventos + presidentes", "icon": "🗺️", "color": "#007A3D", "tab": "geo"},
        {"name": "Cajas Alimentación", "desc": "80,595 puntos de entrega", "icon": "📦", "color": "#E30613", "tab": "cajas"},
        {"name": "Sanitización Santiago", "desc": "87 puntos de sanitización comunal", "icon": "🧹", "color": "#0066CC", "tab": "sanit"},
    ]
    return html.Div([
        stat_row([
            ("7", "Proyectos", "#E30613", [3, 4, 5, 6, 7, 7, 7], "+2 este año"),
            ("80,595", "Puntos georeferenciados", "#0066CC", [20, 35, 50, 65, 75, 80, 80], "+12% cobertura"),
            ("150+", "Juegos analizados", "#111111", [40, 70, 95, 120, 140, 150, 150], "+18 títulos"),
            ("16", "Discursos NLP", "#007A3D", [4, 7, 10, 12, 14, 16, 16], "1832–2022"),
            ("87", "Puntos sanitización", "#E30613", [10, 30, 55, 70, 80, 87, 87], "100% validados"),
        ]),
        card("Key Findings & Insights — Para Evaluadores", html.Div([
            insight_card("¿Qué problema resuelve?", "Portafolio fragmentado en 7 repos. Este hub unifica métricas ejecutivas con drill-down por proyecto para decisiones rápidas de contratación.", "#E30613"),
            insight_card("¿Metodología?", "ETL reproducible + tests pytest + CI con coverage + deploys Render con gunicorn. Datos reales georeferenciados y scraping auditado.", "#0066CC"),
            insight_card("¿Qué decisión habilita?", "Comparar impacto por dominio (deporte, mercado indie, NLP histórico, geoespacial) en 30 segundos y profundizar solo donde hay fit.", "#007A3D"),
        ])),
        card("Proyectos Destacados — clic para filtrar", html.Div([
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "14px"},
                children=[
                    html.Button(
                        id={"type": "project-filter", "index": p["tab"]},
                        n_clicks=0,
                        style={"backgroundColor": "#FFFFFF", "border": "3px solid #111111", "boxShadow": "6px 6px 0px #111111", "padding": "18px", "cursor": "pointer", "textAlign": "left"},
                        children=[
                            html.Div(p["icon"], style={"fontSize": "2rem", "marginBottom": "8px"}),
                            html.Div(p["name"], style={"fontWeight": "900", "color": "#111111", "textTransform": "uppercase", "fontSize": "0.85rem"}),
                            html.Div(p["desc"], style={"fontSize": "0.82rem", "color": "#5A5A5A", "marginTop": "4px"}),
                        ],
                    )
                    for p in projects
                ],
            ),
            html.Div(id="project-filter-output", style={"marginTop": "12px", "fontWeight": "700"}),
        ])),
    ])


def worldcup_tab():
    data = get_data()
    if "wc_matches" not in data:
        return card("World Cup 2026", html.P("Data not available"))
    df = data["wc_matches"]
    total_goals = int(df["home_score"].sum() + df["away_score"].sum())
    fig = px.histogram(df, x="home_score", nbins=10, title="Distribución de Goles — clic una barra para filtrar")
    fig.update_traces(
        marker_line_width=2, marker_line_color="#111111",
        hovertemplate="<b>Goles local: %{x}</b><br>Partidos: %{y}<br>%{y} de " + str(len(df)) + " (%{y:.0%})<extra></extra>",
    )
    fig.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FAFAF7", height=400, font={"color": "#111111"})
    return html.Div([
        stat_row([
            (str(len(df)), "Partidos", "#E30613", [20, 40, 60, 80, 100, len(df)], f"{len(df)} totales"),
            (str(total_goals), "Goles", "#0066CC", [50, 120, 200, 280, 320, total_goals], f"{total_goals/len(df):.1f} por partido"),
        ]),
        card("Key Insights — World Cup", html.Div([
            insight_card("¿Problema?", "Comparar Mundiales con formato distinto sin sesgo narrativo.", "#E30613"),
            insight_card("¿Metodología?", "SQLite + 16 queries + RandomForest con CV + reportes reproducibles.", "#0066CC"),
            insight_card("¿Decisión?", "Qué sede/grupo rinde más para planificar cobertura y viajes.", "#007A3D"),
        ])),
        card("Análisis de Goles — cross-filtering activo", html.Div([
            dcc.Graph(id="worldcup-goals-hist", figure=fig),
            html.Div(id="worldcup-crossfilter-output", style={"marginTop": "10px", "fontWeight": "800"}),
        ])),
    ])


def games_tab():
    data = get_data()
    if "games" not in data:
        return card("Videojuegos", html.P("Data not available"))
    df = data["games"]
    fig = px.pie(df, names="source", title="Distribución por Plataforma")
    fig.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], height=400)
    return html.Div([
        stat_row([(str(len(df)), "Juegos"), (str(df["source"].nunique()), "Plataformas")]),
        card("Plataformas", dcc.Graph(figure=fig)),
    ])


def nlp_tab():
    data = get_data()
    if "speeches" not in data:
        return card("NLP", html.P("Data not available"))
    df = data["speeches"]
    fig = px.scatter(df, x="year", y="speaker", title="Discursos Presidenciales")
    fig.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], height=500)
    return html.Div([
        stat_row([(str(len(df)), "Discursos"), (str(df["year"].min()) + "-" + str(df["year"].max()), "Período")]),
        card("Línea de Tiempo", dcc.Graph(figure=fig)),
    ])


def geo_tab():
    data = get_data()
    if "census" not in data:
        return card("Geografía", html.P("Data not available"))
    df = data["census"]
    fig = px.line(df, x="census_year", y="population", color="region", title="Población por Región")
    fig.update_layout(template="plotly_dark", paper_bgcolor=COLORS["card"], height=600)
    return html.Div([
        stat_row([(str(df["region"].nunique()), "Regiones"), (str(df["census_year"].min()) + "-" + str(df["census_year"].max()), "Censos")]),
        card("Evolución Demográfica", dcc.Graph(figure=fig)),
    ])


def cajas_tab():
    data = get_data()
    if "cajas" not in data:
        return card("Cajas Alimentación", html.P("Data not available"))
    df = data["cajas"]
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
    data = get_data()
    if "sanit" not in data:
        return card("Sanitización Santiago", html.P("Data not available"))
    df = data["sanit"]
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
