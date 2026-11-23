"""Extract the 80 listening tests, answers and audioscripts from the source PDFs -> data/tests.json + assets/figures/.

Usage: python3 scripts/extract.py <tests.pdf> <scripts.pdf>
Questions keep their original line layout (parsed into blocks by build.py); pictures (maps, plans, diagrams) are cropped
from the page at 200 dpi; source headers, footers and page numbers are dropped.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "assets" / "figures"
PT = 1 / 1.5                       # pdftohtml -xml coordinates are at 1.5x
EXTRA = {47: [(266, 376)]}         # pie charts drawn as several small images
PAGE_H, FOOT = 841.92, 790


def run(*a):
    return subprocess.run(a, capture_output=True, text=True, check=True).stdout


def figures(pdf, xml):
    s = Path(xml).read_text(encoding="utf-8", errors="ignore")
    out = {}
    for n, body in re.findall(r'<page number="(\d+)".*?>(.*?)</page>', s, re.S):
        for t, l, w, h in re.findall(r'<image top="(-?\d+)" left="(-?\d+)" width="(\d+)" height="(\d+)"', body):
            t, h, w = int(t) * PT, int(h) * PT, int(w) * PT
            if w > 60 * PT * 1.5 and h > 30 and int(n) != 94:
                out.setdefault(int(n), []).append((t - 4, t + h + 4))
    for p, v in EXTRA.items():
        out[p] = v
    return out


def page_lines(pdf, p, segs):
    """Layout text of page p, skipping the figure bands in segs; a [[FIG ...]] marker replaces each band."""
    lines, y = [], 60.0                      # skip the running header
    for k, (a, b) in enumerate(sorted(segs) + [(FOOT, FOOT)]):
        if a > y:
            txt = run("pdftotext", "-layout", "-f", str(p), "-l", str(p), "-x", "0", "-y", str(int(y)), "-W", "596",
                      "-H", str(int(a - y)), pdf, "-")
            lines += txt.rstrip("\n\f").split("\n")
        if a < FOOT:
            name = f"p{p:03d}_{k + 1}.png"
            r = 200 / 72
            run("pdftoppm", "-png", "-gray", "-r", "200", "-f", str(p), "-l", str(p), "-x", str(int(40 * r)), "-y", str(int(a * r)),
                "-W", str(int(516 * r)), "-H", str(int((b - a) * r)), "-singlefile", pdf, str(FIG / name[:-4]))
            lines.append(f"[[FIG {name}]]")
        y = max(y, b)
    return lines


FIX = {67: [("37 king 39 entertainment", "37 king 38 entertainment")]}   # typo in the source key


def parse_key(n, text):
    """Walk through the key text in question order -> [{q, a, note}]."""
    first = {1: 1, 2: 11, 3: 21, 4: 31}[(n - 1) // 20 + 1]
    for a, b in FIX.get(n, []):
        text = text.replace(a, b)
    text = " " + re.sub(r"\s+", " ", text) + " "
    out, e, pos = [], first, 0
    order = r"(?:\s*IN (?:EITHER|ETHER|ANY) ORDER;?(?:\s*BOTH REQUIRED FOR ONE MARK)?)?"
    while e < first + 10:
        pats = [rf" {e}\s*(?:&|/|and|-|–)\s*(\d{{1,2}})({order}) ", rf" {e}({order}) "]
        m = None
        for k, pat in enumerate(pats):
            m = re.compile(pat).search(text, pos)
            if m and (k == 1 or int(m.group(1)) > e):
                break
            m = None
        if not m:
            raise ValueError(f"test {n}: question {e} not found in key: {text[pos:pos + 80]}")
        last = int(m.group(1)) if m.lastindex == 2 and m.group(1).isdigit() else e
        note = (m.group(m.lastindex) or "").strip().rstrip(";").lower().replace("ether", "either")
        q = f"{e}–{last}" if last > e else str(e)
        out.append({"q": q, "start": m.start(), "body": m.end(), "note": note})
        pos, e = m.end(), last + 1
    for i, o in enumerate(out):
        end = out[i + 1]["start"] if i + 1 < len(out) else len(text)
        o["a"] = text[o.pop("body"):end].strip()
        o.pop("start")
    return out


def answers(pdf, first, last):
    """Two-column answer pages -> {test: [{q, a, note}]}."""
    raw, cur = {}, None
    for p in range(first, last + 1):
        x = run("pdftotext", "-bbox", "-f", str(p), "-l", str(p), pdf, "-")
        words = [(float(a), float(b), w) for a, b, w in re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)"[^>]*>([^<]*)</word>', x)]
        words = [w for w in words if 60 < w[1] < FOOT and "Proper" not in w[2]]
        heads = sorted({round(a) for a, b, w in words if w == "TEST"})
        mid = heads[-1] - 5 if len(heads) > 1 else 300
        for col in (0, 1):
            rows = {}
            for a, b, w in (w for w in words if (w[0] < mid) == (col == 0)):
                key = next((k for k in rows if abs(k - b) < 3), b)
                rows.setdefault(key, []).append((a, w))
            for b in sorted(rows):
                line = html.unescape(" ".join(w for a, w in sorted(rows[b]))).strip()
                if line == "Answers" or re.fullmatch(r"\d{3}", line):
                    continue
                m = re.fullmatch(r"TEST (\d+)", line)
                if m:
                    cur = int(m.group(1)); raw[cur] = []
                elif cur:
                    raw[cur].append(line)
    return {n: parse_key(n, " ".join(v)) for n, v in raw.items()}


def scripts(pdf):
    txt = run("pdftotext", pdf, "-")
    parts = re.split(r"(?m)^\s*Test (\d+)\.?\s*$", txt)
    out = {}
    for i in range(1, len(parts), 2):
        body = re.sub(r"\s*\n\s*", " ", parts[i + 1].replace("\f", "\n")).strip()
        out[int(parts[i])] = body
    return out


def main(tests_pdf, scripts_pdf):
    FIG.mkdir(parents=True, exist_ok=True)
    xml = ROOT / "data" / "_figs"
    subprocess.run(["pdftohtml", "-xml", "-q", "-f", "1", "-l", "128", tests_pdf, str(xml)], capture_output=True)
    figs = figures(tests_pdf, str(xml) + ".xml")
    for f in ROOT.glob("data/_figs*"):
        f.unlink()
    all_lines = []
    for p in range(4, 129):
        all_lines += page_lines(tests_pdf, p, figs.get(p, []))
    tests, cur, part = {}, None, 1
    for ln in all_lines:
        m = re.fullmatch(r"\s*PART (\d)\s*", ln)
        if m:
            part = int(m.group(1)); continue
        m = re.fullmatch(r"\s*TEST (\d+)\s*", ln)
        if m:
            cur = int(m.group(1)); tests[cur] = {"n": cur, "part": part, "lines": []}
            continue
        if cur and not re.fullmatch(r"\s*\d{1,3}\s*", ln):
            tests[cur]["lines"].append(ln.rstrip())
    keys = answers(tests_pdf, 129, 148)
    scr = scripts(scripts_pdf)
    for n, t in tests.items():
        while t["lines"] and not t["lines"][-1].strip():
            t["lines"].pop()
        t["answers"] = keys.get(n, [])
        t["script"] = scr.get(n, "")
    data = {"tests": [tests[k] for k in sorted(tests)]}
    (ROOT / "data" / "tests.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(tests), "tests;", sum(1 for t in tests.values() if t["answers"]), "with answers;",
          sum(1 for t in tests.values() if t["script"]), "scripts;", len(list(FIG.glob("*.png"))), "figures")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
