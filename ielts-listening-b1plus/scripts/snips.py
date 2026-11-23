"""Crop each test's question pages from the tests PDF -> assets/snips/tNN_k.png + data/snips.json.

Usage: python3 scripts/snips.py <tests.pdf>
Each test runs from below its "TEST n" heading to the next TEST / PART heading. The source's running
header (school name) and footer (page number) are left out. Pages are cut at every "Questions …" heading
(and in the middle of very tall groups) so the crops can flow over the book's pages.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pdfplumber
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "snips"
TOP, BOTTOM = 58, 790                  # below the running header, above the footer
X0, X1 = 26, 569                       # content width of the source pages
DPI = 150
MAX_H = 600                            # points; taller chunks are split at a line gap


def lines_of(page):
    words = [w for w in page.extract_words() if TOP < w["top"] < BOTTOM]
    words.sort(key=lambda w: (round(w["top"]), w["x0"]))
    out = []
    for w in words:
        if out and abs(w["top"] - out[-1][0]) <= 3:
            out[-1][1].append(w["text"])
        else:
            out.append([w["top"], [w["text"]]])
    return [(t, " ".join(ws)) for t, ws in out]


def trim(im):
    g = ImageOps.invert(im.convert("L")).point(lambda v: 255 if v > 12 else 0)
    box = g.getbbox()
    if not box:
        return None
    return im.crop((0, max(0, box[1] - 6), im.width, min(im.height, box[3] + 6)))


def main(pdf_path):
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*.png"):
        f.unlink()
    with pdfplumber.open(pdf_path) as pdf:
        pages = {i: lines_of(p) for i, p in enumerate(pdf.pages, 1)}
    last = next(p for p in sorted(pages) if pages[p] and pages[p][0][1] == "Answers")      # answer pages start here
    heads = [(p, t, txt) for p in sorted(pages) if 4 <= p < last for t, txt in pages[p]
             if re.fullmatch(r"(TEST|PART)\s*\d+", txt)]
    heads.append((last, 0, "END"))
    snips = {}
    with tempfile.TemporaryDirectory() as tmp:
        for i, (p, t, txt) in enumerate(heads[:-1]):
            m = re.fullmatch(r"TEST\s*(\d+)", txt)
            if not m:
                continue
            n = int(m.group(1))
            ep, et, _ = heads[i + 1]
            bands = []
            for pg in range(p, ep + 1):
                y0 = t + 20 if pg == p else TOP
                y1 = et - 8 if pg == ep else BOTTOM
                if y1 - y0 > 15:
                    bands.append((pg, y0, y1))
            files = []
            for pg, y0, y1 in bands:
                tops = [lt for lt, _ in pages[pg] if y0 < lt < y1]
                cuts = [lt - 7 for lt, lx in pages[pg] if y0 + 10 < lt < y1 and re.match(r"Questions?\s+\d", lx)]
                edges = [y0] + cuts + [y1]
                chunks = []
                for a, b in zip(edges, edges[1:]):
                    while b - a > MAX_H:                     # split at the line gap nearest the middle
                        mid = (a + b) / 2
                        c = min((lt - 5 for lt in tops if a + 120 < lt - 5 < b - 120), key=lambda y: abs(y - mid), default=None)
                        if c is None:
                            break
                        chunks.append((a, c)); a = c
                    chunks.append((a, b))
                for a, b in chunks:
                    base = Path(tmp) / f"c{pg}_{int(a)}"
                    subprocess.run(["pdftoppm", "-png", "-r", str(DPI), "-f", str(pg), "-l", str(pg),
                                    "-x", str(int(X0 * DPI / 72)), "-y", str(int(a * DPI / 72)),
                                    "-W", str(int((X1 - X0) * DPI / 72)), "-H", str(int((b - a) * DPI / 72)),
                                    "-singlefile", pdf_path, str(base)], check=True)
                    im = trim(Image.open(str(base) + ".png").convert("RGB"))
                    if im is None or im.height < 20:
                        continue
                    name = f"t{n:02d}_{len(files) + 1}.png"
                    im.quantize(colors=64, method=Image.Quantize.MEDIANCUT).save(OUT / name, optimize=True)
                    files.append({"file": name, "w": im.width, "h": im.height})
            snips[n] = files
    (ROOT / "data" / "snips.json").write_text(json.dumps(snips, indent=1), encoding="utf-8")
    print("tests:", len(snips), "crops:", sum(len(v) for v in snips.values()),
          "size:", sum(f.stat().st_size for f in OUT.glob("*.png")) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])
