"""Read layout data from the tests PDF for build.py.

Usage: python3 scripts/tables.py <tests.pdf>
-> data/tables.json  ruled tables with 2+ columns, cell for cell
-> data/lines.json   every text line of pages 4+ with word positions and fonts, plus horizontal rules,
                     so forms and notes can be rebuilt with their real columns
"""
import json
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
TOP, BOTTOM = 60, 790                       # skip the running header and the page number


def flags(font):
    f = font.split("+")[-1].lower()
    return ("b" if "bold" in f else "") + ("i" if "italic" in f or "oblique" in f else "") + ("h" if "boli" in f else "")


def main(pdf_path):
    tables, pages = [], []
    with pdfplumber.open(pdf_path) as pdf:
        for pn, page in enumerate(pdf.pages, 1):
            if pn <= 3:                         # cover, contents and scoreboard
                continue
            for t in page.find_tables():
                rows = [[(c or "").strip() if c is not None else None for c in r] for r in t.extract()]
                if max(len(r) for r in rows) >= 2 and len(rows) >= 2:
                    tables.append({"page": pn, "top": round(t.bbox[1]), "rows": rows})
            words = [w for w in page.extract_words(extra_attrs=["fontname"]) if TOP < w["top"] < BOTTOM]
            words.sort(key=lambda w: (round(w["top"]), w["x0"]))
            lines = []
            for w in words:
                if lines and abs(w["top"] - lines[-1]["top"]) <= 3:
                    lines[-1]["w"].append([round(w["x0"], 1), round(w["x1"], 1), w["text"], flags(w["fontname"])])
                else:
                    lines.append({"top": round(w["top"], 1), "w": [[round(w["x0"], 1), round(w["x1"], 1), w["text"], flags(w["fontname"])]]})
            for ln in lines:
                ln["w"].sort()
            rules = sorted({round(e["top"]) for e in page.horizontal_edges if e["x1"] - e["x0"] > 150 and TOP < e["top"] < BOTTOM})
            pages.append({"page": pn, "lines": lines, "rules": rules})
    (ROOT / "data" / "tables.json").write_text(json.dumps(tables, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "data" / "lines.json").write_text(json.dumps(pages, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("tables:", len(tables), "pages:", len(pages))


if __name__ == "__main__":
    main(sys.argv[1])
