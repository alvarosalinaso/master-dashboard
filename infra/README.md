# Infra — Analytics Portfolio (Docker)

Copia versionada de la infraestructura que vive en `C:\Users\Alvaro\github-limpio\`
(ese directorio padre no es repo git, por eso se versiona aquí).

## Archivos

- `docker-compose.yml` — 8 servicios (`master-dashboard`, `worldcup`, `videogames`,
  `geopolitica`, `geografia`, `cajas`, `sanitizacion`, `nginx`) en red `analytics-network`.
  Los paths están relativos a este directorio (`../../<proyecto>`).
- `nginx.conf` — hub en `:8080/` + redirects `/worldcup`, `/videogames`,
  `/geopolitica`, `/geografia`, `/cajas`, `/sanitizacion` (302 a puertos directos
  para no romper `/_dash-*`).
- `Dockerfile.base` — `python:3.11-slim` + GDAL/GEOS/PROJ + deps comunes.
  El modelo spaCy se instala por wheel pineado directo
  (`es_core_news_sm-3.7.0`) porque `spacy download` generaba URL 404.
- `requirements.analytics.txt` — dependencias consolidadas.

## Uso (desde `C:\Users\Alvaro\github-limpio`)

```cmd
cd C:\Users\Alvaro\github-limpio
docker compose up --build -d
docker compose ps
curl http://localhost:8080/healthz
```

Hub: `http://localhost:8080` — dashboards en `:8050`–`:8056`.
