# Unify 3 Dashboard Variants Under Data-Art oscuro — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle geopolitica-textual-nlp, worldcup-2026, and chilean-videogames-analysis dashboards to full Data-Art oscuro parity so all 7 Dash dashboards share one visual system.

**Architecture:** Per-repo theme block (approach A): each dashboard file embeds the same Data-Art tokens + helpers copied from `master-dashboard/app.py` / `cajas-alimentacion/dashboard.py`. No shared package, no new runtime deps. Order: geopolitica → worldcup → videogames. Each repo ships independently with its own commit/push/badge cycle.

**Tech Stack:** Dash/Plotly (existing), Python 3.10+, ruff, pytest, Edge headless for screenshots (no new deps).

**Spec:** `master-dashboard\docs\superpowers\specs\2026-09-22-unify-data-art-variants-design.md`

## Global Constraints

- NO data-logic changes: callbacks, queries, DataFrame ops, filter semantics untouched.
- NO new runtime dependencies; NO package restructuring.
- Tokens (verbatim): canvas `#0a0e14`, card `#11161f`, border `1px solid rgba(255,255,255,0.08)`, text `#e8edf2`, muted `#8b94a3`, accent `#22d3ee`, radius `12px`–`14px`.
- Okabe-Ito dark palette: `["#56B4E9","#E69F00","#009E73","#F0E442","#CC79A7","#D55E00","#0072B2","#999999"]`.
- Fonts: `FONT_UI = "'Inter','Segoe UI',system-ui,sans-serif"`, `FONT_DATA = "'JetBrains Mono',Consolas,'Courier New',monospace"`; Plotly `template="plotly_dark"`, `paper_bgcolor="rgba(0,0,0,0)"`, ticks JetBrains Mono 12px.
- Removed per repo: geopolitica → parchment/burgundy/gold/Georgia/ornate/neon-net; worldcup → `#0a0a1a`/`#141428`/`#2a2a4a`/gold/neon green+blue/`NEON_POSTER_SVG`; videogames → scanlines CSS, `NEON_CYAN/PINK/GREEN`, glow shadows, letter-spaced Consolas headers.
- Keep cross-filter `clickData` callbacks intact; add missing `hovertemplate` only where a trace lacks it (do not rewrite existing ones).
- Each repo: `python -m ruff check .` + `python -m ruff format --check .` green, full `pytest` green, badge `passing` before next repo.
- Commits use conventional style per repo (check `git log --oneline -5` first); branches: geopolitica/worldcup/videogames use `main` unless `git status -sb` says otherwise.
- Screenshots stored under temp only (`C:\Users\Alvaro\AppData\Local\Temp\opencode\screenshots\`), never committed.
- PowerShell: no `&&`, no `head`; keep commands short.

## Reference code (copy source)

Canonical blocks live in `C:\Users\Alvaro\github-limpio\master-dashboard\app.py`:
- Tokens: lines 20–37 (`FONT_UI`, `FONT_DATA`, `COLORS`)
- Hero texture: lines 39–57 (`DATA_CANVAS_SVG`)
- `CHART_TEMPLATE`: lines 59–88
- `sparkline`: see `cajas-alimentacion\dashboard.py` lines 178–202 (identical pattern in master)
- `insight_card`: master lines ~140–175 (or cajas 205+)
- `chart_card`: master lines 178–213 (title + `Fuente:` + graph)
- Tab styles: master `_tab_style()` lines 91+

---

### Task 1: geopolitica-textual-nlp — theme kit swap

**Files:**
- Modify: `C:\Users\Alvaro\github-limpio\geopolitica-textual-nlp\dashboard.py` (1188 lines)

**Interfaces:**
- Produces: same public names (`app`, `server`, callbacks unchanged); visual layer only.

- [ ] **Step 1: Baseline screenshot + tests**

```powershell
python -m pytest tests/ -q; "EXIT=$LASTEXITCODE"
python -m ruff check .; python -m ruff format --check .
```
Expected: EXIT=0, ruff clean. Save outputs for comparison.

- [ ] **Step 2: Replace theme constants**

In `dashboard.py`, replace the `COLORS = {...parchment/burgundy/gold...}` dict (lines ~20–34) with:

```python
FONT_UI = "'Inter','Segoe UI',system-ui,sans-serif"
FONT_DATA = "'JetBrains Mono',Consolas,'Courier New',monospace"
COLORS = {
    "bg": "#0a0e14",
    "card": "#11161f",
    "border": "1px solid rgba(255,255,255,0.08)",
    "accent": "#22d3ee",
    "text": "#e8edf2",
    "muted": "#8b94a3",
}
OKABE_ITO_DARK = [
    "#56B4E9", "#E69F00", "#009E73", "#F0E442",
    "#CC79A7", "#D55E00", "#0072B2", "#999999",
]
```

Delete `PAPER_TEXTURE` and `NEON_NET_SVG` (lines ~64–84). Add `DATA_CANVAS_SVG` copied verbatim from `master-dashboard\app.py` lines 39–57.

- [ ] **Step 3: Replace plotly template**

Replace `PLOTLY_MANUSCRIPT_TEMPLATE = {...}` (lines ~324+) with:

```python
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
    colorway=OKABE_ITO_DARK,
)
```

Run a file-wide replace: `PLOTLY_MANUSCRIPT_TEMPLATE` → `CHART_TEMPLATE`; `paper_bgcolor=COLORS["parchment_light"]` → `paper_bgcolor="rgba(0,0,0,0)"`; `plot_bgcolor=COLORS["parchment"]` → `plot_bgcolor="rgba(0,0,0,0)"`. Delete the extra per-figure `font family Georgia` dicts (leave font to template). Verify with:

```powershell
python -m ruff check dashboard.py
python -c "import ast; ast.parse(open('dashboard.py',encoding='utf-8').read()); print('syntax ok')"
```

- [ ] **Step 4: Restyle helper components**

- `sparkline`: default `color="#6b1d1d"` → `"#56B4E9"`; keep body.
- `insight_card`: default `accent="#6b1d1d"` → `"#22d3ee"`; body style → `"backgroundColor": "#11161f", "border": "1px solid rgba(255,255,255,0.08)", "borderLeft": f"3px solid {accent}", "borderRadius": "10px"`; fonts `Georgia, serif` → `FONT_UI` / `FONT_DATA`.
- Delete `ornate_border`, `flourish`, `section_divider`, `chapter_header` OR reimplement them as thin Data-Art wrappers (prefer: keep function names so call sites don't break, but body becomes neutral card styling — `ornate_border` returns hairline border only, `flourish` returns muted mono char `—`, `section_divider` returns 1px hr, `chapter_header` returns Inter H2 + mono eyebrow). Grep call sites first: `Select-String dashboard.py -Pattern 'ornate_border|flourish|chapter_header|section_divider'`.
- `card` helper: bg `COLORS["parchment_light"]`/`ornate_border()` → `COLORS["card"]` + hairline; title fonts Georgia → Inter 700 `#e8edf2`.
- Replace page layout bg `COLORS["parchment"]` → `COLORS["bg"]`; hero `NEON_NET_SVG` reference → `DATA_CANVAS_SVG`.
- `stat_row` / KPI blocks: bg → `#11161f`, top accent 3px solid `#56B4E9`, value font `FONT_DATA`.

