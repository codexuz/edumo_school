"""Check the book's data before it is built.

  * every model answer sits inside the word band its task asks for
  * every word list holds exactly 20 complete English/Russian/Uzbek triples
  * every exercise has a sentence-transformation task, and it builds

Usage: python3 scripts/check.py   (exit 1 if anything fails)
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import practice  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BANDS = {"task11": (45, 60, "about 50"), "task12": (120, 150, "120-150"),
         "part2": (180, 200, "180-200")}


def count(paras):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", " ".join(paras)))


bad = 0
for f in sorted((ROOT / "data").glob("exercise-*.json")):
    ex = json.loads(f.read_text(encoding="utf-8"))
    n = ex["n"]
    for key, (lo, hi, label) in BANDS.items():
        c = count(ex["samples"][key])
        ok = lo <= c <= hi
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'}  Exercise {n:>2}  {key:<7} {c:>4} words  (target {label})")
    for key in ("vocab_task1", "vocab_part2"):
        items = ex[key]
        if len(items) != 20:
            bad += 1
            print(f"BAD  Exercise {n:>2}  {key} has {len(items)} items, expected 20")
        if any(len(i) != 3 or not all(i) for i in items):
            bad += 1
            print(f"BAD  Exercise {n:>2}  {key} has an incomplete English/Russian/Uzbek triple")
    try:
        pr = practice.build(ex)
    except Exception as exc:                                   # noqa: BLE001
        bad += 1
        print(f"BAD  Exercise {n:>2}  practice build failed: {exc}")
        continue
    if len(pr["gapfill"]) < 6:
        bad += 1
        print(f"BAD  Exercise {n:>2}  only {len(pr['gapfill'])} gap-fill items could be derived")
    if len(pr["rewrite"]["items"]) < 5:
        bad += 1
        print(f"BAD  Exercise {n:>2}  sentence task has {len(pr['rewrite']['items'])} items")

print("FAIL" if bad else "All model answers, word lists and practice tasks check out.")
sys.exit(1 if bad else 0)
