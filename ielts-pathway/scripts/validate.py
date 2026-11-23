"""Check IELTS Pathway unit files for one level.

Usage: python3 scripts/validate.py a1
Checks: unique IDs, answers for every closed item, valid MCQ/match/choose answers, gaps, form answers,
audio blocks with scripts, listening answers that appear in the script, Uzbek meanings for vocabulary,
word-bank answers, reading length for the level, and the exam-practice score total.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READ_RANGE = {"A1": (120, 250), "A2": (250, 400), "B1": (450, 700), "B2": (750, 900)}
CLOSED = {"short", "gap", "choose", "mcq", "tf", "match", "order", "correct", "form"}
NUM_WORDS = {"19": "nineteen", "23": "twenty-three", "20": "twenty", "8": "eight", "16": "sixteenth", "16th": "sixteenth"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main(level):
    files = sorted((ROOT / level / "data").glob("*-unit-*.json"))
    errors, warns, ids = [], [], {}
    for f in files:
        u = json.loads(f.read_text(encoding="utf-8"))
        tag = f.name
        scripts = {s["id"]: s for s in u.get("scripts", [])}
        used_audio = set()
        exam_total, score_total = 0, None
        for sec in u["sections"]:
            for b in sec["blocks"]:
                t = b["type"]
                if t == "audio":
                    used_audio.add(b["id"])
                    if b["id"] not in scripts:
                        errors.append(f"{tag}: audio {b['id']} has no script")
                if t == "vocab":
                    for v in b["items"]:
                        if not v.get("uz") or not v.get("ex"):
                            errors.append(f"{tag}: vocab '{v.get('word')}' needs uz and ex")
                if t == "passage" and sec["kind"] == "reading" and u["book"] == "SB":
                    w = sum(len(p["text"].split()) for p in b["paras"])
                    lo, hi = READ_RANGE[u["level"]]
                    if not lo <= w <= hi:
                        warns.append(f"{tag}: reading '{b['title']}' has {w} words (level range {lo}-{hi})")
                if t == "score":
                    score_total = b["total"]
                if t != "ex":
                    continue
                i, k = b["id"], b["kind"]
                if i in ids:
                    errors.append(f"{tag}: duplicate id {i} (also in {ids[i]})")
                ids[i] = tag
                if not i.startswith(f"{u['level']}_U{u['unit']:02d}_{u['book']}_"):
                    errors.append(f"{tag}: id {i} does not match level/unit/book")
                if b.get("audio") and b["audio"] not in scripts:
                    errors.append(f"{tag}: {i} uses audio {b['audio']} with no script")
                its = b.get("items", [])
                if k in CLOSED and k not in ("form", "match"):
                    for n, it in enumerate(its, 1):
                        if not str(it.get("a", "")).strip():
                            errors.append(f"{tag}: {i} item {n} has no answer")
                if k == "gap":
                    for n, it in enumerate(its, 1):
                        if it["q"].count("______") != 1:
                            errors.append(f"{tag}: {i} item {n} needs exactly one ______")
                    if b.get("bank"):
                        for n, it in enumerate(its, 1):
                            if it["a"] not in b["bank"]:
                                errors.append(f"{tag}: {i} item {n} answer '{it['a']}' not in the word bank")
                if k == "choose":
                    for n, it in enumerate(its, 1):
                        opts = [o.strip() for m in re.findall(r"\(([^()]*/[^()]*)\)", it["q"]) for o in m.split("/")]
                        if it["a"] not in opts:
                            errors.append(f"{tag}: {i} item {n} answer '{it['a']}' is not an option")
                if k == "mcq":
                    for n, it in enumerate(its, 1):
                        if it["a"] not in "ABCDEFGH"[:len(it["options"])]:
                            errors.append(f"{tag}: {i} item {n} answer {it['a']} out of range")
                    letters = [it["a"] for it in its]
                    if len(its) >= 3 and len(set(letters)) == 1:
                        warns.append(f"{tag}: {i} all answers are {letters[0]}")
                if k == "tf":
                    for n, it in enumerate(its, 1):
                        if it["a"] not in b.get("labels", ["TRUE", "FALSE"]):
                            errors.append(f"{tag}: {i} item {n} answer {it['a']} is not a label")
                if k == "match":
                    a = b["a"]
                    if len(a) != len(b["left"]) or len(set(a)) != len(a) or any(x not in "ABCDEFGH"[:len(b["right"])] for x in a):
                        errors.append(f"{tag}: {i} match answers invalid: {a}")
                if k == "form":
                    gaps = re.findall(r"\((\d{1,2})\)", " ".join(v for _, v in b["rows"]))
                    if sorted(gaps, key=int) != sorted(b["answers"], key=int):
                        errors.append(f"{tag}: {i} form gaps {gaps} vs answers {list(b['answers'])}")
                if b.get("audio") and k in ("form", "short") and b["audio"] in scripts:
                    spoken = norm(" ".join(x for _, x in scripts[b["audio"]]["lines"]))
                    answers = b["answers"].values() if k == "form" else [it["a"] for it in its]
                    for a in answers:
                        alts = [x.strip() for x in re.split(r"/", re.sub(r"\(s\)|\(.*?\)", "", a))]
                        if not any(norm(x) in spoken or norm(NUM_WORDS.get(x.lower(), x)) in spoken for x in alts if x):
                            if not re.fullmatch(r"[\d ]+", a.strip()):
                                warns.append(f"{tag}: {i} answer '{a}' not found word-for-word in {b['audio']}")
                if sec["kind"] == "exam":
                    exam_total += len(b["answers"]) if k == "form" else len(b["a"]) if k == "match" else len(its) if k in CLOSED else 0
        unused = set(scripts) - used_audio
        if unused:
            warns.append(f"{tag}: scripts without an audio block: {sorted(unused)}")
        if score_total is not None and score_total != exam_total:
            errors.append(f"{tag}: exam score box says {score_total}, exam items = {exam_total}")
        print(f"{tag}: {sum(1 for x in ids.values() if x == tag)} exercises, {len(scripts)} scripts")
    for w in warns:
        print("WARN ", w)
    for x in errors:
        print("ERROR", x)
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "a1"))