- [ ] **Step 5: Font sweep**

```powershell
(Select-String dashboard.py -Pattern 'Georgia|Palatino|Book Antiqua').Count
```
Expected: 0 after replacing every `fontFamily` Georgia string with `FONT_UI` (labels) or `FONT_DATA` (numbers). Also swap body `fontFamily` on root layout to `FONT_UI`.

- [ ] **Step 6: Fuente lines + hovertemplates**

- Add `chart_card`-style `Fuente:` subtitle (copy master `chart_card` lines 178–213) and wrap major figures where the card only shows a title today — apply at minimum to the NER bar, sentiment hist, topics bigrams (the three cross-filter charts).
- Grep traces missing hover: `Select-String dashboard.py -Pattern 'hovertemplate'` count vs `go.Bar|go.Scatter|go.Pie` count; add explicit `hovertemplate` to any missing (format follows cajas: `<b>%{x}</b><br>…<extra></extra>`).

- [ ] **Step 7: Launch + screenshot every section**

```powershell
# terminal A (repo root)
python dashboard.py   # PORT=8051
# terminal B
New-Item -ItemType Directory -Force C:\Users\Alvaro\AppData\Local\Temp\opencode\screenshots\geopolitica | Out-Null
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --screenshot="C:\Users\Alvaro\AppData\Local\Temp\opencode\screenshots\geopolitica\overview.png" --window-size=1600,2400 --virtual-time-budget=8000 http://localhost:8051/
```
Geopolitica sections are stacked (single scroll page with NER/Sentimiento/Tópicos/Mapa/Stats) — also capture `full height`: `--window-size=1600,9000` for a full-page shot. Inspect PNGs: dark canvas `#0a0e14`, no parchment, no Georgia, no neon net, KPI sparklines visible. If any figure renders light/white, fix template application and re-shoot.

