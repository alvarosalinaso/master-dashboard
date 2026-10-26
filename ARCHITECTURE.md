# Arquitectura, master-dashboard

## Visión general

Hub Dash de un solo archivo (`app.py`) que funciona como **índice de navegación** del
portafolio: un tab por proyecto que muestra cifras descriptivas leídas de los repos
hermanos. No calcula métricas propias ni entrena modelos; solo agrega y presenta datos
que ya viven en otros repos.

## Datos

- `BASE = Path(__file__).parent.parent`, el directorio padre del repo (no es un
  repositorio git) contiene los proyectos hermanos, y desde ahí se resuelven las rutas.
- `load_data()` lee 7 datasets de 4 repos:
  | Repo hermano | Archivo | Claves en `data` |
  | --- | --- | --- |
  | `worldcup-2026` | `data/worldcup.db` | `wc_matches`, `wc_teams` |
  | `chilean-videogames-analysis` | `data/processed/games.csv` | `games` |
  | `geopolitica-textual-nlp` | `data/processed/speeches.csv` | `speeches` |
  | `chile-geografia-historica` | `data/processed/census.csv`, `events.csv`, `presidents.csv` | `census`, `events`, `presidents` |
- **No hay datos versionados en este repo.**
- Carga perezosa: `get_data()` cachea el resultado de `load_data()` en `_DATA`.
- **Degradación por archivo:** cada lectura va en su propio `try/except`; si el archivo
  falta o está corrupto se registra un warning con `logging` y el resto carga igual.
  El tab correspondiente muestra *Data not available* y su KPI muestra `n/d`.

## Componentes

### `app.py`
- `PROJECTS`, índice de navegación: tab, nombre, colores y repo fuente de cada proyecto.
- `overview_kpis()` / `kpi_value()` / `project_desc()`, cifras del tab *Resumen* y de las
  tarjetas, derivadas siempre de `load_data()` (sin números hardcodeados).
- Layout: encabezado, `dcc.Tabs` (5 tabs) y contenedor `tab-content`.
- Callbacks (6 en total):
  - `render_tab`, dibuja el tab activo.
  - `project_open_tab`, clic en una tarjeta → abre su tab (navegación real).
  - 4 callbacks de clic en gráficos (`worldcup`, `games`, `nlp`, `geo`) que
    **solo informan** y declaran que el hub no filtra; el detalle vive en el repo fuente.
- Helpers de UI: `card`, `stat_row`, `kpi_card`, `insight_card`, `sparkline`.

### `infra/`
- `docker-compose.yml`, 8 servicios (`nginx` + `master-dashboard` + 6 apps) en red
  `analytics-network`, con rutas relativas (`../../<proyecto>`).
- `nginx.conf`, hub en `:8080` y redirects a `:8050`–`:8056`.
- `Dockerfile.base`, `requirements.analytics.txt`, `UX-MATRIX.md`.
- Ver [infra/README.md](infra/README.md).

### `tests/`
- `test_helpers.py`, `card`, `stat_row`, `COLORS`.
- `test_kpis.py`, los KPIs salen de los datos (anti-hardcoding) y degradan a `n/d`.
- `test_load_data.py`, un CSV corrupto/ausente no rompe la carga.
- `test_smoke.py`, la app importa, `GET /` responde 200 y hay 6 callbacks registrados.
- `test_tabs.py`, cada tab con y sin datos.

## Flujo de datos

```
repos hermanos (CSV/DB) → load_data() (try/except por dataset) → get_data() (caché)
                        → tabs / overview_kpis() → callbacks → navegador
```

## CI

`.github/workflows/ci.yml`:

- **lint**, `ruff check` + `ruff format --check` en Python 3.12.
- **test**, `pytest` en 3.10 / 3.11 / 3.12 con `pytest-cov` y subida de `coverage.xml`.

Nota: el paso corre `--cov=src` pero este repo no tiene paquete `src`, así que el
reporte de coverage no mide `app.py` (ajuste pendiente; no afecta a ruff ni a pytest).

## Despliegue

- Local: `.venv\Scripts\python app.py` → `http://localhost:8050`.
- Docker: `docker compose` desde el directorio padre → hub en `:8080`.
- gunicorn: `gunicorn app:server` (ver `requirements-render.txt`); este repo **no**
  incluye `render.yaml` (otros repos hermanos sí lo tienen).

## Pendientes conocidos

- Apuntar `--cov=app` en CI para que el coverage mida algo real.
- El hub cubre 5 tabs sobre 4 repos públicos; `cajas-alimentacion` y
  `sanitizacion-santiago` son privados por datos personales y no forman parte del hub.
