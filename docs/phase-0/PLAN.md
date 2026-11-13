# World Atlas with World Impact: phase 0 plan

Status: **approved 2026-11-13.** Decisions:
- **Audience:** private, single user. All ⚠️ restricted sources are allowed, with attribution.
- **Sovereign wealth:** build a full curated dataset from official fund reports and reputable trackers.
- **Deploy target:** deferred.
- **Default supplier/buyer balance α:** set to **0.6**, reasoned below.

Phase 0 deliverables:
- This plan.
- [SOURCES.md](SOURCES.md): the checked list of data sources.
- [SPIKE.md](SPIKE.md): the globe prototype comparison.
- [`config/markets.yaml`](../../config/markets.yaml): the market list.
- `spike/`: runnable prototypes of both globe options.

> ⚠️ **The original World Atlas brief is not in this repo.** The repo started with only a README. This plan therefore covers the addendum in full, and makes assumptions about phase 1 (the core pipeline and groups), listed under Open questions. Please add the brief to `docs/brief.md`, or paste it to me, so I can reconcile the two.

## 1. Architecture

```
pipeline/ (Python 3.12, DuckDB + pandas)       web/ (Vite + React + TypeScript)
  fetch/   one module per source, cached raw     state/   Zustand store <-> URL (query-string, zod-validated)
  build/   ISO3 harmonisation, groups, years     globe/   MapLibre GL 5 globe + deck.gl 9.4 (arcs, columns)
  impact/  shares, HHI, weights, score, why      charts/  ECharts (built-in dataZoom + brush) for time series/scatter
  tests/   pytest (share, HHI, score, why)       panels/  slicers, sliders, KPI cards, profile, chips
        │ emits                                         ▲ lazy-loads
        └── data/out/{pillar}.json, impact.json, flows/{market}.json, provenance.json
```

- **Data is static JSON** split into one file per pillar and one per market. Phase 5 deploys it as a static site. There is no backend.
- **Every stored number carries `{value, source_id, year, unit, proxy}`.** Tooltips, the "why" sentences and the methodology page all read from this provenance.
- **Boundaries come from Natural Earth admin-0.** The 110m file loads at globe scale and swaps to 50m at zoom 3 or closer (proven in the spike). Disputed and breakaway areas get a hatched overlay and a flag in the tooltip.
- **Semantic zoom:**
  - Below zoom 2: regions and blocs, colored by aggregate values.
  - Zoom 2 to 4: individual countries.
  - Zoom 4 and closer: labels, values and capitals.
- **Fonts and glyphs are self-hosted.** No third-party tile server is needed.

## 2. World Impact scoring (our own construct; this is the formula the methodology page will publish)

For market *m*, country *c* and side *k* ∈ {supplier, buyer}, where *x* is that market's metric from `markets.yaml` (exports, production, imports, …):

1. **Share:** `s(c,m,k) = x(c,m,k) / Σ_c x(c,m,k)`. Shares run from 0 to 1, and the world total is computed over the countries that have data.
2. **Concentration:** `HHI(m) = Σ_c s(c,m,supplier)²`, between 0 and 1.
3. **Systemic weight:** `W(m) = size_share(m) × HHI(m)`, where `size_share(m) = size(m) / Σ size`. Size is world trade or production value in USD. The final weight is then `w(m) = u(m)·W(m) / Σ u·W`, where `u(m)` is the market-weight slider (default 1).
4. **Country impact:** `I(c) = Σ_m w(m) · [ α·s(c,m,supplier) + (1−α)·s(c,m,buyer) ]`. α is the supplier/buyer slider (default **0.6**; 1 means supplier side only).
   *Why 0.6:* supply-side concentration is the main way one country can move a world price (export bans, OPEC cuts, mineral export controls), so supply leads. Buyer power still moves prices: China in iron ore and soybeans, for example, or the EU in LNG. Weighting the buyer side at 0.4 keeps that visible without letting large importers outrank the suppliers that set prices.
