from types import SimpleNamespace

from worldatlas import geo

FIELDS = ["ADM0_A3", "ISO_A3", "ISO_A3_EH", "NAME"]


def fake(rows):
    shape = SimpleNamespace(__geo_interface__={"type": "Point", "coordinates": [0, 0]})
    return lambda res, name: (FIELDS, [SimpleNamespace(record=r, shape=shape) for r in rows])


def test_two_pass_iso_assignment(monkeypatch):
    monkeypatch.setattr(geo, "_read", fake([
        ["ATC", "-99", "AUS", "Ashmore Is."],   # dependency would steal AUS on EH
        ["AUS", "AUS", "AUS", "Australia"],
        ["FRA", "-99", "FRA", "France"],        # NE quirk: ISO_A3 is -99 for France
        ["KOS", "-99", "-99", "Kosovo"],        # fixed via NE_FIX
        ["SOL", "-99", "-99", "Somaliland"],    # unrecognised → no iso3, disputed
    ]))
    fc = geo.countries_geojson("50m", {"AUS", "FRA", "XKX"})
    by = {f["id"]: f["properties"] for f in fc["features"]}
    assert by["AUS"]["name"] == "Australia"
    assert by["ATC"]["iso3"] is None
    assert by["FRA"]["iso3"] == "FRA" and by["XKX"]["iso3"] == "XKX"
    assert by["SOL"]["iso3"] is None and by["SOL"]["disputed"] is True
