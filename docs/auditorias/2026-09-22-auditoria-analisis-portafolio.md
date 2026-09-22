# Auditoría de calidad analítica — portafolio de 10 proyectos

**Autor:** Alvaro Salinas O. · **Fecha:** 2026-09-22 · **Estado:** final — incorpora ronda de revisión por expertos
**Alcance:** metodología, corrección de análisis, coherencia README↔código, tests y validación de datos de los 10 repos del portafolio. *Excluido por ahora: calidad visual de dashboards (fase posterior, plan `docs/superpowers/plans/2026-09-22-unify-data-art-variants.md`).*

---

## 1. Resumen ejecutivo

Revisé los 10 proyectos con un equipo de auditores en paralelo (un revisor por dominio: NLP, sports analytics, web/market data, geo/presupuesto/ETL, portafolio+hub) y después sometí el borrador a un comité de 3 expertos externos (Chief Data Scientist, hiring manager de portafolios, platform engineer). Esta versión ya incorpora sus correcciones.

**Veredicto global: los análisis están a nivel "parcial" — la ingeniería y la higiene de código son sólidas en general, pero varias métricas estrella son metodológicamente inválidas o tautológicas, y varias afirmaciones del README no están respaldadas por código reproducible en el repo.** Antes de vender los dashboards como ciencia de datos, hay que corregir una lista corta de fallos de severidad alta; los complementos entran en una segunda oleada.

Tres patrones se repiten en casi todos los repos:

1. **Tautología / circularidad** — métricas que se correlacionan con algo derivado de sí mismas (videogames RQ5, A/B Steam vs Itch, "event_impact" en geo).
2. **README adelantado al código** — promesas de métodos (DiD, xT, HHI, ARIMA, "alianzas") que no existen o no corren (manutd, united-passing, videogames, geopolitica, worldcup).
3. **Validación de datos ausente o blanda** — invariantes rotos sin test (goles worldcup, join censo↔geojson, precios itch=0, CSVs que nadie valida en CI).

*Matiz incorporado en revisión:* varios hallazgos ya estaban **autodeclarados internamente** (IC y límites del forecast de geo en `forecast_analysis.py:3-9`, problemas de join en `chile-geografia-historica\ARCHITECTURE.md:45-49`, obsolescencia de `master-dashboard\ARCHITECTURE.md`, disclaimer sintético en `geopolitica\README.md:9,51-57`). El trabajo pendiente no es descubrirlos, sino **cerrarlos**: actualizar README/dashboard y poner test que impida regresión.

---

## 2. Hallazgos por proyecto

Leyenda de severidad: **alta** = invalida una conclusión o rompe reproducibilidad; **media** = degrada solidez; **baja** = higiene.

### 2.1 geopolitica-textual-nlp — *parcial*

- **[alta]** Sentimiento con TextBlob (léxico **inglés**) sobre texto español: `src/sentiment_analysis.py:25-44`. Umbrales ±0.1 arbitrarios, sin calibración ni gold standard. → **Decisión del comité:** gold standard ~200 oraciones anotadas + reportar F1 de TextBlob (muestra honestamente lo malo) + léxico ES propio; `pysentimiento` (torch) solo con aprobación explícita de dependencia y rewrite de `tests/test_sentiment_analysis.py:27-31` (exige `polarity`/`subjectivity` y etiquetas `positivo/negativo/neutral`) en el mismo PR.
- **[alta]** Test χ² mal planteado: `src/statistical_tests.py:46-53` cuenta *tipos* entre las 30 entidades únicas del top-30 e ignora frecuencias; H0 sin sentido teórico. → Usar frecuencias completas con esperados justificados, o eliminar.
- **[alta]** LDA con k=5 fijo, sin lematización, sin coherence/perplexity: `src/topic_analysis.py:76,101`. Stopwords manuales contienen bigramas (`"han sido"`) que `text.split()` nunca matchea. → Grid de k con `coherence_model` + lematización spaCy.
- **[alta]** NER sin evaluación; `confidence = getattr(ent, "confidence", 1.0)` (`src/corpus_processor.py:77`) es confianza falsa. → Set de oro ~300 entidades, P/R/F1; no exponer confidence inventada.
- **[media]** Geocoding con solo 15 ciudades hardcodeadas (`src/export_visualizations.py:13-29`); co-ocurrencias por año ≈ arcos triviales leídos como "alianzas geopolíticas" (README:55).
- **Coherencia README:** disclaimer sintético **sí existe** (README:9) — corregido el hallazgo inicial; queda: ">70% eje metropolitano" y "342 menciones (42%)" sin script/CSV que los produzcan; `es_core_news_md` (README) vs `es_core_news_sm` (código); notebook cita "Cuentas Públicas 1842-2000" con datos sintéticos (n=16). *Falta: el disclaimer no aparece en el dashboard.*
- **Fortalezas:** aviso claro de datos sintéticos, orquestador `analyze_all.py`, CI multi-Python, tests aislados con `tmp_path`.

