# Impact data sources: checked 13 Nov 2026

**How these were checked.** This sandbox can't reach most of the source websites; only package registries and raw GitHub are open. So I checked each source by web search against its official pages; the links are in the table. Wherever a row says "unverified", I found no official statement. Licence notes are my reading of each source's terms. They are not legal advice.

**Status codes used in the table:**
- ✅ **Open:** fine to redistribute with attribution.
- ⚠️ **Restricted:** free to download, but republishing is limited or needs permission.
- 💲 **Paid.**
- ❌ **No open source exists.** We use a trade proxy instead and label it as a proxy.

## Source table

| # | Source | Used for (markets) | Access | Cost | Licence | Latest data | Status |
|---|---|---|---|---|---|---|---|
| 1 | **CEPII BACI** (HS6 bilateral trade) | Supplier and buyer shares for every traded good. Trade-flow arcs. Proxies for semiconductors, EVs, batteries, pharma, textiles, machinery, refined products, fertilizers. | Bulk CSV ([doc](https://www.cepii.fr/DATA_DOWNLOAD/baci/doc/baci_webpage.html)) | Free | Etalab Open Licence 2.0 | V202601, data to 2024 | ✅ **Main trade source** |
| 2 | UN Comtrade | Fallback and cross-check only | API (free key: 500 calls/day) | Bulk downloads are 💲 Premium | Custom UN licence ([terms](https://comtrade.un.org/licenseagreement.html)). Republishing raw data needs Premium Pro. | Continuous | ⚠️ |
| 3 | Harvard Atlas of Economic Complexity | Services trade, complexity context | Dataverse download | Free | Set per dataset (unverified). The paper is CC BY-NC-ND. | HS92 data from 1995 | ⚠️ Unverified |
| 4 | **USGS Mineral Commodity Summaries 2026** | Lithium, cobalt, nickel, copper, rare earths, graphite (mine output and reserves). Gallium and germanium (refinery output). | CSV data release ([doi 10.5066/P1WKQ63T](https://www.usgs.gov/data/mineral-commodity-summaries-2026-data-release)) | Free | Public domain (CC0) | Feb 2026, data for 2025 | ✅ Need to check that reserves are in the CSV |
| 5 | OECD-NEA Red Book / World Nuclear Association | Uranium | PDF and web tables | Free to read | © OECD / WNA. Redistribution unverified. | 2024 data | ⚠️ Fallback: BACI HS 2612 |
| 6 | Energy Institute Statistical Review | Oil, gas, LNG, coal (production and consumption) | Excel / CSV | Free | **All rights reserved.** Extensive reproduction needs permission. | 2026 edition, data to 2025 | ⚠️ **Ask permission, or use fallbacks** |
| 6b | Fallbacks for 6: Ember (power), BACI energy chapters (HS 27xx), US EIA international data (public domain) | Energy | CSV / API | Free | CC BY 4.0 / public domain | 2025 | ✅ |
| 7 | **FAOSTAT** | Wheat, rice, maize, soybeans, palm oil, fertilizers (production and trade) | Bulk CSV / API | Free | CC BY 4.0 plus FAO terms ([terms](https://www.fao.org/contact-us/terms/db-terms-of-use)) | About 2024 | ✅ |
| 8 | IMF COFER | Share of world reserves held in each currency | Data portal | Free | IMF terms ([terms](https://www.imf.org/en/about/copyright-and-terms)). Commercial reuse needs permission. | Quarterly | ⚠️ **By currency only, not by country.** Map USD→US, EUR→euro-area members (split by GDP), and so on. |
| 9 | BIS Triennial Survey 2025 | FX turnover by currency and by trading jurisdiction | CSV ([rpfx25](https://bis.org/statistics/rpfx25.htm)) | Free | © BIS. Limited extracts allowed with attribution. | Apr 2025 survey | ⚠️ Full redistribution terms unverified |
| 10 | **UNCTADstat** | Outward FDI, container port throughput, merchant fleet (by flag and by owner) | Bulk / API | Free | CC BY 3.0 IGO | 2025 | ✅ |
| 11 | IMF PortWatch | Exposure to shipping chokepoints (Hormuz, Bab el-Mandeb/Suez, Malacca, Panama, Bosporus) | API / HDX | Free | IMF special terms. Commercial use needs permission. | Weekly | ⚠️ Port-level data; we roll it up to countries ourselves |
| 12 | **World Bank WDI** | Remittances paid and received, household consumption, imports, population, income groups | API / CSV | Free | CC BY 4.0 | 2026 update | ✅ |
| 13 | UN Tourism (formerly UNWTO) | Outbound tourism spending | Dashboard; some series on request | Partly free | Unverified | Recent years | ⚠️ The WDI copy (`ST.INT.XPND.CD`) **stops at 2020**. The OWID republication is the fallback. |
| 14 | SIPRI MILEX and Arms Transfers (TIV) | Military spending, arms exports | Excel | Free | **Republishing needs SIPRI's authorization** ([terms](https://www.sipri.org/databases/terms)). Commercial use needs a licence. | 2025 spending; TIV to Mar 2026 | ⚠️ **Ask permission** |
| 15 | **Our World in Data CO₂** (Global Carbon Budget 2026) | Share of world CO₂ emissions | CSV (catalog.ourworldindata.org; the GitHub repo is frozen) | Free | CC BY 4.0 for OWID's own work; underlying data keeps its original terms | Nov 2026 | ✅ |
| 16 | Ember | Clean power (stand-in for clean-tech context) | CSV | Free | CC BY 4.0 | 2025 | ✅ |
| 17 | **Natural Earth** | Boundaries (110m and 50m), disputed areas, capitals | GeoJSON / TopoJSON | Free | Public domain | v5.x | ✅ Use the de-facto boundaries plus the "breakaway/disputed" layer, which we flag on the map ([policy](https://www.naturalearthdata.com/about/disputed-boundaries-policy/)). Avoid UN Geospatial boundaries (non-commercial only, needs clearance). |

## Gaps (paid or no open source)

| Market | Problem | What we'll do |
|---|---|---|
| Semiconductor production | WSTS (~$30k/yr) and SEMI (~$5–15k) are 💲. No open source. | ❌ Use **exports of HS 8541/8542 as a proxy**, labelled as a proxy. |
| Clean-tech manufacturing | IEA data is 💲 or CC BY-NC-SA, and BNEF is 💲. | ❌ Use **exports of solar modules (HS 854142/854143), Li-ion batteries (850760) and EVs (870380) as a proxy**, labelled as a proxy. |
| Sovereign wealth assets | GlobalSWF and SWFI are 💲. The academic SWIFT dataset stops in 2023 and its licence is unverified. | Use a static, cited list of fund assets taken from public annual reports, labelled with its year. Or drop the metric. **Your call.** |
| Bilateral remittances | KNOMAD has closed; its last bilateral matrix is 2021. | Use WDI totals (paid and received) for scoring, and show no remittance arcs. |
| Uranium | The Red Book's licence is unclear. | Use BACI HS 2612 trade as a proxy until NEA confirms. |

## Licensing decisions (resolved 2026-11-13)
1. **The dashboard is private, for a single user.** EI, SIPRI, BIS, IMF (COFER, CPIS, PortWatch), UN Tourism and the NEA Red Book are therefore **primary sources**, cited on every value. If the dashboard is ever published, `license_status: restricted` in `config/sources.yaml` marks exactly which data must be swapped out or cleared first.
2. **Sovereign wealth:** build a curated dataset in `config/sovereign_wealth.yaml`. Each fund entry cites its own annual report, with IFSWF and reputable trackers used as cross-checks.
