# Phase 1: core pipeline and groups

Run:
- `make setup`: one-time setup
- `make data`: downloads into a cache, then builds to `data/out/`
- `make test`: runs the unit tests

## What the pipeline produces (`data/out/`)
| File | Contents |
|---|---|
| `countries.json` | Master list of **251** countries and areas, keyed by ISO3. **220** are in the default universe (independent states, World Bank economies, Taiwan, Palestine, Western Sahara). Each entry has: names, M49 codes, UN region / sub-region / intermediate region, World Bank region, income group, lending type, LDC/LLDC/SIDS flags, currency, capital and its coordinates, and a status note for disputed entities. |
| `groups.json` | **Regions:** 4 schemes (UN region 5 groups, UN sub-region 17, UN intermediate region 23, World Bank region 7). **Income:** 4 World Bank tiers plus the UN LDC, LLDC and SIDS lists. **Blocs:** 22, each with its official source, since/until years and notes. |
| `pillars/{core,trade,people,security}.json` | One file per pillar, so the web app can load them lazily. Each holds a time series per indicator and country. |
| `observations.parquet` | The full long table. Each row is (iso3, indicator, year, value, unit, source_id, proxy). It is checked before writing: rows with a missing source, an unknown country or a duplicate are rejected. |
| `coverage.json` | For each indicator: how many countries report it, its latest year, and the newest year in which at least 80% of the default universe reports. This feeds the minimum-coverage slider. |
| `provenance.json` | The source registry plus every download's URL, SHA-256 hash and fetch time. |
| `geo/countries-{110m,50m}.topo.json`, `geo/disputed-50m.topo.json` | Natural Earth boundaries keyed by ISO3, plus 28 breakaway/disputed areas. |

## Design notes
- **One country list for everything.** Every country code in every output must be in the master list, which the build enforces. The World Bank's non-ISO codes are handled explicitly: Kosovo is `XKX`, and the Channel Islands are `CHI`, covering Jersey and Guernsey.
- **Bloc membership changes over time.** `member_in_year()` lets the year slider show, for example, the UK in the EU up to 2020, Bulgaria in the euro area from 2026, and Mali, Burkina Faso and Niger in ECOWAS up to 2025.
- **Boundaries are de facto.** Somaliland, Northern Cyprus and Siachen are drawn but flagged `disputed` and carry no data. The disputed-areas overlay will be drawn hatched in phase 2.
- **Small places need markers.** At 50m, Gibraltar and the Channel Islands have no shape, and at 110m many small islands are missing. Phase 2 will draw these as point markers placed at their capitals.

## Data checks from the first build (World Bank data, Nov 2026)
- Population: 217 countries report it, with data for 2025 covering 98.6% of the universe.
- GDP: 214 countries, data for 2025.
- Trade and household consumption: the newest year with at least 80% coverage is **2022**, because recent years are not yet filled in. Indicators will default to their newest well-covered year.
- Military spending as % of GDP: no year reaches 80% coverage through the World Bank copy of SIPRI's data. Phase 4 will take it directly from SIPRI.

## Open item
The original World Atlas brief is still missing. When it arrives, I'll add the extra pillars and indicators to `config/indicators.yaml`. No code changes are needed for that.
