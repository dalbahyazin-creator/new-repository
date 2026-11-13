"""Run the full phase-1 build: master list → groups → indicators → validation → static JSON."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from . import countries, geo, groups, wdi
from .fetch import _manifest
from .paths import OUT
from .provenance import sources, validate_observations


def _dump(path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, separators=(",", ":"), ensure_ascii=False, allow_nan=False))


def coverage(obs: pd.DataFrame, universe: list[str]) -> dict:
    out = {}
    for ind, g in obs.groupby("indicator"):
        per_year = g.groupby("year").iso3.nunique()
        good = per_year[per_year >= 0.8 * len(universe)]
        latest_good = int(good.index.max()) if len(good) else None
        out[ind] = {
            "countries_any_year": int(g.iso3.nunique()),
            "latest_year": int(g.year.max()),
            "latest_year_80pct": latest_good,  # newest year where at least 80% of the default universe reports
            "share_universe_latest80": round(per_year.get(latest_good, 0) / len(universe), 3) if latest_good else 0,
        }
    return out


def pillar_payload(obs: pd.DataFrame, cfg: dict, pillar: str) -> dict:
    keys = [k for k, s in cfg["indicators"].items() if s["pillar"] == pillar]
    data = {}
    for k in keys:
        g = obs[obs.indicator == k]
        data[k] = {iso: [[int(y), float(v)] for y, v in zip(s.year, s.value)] for iso, s in g.groupby("iso3")}
    meta = {k: {"label": cfg["indicators"][k]["label"], "unit": cfg["indicators"][k]["unit"],
                "source_id": "wb_wdi", "wdi_code": cfg["indicators"][k]["code"]} for k in keys}
    return {"pillar": pillar, "indicators": meta, "data": data}


def run(skip_geo: bool = False) -> dict:
    master = countries.build_master()
    known = set(master.iso3)
    universe = sorted(master[master.in_default_universe].iso3)

    grp = {"regions": groups.region_schemes(master), "income": groups.income_groups(master),
           "blocs": groups.load_blocs(known)}

    obs = validate_observations(wdi.fetch_all(known), known)
    cfg = wdi.indicator_config()

    OUT.mkdir(parents=True, exist_ok=True)
    rec = json.loads(master.astype(object).where(master.notna(), None).to_json(orient="records"))
    _dump(OUT / "countries.json", rec)
    _dump(OUT / "groups.json", grp)
    obs.to_parquet(OUT / "observations.parquet", index=False)
    for p in sorted({s["pillar"] for s in cfg["indicators"].values()}):
        _dump(OUT / "pillars" / f"{p}.json", pillar_payload(obs, cfg, p))
    cov = coverage(obs, universe)
    _dump(OUT / "coverage.json", cov)
    _dump(OUT / "provenance.json", {"built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                     "sources": sources(), "downloads": _manifest()})
    geo_report = None if skip_geo else geo.build(known)
    report = {"countries_master": len(master), "default_universe": len(universe),
              "observations": len(obs), "blocs": {k: len(v["members"]) for k, v in grp["blocs"].items()},
              "coverage": cov, "geo": geo_report}
    _dump(OUT / "build_report.json", report)
    return report
