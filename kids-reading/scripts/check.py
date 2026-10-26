"""Check unit data against SCHEMA.md before building.

Usage: python3 scripts/check.py [1|2]   (default: 1)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = sys.argv[1] if len(sys.argv) > 1 else "1"
UNIT_DIR = ROOT / "data" / ("units" if BOOK == "1" else f"units-{BOOK}")
TYPES = {"email", "blog", "story", "poster", "diary", "chat", "interview", "letter", "quiz", "article"}
COUNTS = {"tf": 5, "mcq": 4, "match": 5, "gaps": 5, "wordsearch": 8, "about_you": 3}

bad = 0
seen_types, seen_colors = {}, {}
for f in sorted(UNIT_DIR.glob("*.json")):
    u = json.loads(f.read_text(encoding="utf-8"))
    n = u["n"]

    def fail(msg):
        global bad
        bad += 1
        print(f"BAD  unit {n:>2}  {msg}")

    if len(u["before"]["words"]) != 6:
        fail(f"before.words has {len(u['before']['words'])}, expected 6")
    if any(len(x) != 3 or not all(x) for x in u["before"]["words"]):
        fail("before.words needs [English, Uzbek, emoji] for every entry")
    for key, want in COUNTS.items():
        if len(u[key]) != want:
            fail(f"{key} has {len(u[key])}, expected {want}")
    if u["text_type"] not in TYPES:
        fail(f"unknown text_type {u['text_type']!r}")
    words = len(re.findall(r"[A-Za-z][A-Za-z'’-]*", " ".join(u["text"]["paragraphs"])))
    if not 120 <= words <= 185:
        fail(f"text is {words} words, expected 120-185")

    # the 6 "before" words must each be highlighted somewhere in the text
    body = " ".join(u["text"]["paragraphs"]).lower()
    marked = {m.lower() for m in re.findall(r"\*\*(.+?)\*\*", body)}
    for en, _, _ in u["before"]["words"]:
        head = en.lower().split()[-1]
        if not any(head in m or m in en.lower() for m in marked):
            print(f"note unit {n:>2}  '{en}' is not highlighted in the text")

    for w in u["wordsearch"]:
        if not re.fullmatch(r"[A-Z]{3,8}", w):
            fail(f"wordsearch {w!r} must be A-Z, 3-8 letters")
    for q in u["mcq"]:
        if len(q["options"]) != 3 or not 0 <= q["answer"] <= 2:
            fail(f"mcq {q['q']!r} needs 3 options and an answer index 0-2")
    for s, a in u["gaps"]:
        if s.count("___") != 1:
            fail(f"gap {s!r} needs exactly one ___")
    seen_types.setdefault(u["text_type"], []).append(n)
    seen_colors.setdefault(u["color"], []).append(n)

dupes = {c: ns for c, ns in seen_colors.items() if len(ns) > 1}
if dupes:
    print("note colours used more than once:", dupes)
print(f"text types: {len(seen_types)}/10 used")
print("FAIL" if bad else f"Read Time! {BOOK}: all units match SCHEMA.md")
sys.exit(1 if bad else 0)
