# Matriz UX/UI — Portfolio Analytics (Fase B)

Patrón aplicado por proyecto. Estilos: **Bauhaus** (claro, borde negro grueso,
sombra dura, póster geométrico) / **Neon** (oscuro, glow, red de datos).

| Proyecto | Estilo | Hero póster | KPI sparklines + deltas | Cross-filtering | Insights (problema/metodología/decisión) | Hovertemplate rico | Commit |
|---|---|---|---|---|---|---|---|
| master-dashboard | Bauhaus claro | SVG Bauhaus inline | Sí (5 KPIs) | Botones proyecto → mensaje + hist WorldCup click | Sí (hub) | Sí (WorldCup bars) | `00decf5` |
| sanitizacion-santiago | Bauhaus Mondrian | Tira SVG Bauhaus | Sí (tipos) | Checklist/dropdown global + bar click → mensaje | Sí (mapa) | Sí (mapa + barras) | `c798dee` |
| cajas-alimentacion | Bauhaus Haring | Formas Haring (círculo/cuadrado/triángulo) | Sí (clusters) | Bar clusters click → mensaje | Sí (mapa) | Sí (mapa + barras) | `5c3d187` |
| chile-geografia-historica | Bauhaus tierra | Tira SVG Bauhaus tierra | Sí (serie nacional) | Línea censal click → mensaje | Sí (censo) | Sí (línea censal) | `5aa3789` |
| worldcup-2026 | Neon oscuro | Hero glow SVG (líneas + dots) | Sí (goles/partidos) | Barras por ronda click → mensaje | Sí (overview) | Sí (barras, líneas, pie) | `87e1de8` |
| geopolitica-textual-nlp | Manuscrito + Neon | Strip red neón sobre manuscrito | Sí (entidades) | Barras NER click → mensaje | Sí (NER) | Sí (barras NER) | `22eba1a` |
| chilean-videogames-analysis | Neon cyberpunk | Existente (scanlines + glow) | Sí (mercado) | Pie plataformas click → mensaje | Sí (mercado) | Sí (pie plataformas) | `a936245` |
| manchester-united-analisis | Estático (PNG) | N/A — salida matplotlib | Parcial (tablas resumen) | N/A (sin Dash) | Vía `generate_report.py` | N/A | — |
| united-passing-efficiency-24-25 | Estático (PNG) | N/A — salida matplotlib | Parcial (tablas resumen) | N/A (sin Dash) | Vía `generate_report.py` | N/A | — |
| tactical-narrative-graph-analysis | Estático (HTML pyvis) | N/A — grafo interactivo pyvis | Parcial (métricas JSON) | Nativo pyvis (zoom/vecinos) | Vía reporte + métricas | Nativo pyvis | — |

## Componentes reutilizables (copiar/pegar entre dashboards)

- `sparkline(values, color)` — micro-gráfico 34–40px sin ejes para KPI cards.
- `insight_card(pregunta, respuesta, acento)` — tarjeta con borde lateral de acento.
- Callback cross-filter: `Input(<chart-id>, "clickData")` → `Output(<msg-id>, "children")`
  con `prevent_initial_call=True` y `no_update` si no hay clic.
- `hovertemplate` explícito en cada trace (nunca el tooltip crudo de Plotly).

## Reglas por estilo

- **Bauhaus:** fondo claro `#FAFAF7`/`#FFFFFF`, texto `#111111`/`#2c2c2c`,
  bordes `3px solid`, sombras duras (`6–8px` offset sólido), formas primarias
  (círculo/triángulo/cuadrado) en hero SVG, tipografía bold uppercase.
- **Neon:** fondo `#0a0a1a`, tarjetas `rgba` con glow (`box-shadow` + `text-shadow`),
  hero SVG con líneas de red y nodos brillantes, monoespaciada donde aplique.

## Verificación

- `pytest tests/ -q` verde en cada repo tras el rediseño.
- Apertura manual `:8050`–`:8056` + un clic cross-filter por dashboard.
- `docker compose ps` con 8 servicios `healthy` + `curl :8080/healthz` → `ok`.
