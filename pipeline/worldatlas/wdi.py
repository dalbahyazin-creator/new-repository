"""World Bank WDI indicators, written as provenance-tagged observations."""
from __future__ import annotations

import json

import pandas as pd
import yaml

from .fetch import download
from .paths import CONFIG

API = "https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=20000&date={y0}:{y1}"


def indicator_config() -> dict:
    return yaml.safe_load((CONFIG / "indicators.yaml").read_text())


def fetch_indicator(key: str, spec: dict, years: tuple[int, int]) -> pd.DataFrame:
    path = download(API.format(code=spec["code"], y0=years[0], y1=years[1]), f"wdi/{spec['code']}.json", max_age_days=14)
    payload = json.loads(path.read_text())
    if len(payload) < 2 or payload[1] is None:
        raise RuntimeError(f"WDI returned no data for {spec['code']}: {payload[0]}")
    meta, rows = payload
    if meta.get("pages", 1) > 1:
        raise RuntimeError(f"{spec['code']}: response paginated ({meta['pages']} pages); increase per_page")
    recs = [{"iso3": r["countryiso3code"], "year": int(r["date"]), "value": r["value"]}
            for r in rows if r["value"] is not None and r["countryiso3code"]]
    df = pd.DataFrame(recs)
    df["indicator"], df["unit"], df["source_id"], df["proxy"] = key, spec["unit"], "wb_wdi", False
    return df


def fetch_all(known_iso3: set[str]) -> pd.DataFrame:
    cfg = indicator_config()
    years = tuple(cfg["wdi_years"])
    frames = [fetch_indicator(k, s, years) for k, s in cfg["indicators"].items()]
    df = pd.concat(frames, ignore_index=True)
    return df[df.iso3.isin(known_iso3)]  # drops WB aggregates (WLD, EUU, …)
