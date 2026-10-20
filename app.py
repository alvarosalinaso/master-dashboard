"""Master Dashboard — Todos los proyectos de Álvaro Salinas."""

import logging
import sqlite3
from pathlib import Path
from typing import Any

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import ALL, Input, Output, callback, dcc, html, no_update

logger = logging.getLogger(__name__)

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
    + "".join(
        f"%3Ccircle cx='{x}' cy='{y}' r='2'/%3E"
        for x in range(30, 1200, 60)
        for y in range(20, 240, 44)
    )
    + "%3C/g%3E%3Cg fill='none' stroke='%2322d3ee' stroke-width='1.5' opacity='0.35'%3E"
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
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        zerolinecolor="rgba(255,255,255,0.12)",
        title=dict(font=dict(size=13)),
        tickfont=dict(family="JetBrains Mono,monospace", size=12),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        zerolinecolor="rgba(255,255,255,0.12)",
        title=dict(font=dict(size=13)),
        tickfont=dict(family="JetBrains Mono,monospace", size=12),
    ),
    legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
    # Okabe-Ito (2008), ordenado para dark: colorblind-safe categórico.
    colorway=[
        "#56B4E9",
        "#E69F00",
        "#009E73",
        "#F0E442",
        "#CC79A7",
        "#D55E00",
        "#0072B2",
        "#999999",
    ],
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
    fig.add_trace(
        go.Scatter(
            y=list(values),
            mode="lines",
            line={"color": color, "width": 3, "shape": "spline"},
            fill="tozeroy",
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.update_layout(
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"visible": False},
        yaxis={"visible": False},
        height=36,
    )
    return dcc.Graph(
        figure=fig, config={"displayModeBar": False}, style={"height": "36px"}
    )


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
            html.Div(
                question,
                style={
                    "fontWeight": "700",
                    "fontSize": "0.75rem",
                    "letterSpacing": "0.08em",
                    "textTransform": "uppercase",
                    "color": accent,
                    "fontFamily": FONT_UI,
                },
            ),
            html.Div(
                answer,
                style={
                    "marginTop": "6px",
                    "color": "#e8edf2",
                    "lineHeight": "1.55",
                    "fontSize": "0.95rem",
                },
            ),
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
            html.H3(
                title,
                style={
                    "color": "#e8edf2",
                    "fontSize": "1.15rem",
                    "fontWeight": "700",
                    "margin": "0 0 4px 0",
                    "fontFamily": FONT_UI,
                },
            ),
            html.Div(
                f"Fuente: {source}" if source else "",
                style={
                    "color": "#8b94a3",
                    "fontSize": "0.78rem",
                    "fontFamily": FONT_DATA,
                    "marginBottom": "10px",
                },
            ),
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
PRESIDENTS_CSV = (
    BASE / "chile-geografia-historica" / "data" / "processed" / "presidents.csv"
)
CAJAS_CSV = BASE / "cajas-alimentacion" / "data" / "raw" / "coordinates.csv"
SANIT_CSV = BASE / "sanitizacion-santiago" / "data" / "raw" / "sanitization_points.csv"

# Índice de navegación: cada tab apunta al repo hermano del que lee sus datos.
PROJECTS: list[dict[str, Any]] = [
    {
        "tab": "worldcup",
        "name": "World Cup 2026",
        "icon": "⚽",
        "color": "#22d3ee",
        "desc": "Dashboard comparativo de Mundiales",
        "source_repo": "worldcup-2026",
    },
    {
        "tab": "games",
        "name": "Videojuegos Chile",
        "icon": "🎮",
        "color": "#f472b6",
        "desc": "ETL + clustering de juegos",
        "desc_count": "ETL + clustering de {n} juegos",
        "count_key": "games",
        "source_repo": "chilean-videogames-analysis",
    },
    {
        "tab": "nlp",
        "name": "Discurso NLP",
        "icon": "📜",
        "color": "#fbbf24",
        "desc": "NER + sentimiento presidencial",
        "source_repo": "geopolitica-textual-nlp",
    },
    {
        "tab": "geo",
        "name": "Geografía Chile",
        "icon": "🗺️",
        "color": "#34d399",
        "desc": "Censos + eventos + presidentes",
        "source_repo": "chile-geografia-historica",
    },
    {
        "tab": "cajas",
        "name": "Cajas Alimentación",
        "icon": "📦",
        "color": "#a78bfa",
        "desc": "Puntos de entrega de cajas",
        "desc_count": "{n} puntos de entrega",
        "count_key": "cajas",
        "source_repo": "cajas-alimentacion",
    },
    {
        "tab": "sanit",
        "name": "Sanitización Santiago",
        "icon": "🧹",
        "color": "#54a0ff",
        "desc": "Puntos de sanitización comunal (datos no disponibles)",
        "desc_count": "{n} puntos de sanitización comunal",
        "count_key": "sanit",
        "source_repo": "sanitizacion-santiago",
    },
]


def _load_error(path: Path, exc: Exception) -> None:
    logger.warning("Dataset no disponible (%s): %s", path, exc)


def load_data() -> dict[str, Any]:
    """Carga cada dataset por separado.

    Degradación por archivo: si falta o falla la lectura de uno, se registra el
    aviso y el resto de los datasets se carga igual (nunca un crash global).
    """
    data: dict[str, Any] = {}
    if WC_DB.exists():
        try:
            with sqlite3.connect(str(WC_DB)) as conn:
                data["wc_matches"] = pd.read_sql("SELECT * FROM matches", conn)
                data["wc_teams"] = pd.read_sql("SELECT * FROM teams", conn)
        except Exception as exc:
            _load_error(WC_DB, exc)
    csv_datasets: tuple[tuple[str, Path], ...] = (
        ("games", GAMES_CSV),
        ("speeches", SPEECHES_CSV),
        ("census", CENSUS_CSV),
        ("events", EVENTS_CSV),
        ("presidents", PRESIDENTS_CSV),
        ("cajas", CAJAS_CSV),
        ("sanit", SANIT_CSV),
    )
    for key, path in csv_datasets:
        if not path.exists():
            continue
        try:
            data[key] = pd.read_csv(path)
        except Exception as exc:
            _load_error(path, exc)
    return data


# Lazy load - DATA is loaded on first access via get_data()
_DATA: dict[str, Any] | None = None


def get_data() -> dict[str, Any]:
    """Get data with lazy loading."""
    global _DATA
    if _DATA is None:
        _DATA = load_data()
    return _DATA


def overview_kpis() -> dict[str, int | None]:
    """Cifras del tab Resumen, derivadas de load_data(). None = dataset no disponible."""
    data = get_data()

    def rows(key: str) -> int | None:
        frame = data.get(key)
        return None if frame is None else len(frame)

    return {
        "projects": len(PROJECTS),
        "games": rows("games"),
        "speeches": rows("speeches"),
        "cajas_points": rows("cajas"),
        "sanit_points": rows("sanit"),
    }


def kpi_value(value: int | None) -> str:
    """Renderiza un KPI: miles con coma o n/d si el dataset no está disponible."""
    return "n/d" if value is None else f"{value:,}"


def project_desc(project: dict[str, Any]) -> str:
    """Descripción del proyecto; usa el recuento real cuando hay datos en disco."""
    template = project.get("desc_count")
    if template is None:
        return str(project["desc"])
    frame = get_data().get(str(project.get("count_key")))
    if frame is None:
        return str(project["desc"])
    return template.format(n=f"{len(frame):,}")


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
                "backgroundImage": f'url("{DATA_CANVAS_SVG}")',
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "padding": "56px 20px 44px 20px",
                "textAlign": "center",
                "borderBottom": "1px solid rgba(255,255,255,0.08)",
            },
            children=[
                html.Div(
                    "PORTFOLIO · DATA ART",
                    style={
                        "display": "inlineBlock",
                        "color": "#22d3ee",
                        "fontWeight": "700",
                        "letterSpacing": "0.28em",
                        "fontSize": "0.72rem",
                        "fontFamily": FONT_DATA,
                        "padding": "6px 0",
                        "marginBottom": "12px",
                        "borderBottom": "1px solid rgba(34,211,238,0.4)",
                    },
                ),
                html.H1(
                    "Álvaro Salinas Ortiz",
                    style={
                        "fontSize": "2.6rem",
                        "fontWeight": "800",
                        "color": "#e8edf2",
                        "margin": "0",
                        "letterSpacing": "-0.01em",
                    },
                ),
                html.P(
                    "Data Analyst — Python · SQL · NLP · Dashboards",
                    style={
                        "color": "#8b94a3",
                        "marginTop": "10px",
                        "fontSize": "1rem",
                        "fontFamily": FONT_DATA,
                    },
                ),
            ],
        ),
        dcc.Tabs(
            id="tabs",
            value="overview",
            style={
                "backgroundColor": COLORS["card"],
                "borderBottom": f"1px solid {COLORS['border']}",
            },
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
        html.Div(
            id="tab-content",
            style={"maxWidth": "1200px", "margin": "0 auto", "padding": "30px 20px"},
        ),
    ],
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def card(title, children, color=COLORS["card"]):
    child_list = children if isinstance(children, list) else [children]
    return html.Div(
        style={
            "backgroundColor": color,
            "borderRadius": "14px",
            "padding": "22px",
            "marginBottom": "22px",
            "border": "1px solid rgba(255,255,255,0.08)",
            "boxShadow": "0 8px 32px rgba(0,0,0,0.35)",
        },
        children=[
            html.H3(
                title,
                style={
                    "color": "#e8edf2",
                    "fontSize": "1.15rem",
                    "fontWeight": "700",
                    "margin": "0 0 4px 0",
                    "fontFamily": FONT_UI,
                },
            ),
            html.Div(
                "insights · metodología · decisión",
                style={
                    "color": "#8b94a3",
                    "fontSize": "0.75rem",
                    "fontFamily": FONT_DATA,
                    "marginBottom": "12px",
                },
            ),
        ]
        + child_list,
    )


