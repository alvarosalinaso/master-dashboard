# Arquitectura — master-dashboard

## Visión general
Dashboard maestro que integra/consolida métricas de múltiples proyectos. Single-file Dash app.

## Componentes principales

### Dashboard
- `app.py` — Dash app:
  - Layout con tabs por proyecto
  - Iframes o links a dashboards desplegados
  - Navegación centralizada

### Datos
- No hay datos locales — agrega dashboards externos

## Flujo de datos
```
Dashboards externos (Render/otros) → master-dashboard (iframes/links)
```

## Despliegue
- Render: `gunicorn app:server` (ver `render.yaml` — por crear)
- Puerto: `$PORT`

## Tests
- `tests/` — Por crear (validación de links, estructura layout)
- CI: pytest + coverage + ruff (Python 3.10, 3.11, 3.12)

## Pendiente
- Crear render.yaml
- Definir lista de dashboards a integrar
- Tests de smoke para verificación de URLs