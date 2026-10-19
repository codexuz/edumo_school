"""Check every sample answer against the word band its task requires.

Usage: python3 scripts/check.py        (exit 1 if any sample is outside its band)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANDS = {"task11": (45, 60, "about 50"), "task12": (120, 150, "120-150"),
         "part2": (180, 200, "180-200")}


def count(paras):
    text = " ".join(paras)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", text))


bad = 0
for f in sorted((ROOT / "data").glob("exercise-*.json")):
    ex = json.loads(f.read_text(encoding="utf-8"))
    for key, (lo, hi, label) in BANDS.items():
        n = count(ex["samples"][key])
        ok = lo <= n <= hi
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'}  Exercise {ex['n']:>2}  {key:<7} {n:>4} words  (target {label})")
    for key in ("vocab_task1", "vocab_part2"):
        items = ex[key]
        if len(items) != 20:
            bad += 1
            print(f"BAD  Exercise {ex['n']:>2}  {key} has {len(items)} items, expected 20")
        if any(len(i) != 2 or not all(i) for i in items):
            bad += 1
            print(f"BAD  Exercise {ex['n']:>2}  {key} has an incomplete pair")
print("FAIL" if bad else "All samples are inside their word bands.")
sys.exit(1 if bad else 0)
