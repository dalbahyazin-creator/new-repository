import argparse
import json

from .build import run

p = argparse.ArgumentParser(prog="worldatlas")
p.add_argument("command", choices=["build"])
p.add_argument("--skip-geo", action="store_true", help="skip boundary processing (needs npx/mapshaper)")
a = p.parse_args()
print(json.dumps(run(skip_geo=a.skip_geo), indent=1))
