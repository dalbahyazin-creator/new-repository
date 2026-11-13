"""Country master list. ISO3 is the key everywhere.

The universe is the union of:
- UN M49 countries and areas (country-codes dataset)
- World Bank economies (adds Kosovo, XKX)

Each country carries flags for the default dashboard universe.
"""
from __future__ import annotations

import json

import pandas as pd

from .fetch import download

M49_URL = "https://raw.githubusercontent.com/datasets/country-codes/main/data/country-codes.csv"
WB_URL = "https://api.worldbank.org/v2/country?format=json&per_page=400"

# Rows the M49 file lacks. Each is documented on the methodology page.
EXTRA = [
    {"iso3": "XKX", "iso2": "XK", "m49": None, "name": "Kosovo", "un_region": "Europe",
     "un_subregion": "Southern Europe", "un_intermediate": None, "continent": "EU", "is_independent": True,
     "note": "Not a UN member; included as a World Bank economy. Status disputed."},
    {"iso3": "CHI", "iso2": None, "m49": "830", "name": "Channel Islands", "un_region": "Europe",
     "un_subregion": "Northern Europe", "un_intermediate": "Channel Islands", "continent": "EU", "is_independent": False,
     "note": "World Bank reports Jersey and Guernsey (JEY, GGY) together under the code CHI."},
]
# Sovereignty notes that tooltips and profiles show next to the name.
STATUS_NOTES = {
    "TWN": "Not a UN member; M49 lists it as part of China. Shown separately because data is reported separately.",
    "PSE": "UN non-member observer state.",
    "ESH": "Non-self-governing territory; sovereignty disputed.",
    "XKX": "Not a UN member; recognised by some states.",
    "VAT": "UN non-member observer state.",
}


def _m49() -> pd.DataFrame:
    df = pd.read_csv(download(M49_URL, "m49/country-codes.csv"), dtype=str, keep_default_na=False)
    df = df[df["ISO3166-1-Alpha-3"].str.len() == 3]
    out = pd.DataFrame({
        "iso3": df["ISO3166-1-Alpha-3"],
        "iso2": df["ISO3166-1-Alpha-2"],
        "m49": df["M49"].replace("", None),
        "name": df["CLDR display name"].where(df["CLDR display name"] != "", df["UNTERM English Short"]),
        "official_name": df["official_name_en"],
        "un_region": df["Region Name"].replace("", None),
        "un_subregion": df["Sub-region Name"].replace("", None),
        "un_intermediate": df["Intermediate Region Name"].replace("", None),
        "continent": df["Continent"].replace("", None),
        "is_independent": df["is_independent"].eq("Yes"),
        "sids": df["Small Island Developing States (SIDS)"].eq("x"),
        "lldc": df["Land Locked Developing Countries (LLDC)"].eq("x"),
        "ldc": df["Least Developed Countries (LDC)"].eq("x"),
        "currency": df["ISO4217-currency_alphabetic_code"].replace("", None),
        "capital": df["Capital"].replace("", None),
    })
    return out


def _wb() -> pd.DataFrame:
    meta, rows = json.loads(download(WB_URL, "wb/countries.json").read_text())
    recs = []
    for r in rows:
        if r["region"]["value"] == "Aggregates":
            continue
        recs.append({
            "iso3": r["id"],
            "wb_name": r["name"],
            "wb_region": r["region"]["value"].strip(),
            "income_group": r["incomeLevel"]["value"].strip() or None,
            "income_code": r["incomeLevel"]["id"] or None,
            "lending": r["lendingType"]["value"].strip() or None,
            "wb_capital": r["capitalCity"] or None,
            "cap_lon": float(r["longitude"]) if r["longitude"] else None,
            "cap_lat": float(r["latitude"]) if r["latitude"] else None,
        })
    return pd.DataFrame(recs)


def build_master() -> pd.DataFrame:
    m49 = pd.concat([_m49(), pd.DataFrame(EXTRA)], ignore_index=True)
    wb = _wb()
    df = m49.merge(wb, on="iso3", how="outer", indicator=True)
    unmatched = df[df._merge == "right_only"].iso3.tolist()
    if unmatched:
        raise ValueError(f"World Bank economies missing from M49 master: {unmatched}")
    df = df.drop(columns="_merge")
    df["wb_economy"] = df["wb_region"].notna()
    df["income_group"] = df["income_group"].replace("Not classified", None)
    df["capital"] = df["capital"].fillna(df["wb_capital"])
    df["status_note"] = df["iso3"].map(STATUS_NOTES).fillna(df.get("note"))
    # Default universe: independent states, World Bank economies, and a few
    # entities with separately reported data. Other dependencies stay in the
    # master list but are hidden by default.
    df["in_default_universe"] = df["is_independent"].fillna(False) | df["wb_economy"] | df["iso3"].isin(["TWN", "PSE", "ESH"])
    cols = ["iso3", "iso2", "m49", "name", "official_name", "status_note", "un_region", "un_subregion", "un_intermediate",
            "continent", "wb_region", "income_group", "income_code", "lending", "is_independent", "wb_economy",
            "in_default_universe", "sids", "lldc", "ldc", "currency", "capital", "cap_lat", "cap_lon"]
    df = df[cols].sort_values("iso3").reset_index(drop=True)
    assert df.iso3.is_unique, "duplicate iso3 in master"
    return df