### 2.2 worldcup-2026 — *parcial*

- **[alta]** Entrenamiento con 48 partidos de eliminatorias (el notebook lo admite; docstring `match_predictor.py:3-8` ya advierte) mientras `match_predictor.py:4` promete "~192 matches"; **leakage**: `rank_diff` usa ranking FIFA 2026 sobre partidos 2014-2022 (`:97,245`); confederaciones desconocidas caen a `"UEFA"` (`:95-96`). **⚠ CI:** `tests/test_match_predictor.py:385,406` assertionean la columna `rank_diff` → recalcular con ranking histórico **manteniendo el nombre** y actualizar asserts en el mismo commit; no tocar el gate `--cov-fail-under=60` (`pyproject.toml:20`).
- **[alta]** Predicciones sin baseline (Elo/Poisson), sin Brier/log-loss ni calibración, pese a que el dashboard muestra `predict_proba` como % (`dashboard/app.py:1057-1074`). Train/test aleatorio = fuga temporal.
- **[alta]** Invariante roto y **codificado en el test**: `SUM(goals)=312` vs `SUM(home+away)=308` (4 partidos descuadrados); `tests/test_queries.py:116` exige 308 (valor erróneo). → Corregir los 4 partidos **y** el assert, e invariante `SUM(goals)==SUM(home+away)` sobre `data/worldcup.db`. (El test usa fixture tmp — seguro para el badge.)
- **[alta]** Módulos estadísticos sobre CSV con columnas ajenas: ARIMA sobre `capacity/lat/lon` de 16 filas (`forecasting.py:42`); Pearson renombrado a ciegas (`statistical_tests.py:33`); z-scores de lat/lon en ranking/clustering; sensibilidad `N(mean, 0.15σ)` ≈ 0.5 por construcción.
- **[media]** `AVG(home+away)` presentado como métrica de equipo; victorias absolutas con sesgo de supervivencia (R32 sale con 3-4 partidos, campeón juega 8).
- **Coherencia README:** "285 goles" vs 308/312 reales; `ARCHITECTURE.md` dice 1930-2022 (real 2014-2022) y "dashboard consume la API" (consume SQLite directo); conclusiones del notebook ("CV confirma que generaliza") no sostenidas por 48 partidos.
- **Fortalezas:** disclaimers de simulación consistentes, esquema SQL con CHECK/FK, `test_queries.py` sólido (27 tests), arquitectura modular.

### 2.3 chilean-videogames-analysis — *parcial, el más afectado*

