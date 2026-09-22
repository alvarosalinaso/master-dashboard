# Matriz UX/UI — Portfolio Analytics (Fase B, rev. Data-Art)

Sistema único **Data-Art Poster oscuro** en los 7 dashboards Dash.
Bauhaus/Mondrian/Haring eliminados por completo (2026-09-22).

## Fundamento profesional

- **Tufte** — data-ink ratio: sin bordes gruesos, sin sombras duras, sin grids
  pesados; se borra todo lo que no codifique dato (chartjunk).
- **Okabe-Ito (2008)** — paleta categórica colorblind-safe (estándar Nature Methods),
  adaptada a dark: `#56B4E9` `#E69F00` `#009E73` `#F0E442` `#CC79A7` `#D55E00` `#0072B2` `#999999`.
- **ColorBrewer/viridis** — escalas continuas (densidades, heatmaps, coropletas).
- **Data-Viz-Art / magazine genre** — el gráfico como héroe: titular + línea de fuente,
  tipografía mono para datos (`JetBrains Mono`/Consolas), storytelling editorial al lado.
- **Lupi (Data Humanism)** — cada visual responde problema → metodología → decisión.

## Tokens del sistema

- Canvas `#0a0e14`, tarjetas `#11161f`, borde `1px rgba(255,255,255,0.08)`, radio 12–14px.
- Texto `#e8edf2`, muted `#8b94a3`, acento UI `#22d3ee`.
- Títulos Inter 700–800, datos en mono; labels ≥0.75rem, ticks mono 12px.
- Fondo con textura de datos (dot-grid + anillos de contorno + scatter, SVG inline, sin assets).

## Componentes reutilizables

- `sparkline(values, color)` — micro-gráfico 32–40px sin ejes para KPI cards.
- `insight_card(pregunta, respuesta, acento)` — borde lateral de acento.
- `chart_card` / `card` — titular + línea `Fuente:` + gráfico.
- Callback cross-filter: `Input(<chart-id>, "clickData")` → `Output(<msg-id>, "children")`
  con `prevent_initial_call=True` y `no_update` sin clic.
- `hovertemplate` explícito en cada trace (nunca el tooltip crudo).

## Estado por proyecto

| Proyecto | Sistema | Hero | KPI sparklines + deltas | Cross-filtering | Insights | Hover rico | 3D rotativo | Commit |
|---|---|---|---|---|---|---|---|---|
| master-dashboard | Data-Art oscuro | Canvas dots+contornos+scatter | Sí (5 KPIs) | Botones proyecto + hist WorldCup | Sí (hub) | Sí | — | `d92b282` |
| worldcup-2026 | Neón oscuro | Hero glow SVG | Sí | Barras por ronda | Sí | Sí | Radar polar (compare) | `99006ea` |
| geopolitica-textual-nlp | Manuscrito + red neón | Strip red neón | Sí (entidades) | Barras NER | Sí (NER) | Sí | — | `872dc37` |
| chilean-videogames-analysis | Neon cyberpunk | Existente scanlines+glow | Sí (mercado) | Pie plataformas | Sí (mercado) | Sí (burbujas) | Burbujas log-log | `40935e4` |
| chile-geografia-historica | Data-Art oscuro | Tira canvas | Sí (serie nacional) | Línea censal | Sí (censo) | Sí | — | `8d5b64e` |
| cajas-alimentacion | Data-Art oscuro | Formas Haring retiradas | Sí (clusters) | Barras clusters | Sí (mapa) | Sí | Scatter3d + contornos | `d9c8a7e` |
| sanitizacion-santiago | Data-Art oscuro | Tira canvas | Sí (tipos) | Barras tipos | Sí (mapa) | Sí | Torre 3D por tipo | `ee54928` |
| manchester-united-analisis | Estático (PNG) | N/A | Tablas resumen | N/A | En reporte | N/A | — | `6234e1f` |
| united-passing-efficiency-24-25 | Estático (PNG) | N/A | Tablas resumen | N/A | Captions en plots | N/A | — | `3c65365` |
| tactical-narrative-graph-analysis | Estático (pyvis) | N/A | Métricas JSON | Nativo pyvis | En snippets | Nativo pyvis | Grafo 3D pyvis | `0d8073a` |

## Verificación

- `pytest tests/ -q` verde en cada repo tras cada rediseño.
- Render de tabs verificado en Python (map/dist/analysis/data) donde aplica.
- `docker compose ps` con 8 servicios + `curl :8080/healthz` → `ok` (corre en PC del dueño).
