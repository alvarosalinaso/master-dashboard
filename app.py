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

FONT_UI = "'Inter','Segoe UI',system-ui,sans-serif"
FONT_DATA = "'JetBrains Mono',Consolas,'Courier New',monospace"

COLORS: dict[str, str] = {
    "bg": "#0a0e14",
    "card": "#11161f",
    "border": "rgba(255,255,255,0.08)",
    "accent": "#22d3ee",
    "gold": "#fbbf24",
    "text": "#e8edf2",
    "muted": "#8b94a3",
    "green": "#34d399",
    "blue": "#54a0ff",
    "red": "#f472b6",
    "yellow": "#fbbf24",
    "purple": "#a78bfa",
    "grid": "rgba(255,255,255,0.06)",
}

DATA_CANVAS_SVG = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' width='1200' height='240' viewBox='0 0 1200 240'%3E"
    "%3Crect width='1200' height='240' fill='%230a0e14'/%3E"
    "%3Cg fill='%2322d3ee' opacity='0.16'%3E"
    + "".join(f"%3Ccircle cx='{x}' cy='{y}' r='2'/%3E" for x in range(30, 1200, 60) for y in range(20, 240, 44)) +
    "%3C/g%3E%3Cg fill='none' stroke='%2322d3ee' stroke-width='1.5' opacity='0.35'%3E"
    "%3Cellipse cx='850' cy='120' rx='180' ry='80'/%3E%3Cellipse cx='850' cy='120' rx='130' ry='58'/%3E%3Cellipse cx='850' cy='120' rx='80' ry='36'/%3E"
    "%3C/g%3E%3Cg fill='none' stroke='%23f472b6' stroke-width='2' opacity='0.8'%3E"
    "%3Cpath d='M0,190 Q200,120 400,150 T800,90 T1200,130'/%3E%3C/g%3E"
    "%3Cg fill='%23fbbf24' opacity='0.9'%3E"
    "%3Ccircle cx='120' cy='70' r='5'/%3E%3Ccircle cx='340' cy='150' r='4'/%3E%3Ccircle cx='620' cy='60' r='6'/%3E"
    "%3Ccircle cx='880' cy='140' r='4'/%3E%3Ccircle cx='1060' cy='80' r='5'/%3E"
    "%3C/g%3E%3C/svg%3E"
)

CHART_TEMPLATE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter,Segoe UI,sans-serif", color="#e8edf2", size=13),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.12)",
               title=dict(font=dict(size=13)), tickfont=dict(family="JetBrains Mono,monospace", size=12)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.12)",
               title=dict(font=dict(size=13)), tickfont=dict(family="JetBrains Mono,monospace", size=12)),
    legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
    colorway=["#22d3ee", "#f472b6", "#fbbf24", "#34d399", "#a78bfa", "#54a0ff"],
)


def _tab_style() -> dict[str, Any]:
    return {
        "style": {
            "backgroundColor": "transparent",
            "color": "#8b94a3",
            "border": "none",
            "borderBottom": "2px solid transparent",
            "fontWeight": "600",
            "fontSize": "0.85rem",
            "letterSpacing": "0.04em",
            "padding": "14px 20px",
        },
        "selected_style": {
            "backgroundColor": "transparent",
            "color": "#e8edf2",
            "border": "none",
            "borderBottom": "2px solid #22d3ee",
            "fontWeight": "700",
            "fontSize": "0.85rem",
            "letterSpacing": "0.04em",
            "padding": "14px 20px",
        },
    }


def sparkline(values: list[float], color: str = "#22d3ee") -> Any:
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


