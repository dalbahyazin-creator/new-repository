"""Cached downloads. Each file in data/raw has a sidecar manifest entry (url, sha256, bytes, fetched_at)."""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from .paths import RAW

MANIFEST = RAW / "manifest.json"
UA = {"User-Agent": "worldatlas-pipeline/0.1 (research; private)"}


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}


def download(url: str, name: str, max_age_days: float = 30, retries: int = 4) -> Path:
    """Download url to data/raw/<name> unless a fresh cached copy exists."""
    RAW.mkdir(parents=True, exist_ok=True)
    dest = RAW / name
    man = _manifest()
    entry = man.get(name)
    if dest.exists() and entry:
        age = (time.time() - datetime.fromisoformat(entry["fetched_at"]).timestamp()) / 86400
        if age < max_age_days:
            return dest
    last: Exception | None = None
    for i in range(retries):
        try:
            r = requests.get(url, headers=UA, timeout=120)
            r.raise_for_status()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(r.content)
            man[name] = {
                "url": url,
                "sha256": hashlib.sha256(r.content).hexdigest(),
                "bytes": len(r.content),
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True))
            return dest
        except Exception as e:  # network errors: back off and retry
            last = e
            time.sleep(2 ** i)
    if dest.exists():  # stale cache beats failure; caller sees manifest age
        return dest
    raise RuntimeError(f"download failed for {url}: {last}")


def fetched_at(name: str) -> str | None:
    return _manifest().get(name, {}).get("fetched_at")
