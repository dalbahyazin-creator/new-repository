from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
RAW = ROOT / "data" / "raw"      # cached downloads (gitignored)
OUT = ROOT / "data" / "out"      # build outputs (gitignored; web copies at build time)