5. **Score from 0 to 100:** `Score(c) = 100 · sqrt( I(c) / max_c I(c) )`. The square root spreads out the middle of the range, which share data otherwise bunches near zero. Both the transform and the anchor are configurable.
6. **Tier:** Systemic, Major, Regional or Niche, using the thresholds in `markets.yaml` (default 60/30/10). I'll calibrate them in phase 4 by checking that the Systemic tier is small (about 5–10 countries) and makes sense.
7. **Exposure (the reverse view):** `E(c,m) = import_dependence(c,m) × HHI of c's own suppliers for m`. Import dependence is imports ÷ (production + imports − exports), capped to the range 0–1. Where production data is missing, imports ÷ consumption is used instead.
8. **Drivers:** a market's contribution is `w(m)·[α s_sup + (1−α) s_buy]`. The top 3–5 contributions are the drivers shown for each country.
9. **Coverage:** each country's score shows the share of total weight `w` that had data. The minimum-coverage slider hides countries below a threshold.

**"Why" sentences are built from templates in `config/why_templates.yaml`.** Each placeholder must point to a stored data point. If any placeholder can't be filled, the whole sentence is dropped, never partially written. Proxy markets add "(trade proxy)". Example:
`Supplies {share}% of world {market} {metric}, rank #{rank} ({source}, {year}). Top 3 suppliers hold {top3_share}%.`

**Unit tests (pytest) will cover:**
- Shares sum to 1.
- HHI equals 1 for a single supplier and 1/n for n equal suppliers.
- The weights stay normalised when sliders change.
- Score is monotonic in a country's share and is 100 for the top country.
- Exposure stays between 0 and 1.
- A template with a missing placeholder produces no sentence.
- Every "why" sentence resolves to provenance IDs.

The front end will reuse the same formulas, ported to TypeScript and checked against shared fixtures, so the sliders can recompute scores live without a backend.

## 3. Dashboard and state
- **One Zustand store** holds: `{year, playing, regionScheme, regions[], blocs[], incomeGroups[], countries[], pillar, indicator, markets[], sources{}, side, pillarWeights{}, marketWeights{}, popRange, threshold, minCoverage, extrusionScale, arcMin, view:'globe'|'flat', camera, selection, brush}`.
  - It is serialised to the URL with short keys, and the URL is debounced while the camera is moving.
  - **Saved views** are named URL snapshots kept in localStorage, and they can be exported as JSON.
- **Cross-filtering:** every view reads from selectors on the one store, and no view holds its own copy of the data.
  - Clicking the globe sets `selection`. Brushing the scatter sets `brush`, which the globe shows as a highlight.
  - Slicers write to the store, and the chip bar is drawn from the active filters.
- **Layout:**
  - Desktop is a CSS grid: KPI cards on top, slicers on the left, globe in the middle, detail on the right, charts below.
  - On phones (under 768px) the globe is full width and the slicers sit in a bottom sheet.
- **Selecting a market:**
  - The globe switches to a two-color scale: suppliers in teal and buyers in amber, with saturation showing share.
  - Arcs from BACI bilateral flows appear, filtered by the arc-minimum slider. Arc width shows value, and arcs are capped at the top 500 flows.

## 4. Phases (revised per the addendum)
| Phase | Scope | Exit check |
|---|---|---|
| 0 | This plan, source table, globe spike | **Your approval** |
| 1 | Core pipeline and groups (per the original brief), ISO3 master list, provenance model, Natural Earth boundaries | `make data` builds the output; tests pass |
| 2 | MapLibre globe with zoom controls, fly-to search, zoom to selection, semantic zoom and flat toggle; country profile; slicer panel; URL state | Real-device frame-rate check (60 fps desktop, usable on a mid-range Android); URL round-trips the view |
| 3 | Bloc comparison, all sliders, composites and lenses, full cross-filtering, chip bar, saved views | Cross-filter end-to-end tests |
| 4 | Remaining pillars, then World Impact: markets.yaml, scoring, "why" templates, arcs, exposure view | Every country has a score, a tier, top markets and a fully sourced "why"; scoring unit tests pass |
| 5 | Scatter, rankings, membership matrix, methodology page, export (CSV/PNG), mobile polish, deploy | Lighthouse ≥ 90, accessibility checks pass |

## 5. Open questions (these block or shape later phases)
1. **The original World Atlas brief.** Please add it to the repo, or paste it to me.
2. **Audience and licensing:** private, public non-commercial, or commercial? This decides whether we can use the EI, SIPRI, IMF and BIS data (see SOURCES.md).
3. **Sovereign wealth:** use a static list from public annual reports, or drop it?
4. **Deploy target** for phase 5: GitHub Pages, Vercel, Netlify, or something else?
5. **The default supplier/buyer balance α:** 0.5, or lean toward suppliers (e.g. 0.7), since "moves markets" mostly means supply?
