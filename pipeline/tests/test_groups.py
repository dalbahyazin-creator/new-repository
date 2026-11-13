import json

import pandas as pd
import pytest

from worldatlas import groups
from worldatlas.paths import OUT


def master():
    return pd.DataFrame([
        {"iso3": "FRA", "un_region": "Europe", "un_subregion": "Western Europe", "un_intermediate": None,
         "wb_region": "Europe & Central Asia", "income_group": "High income", "in_default_universe": True,
         "ldc": False, "lldc": False, "sids": False},
        {"iso3": "NER", "un_region": "Africa", "un_subregion": "Sub-Saharan Africa", "un_intermediate": "Western Africa",
         "wb_region": "Sub-Saharan Africa", "income_group": "Low income", "in_default_universe": True,
         "ldc": True, "lldc": True, "sids": False},
        {"iso3": "ABW", "un_region": "Americas", "un_subregion": "Latin America and the Caribbean", "un_intermediate": "Caribbean",
         "wb_region": "Latin America & Caribbean", "income_group": None, "in_default_universe": False,
         "ldc": False, "lldc": False, "sids": True},
    ])


def test_region_schemes_respect_universe_and_intermediate_fallback():
    s = groups.region_schemes(master())
    assert s["un_region"]["groups"]["europe"]["members"] == ["FRA"]
    assert "americas" not in s["un_region"]["groups"]           # ABW is outside the default universe
    inter = s["un_intermediate"]["groups"]
    assert inter["western-europe"]["members"] == ["FRA"]       # falls back to its sub-region
    assert inter["western-africa"]["members"] == ["NER"]


def test_income_groups_ordered_and_dev_flags():
    g = groups.income_groups(master())["groups"]
    assert list(g)[:4] == ["low-income", "lower-middle-income", "upper-middle-income", "high-income"]
    assert g["ldc"]["members"] == ["NER"] and g["sids"]["members"] == ["ABW"]


def test_member_in_year_handles_since_and_former():
    bloc = {"members": ["BGR", "DEU"], "since": {"BGR": 2026}, "former": {"GBR": {"since": 1973, "until": 2020}}}
    assert groups.member_in_year(bloc, "DEU", 1990)
    assert not groups.member_in_year(bloc, "BGR", 2025) and groups.member_in_year(bloc, "BGR", 2026)
    assert groups.member_in_year(bloc, "GBR", 2019) and not groups.member_in_year(bloc, "GBR", 2021)
    assert not groups.member_in_year(bloc, "GBR", 1960)
    assert not groups.member_in_year(bloc, "USA", 2020)


def test_unknown_bloc_member_rejected(tmp_path, monkeypatch):
    (tmp_path / "blocs.yaml").write_text("as_of: x\nblocs:\n  X: {name: X, type: t, source: s, members: [FRA, ZZZ]}\n")
    monkeypatch.setattr(groups, "CONFIG", tmp_path)
    with pytest.raises(ValueError, match="ZZZ"):
        groups.load_blocs({"FRA"})


@pytest.mark.skipif(not (OUT / "countries.json").exists(), reason="run `make data` first")
def test_real_bloc_file_is_consistent():
    known = {c["iso3"] for c in json.loads((OUT / "countries.json").read_text())}
    b = groups.load_blocs(known)
    assert len(b["EU"]["members"]) == 27 and len(b["NATO"]["members"]) == 32
    assert len(b["AU"]["members"]) == 55 and len(b["OECD"]["members"]) == 38
    assert set(b["EA"]["members"]) <= set(b["EU"]["members"])
    assert set(b["OPEC"]["members"]) <= set(b["OPEC_PLUS"]["members"])
    assert set(b["G7"]["members"]) <= set(b["G20"]["members"])
