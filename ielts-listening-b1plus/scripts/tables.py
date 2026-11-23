"""Read the ruled tables (2+ columns) of the tests PDF -> data/tables.json, so build.py can draw them cell for cell.

Usage: python3 scripts/tables.py <tests.pdf>
"""
import json
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent


def main(pdf_path):
    out = []
    with pdfplumber.open(pdf_path) as pdf:
        for pn, page in enumerate(pdf.pages, 1):
            for t in page.find_tables():
                rows = [[(c or "").strip() if c is not None else None for c in r] for r in t.extract()]
                if pn <= 3 or max(len(r) for r in rows) < 2 or len(rows) < 2:   # skip the cover, contents and scoreboard pages
                    continue
                out.append({"page": pn, "top": round(t.bbox[1]), "rows": rows})
    (ROOT / "data" / "tables.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("tables:", len(out))


if __name__ == "__main__":
    main(sys.argv[1])
