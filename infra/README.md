# Infra, Analytics Portfolio (Docker)

Copia versionada de la infraestructura del portafolio. El directorio padre de este repo
reúne los proyectos hermanos y **no es un repositorio git**, por eso los archivos se
versionan dentro de `master-dashboard/infra/`.

## Archivos

- `docker-compose.yml`, 8 servicios (`master-dashboard`, `worldcup`, `videogames`,
  `geopolitica`, `geografia`, `cajas`, `sanitizacion`, `nginx`) en red `analytics-network`.
  Todos los `build.context` y `volumes` son rutas relativas al propio archivo
  (`../../<proyecto>`): no hay rutas absolutas de usuario en este repo.
- `nginx.conf`, hub en `:8080/` + redirects `/worldcup`, `/videogames`,
  `/geopolitica`, `/geografia`, `/cajas`, `/sanitizacion` (302 a puertos directos
  para no romper `/_dash-*`).
- `Dockerfile.base`, `python:3.11-slim` + GDAL/GEOS/PROJ + deps comunes.
  El modelo spaCy se instala por wheel pineado directo
  (`es_core_news_sm-3.7.0`) porque `spacy download` generaba URL 404.
- `requirements.analytics.txt`, dependencias consolidadas.
- `UX-MATRIX.md`, matriz de decisiones de UX del hub.

## Uso

Las rutas del compose son relativas al propio `docker-compose.yml`, así que el comando
funciona desde el directorio padre (el que contiene los repos hermanos):

```cmd
REM desde el directorio padre de este repo (el que contiene los repos hermanos)
docker compose -f master-dashboard\infra\docker-compose.yml up --build -d
docker compose -f master-dashboard\infra\docker-compose.yml ps
curl http://localhost:8080/healthz
```

Sin cambiar de directorio, el equivalente es lanzarlo desde `master-dashboard/` con
`docker compose -f infra\docker-compose.yml up --build -d`.

Hub: `http://localhost:8080`, apps en `:8050`–`:8056` (7 servicios + nginx).