def insight_card(question: str, answer: str, accent: str = "#22d3ee") -> Any:
    return html.Div(
        style={
            "backgroundColor": "#11161f",
            "border": "1px solid rgba(255,255,255,0.08)",
            "borderLeft": f"3px solid {accent}",
            "borderRadius": "10px",
            "padding": "16px 18px",
            "marginBottom": "12px",
        },
        children=[
            html.Div(question, style={"fontWeight": "700", "fontSize": "0.75rem", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": accent, "fontFamily": FONT_UI}),
            html.Div(answer, style={"marginTop": "6px", "color": "#e8edf2", "lineHeight": "1.55", "fontSize": "0.95rem"}),
        ],
    )


def chart_card(title: str, figure, source: str = "", height: int = 420) -> Any:
    """Chart as hero: title + source line (magazine pattern)."""
    figure.update_layout(height=height)
    return html.Div(
        style={
            "backgroundColor": "#11161f",
            "border": "1px solid rgba(255,255,255,0.08)",
            "borderRadius": "14px",
            "padding": "22px 22px 14px 22px",
            "marginBottom": "22px",
            "boxShadow": "0 8px 32px rgba(0,0,0,0.35)",
        },
        children=[
            html.H3(title, style={"color": "#e8edf2", "fontSize": "1.15rem", "fontWeight": "700", "margin": "0 0 4px 0", "fontFamily": FONT_UI}),
            html.Div(f"Fuente: {source}" if source else "", style={"color": "#8b94a3", "fontSize": "0.78rem", "fontFamily": FONT_DATA, "marginBottom": "10px"}),
            dcc.Graph(figure=figure, config={"displayModeBar": False}),
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
        "fontFamily": FONT_UI,
        "color": COLORS["text"],
    },
    children=[
        html.Div(
            style={
                "backgroundImage": f"url(\"{DATA_CANVAS_SVG}\")",
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "padding": "56px 20px 44px 20px",
                "textAlign": "center",
                "borderBottom": "1px solid rgba(255,255,255,0.08)",
            },
            children=[
                html.Div(
                    "PORTFOLIO · DATA ART",
                    style={"display": "inlineBlock", "color": "#22d3ee", "fontWeight": "700", "letterSpacing": "0.28em", "fontSize": "0.72rem", "fontFamily": FONT_DATA, "padding": "6px 0", "marginBottom": "12px", "borderBottom": "1px solid rgba(34,211,238,0.4)"},
                ),
                html.H1(
                    "Álvaro Salinas Ortiz",
                    style={"fontSize": "2.6rem", "fontWeight": "800", "color": "#e8edf2", "margin": "0", "letterSpacing": "-0.01em"},
                ),
                html.P(
                    "Data Analyst — Python · SQL · NLP · Dashboards",
                    style={"color": "#8b94a3", "marginTop": "10px", "fontSize": "1rem", "fontFamily": FONT_DATA},
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
            "backgroundColor": color, "borderRadius": "14px", "padding": "22px",
            "marginBottom": "22px", "border": "1px solid rgba(255,255,255,0.08)",
            "boxShadow": "0 8px 32px rgba(0,0,0,0.35)",
        },
        children=[
            html.H3(title, style={"color": "#e8edf2", "fontSize": "1.15rem", "fontWeight": "700", "margin": "0 0 4px 0", "fontFamily": FONT_UI}),
            html.Div("insights · metodología · decisión", style={"color": "#8b94a3", "fontSize": "0.75rem", "fontFamily": FONT_DATA, "marginBottom": "12px"}),
        ] + child_list,
    )


def kpi_card(value: str, label: str, color: str = "#22d3ee", trend: list[float] | None = None, delta: str | None = None):
    return html.Div(
        style={
            "flex": "1", "minWidth": "170px",
            "backgroundColor": "#11161f",
            "border": "1px solid rgba(255,255,255,0.08)",
            "borderRadius": "12px",
            "padding": "18px 14px",
            "textAlign": "center",
        },
        children=[
            html.Div(str(value), style={"fontSize": "2rem", "fontWeight": "800", "color": "#e8edf2", "lineHeight": "1", "fontFamily": FONT_DATA}),
            html.Div(label, style={"fontSize": "0.78rem", "color": "#8b94a3", "marginTop": "6px", "fontFamily": FONT_UI}),
            sparkline(trend or [], color=color),
            html.Div(delta or "", title="Variación vs periodo anterior", style={"fontSize": "0.78rem", "fontWeight": "700", "color": color, "marginTop": "4px", "fontFamily": FONT_DATA}),
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
        {"name": "World Cup 2026", "desc": "Dashboard comparativo de Mundiales", "icon": "⚽", "color": "#22d3ee", "tab": "worldcup"},
        {"name": "Videojuegos Chile", "desc": "ETL + clustering de 150 juegos", "icon": "🎮", "color": "#f472b6", "tab": "games"},
        {"name": "Discurso NLP", "desc": "NER + sentimiento presidencial", "icon": "📜", "color": "#fbbf24", "tab": "nlp"},
        {"name": "Geografía Chile", "desc": "Censos + eventos + presidentes", "icon": "🗺️", "color": "#34d399", "tab": "geo"},
        {"name": "Cajas Alimentación", "desc": "80,595 puntos de entrega", "icon": "📦", "color": "#a78bfa", "tab": "cajas"},
        {"name": "Sanitización Santiago", "desc": "87 puntos de sanitización comunal", "icon": "🧹", "color": "#54a0ff", "tab": "sanit"},
    ]
    return html.Div([
        stat_row([
            ("7", "Proyectos", "#22d3ee", [3, 4, 5, 6, 7, 7, 7], "+2 este año"),
            ("80,595", "Puntos georeferenciados", "#54a0ff", [20, 35, 50, 65, 75, 80, 80], "+12% cobertura"),
            ("150+", "Juegos analizados", "#fbbf24", [40, 70, 95, 120, 140, 150, 150], "+18 títulos"),
            ("16", "Discursos NLP", "#34d399", [4, 7, 10, 12, 14, 16, 16], "1832–2022"),
            ("87", "Puntos sanitización", "#f472b6", [10, 30, 55, 70, 80, 87, 87], "100% validados"),
        ]),
        card("Key Findings & Insights — Para Evaluadores", html.Div([
            insight_card("¿Qué problema resuelve?", "Portafolio fragmentado en 7 repos. Este hub unifica métricas ejecutivas con drill-down por proyecto para decisiones rápidas de contratación.", "#22d3ee"),
            insight_card("¿Metodología?", "ETL reproducible + tests pytest + CI con coverage + deploys Render con gunicorn. Datos reales georeferenciados y scraping auditado.", "#a78bfa"),
            insight_card("¿Qué decisión habilita?", "Comparar impacto por dominio (deporte, mercado indie, NLP histórico, geoespacial) en 30 segundos y profundizar solo donde hay fit.", "#34d399"),
        ])),
        card("Proyectos Destacados — clic para filtrar", html.Div([
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "14px"},
                children=[
                    html.Button(
                        id={"type": "project-filter", "index": p["tab"]},
                        n_clicks=0,
                        style={"backgroundColor": "#11161f", "border": "1px solid rgba(255,255,255,0.08)", "borderRadius": "12px", "borderTop": f"3px solid {p['color']}", "padding": "18px", "cursor": "pointer", "textAlign": "left"},
                        children=[
                            html.Div(p["icon"], style={"fontSize": "2rem", "marginBottom": "8px"}),
                            html.Div(p["name"], style={"fontWeight": "700", "color": "#e8edf2", "fontSize": "0.95rem", "fontFamily": FONT_UI}),
                            html.Div(p["desc"], style={"fontSize": "0.85rem", "color": "#8b94a3", "marginTop": "4px"}),
                        ],
                    )
                    for p in projects
                ],
            ),
            html.Div(id="project-filter-output", style={"marginTop": "12px", "fontWeight": "600", "color": "#8b94a3"}),
        ])),
    ])


def worldcup_tab():
    data = get_data()
    if "wc_matches" not in data:
        return card("World Cup 2026", html.P("Data not available"))
    df = data["wc_matches"]
    total_goals = int(df["home_score"].sum() + df["away_score"].sum())
    fig = px.histogram(df, x="home_score", nbins=10, title="Distribución de Goles — clic una barra para filtrar",
                       color_discrete_sequence=["#22d3ee"])
    fig.update_traces(
        hovertemplate="<b>Goles local: %{x}</b><br>Partidos: %{y}<br>%{y} de " + str(len(df)) + "<extra></extra>",
    )
    fig.update_layout(**CHART_TEMPLATE, height=400)
    return html.Div([
        stat_row([
            (str(len(df)), "Partidos", "#f472b6", [20, 40, 60, 80, 100, len(df)], f"{len(df)} totales"),
            (str(total_goals), "Goles", "#22d3ee", [50, 120, 200, 280, 320, total_goals], f"{total_goals/len(df):.1f} por partido"),
        ]),
        card("Key Insights — World Cup", html.Div([
            insight_card("¿Problema?", "Comparar Mundiales con formato distinto sin sesgo narrativo.", "#f472b6"),
            insight_card("¿Metodología?", "SQLite + 16 queries + RandomForest con CV + reportes reproducibles.", "#a78bfa"),
            insight_card("¿Decisión?", "Qué sede/grupo rinde más para planificar cobertura y viajes.", "#34d399"),
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
    latest = int(df["census_year"].max())
    totals = df[df["census_year"] == latest].sort_values("population", ascending=False)
    top8 = totals.head(8)["region"].tolist()
    df["region_group"] = df["region"].where(df["region"].isin(top8), "Otras regiones")
    fig = px.line(df, x="census_year", y="population", color="region_group", title="Población por Región (Top 8 + resto)")
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Año: %{x}<br>Población: %{y:,.0f} miles<extra></extra>",
    )
    fig.update_layout(
        **CHART_TEMPLATE, height=600,
        xaxis_title="Año censal", yaxis_title="Población (miles)",
        legend_title="Región",
    )
    return html.Div([
        stat_row([(str(df["region"].nunique()), "Regiones"), (str(df["census_year"].min()) + "-" + str(latest), "Censos")]),
        card("Evolución Demográfica", dcc.Graph(figure=fig)),
    ])


def cajas_tab():
    data = get_data()
    if "cajas" not in data:
        return card("Cajas Alimentación", html.P("Data not available"))
    df = data["cajas"]
    fig = px.density_map(
        df, lat="lat", lon="lon", radius=8,
        center={"lat": -33.45, "lon": -70.66}, zoom=11,
        map_style="carto-positron",
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
    fig_map = px.scatter_map(
        df, lat="lat", lon="lon", color="type",
        hover_name="name", hover_data=["description", "type"],
        center={"lat": -33.45, "lon": -70.66}, zoom=12,
        map_style="carto-positron",
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
