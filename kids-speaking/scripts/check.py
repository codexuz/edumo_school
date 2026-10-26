"""Check unit data against SCHEMA.md, including that the questions match the source.

Usage: python3 scripts/check.py [1|2]   (default: 1)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = sys.argv[1] if len(sys.argv) > 1 else "1"
UNIT_DIR = ROOT / "data" / ("units" if BOOK == "1" else f"units-{BOOK}")
SRC = ROOT / "src" / f"teen2teen{BOOK}.txt"
GAME_ITEMS = {"find": 8, "dice": 6, "board": 12, "spinner": 8, "bingo": 9, "guess": 6}


def source_questions():
    """unit number -> the questions as printed in the source document."""
    out, cur = {}, None
    for line in SRC.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        m = re.match(r"^Unit (\d+):", line)
        if m:
            cur = int(m.group(1))
            out[cur] = []
        elif cur and re.match(r"^\d+\.\s", line):
            out[cur].append(re.sub(r"^\d+\.\s*", "", line))
    return out


src = source_questions()
bad = 0
games = {}
for f in sorted(UNIT_DIR.glob("*.json")):
    u = json.loads(f.read_text(encoding="utf-8"))
    n = u["n"]

    def fail(msg):
        global bad
        bad += 1
        print(f"BAD  unit {n:>2}  {msg}")

    for key, want in (("words", 12), ("questions", 10), ("starters", 10), ("samples", 3), ("cando", 3)):
        if len(u[key]) != want:
            fail(f"{key} has {len(u[key])}, expected {want}")
    if any(len(w) != 3 or not all(w) for w in u["words"]):
        fail("words need [English, Uzbek, emoji] for every card")
    emojis = [w[2] for w in u["words"]]
    dupes = sorted({x for x in emojis if emojis.count(x) > 1})
    if dupes:
        fail(f"word cards share a picture: {' '.join(dupes)}")
    if u["questions"] != src.get(n):
        fail("questions do not match src/teen2teen%s.txt" % BOOK)
    if any(len(s) != 2 or not all(s) for s in u["samples"]):
        fail("samples need [question, answer] pairs")
    for q, _ in u["samples"]:
        if q not in u["questions"]:
            fail(f"sample question is not one of the unit's ten: {q!r}")
    g = u["game"]
    if g["type"] not in GAME_ITEMS:
        fail(f"unknown game type {g['type']!r}")
    elif len(g["items"]) != GAME_ITEMS[g["type"]]:
        fail(f"{g['type']} game has {len(g['items'])} items, expected {GAME_ITEMS[g['type']]}")
    rows = u["grammar_box"]["rows"]
    if not 4 <= len(rows) <= 6 or any(len(r) != 3 for r in rows):
        fail(f"grammar_box needs 4-6 rows of 3 cells, got {len(rows)}")
    if not 3 <= len(u["mini_talk"]["plan"]) <= 4:
        fail(f"mini_talk.plan has {len(u['mini_talk']['plan'])} steps, expected 3-4")
    words = len(re.findall(r"[A-Za-z][A-Za-z'’-]*", u["mini_talk"]["model"]))
    if not 40 <= words <= 85:
        fail(f"mini_talk.model is {words} words, expected 40-85")
    games.setdefault(g["type"], []).append(n)

print("games used:", {k: v for k, v in sorted(games.items())})
print("FAIL" if bad else f"Talk Time! {BOOK}: all units match SCHEMA.md")
sys.exit(1 if bad else 0)