- **[alta]** RQ5 circular: `revenue = recommendations×40×price` y luego Pearson recommendations↔revenue (`statistical_tests.py:97-116`, r=0.90) mide una identidad aritmética. → Retirar o correlacionar contra variable no derivada. El factor ×40 es convención Boxleiter documentada y testada (`analyze_all.py:28-42`) — **no es hallazgo**, lo pedido es sensibilidad 20–60×.
- **[alta]** Steam vs Itch tautológico: itch tiene `recommendations=0` y copias=0 **por diseño** (`clean.py:60`) → todo revenue Itch=0; Mann-Whitney y "recomendación de plataforma" (`ab_testing.py:149-187`) concluyen lo inevitable.
- **[alta]** Precios itch todos en 0: selector `.game_text a.price_value` (`collect_itch.py:59`) nunca matchea (66/66) → t-test con varianza 0 e IC `[NaN,NaN]`. → Corregir selector, re-scrapear, test `≥1 precio>0`.
- **[alta]** Forecasting silenciosamente roto por case: `forecasting.py:126` filtra `source=="Steam"` sobre datos `"steam"` → subconjunto vacío (ya cubierto por "source casefold" de A3, explícito aquí). Años `str` + mayoría `"Unknown"` → TypeError en rama temporal.
- **[alta]** A/B no corre: `ab_testing.py` lee `games.csv` sin columnas necesarias → 3 tests se saltan y `ab_summary` emite conclusiones igual. → Leer `chilean_games_final.csv` + test de que ≥1 test se ejecuta.
- **[alta]** Rutas rotas: `_PROJECT_ROOT` apunta a `src/`; README y `update_data.bat` invocan `src/collect.py` inexistente → arreglar **en código/CI** (reproducibilidad barata).
- **[media]** Géneros confundidos por idioma (Steam `l=spanish` vs itch en inglés) → chi2 detecta idioma; HHI anunciado en README **sin implementación**. ≥7 p-values sin corrección; tests solo con fixtures sintéticas (CI no clona `data/`).
- **Coherencia README:** "HHI<1500" sin código; "35 juegos en Acción" vs 50; "35% sin recomendaciones" vs 76% de Steam con 0; "2009-2025" con 62% años `Unknown`; ARIMA/A-B/K-Means-CV presentados como funcionales.
- **Fortalezas:** Boxleiter explícito y testado, effect sizes + ICs, ADF antes de ARIMA, gate 45 **no se toca** (subirlo, no bajarlo), parsers con casos borde.

### 2.4 chile-geografia-historica — *parcial*

- **[alta]** El join censo↔GeoJSON **nunca matchea** (`"Región de Tarapacá"` vs `"Tarapacá"`): `map_demographics.py:39-40`, `combine_layers.py:90-91` → población 0 en todos los mapas. *Ya admitido en ARCHITECTURE:48 — falta cerrar en README + test.*
- **[alta]** `modern_region` se calcula (`collect_census.py:185`) y no se usa → unidades no comparables entre censos.
- **[alta]** "event_impact" = diferencia entre dos censos con n=5-6 (`forecast_analysis.py:96-110`) → asociación temporal etiquetada como impacto. **⚠ CI:** `tests/test_forecast_analysis.py:50,162-164` assertionean la key `event_impact` → renombrar + tests + `dashboard.py:972-974` + JSON en **un solo commit**, o conservar la key interna y renombrar solo UI/README. El docstring ya advertía limitaciones y hay IC 95% (`:48-67`) — reencuadrar como "advertido, falta renombrar".
- **[media]** Población "en miles" sin unidad; escala `pop/3000` hardcodeada; "23→54 provincias" es HTML hardcodeado sin dataset.
- **Fortalezas:** docstring honesto, tests de forecast aislados, CI.

### 2.5 cajas-alimentacion — *parcial*