def kpi_card(
    value: str,
    label: str,
    color: str = "#22d3ee",
    trend: list[float] | None = None,
    delta: str | None = None,
):
    return html.Div(
        style={
            "flex": "1",
            "minWidth": "170px",
            "backgroundColor": "#11161f",
            "border": "1px solid rgba(255,255,255,0.08)",
            "borderRadius": "12px",
            "padding": "18px 14px",
            "textAlign": "center",
        },
        children=[
            html.Div(
                str(value),
                style={
                    "fontSize": "2rem",
                    "fontWeight": "800",
                    "color": "#e8edf2",
                    "lineHeight": "1",
                    "fontFamily": FONT_DATA,
                },
            ),
            html.Div(
                label,
                style={
                    "fontSize": "0.78rem",
                    "color": "#8b94a3",
                    "marginTop": "6px",
                    "fontFamily": FONT_UI,
                },
            ),
            sparkline(trend or [], color=color),
            html.Div(
                delta or "",
                title="Variación vs periodo anterior",
                style={
                    "fontSize": "0.78rem",
                    "fontWeight": "700",
                    "color": color,
                    "marginTop": "4px",
                    "fontFamily": FONT_DATA,
                },
            ),
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
        raise ValueError(
            f"stat_row item debe ser (val,label) o (val,label,color,trend,delta), got {item}"
        )

    return html.Div(
        style={
            "display": "flex",
            "gap": "14px",
            "flexWrap": "wrap",
            "marginBottom": "22px",
        },
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
    Output("tabs", "value"),
    Input({"type": "project-filter", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def project_open_tab(*_clicks):
    """Clic en una tarjeta de proyecto → abre su tab (navegación, no drill-down)."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update
    triggered = ctx.triggered_id
    if not isinstance(triggered, dict):
        return no_update
    return triggered.get("index") or no_update


@callback(
    Output("worldcup-crossfilter-output", "children"),
    Input("worldcup-goals-hist", "clickData"),
    prevent_initial_call=True,
)
def worldcup_crossfilter(click):
    """Feedback honesto: el clic solo informa; este hub no aplica filtros."""
    if not click:
        return no_update
    x = click["points"][0].get("x", "?")
    return (
        f"Goles del local en la barra seleccionada: {x}. "
        "Este hub no filtra datos: el detalle está en el repo worldcup-2026."
    )


# ── Tabs ──────────────────────────────────────────────────────────────────────


def overview_tab():
    kpis = overview_kpis()
    projects = [{**p, "desc": project_desc(p)} for p in PROJECTS]
    return html.Div(
        [
            stat_row(
                [
                    (kpi_value(kpis["projects"]), "Proyectos", "#22d3ee"),
                    (kpi_value(kpis["games"]), "Juegos analizados", "#fbbf24"),
                    (kpi_value(kpis["speeches"]), "Discursos NLP", "#34d399"),
                    (kpi_value(kpis["cajas_points"]), "Puntos de entrega", "#54a0ff"),
                    (kpi_value(kpis["sanit_points"]), "Puntos sanitización", "#f472b6"),
                ]
            ),
            html.Div(
                "n/d = dataset no disponible en disco (archivo ausente o ilegible); "
                "el resto de los KPIs se recalcula al iniciar la app desde load_data().",
                style={
                    "color": COLORS["muted"],
                    "fontSize": "0.75rem",
                    "fontFamily": FONT_DATA,
                    "marginTop": "-14px",
                    "marginBottom": "22px",
                },
            ),
            card(
                "Key Findings & Insights — Para Evaluadores",
                html.Div(
                    [
                        insight_card(
                            "¿Qué problema resuelve?",
                            f"Portafolio repartido en {len(PROJECTS)} proyectos más este hub. "
                            "Este tab reúne sus cifras en una sola pantalla para compararlas rápido.",
                            "#22d3ee",
                        ),
                        insight_card(
                            "¿Metodología?",
                            "Los datos no se copian aquí: cada tab lee el CSV/DB de su repo hermano "
                            "con rutas relativas. Tests con pytest y CI con ruff + pytest en GitHub "
                            "Actions; infraestructura Docker con gunicorn (infra/).",
                            "#a78bfa",
                        ),
                        insight_card(
                            "¿Qué decisión habilita?",
                            "Comparar cobertura por dominio (deporte, mercado indie, NLP histórico, "
                            "geoespacial) y decidir en qué proyecto profundizar abriendo su tab.",
                            "#34d399",
                        ),
                    ]
                ),
            ),
            card(
                "Proyectos Destacados — clic para abrir su tab",
                html.Div(
                    [
                        html.Div(
                            style={
                                "display": "grid",
                                "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                                "gap": "14px",
                            },
                            children=[
                                html.Button(
                                    id={"type": "project-filter", "index": p["tab"]},
                                    n_clicks=0,
                                    style={
                                        "backgroundColor": "#11161f",
                                        "border": "1px solid rgba(255,255,255,0.08)",
                                        "borderRadius": "12px",
                                        "borderTop": f"3px solid {p['color']}",
                                        "padding": "18px",
                                        "cursor": "pointer",
                                        "textAlign": "left",
                                    },
                                    children=[
                                        html.Div(
                                            p["icon"],
                                            style={
                                                "fontSize": "2rem",
                                                "marginBottom": "8px",
                                            },
                                        ),
                                        html.Div(
                                            p["name"],
                                            style={
                                                "fontWeight": "700",
                                                "color": "#e8edf2",
                                                "fontSize": "0.95rem",
                                                "fontFamily": FONT_UI,
                                            },
                                        ),
                                        html.Div(
                                            p["desc"],
                                            style={
                                                "fontSize": "0.85rem",
                                                "color": "#8b94a3",
                                                "marginTop": "4px",
                                            },
                                        ),
                                    ],
                                )
                                for p in projects
                            ],
                        ),
                    ]
                ),
            ),
        ]
    )


def worldcup_tab():
    data = get_data()
    if "wc_matches" not in data:
        return card("World Cup 2026", html.P("Data not available"))
    df = data["wc_matches"]
    total_goals = int(df["home_score"].sum() + df["away_score"].sum())
    fig = px.histogram(
        df,
        x="home_score",
        nbins=10,
        title="Distribución de Goles por partido",
        color_discrete_sequence=["#22d3ee"],
    )
    fig.update_traces(
        hovertemplate="<b>Goles local: %{x}</b><br>Partidos: %{y}<br>%{y} de "
        + str(len(df))
        + "<extra></extra>",
    )
    fig.update_layout(**CHART_TEMPLATE, height=400)
    return html.Div(
        [
            stat_row(
                [
                    (
                        str(len(df)),
                        "Partidos",
                        "#f472b6",
                        None,
                        f"{len(df)} totales",
                    ),
                    (
                        str(total_goals),
                        "Goles",
                        "#22d3ee",
                        None,
                        f"{total_goals / len(df):.1f} por partido",
                    ),
                ]
            ),
            card(
                "Key Insights — World Cup",
                html.Div(
                    [
                        insight_card(
                            "¿Problema?",
                            "Comparar Mundiales con formato distinto sin sesgo narrativo.",
                            "#f472b6",
                        ),
                        insight_card(
                            "¿Metodología?",
                            "SQLite + consultas analíticas en queries.py + reportes reproducibles "
                            "(todo vive en el repo worldcup-2026).",
                            "#a78bfa",
                        ),
                        insight_card(
                            "¿Decisión?",
                            "Qué sede/grupo rinde más para planificar cobertura y viajes.",
                            "#34d399",
                        ),
                    ]
                ),
            ),
            card(
                "Análisis de Goles",
                html.Div(
                    [
                        dcc.Graph(id="worldcup-goals-hist", figure=fig),
                        html.Div(
                            id="worldcup-crossfilter-output",
                            style={"marginTop": "10px", "fontWeight": "800"},
                        ),
                    ]
                ),
            ),
        ]
    )


def games_tab():
    data = get_data()
    if "games" not in data:
        return card("Videojuegos", html.P("Data not available"))
    df = data["games"]
    fig = px.pie(df, names="source", title="Distribución por Plataforma")
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Juegos: %{value}<br>%{percent}<extra></extra>",
    )
    fig.update_layout(**CHART_TEMPLATE, height=400)
    return html.Div(
        [
            stat_row(
                [(str(len(df)), "Juegos"), (str(df["source"].nunique()), "Plataformas")]
            ),
            card(
                "Plataformas",
                html.Div(
                    [
                        dcc.Graph(id="m-games-pie", figure=fig),
                        html.Div(
                            id="m-games-output",
                            style={
                                "marginTop": "8px",
                                "color": "#8b94a3",
                                "fontWeight": "600",
                            },
                        ),
                    ]
                ),
            ),
        ]
    )


def nlp_tab():
    data = get_data()
    if "speeches" not in data:
        return card("NLP", html.P("Data not available"))
    df = data["speeches"]
    fig = px.scatter(
        df,
        x="year",
        y="speaker",
        title="Discursos Presidenciales por año",
    )
    fig.update_traces(
        marker=dict(size=10),
        hovertemplate="Año: %{x}<br>%{y}<extra></extra>",
    )
    fig.update_layout(**CHART_TEMPLATE, height=500)
    return html.Div(
        [
            stat_row(
                [
                    (str(len(df)), "Discursos"),
                    (str(df["year"].min()) + "-" + str(df["year"].max()), "Período"),
                ]
            ),
            card(
                "Línea de Tiempo",
                html.Div(
                    [
                        dcc.Graph(id="m-nlp-scatter", figure=fig),
                        html.Div(
                            id="m-nlp-output",
                            style={
                                "marginTop": "8px",
                                "color": "#8b94a3",
                                "fontWeight": "600",
                            },
                        ),
                    ]
                ),
            ),
        ]
    )


def geo_tab():
    data = get_data()
    if "census" not in data:
        return card("Geografía", html.P("Data not available"))
    df = data["census"]
    latest = int(df["census_year"].max())
    totals = df[df["census_year"] == latest].sort_values("population", ascending=False)
    top8 = totals.head(8)["region"].tolist()
    df["region_group"] = df["region"].where(df["region"].isin(top8), "Otras regiones")
    fig = px.line(
        df,
        x="census_year",
        y="population",
        color="region_group",
        title="Población por Región (Top 8 + resto)",
    )
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Año: %{x}<br>Población: %{y:,.0f} miles<extra></extra>",
    )
    fig.update_layout(
        **CHART_TEMPLATE,
        height=600,
        xaxis_title="Año censal",
        yaxis_title="Población (miles)",
        legend_title="Región",
    )
    return html.Div(
        [
            stat_row(
                [
                    (str(df["region"].nunique()), "Regiones"),
                    (str(df["census_year"].min()) + "-" + str(latest), "Censos"),
                ]
            ),
            card(
                "Evolución Demográfica",
                html.Div(
                    [
                        dcc.Graph(id="m-geo-line", figure=fig),
                        html.Div(
                            id="m-geo-output",
                            style={
                                "marginTop": "8px",
                                "color": "#8b94a3",
                                "fontWeight": "600",
                            },
                        ),
                    ]
                ),
            ),
        ]
    )


def cajas_tab():
    data = get_data()
    if "cajas" not in data:
        return card("Cajas Alimentación", html.P("Data not available"))
    df = data["cajas"]
    fig = px.density_map(
        df,
        lat="lat",
        lon="lon",
        radius=8,
        center={"lat": -33.45, "lon": -70.66},
        zoom=11,
        map_style="carto-positron",
        title="Puntos de Entrega — Cajas de Alimentación",
    )
    fig.update_layout(**CHART_TEMPLATE, height=600)
    return html.Div(
        [
            stat_row([(str(len(df)), "Puntos de entrega")]),
            card(
                "Mapa de Entregas",
                html.Div(
                    [
                        dcc.Graph(figure=fig),
                        html.Div(
                            "Mapa de densidad agregado — ver detalle por cluster en el repo cajas-alimentacion.",
                            style={
                                "color": "#8b94a3",
                                "fontSize": "0.85rem",
                                "marginTop": "8px",
                            },
                        ),
                    ]
                ),
            ),
        ]
    )


def sanit_tab():
    data = get_data()
    if "sanit" not in data:
        return card("Sanitización Santiago", html.P("Data not available"))
    df = data["sanit"]
    tipo_counts = df["type"].value_counts()
    fig_map = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        color="type",
        hover_name="name",
        hover_data=["description", "type"],
        center={"lat": -33.45, "lon": -70.66},
        zoom=12,
        map_style="carto-positron",
        title="Puntos de Sanitización — Comuna de Santiago",
        color_discrete_map={
            "Cité": "#e74c3c",
            "Pasaje": "#3498db",
            "Edificio": "#2ecc71",
            "Domicilio": "#f39c12",
            "Calle": "#9b59b6",
            "Otro": "#95a5a6",
        },
    )
    fig_map.update_layout(**CHART_TEMPLATE, height=600)
    fig_bar = px.bar(
        x=tipo_counts.index,
        y=tipo_counts.values,
        title="Ubicaciones por Tipo",
        labels={"x": "Tipo", "y": "Cantidad"},
        color=tipo_counts.index,
        color_discrete_sequence=["#56B4E9", "#E69F00", "#009E73", "#F0E442", "#CC79A7"],
    )
    fig_bar.update_traces(
        hovertemplate="<b>%{x}</b><br>Puntos: %{y}<extra></extra>",
    )
    fig_bar.update_layout(**CHART_TEMPLATE, height=400, showlegend=False)
    return html.Div(
        [
            stat_row(
                [
                    (str(len(df)), "Puntos de sanitización"),
                    (str(df["type"].nunique()), "Categorías"),
                ]
            ),
            card("Mapa de Sanitización", dcc.Graph(figure=fig_map)),
            card(
                "Distribución por Tipo",
                html.Div(
                    [
                        dcc.Graph(id="m-sanit-bar", figure=fig_bar),
                        html.Div(
                            id="m-sanit-output",
                            style={
                                "marginTop": "8px",
                                "color": "#8b94a3",
                                "fontWeight": "600",
                            },
                        ),
                    ]
                ),
            ),
        ]
    )


@callback(
    Output("m-games-output", "children"),
    Input("m-games-pie", "clickData"),
    prevent_initial_call=True,
)
def m_games_crossfilter(click):
    if not click:
        return no_update
    label = click["points"][0].get("label", "?")
    return (
        f"Plataforma: {label}. Este hub no filtra datos: el detalle está en el repo "
        "chilean-videogames-analysis."
    )


@callback(
    Output("m-nlp-output", "children"),
    Input("m-nlp-scatter", "clickData"),
    prevent_initial_call=True,
)
def m_nlp_crossfilter(click):
    if not click:
        return no_update
    pt = click["points"][0]
    return (
        f"Discurso: {pt.get('y', '?')} ({pt.get('x', '?')}). Este hub no filtra datos: "
        "el detalle está en el repo geopolitica-textual-nlp."
    )


@callback(
    Output("m-geo-output", "children"),
    Input("m-geo-line", "clickData"),
    prevent_initial_call=True,
)
def m_geo_crossfilter(click):
    if not click:
        return no_update
    pt = click["points"][0]
    serie = pt.get("legendgroup", pt.get("curveNumber", "?"))
    return (
        f"Serie: {serie} año {pt.get('x', '?')}. Este hub no filtra datos: "
        "el detalle está en el repo chile-geografia-historica."
    )


@callback(
    Output("m-sanit-output", "children"),
    Input("m-sanit-bar", "clickData"),
    prevent_initial_call=True,
)
def m_sanit_crossfilter(click):
    if not click:
        return no_update
    tipo = click["points"][0].get("x", "?")
    return (
        f"Tipo: {tipo}. Este hub no filtra datos: el detalle está en el repo "
        "sanitizacion-santiago."
    )


if __name__ == "__main__":
    app.run(debug=False, port=8050)
