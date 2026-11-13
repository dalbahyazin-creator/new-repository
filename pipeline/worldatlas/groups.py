"""Region schemes, income groups and blocs.

Every grouping is exported as {scheme: {group_id: {name, members[]}}}. Blocs can also carry since/until
years, so a time-aware membership check works with the year slider.
"""
from __future__ import annotations

import re

import pandas as pd
import yaml

from .paths import CONFIG

INCOME_ORDER = ["Low income", "Lower middle income", "Upper middle income", "High income"]


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def region_schemes(master: pd.DataFrame) -> dict:
    u = master[master.in_default_universe]
    schemes = {}
    for scheme, col, label in [
        ("un_region", "un_region", "UN M49 region"),
        ("un_subregion", "un_subregion", "UN M49 sub-region"),
        ("wb_region", "wb_region", "World Bank region"),
    ]:
        groups = {}
        for name, g in u.dropna(subset=[col]).groupby(col):
            groups[_slug(name)] = {"name": name, "members": sorted(g.iso3)}
        schemes[scheme] = {"label": label, "groups": groups}
    # The M49 "intermediate region" splits Africa and the Americas further. Countries without one fall back to their sub-region.
    inter = u.assign(r=u.un_intermediate.fillna(u.un_subregion)).dropna(subset=["r"])
    schemes["un_intermediate"] = {"label": "UN M49 intermediate region",
                                  "groups": {_slug(n): {"name": n, "members": sorted(g.iso3)} for n, g in inter.groupby("r")}}
    return schemes


def income_groups(master: pd.DataFrame) -> dict:
    u = master[master.in_default_universe].dropna(subset=["income_group"])
    groups = {}
    for name in INCOME_ORDER:
        mem = sorted(u[u.income_group == name].iso3)
        groups[_slug(name)] = {"name": name, "members": mem}
    extra = {"ldc": ("Least developed countries (UN)", "ldc"), "lldc": ("Landlocked developing countries (UN)", "lldc"),
             "sids": ("Small island developing states (UN)", "sids")}
    for gid, (name, col) in extra.items():
        groups[gid] = {"name": name, "members": sorted(master[master[col].astype("boolean").fillna(False)].iso3)}
    return {"label": "Income & development group", "source_ids": ["wb_class", "un_m49"], "groups": groups}


def load_blocs(known_iso3: set[str]) -> dict:
    cfg = yaml.safe_load((CONFIG / "blocs.yaml").read_text())
    out = {}
    for bid, b in cfg["blocs"].items():
        mem = b["members"]
        unknown = set(mem) - known_iso3
        if unknown:
            raise ValueError(f"bloc {bid}: unknown iso3 {sorted(unknown)}")
        if len(mem) != len(set(mem)):
            raise ValueError(f"bloc {bid}: duplicate members")
        out[bid] = {
            "name": b["name"], "type": b["type"], "source": b["source"], "as_of": cfg["as_of"],
            "members": sorted(mem), "since": b.get("since", {}), "former": b.get("former", {}),
            "note": b.get("note"),
        }
    return out


def member_in_year(bloc: dict, iso3: str, year: int) -> bool:
    """True if iso3 belonged to the bloc in that year. Members with no 'since' are assumed to be members for all years."""
    if iso3 in bloc["members"]:
        return year >= bloc["since"].get(iso3, -10**9)
    f = bloc["former"].get(iso3)
    return bool(f) and year <= f["until"] and year >= f.get("since", -10**9)
