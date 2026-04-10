"""Write technology_foresight_seed.json from foresight_catalog.

Run: backend\\venv\\Scripts\\python.exe scripts\\write_foresight_json.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.foresight_catalog import build_seed_document

OUT = Path(__file__).parent.parent / "data" / "technology_foresight_seed.json"


def main():
    doc = build_seed_document()
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT} ({len(doc['programmes'])} programmes)")


if __name__ == "__main__":
    main()
