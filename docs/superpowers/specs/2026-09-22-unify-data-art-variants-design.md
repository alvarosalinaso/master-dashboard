# Design: Unify 3 dashboard variants under Data-Art oscuro

Date: 2026-09-22 · Status: approved · Scope: first sub-project of the design/UX phase (portfolio target 8.5/10)

## Goal

The portfolio claims a single **Data-Art Poster oscuro** system (see `master-dashboard/infra/UX-MATRIX.md`), but three of the seven Dash dashboards ship divergent themes. This work brings them to full system parity so the recruiter experience is consistent across the portfolio.

| Repo | Current theme | Target |
|---|---|---|
| `geopolitica-textual-nlp` (`dashboard.py`, 1135 lines) | Manuscrito: parchment-light, custom manuscript template | Data-Art oscuro |
| `worldcup-2026` (`dashboard/app.py`, 1256 lines) | Neón oscuro: glow accents, `#141428` hero | Data-Art oscuro |
| `chilean-videogames-analysis` (`dashboard.py`, 793 lines) | Neon cyberpunk: scanlines, neon cyan/pink, `rgba(13,13,13,…)` cards | Data-Art oscuro |

Implementation order: **geopolitica → worldcup → videogames**.

## Design system (source of truth: UX-MATRIX tokens)

Adopt exactly the tokens and language already used by `master-dashboard`, `chile-geografia-historica`, `cajas-alimentacion`, `sanitizacion-santiago`:

- **Canvas** `#0a0e14` · **cards** `#11161f` · **border** `1px rgba(255,255,255,0.08)` · **radius** 12–14px
- **Text** `#e8edf2` · **muted** `#8b94a3` · **UI accent** `#22d3ee`
- **Plotly**: `template="plotly_dark"`, `paper_bgcolor="rgba(0,0,0,0)"`, ticks JetBrains Mono 12px
- **Categorical palette**: Okabe-Ito adapted for dark (`#56B4E9` `#E69F00` `#009E73` `#F0E442` `#CC79A7` `#D55E00` `#0072B2` `#999999`)
- **Continuous scales**: ColorBrewer/viridis family
- **Typography**: Inter 700–800 titles, JetBrains Mono for data/numbers; labels ≥0.75rem
- **Texture background**: inline SVG dot-grid + contour rings + scatter (no asset files)
- **Removed entirely**: neon glow, cyberpunk scanlines, parchment/manuscript light theme, bespoke light templates

## Components (full system parity, not tokens-only)

Each target dashboard gains/keeps the component vocabulary of the four reference dashboards:

1. **Hero strip** — Data-Art canvas texture (dots + contours + scatter), replacing glow SVG / scanlines / manuscript strip.
2. **KPI cards** — value + label + `sparkline(values, color)` micro-chart (32–40px, no axes) + delta where a prior period exists.
3. **`chart_card`** — title + explicit `Fuente:` source line + chart; Tufte data-ink (no heavy grids/shadows).
4. **`insight_card`** — question → answer with lateral accent border (`#22d3ee` or series color).
5. **`hovertemplate`** — explicit on every trace (no raw Plotly tooltips).
6. **Cross-filtering** — keep existing callbacks; where a bar chart lacks `clickData` wiring that the reference dashboards have, add it with `prevent_initial_call=True` + `no_update` on no-click.

## Implementation approach (approved)

- **Per-repo theme block** (approach A): each `dashboard.py` (or `dashboard/app.py`) embeds the same token constants + helper functions, mirroring how cajas/sanitizacion/geografia already do it. No shared package, no new runtime dependencies, no cross-repo coupling. Duplication of ~150 lines ×3 is the accepted trade-off.
- **Data logic untouched**: analysis code, CSV/parquet reads, callbacks' data flow, filter semantics, and route structure stay byte-identical where possible. Restyle = layout dict values, CSS strings, figure `layout` updates, added display-only helpers.
- **No new runtime deps**: verification uses **Edge headless** screenshots (`msedge --headless --screenshot=…` against `localhost:<port>`), not playwright/selenium.

## Verification (per repo, before moving to the next)

1. `python -m ruff check .` and `python -m ruff format --check .` green (repo's config).
2. Full `pytest` green (none of the three currently test the dashboard; suite must not regress).
3. Launch dashboard locally; Edge-headless screenshots of **every tab/section** at 1600×2400.
4. Visual diff against a reference Data-Art dashboard (master-dashboard or cajas): tokens, texture, sparklines, Fuente lines, hover style.
5. Commit → push → workflow badge `passing` on `https://github.com/alvarosalinaso/<repo>/actions/workflows/ci.yml/badge.svg`.
6. Update the repo's row in `master-dashboard/infra/UX-MATRIX.md` (system column → `Data-Art oscuro`, new commit hash).

## Error handling / edge cases

- **geopolitica manuscript template**: `PLOTLY_MANUSCRIPT_TEMPLATE` and `COLORS["parchment_light"]` are referenced from multiple figure builders — replace at the definition site and audit every `template=`/`bgcolor` usage (grep-driven, ~20 occurrences).
- **Fonts**: dashboards load Inter/JetBrains via existing Google Fonts link or system fallbacks; do not add font asset files.
- **3D scenes** (worldcup radar/videogames bubbles if present): keep scene data, recolor `layout.scene` bgcolor/text to tokens.
- **CI after each push**: badge sweep of all 10 repos; a red badge blocks proceeding to the next repo.
- **HuggingFace/Render mirrors** (`C:\Users\Alvaro\Temp\hf_spaces\*`, `requirements-render.txt`): out of scope unless a deploy breaks from the restyle (it should not — no dep changes).

## Out of scope (later sub-projects)

- `manchester-united-analisis` light-theme `dashboard.html`
- New dashboards for `united-passing-efficiency-24-25` and `tactical-narrative-graph-analysis`
- Shared theme pip package
- README screenshot refreshes (optional follow-up after all three land)

## Success criteria

- 7/7 Dash dashboards on identical Data-Art oscuro tokens; UX-MATRIX intro claim ("sistema único") is true.
- All 10 portfolio badges green.
- Each of the 3 repos: ruff + pytest green, screenshots reviewed against reference.