- **[alta]** KMeans sobre `lat,lon` en **grados** (`src/analyze.py:24`) → distorsión ~8% en longitud. → Proyectar UTM 19S **solo para distancia** y **exportar centroides inversos a WGS84** (si no, se rompe el dashboard; tests `==10` clusters y `80595` filas siguen pasando por la fórmula `min(10, n//100)`).
- **[alta]** No existe población, tasa per cápita ni presupuesto: `coordinates.csv` solo `lat,lon`. El dashboard habla de "reasignar flota" sin insumo de costos/rutas ni tasas por comuna (INE).
- **[media]** Silhouette/DB sobre muestra sin `random_state` (`analyze.py:55`, `np.random.choice`) → no reproducible; grilla 0.01° con celdas de área desigual llamada `grid_density`.
- **[media]** Tests frágiles: exigen `== 10` clusters y hardcodean `80595`.
- **Fortalezas:** semilla fija en KMeans, fixtures con `tmp_path`, paleta Okabe-Ito, ARCHITECTURE honesto.

### 2.6 sanitizacion-santiago — *parcial*

- **[alta]** **No hay ETL**: CSV nace de conversión KML→CSV **manual** (README:59). → `src/etl_kml.py` versionado + test de idempotencia/esquema sobre el CSV commiteado; regeneración manual documentada si el KML es sensible.
- **[alta]** `load_data()` valida pero solo imprime warnings, no rechaza (`dashboard.py:104-111`); posibles duplicados (`Mapocho 1478/1484`). → fallar en error + anti-duplicados en CI.
- **[media]** **Tres juegos de bounds inconsistentes** sin solapamiento total (por eso los tests no fallan): `dashboard.py:104-111` vs `test_dashboard.py:14-15` vs `test_data_integrity.py:41,52`; docstrings intercambiados. → constante única en `tests/conftest.py`. `test_dashboard.py` no importa el dashboard (0% callbacks).
- **[media]** Dato sensible (COVID, domicilios) en repo público — detectado, sin resolver. → Ofuscar o privado (anonimizar no rompe tests: tipos son issubset).
- **Fortalezas:** validación de columnas/rangos, cache lazy, fixtures `scope="module"`, ARCHITECTURE con seguridad.

### 2.7 manchester-united-analisis — *promesa rota*

- **[alta]** El "DiD" no es DiD: `src/causal_inference.py:68-69` es `post − pre` sin grupo control, pese a README:36/25. **Decisión del comité:** renombrar a "before/after descriptivo" + retirar "causal effect" del README; synthetic control **no** ahora (n pequeño, sin tendencias paralelas verificables); stretch posterior: un benchmark (media PL sin MU).
- **[alta]** Indemnización "£32M" sin código ni fuente → fuente con link o retirar.
- **[media]** Cifras README vs `dashboard.html` divergentes (gap 20 vs 23.8); placebo débil; tests solo smoke.
- **Fortalezas:** validación de columnas, KPIs de brecha bien definidos, CI, notebook+CSV auditables.

### 2.8 united-passing-efficiency-24-25 — *promesa rota*

- **[alta]** **No existe xT/EPV** (solo README:18); rankings `Prog/Cmp` crudo sin per-90 pese a columna `90s` → comparabilidad rota. → per-90 + xT real o retirar promesa.
- **[alta]** README rutas inexistentes (`src/data.py`, `src/benchmark.py`); hallazgos "Bruno 45% / −8% vs Top6" no rastreables → fuente o retirar.
- **[media]** `betweenness_centrality(G)` sin pesos (`graph_analysis.py:46`); tests solo smoke.
- **Fortalezas:** `_prog_ratio` robusto, validaciones de ruta, separación data/analysis/plot.

### 2.9 tactical-narrative-graph-analysis — *base sólida, README a ajustar*

- **[alta]** `betweenness_centrality(G, weight="weight")` (`graph_builder.py:209`) trata **frecuencia como longitud de camino** → signado invertido; además `graph_analysis.py:71` sin peso → pipelines no comparables. → Unificar semántica.
- **[alta]** `_load_aggregate_stats` (`graph_builder.py:126-171`) fabrica grafo heurístico → marcar como "ilustrativo".
- **[media]** README no indica variante de centralidad (Ounahi 0.047).
- **Fortalezas:** StatsBomb evento-level real, builder con tests serios, auto-loops evitados, exports.