- [ ] **Step 8: Verify + commit + push**

```powershell
python -m pytest tests/ -q; "EXIT=$LASTEXITCODE"
python -m ruff check .; python -m ruff format --check .
git add dashboard.py; git commit -m "style: unify dashboard to Data-Art oscuro tokens"; git push origin main
```
Expected: EXIT=0, ruff clean, push OK. Sleep 110s, badge check:

```powershell
(Invoke-WebRequest -UseBasicParsing "https://github.com/alvarosalinaso/geopolitica-textual-nlp/actions/workflows/ci.yml/badge.svg").Content -match 'passing'
```
Expected: True. **Gate: badge must pass before Task 2.**

---

### Task 2: worldcup-2026 — theme kit swap

**Files:**
- Modify: `C:\Users\Alvaro\github-limpio\worldcup-2026\dashboard\app.py` (1340 lines)

**Interfaces:**
- Consumes: nothing from Task 1 (independent repo); same global tokens.

- [ ] **Step 1: Baseline**

```powershell
python -m pytest tests/ -q; python -m ruff check .
```
Both green (current state).

- [ ] **Step 2: Replace COLORS + delete neon hero**

Replace `COLORS = {...#0a0a1a/#141428/#e94560/#00ffcc...}` (lines 67–77) with the same Data-Art `COLORS` dict as Task 1 Step 2 (include `"gold"` only if referenced — grep first: `Select-String dashboard\app.py -Pattern 'COLORS\["gold"\]|COLORS\["accent"\]|COLORS\["neon'`). Map any kept keys:
- `bg` → `#0a0e14`, `card` → `#11161f`, `border` → `rgba(255,255,255,0.08)` (note: current border is a solid hex used as `backgroundColor` for table headers — change those usages to the rgba string or `#1c2433` if a hex is required; grep `COLORS["border"]` and fix each).
- `text` → `#e8edf2`, `muted` → `#8b94a3`, `accent` → `#22d3ee`.
- Delete `neon_green`, `neon_blue`, `gold` if unreferenced; if `gold` referenced, remap to `#E69F00`.

Delete `NEON_POSTER_SVG` (lines 79–93); add `DATA_CANVAS_SVG` from master lines 39–57. Replace its usage in layout (`backgroundImage: f'url("{NEON_POSTER_SVG}")'` around line 185) with `DATA_CANVAS_SVG`.

- [ ] **Step 3: Fonts + tab styles**

- `sparkline` default color `"#e94560"` → `"#56B4E9"`.
- Root layout `fontFamily: "Segoe UI, sans-serif"` → `FONT_UI` (define `FONT_UI`/`FONT_DATA` at top as in Task 1).
- Add `CHART_TEMPLATE` (same dict as Task 1 Step 3, including `colorway=OKABE_ITO_DARK`) and ensure every `fig.update_layout(...)` / `px.*` uses `**CHART_TEMPLATE` or at minimum `template="plotly_dark"` + transparent paper (grep `template=` occurrences and unify).
- Tab styles: point `dcc.Tab` selected style accent bar to `#22d3ee`; unselected text `#8b94a3`.

