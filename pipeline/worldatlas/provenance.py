"""The observation schema every indicator must follow, plus validation against the source registry."""
from __future__ import annotations

from functools import lru_cache

import pandas as pd
import yaml

from .paths import CONFIG

OBS_COLUMNS = ["iso3", "indicator", "year", "value", "unit", "source_id", "proxy"]


@lru_cache
def sources() -> dict:
    return yaml.safe_load((CONFIG / "sources.yaml").read_text())["sources"]


class ProvenanceError(ValueError):
    pass


def validate_observations(df: pd.DataFrame, known_iso3: set[str]) -> pd.DataFrame:
    """Raise if any row lacks provenance or references an unknown country/source. Returns df in canonical order."""
    missing = [c for c in OBS_COLUMNS if c not in df.columns]
    if missing:
        raise ProvenanceError(f"missing columns: {missing}")
    if df[OBS_COLUMNS].drop(columns="value").isna().any().any():
        raise ProvenanceError("null provenance fields")
    bad_src = set(df.source_id) - set(sources())
    if bad_src:
        raise ProvenanceError(f"unregistered source ids: {sorted(bad_src)}")
    bad_iso = set(df.iso3) - known_iso3
    if bad_iso:
        raise ProvenanceError(f"unknown iso3 codes: {sorted(bad_iso)[:10]}")
    if df.duplicated(["iso3", "indicator", "year", "source_id"]).any():
        raise ProvenanceError("duplicate (iso3, indicator, year, source_id) rows")
    out = df[OBS_COLUMNS].copy()
    out["year"] = out["year"].astype(int)
    out["proxy"] = out["proxy"].astype(bool)
    return out.sort_values(["indicator", "iso3", "year"]).reset_index(drop=True)