### 2.10 master-dashboard (hub) — *promesa > implementación*

- **[alta]** `project_crossfilter` (`app.py:494-509`) solo devuelve texto "Filtro activo: X" — **no filtra nada**; el mensaje (`:517-521`) promete drill-down inexistente. **Decisión del comité:** los dominios no comparten claves (16 discursos vs 80k puntos…) → **renombrar a "índice de navegación del portafolio"** con KPIs globales derivados (nº proyectos, tests, cobertura, última actualización); cross-filter real solo *después* y **dentro** de un mismo dataset.
- **[alta]** KPIs del overview hardcodeados (`app.py:576-604`), no derivan de datos.
- **[media]** `ARCHITECTURE.md` obsoleto; `UX-MATRIX.md` promete "sistema único" frente a variantes (en unificación — plan visual aparte).
- **[media]** Tests cubren tabs/helpers pero no callbacks cross-filter.
- **Fortalezas:** lazy `get_data()`, `prevent_initial_call`/`no_update`, hovertemplate, paleta colorblind-safe.

---

## 3. Plan de acción (post-revisión de expertos)

### 3.0 Oleada A — correcciones de severidad alta

**A0 (nuevo, primera tarea):** inventario de **cifras públicas afectadas** (READMEs, dashboards, notebooks) y su retractilación/actualización — sin esto, corregir código deja los READMEs mintiendo (riesgo #1 del comité).

Columna **Percepción** = impacto visible para un reclutador (60 s: README → dashboard → cifras).

| # | Repo | Acción | Esfuerzo* | Percepción |
|---|------|--------|-----------|------------|
| A1 | worldcup | Corregir 4 partidos + test 308→invariante `goals==marcador` | bajo | **alto** (tartas del dashboard) |
| A6 | geo | Join censo↔GeoJSON + test + `modern_region` | bajo | **alto** (mapas en 0) |
| A7 | geo | Renombrar `event_impact` + tests/dashboard/JSON mismo commit | bajo | alto (honestidad) |
| A10 | manutd | DiD→before/after + fuente/retiro £32M | bajo | alto (honestidad) |
| A12 | tactical | Unificar peso betweenness + marcar fallback ilustrativo | bajo | medio |
| A13 | hub | Cross-filter → índice de navegación + KPIs desde datos + quitar promesa drill-down | **alto** | **alto** (primera pantalla del portafolio) |
| A3 | videogames | Rutas `src/` + `source` casefold (cierra bug `forecasting.py:126`) + A/B CSV correcto + precios itch | medio | **alto** (precios=0) |
| A4 | videogames | RQ5 fuera/reformular + Holm/FDR + HHI real | medio | alto |
| A11 | passing | Per-90 + xT o retirar + rutas README | medio | alto (promesa rota) |
| A5 | geopolitica | Gold standard F1 + léxico ES + χ² corregido/eliminado + grid-k coherence | **alto** (sin deps nuevas) | medio-bajo (invisible en 60 s) |
| A9 | sanit | ETL KML + `load_data` que falle + bounds unificados + anonimizar | medio | medio |
| A2 | worldcup | Baseline Elo/Poisson + Brier/calibración + rank_diff histórico (con asserts) | medio-alto | medio (si README lo promete) |
| A8 | cajas | UTM solo distancia + centroides inversos WGS84 + `random_state` en muestreo | bajo | bajo (invisible) |

\* Esfuerzo corregido por el comité: A5 y A13 pasan de "medio" a **alto**.

**Surgical A′:** A1, A6, A3, A13 se **adelantan** porque sus cifras ya están públicas en dashboards.

**Tandas de ejecución (mantiene los 10 badges verdes — paralelo entre repos, serial dentro de cada repo, 1 commit = 1 A#):**

1. **Tanda 1 (bajo esfuerzo):** worldcup A1 · geo A6→A7 · cajas A8 · manutd A10 · tactical A12
2. **Tanda 2:** passing A11 · sanit A9 · hub A13
3. **Tanda 3:** videogames A3→A4 (gate 45 intacto; fix de casefold puede cambiar salidas — correr suite antes de A4)
4. **Tanda 4 (alto riesgo, al final):** worldcup A2 (con asserts en mismo commit) · geopolitica A5 (solo vía gold standard; pysentimiento requiere aprobación)

**Repos menores — rigor proporcional diferenciado:**
- *Promesa rota* (manutd, passing): Oleada A completa + plantilla de README honesto (§3.2).
- *Base sólida* (tactical): solo A12 + README con semántica de centralidad.
- *Hub* (master-dashboard): A13 prioritario por ser la primera pantalla del portafolio.

### 3.1 Oleada B — complementos (solidez)

1. **B3 adelantado a la Oleada A** — primeros tests de validación en CI (baratos, cero deps nuevas, suben cobertura):
   1. Worldcup: invariante goles vs `home+away` sobre `data/worldcup.db`
   2. Geo: join censo↔geojson con normalización → `>0` regiones con población
   3. Sanit: `load_data` lanza en error + anti-duplicados
   4. Videogames: `price>=0` y `≥1 precio itch>0` (skip si no hay datos — CI no clona `data/`)
   5. Cajas: `lat/lon` en bounds de Santiago + no-nulos en `coordinates.csv`
2. Intervalos de incertidumbre: IC bootstrap worldcup, sensibilidad revenue 20–60× videogames, tasas por 10k hab con población INE cajas.
3. Unificación de fuentes de verdad (CSV vs BD worldcup; ARCHITECTURE/README desactualizados).
4. Análisis temporal reproducible: walk-forward worldcup, cohortes videogames, diacrónico geopolitica.
5. Tests de callbacks de dashboards tras la unificación visual.

### 3.2 Plantilla README de honestidad ejecutable (por revisor de portafolios)

4 bullets por README:
- **Qué mida y qué no** (ej. manutd: "before/after descriptivo, no causal").
- **Fuente de cada cifra pública** con link a script/CSV — obligatorio para £32M, "HHI<1500", "42% menciones"; si no, se retira.
- **Limitaciones** (n=48, datos sintéticos, join no resuelto).
- **Reproducción**: comando exacto + badge CI.

*Y en el README de perfil (línea ~46):* reemplazar "Todos usan datos reales… Ninguno usa datos inventados" por *"Todos parten de fuentes reales y verificables; cuando uso datos sintéticos o simulaciones, lo indico explícitamente."*

### 3.3 Oleada C — dashboards (fase posterior)

Unificación Data-Art oscuro (plan `2026-09-22-unify-data-art-variants.md`: geopolitica → worldcup → videogames). **Estrategia de ramas (comité):** desarrollo **en paralelo** en ramas separadas (C no depende de cifras), pero **merge en orden A → C** con rebase de C tras cada A del mismo archivo; no iniciar C en worldcup/geopolitica/videogames hasta cerrar A1-A2/A5/A3-A4 respectivamente si tocan `dashboard.py`/`app.py` (evita conflictos y screenshots con cifras viejas). A13 (hub) no bloquea a los 3 y puede correr con C.

### Riesgos y no-hacer

- **No bajar** el gate 45 de videogames; subirlo con los nuevos tests. Tampoco tocar `--cov-fail-under=60` de worldcup.
- **No introducir** dependencias nuevas sin aprobación (`pysentimiento`/torch = ticket explícito).
- **No romper** CI: 1 commit = 1 A# = badge verde antes del siguiente en el mismo repo; los 3 commits de riesgo (A2, A5, A7) llevan sus asserts actualizados en el mismo commit.
- **No publicar** cifras nuevas sin script/CSV asociado (A0 protege contra esto).

---

## 4. Preguntas abiertas — resueltas por el comité

1. **Orden A→B→C:** correcto; adelantar B3 (tests de validación) dentro de A.
2. **Synthetic control manutd:** no ahora — renombrar a before/after; benchmark PL como stretch.
3. **`pysentimiento` vs gold standard:** gold standard ~200 oraciones + F1 de TextBlob + léxico ES; torch solo si F1<0.6 y con aprobación de dependencia.
4. **Repos menores:** rigor proporcional — promesa rota (manutd, passing) = Oleada A + plantilla README; base sólida (tactical) = A12 + README; hub = A13 prioritario. *(Nota: "4 menores" = manutd, passing, tactical, master-dashboard.)*
5. **Hub:** no filtra datasets entre dominios → "índice de navegación" + KPIs globales reales; promesa de drill-down eliminada.

---

## 5. Ronda de revisión por expertos — comentarios e incorporación

Borrador sometido a 3 revisores independientes (solo lectura). Resumen de comentarios y su incorporación:

### Revisor A — Chief Data Scientist (metodología)
- **[Menor]** Hallazgos ya autodeclarados (forecast IC, join en ARCHITECTURE, disclaimers) presentados como descubrimientos → *incorporado: §1 matiz + reapertura como "falta cerrar".*
- **[Menor]** Disclaimer sintético de geopolitica sí existe en README → *corregido en §2.1.*
- **[Menor]** Boxleiter ×40 mal contextualizado → *movido de hallazgo a sensibilidad B2.*
- **[Crítico]** Bug `forecasting.py:126` casefold explícito → *añadido a A3.*
- **[Importante]** Bounds triples en sanit; test worldcup codifica 308 erróneo → *incorporados en §2.6 y A1.*
- **[Importante]** Esfuerzos A5/A13 subestimados; falta A0 (cifras publicadas) → *corregido en tabla §3.0.*
- Respuestas a las 5 preguntas → *incorporadas en §4.*

### Revisor B — Hiring manager (percepción de portafolio)
- **[Crítico]** Falta traducir a "qué ve el reclutador" → *añadida columna Percepción.*
- **[Importante]** A13 (hub) subir en la tabla → *reordenado, A′ adelanta A13.*
- **[Crítico]** Falta narrativa README honesta → *plantilla de 4 bullets en §3.2 + fix del README de perfil.*
- **[Crítico]** Synthetic control y hub-cross-filter: no → *decisiones en §4 (P2, P5).*
- **[Importante]** Menores agrupados mal (manutd/passing lesionan credibilidad entera) → *sub-bloques en §3.0.*
- Prioridad final percepción×esfuerzo → *reflejada en el orden de la tabla y el Surgical A′.*

### Revisor C — Platform engineer (CI/secuenciación)
- **[Crítico]** A2 rompe `test_match_predictor.py` si se quita `rank_diff` a secas → *guardado en §2.2 y Tanda 4 con asserts en mismo commit.*
- **[Crítico]** A5 choca con regla de deps y con tests de sentimiento → *construido como gold standard sin deps nuevas; pysentimiento condicionado.*
- **[Crítico]** A7 renombra key assertioneada en geo → *aviso "mismo commit" en §2.4.*
- **[Importante]** A3/A4 orden y gate 45; A8 centroides inversos para no romper dashboard → *incorporados en §2.3, §2.5, Tanda 3.*
- **[Importante]** Criterio ETL vs rutas; lista de 5 primeros tests CI; paralelismo A/C con merge ordenado → *B3, §3.1 y §3.3.*

**Discusiones abiertas tras la ronda:** ninguna — los tres revisores convergieron en A0 primero, hub como índice de navegación, y gold standard en vez de pysentimiento.

---

*Proceso: 5 agentes auditores de dominio → consolidación (este documento) → 3 revisores externos (metodología, hiring, CI) → incorporación. Siguiente fase: ejecución de la Oleada A por tandas y, en paralelo según §3.3, el plan de unificación visual de dashboards.*
