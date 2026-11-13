"""Natural Earth boundaries → TopoJSON (110m for the globe, 50m for close zoom) plus a disputed-areas overlay.

Each feature gets:
- id:       the ISO3 code where Natural Earth's mapping matches the master list, otherwise NE's own ADM0_A3 code
- iso3:     null for entities outside the master list (Somaliland, N. Cyprus, Siachen)
- name
- disputed: true for those unrecognised entities and for every feature in the breakaway/disputed layer
"""
from __future__ import annotations

import io
import json
import subprocess
import zipfile
from pathlib import Path

import shapefile

from .fetch import download
from .paths import OUT

NE = "https://naciscdn.org/naturalearth/{res}/cultural/{name}.zip"
MAPSHAPER = ["npx", "--yes", "mapshaper@0.7.101"]
# Fixes for Natural Earth codes that differ from the ISO3 codes we use
NE_FIX = {"KOS": "XKX", "SDS": "SSD", "SAH": "ESH", "PSX": "PSE"}


def _read(res: str, name: str) -> tuple[list[str], list]:
    z = zipfile.ZipFile(download(NE.format(res=res, name=name), f"ne/{name}.zip", max_age_days=365))
    base = next(n for n in z.namelist() if n.endswith(".shp"))[:-4]
    r = shapefile.Reader(shp=io.BytesIO(z.read(base + ".shp")), dbf=io.BytesIO(z.read(base + ".dbf")))
    fields = [f[0] for f in r.fields[1:]]
    return fields, list(r.iterShapeRecords())


# Entities with no ISO3 code that are disputed or unrecognised
UNRECOGNISED = {"SOL": "Somaliland", "CYN": "N. Cyprus", "KAS": "Siachen Glacier"}


def countries_geojson(res: str, known: set[str]) -> dict:
    """Two-pass ISO3 assignment.
    1. Match NE's ADM0_A3 code, after applying NE_FIX.
    2. Unmatched features take ISO_A3_EH, unless that code is already used. That stops small dependencies such as Ashmore Is. (ISO_A3_EH = AUS) from claiming a sovereign's id.
    """
    fields, srs = _read(res, f"ne_{res}_admin_0_countries")
    recs = [dict(zip(fields, sr.record)) for sr in srs]
    ids = [NE_FIX.get(r["ADM0_A3"], r["ADM0_A3"]) for r in recs]
    iso = [i if i in known else None for i in ids]
    taken = {i for i in iso if i}
    for k, r in enumerate(recs):
        eh = r.get("ISO_A3_EH")
        if iso[k] is None and eh in known and eh not in taken:
            iso[k] = eh
            taken.add(eh)
    feats, seen = [], set()
    for sr, r, i, fallback in zip(srs, recs, iso, ids):
        fid = i or fallback
        if fid in seen:
            raise ValueError(f"duplicate feature id {fid} at {res}")
        seen.add(fid)
        feats.append({"type": "Feature", "id": fid, "geometry": sr.shape.__geo_interface__,
                      "properties": {"iso3": i, "name": r["NAME"], "disputed": r["ADM0_A3"] in UNRECOGNISED}})
    return {"type": "FeatureCollection", "features": feats}


def disputed_geojson() -> dict:
    fields, srs = _read("50m", "ne_50m_admin_0_breakaway_disputed_areas")
    feats = []
    for i, sr in enumerate(srs):
        rec = dict(zip(fields, sr.record))
        feats.append({"type": "Feature", "id": f"disp{i}", "geometry": sr.shape.__geo_interface__,
                      "properties": {"name": rec.get("BRK_NAME") or rec["NAME"], "controlled_by": rec["SOVEREIGNT"],
                                     "note": rec.get("NOTE_BRK") or None}})
    return {"type": "FeatureCollection", "features": feats}


def _topo(geo: dict, dest: Path, layer: str) -> None:
    tmp = dest.with_suffix(".geo.json")
    tmp.write_text(json.dumps(geo))
    subprocess.run([*MAPSHAPER, "-i", str(tmp), "name=" + layer, "-o", str(dest), "format=topojson",
                    "quantization=100000", "id-field=id"], check=True, capture_output=True)
    tmp.unlink()


def build(known: set[str]) -> dict:
    out = OUT / "geo"
    out.mkdir(parents=True, exist_ok=True)
    report = {}
    for res in ("110m", "50m"):
        geo = countries_geojson(res, known)
        _topo(geo, out / f"countries-{res}.topo.json", "countries")
        report[res] = {"features": len(geo["features"]),
                       "unmatched": sorted(f["id"] for f in geo["features"] if f["properties"]["iso3"] is None)}
    d = disputed_geojson()
    _topo(d, out / "disputed-50m.topo.json", "disputed")
    report["disputed_areas"] = len(d["features"])
    return report