- [ ] **Step 4: Table + card colors**

Grep `backgroundColor` values that are off-token (`#141428`, `#2a2a4a`, `#2a1a1a`, `#1a1a2e`) → map to `#11161f` (cards), `rgba(255,255,255,0.08)`/`#1c2433` (borders), `#0a0e14` (canvas). Remove glow/textShadow if present.

- [ ] **Step 5: Fuente + hover**

- Ensure overview + goals tab charts have a `Fuente:` line (reuse/add `chart_card` pattern or an inline muted mono div `f"Fuente: {source}"` under each H3 — sources: FIFA/Stats Perform style strings already used in README, or "base de datos histórica del repo").
- Add missing `hovertemplate` on traces (grep count check as Task 1 Step 6). Cross-filter callbacks: leave untouched.

- [ ] **Step 6: Launch + screenshots (7 tabs)**

```powershell
python dashboard/app.py   # PORT=8050
```
Tabs: overview, goals, stadiums, teams, knockout, predictions, compare. Screenshot technique — temporarily set `dcc.Tabs(..., value="<tab>")` (line ~198) to each tab value, restart, Edge screenshot to `screenshots\worldcup\<tab>.png`, revert `value` back to `"overview"` before commit. Verify: dark canvas, no neon poster, Inter titles, Okabe-Ito series colors, Fuente visible.

- [ ] **Step 7: Verify + commit + push**

```powershell
python -m pytest tests/ -q; python -m ruff check .; python -m ruff format --check .
git add dashboard/app.py; git commit -m "style: unify dashboard to Data-Art oscuro tokens"; git push origin main
```
Badge check after 110s (same URL pattern, repo `worldcup-2026`). **Gate: badge must pass before Task 3.**

---

### Task 3: chilean-videogames-analysis — theme kit swap

**Files:**
- Modify: `C:\Users\Alvaro\github-limpio\chilean-videogames-analysis\dashboard.py` (859 lines)

**Interfaces:**
- Consumes: nothing from Tasks 1–2; same tokens.

- [ ] **Step 1: Baseline**

```powershell
python -m pytest tests/ -q; python -m ruff check .
```
Note: coverage gate `--cov-fail-under=45` must stay green — restyle must not break imports.

- [ ] **Step 2: Kill cyberpunk chrome**

- Delete both `SCANLINE_CSS` blocks and the custom `app.index_string` animation styles (lines 12–15, 24–41, 52–75). If `app.index_string` is needed for anything else, keep the shell but empty the `<style>`; prefer removing `index_string` entirely and using default Dash index.
- Delete `NEON_CYAN/PINK/GREEN`, `BG_BLACK`, `CARD_BG`, `TEXT_WHITE`, `TEXT_MUTED`, `GRID_DOT` (lines 43–50); add standard `FONT_UI`, `FONT_DATA`, `COLORS`, `OKABE_ITO_DARK`, `CHART_TEMPLATE`, `DATA_CANVAS_SVG` (same blocks as Task 1).
- `card(title, children, glow_color=NEON_PINK)` → `card(title, children)` with Data-Art style: bg `#11161f`, `border: 1px solid rgba(255,255,255,0.08)`, `borderRadius: 14px`, no boxShadow glow, no backdrop blur, title `#e8edf2` Inter 700 (no textShadow, no letter-spacing 2px uppercase → use uppercase only if reference does; reference uses normal case Inter — use normal case). Update all call sites `card("X", fig, NEON_PINK)` → `card("X", fig)` (grep `NEON_` to find them).

- [ ] **Step 3: Restyle inner helpers**

- `insight_card` default accent → `#22d3ee`; body → card tokens + Inter/mono fonts.
- `_tab_style`: selected border `#22d3ee`, text `#e8edf2`/`#8b94a3`.
- All `fontFamily: "Consolas, 'Courier New', monospace"` display headers → `FONT_UI` (labels stay `FONT_DATA` only for numeric values).
- Root layout: bg `#0a0e14`, color `#e8edf2`; KPI/stat blocks bg `#11161f` + top accent `3px solid #56B4E9`.
- Figures: ensure `"template": "plotly_dark"` + transparent bg everywhere (grep `template`); apply `CHART_TEMPLATE` where update_layout is explicit.
- Hero: if layout has a neon strip/hero, replace with `DATA_CANVAS_SVG` background; else add the standard hero strip at top (title + mono subtitle + texture bg) matching master.

- [ ] **Step 4: Fuente + hover**

- Add `Fuente: Steam API + Itch.io scraping` line under chart card titles (matches existing `generate_tables` source note).
- Missing `hovertemplate` sweep (5 tabs: overview, prices, revenue, genres, correlation). Cross-filter callbacks untouched.

- [ ] **Step 5: Launch + screenshots (5 tabs)**

```powershell
python dashboard.py   # PORT=8053
```
Tabs: overview, prices, revenue, genres, correlation. Same temporary-`value` flip technique as Task 2 Step 6. Output: `screenshots\videogames\<tab>.png`. Verify: no scanlines, no neon glow, Okabe-Ito pies/bars, dark cards.

- [ ] **Step 6: Verify + commit + push**

```powershell
python -m pytest tests/ -q   # must include cov-fail-under=45 pass
python -m ruff check .; python -m ruff format --check .
git add dashboard.py; git commit -m "style: unify dashboard to Data-Art oscuro tokens"; git push origin main
```
Badge check after 110s. **Gate: badge must pass before Task 4.**

---

### Task 4: Update UX-MATRIX + final sweep

**Files:**
- Modify: `C:\Users\Alvaro\github-limpio\master-dashboard\infra\UX-MATRIX.md`

- [ ] **Step 1: Edit matrix rows**

In the "Estado por proyecto" table set Sistema = `Data-Art oscuro` for `worldcup-2026`, `geopolitica-textual-nlp`, `chilean-videogames-analysis`; Hero column → `Canvas dots+contornos+scatter` (or `—` if no hero strip); Commit column → the new short SHAs from Tasks 1–3 (`git rev-parse --short HEAD` in each repo).

- [ ] **Step 2: Badge sweep all 10 repos**

```powershell
$repos = @("worldcup-2026","geopolitica-textual-nlp","chilean-videogames-analysis","chile-geografia-historica","cajas-alimentacion","sanitizacion-santiago","manchester-united-analisis","united-passing-efficiency-24-25","tactical-narrative-graph-analysis","master-dashboard")
foreach ($r in $repos) { $s = (Invoke-WebRequest -UseBasicParsing "https://github.com/alvarosalinaso/$r/actions/workflows/ci.yml/badge.svg").Content; if ($s -match 'CI - (\w+)') { "$r : $($Matches[1])" } }
```
Expected: 10 × `passing`.

- [ ] **Step 3: Commit matrix**

```powershell
git add infra/UX-MATRIX.md; git commit -m "docs: mark 3 dashboards as Data-Art oscuro in UX-MATRIX"; git push origin master
```
(master-dashboard uses branch `master`.)

## Self-Review

1. **Spec coverage:** tokens ✓, hero texture ✓, sparklines ✓, Fuente ✓, insight cards ✓, hovertemplates ✓, cross-filter preserved ✓, Edge screenshots ✓, order geopolitica→worldcup→videogames ✓, UX-MATRIX update ✓, badge gates ✓, no new deps ✓, no data-logic changes ✓.
2. **Placeholders:** none — every step has commands or exact code.
3. **Name consistency:** `CHART_TEMPLATE`, `DATA_CANVAS_SVG`, `FONT_UI`, `FONT_DATA`, `COLORS`, `OKABE_ITO_DARK` used identically across all tasks; helper signatures `card(title, children)`, `insight_card(question, answer, accent)`, `sparkline(values, color)` match existing call patterns after arg cleanup.
