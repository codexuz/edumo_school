"""Check every data/units/NN.json against SCHEMA.md. Usage: python3 scripts/check.py"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"]
LIMIT = {"ONE WORD ONLY": 1, "NO MORE THAN TWO WORDS": 2, "NO MORE THAN THREE WORDS": 3,
         "NO MORE THAN TWO WORDS AND/OR A NUMBER": 2, "NO MORE THAN THREE WORDS AND/OR A NUMBER": 3, "ONE WORD AND/OR A NUMBER": 1}


def alts(a):
    return [x.strip() for x in re.sub(r"\(.*?\)", "", a).split("/") if x.strip()]


def in_text(a, text):
    return re.search(r"(?<![\w-])" + re.escape(a.lower()) + r"(?![\w-])", text.lower()) is not None


def main():
    allw, bad = Counter(), 0
    for f in sorted((ROOT / "data" / "units").glob("*.json")):
        u = json.loads(f.read_text(encoding="utf-8"))
        P = " ".join(u["passage"])
        err = []
        wc = len(P.split())
        if len(u["vocab"]) != 15 or len(u["passage"]) != 7 or len(u["vocab_match"]) != 6 or len(u["gapfill"]) != 6:
            err.append("counts")
        if not 600 <= wc <= 790:
            err.append(f"{wc} words")
        vw = [v["word"] for v in u["vocab"]]
        for v in u["vocab"]:
            allw[v["word"]] += 1
            w = v["word"].lower()
            if w[:max(4, len(w) - 2)] not in P.lower():
                err.append(f"vocab not in passage: {v['word']}")
            if not v.get("uz") or not v.get("ex"):
                err.append(f"vocab fields: {v['word']}")
        for m in u["vocab_match"]:
            if m["word"] not in vw:
                err.append(f"match word {m['word']}")
        for g in u["gapfill"]:
            if g["a"] not in vw or g["s"].count("______") != 1:
                err.append(f"gapfill {g['a']}")
        total, types = 0, []
        for g in u["groups"]:
            t = g["type"]
            types.append(t)
            if t == "headings":
                n = len(g["paras"])
                if len(g["a"]) != n or len(set(g["a"])) != n or any(a not in ROMAN[:len(g["options"])] for a in g["a"]) or len(g["options"]) < n + 2:
                    err.append(f"headings {g['a']}")
            elif t in ("tfng", "ynng"):
                n = len(g["items"])
                labels = {"tfng": {"TRUE", "FALSE", "NOT GIVEN"}, "ynng": {"YES", "NO", "NOT GIVEN"}}[t]
                got = {q["a"] for q in g["items"]}
                if got != labels:
                    err.append(f"{t} labels {got}")
            elif t == "mcq":
                n = len(g["items"])
                for q in g["items"]:
                    if len(q["options"]) != 4 or q["a"] not in "ABCD":
                        err.append(f"mcq {q['q'][:30]}")
                if len({q["a"] for q in g["items"]}) < min(n, 3):
                    err.append("mcq answers too similar")
            elif t == "matching_info":
                n = len(g["items"])
                if any(q["a"] not in "ABCDEFG" for q in g["items"]):
                    err.append("matching_info letter")
            elif t in ("matching_features", "sentence_endings"):
                n = len(g["items"])
                opts = g["features"] if t == "matching_features" else g["endings"]
                if any(q["a"] not in "ABCDEFGHIJ"[:len(opts)] for q in g["items"]):
                    err.append(f"{t} letter")
                if t == "sentence_endings" and (len({q["a"] for q in g["items"]}) != n or len(opts) < n + 2):
                    err.append("endings")
            elif t in ("summary", "notes"):
                n = len(g["a"])
                gaps = (g["text"] if t == "summary" else " ".join(g["lines"])).count("______")
                if gaps != n:
                    err.append(f"{t}: {gaps} gaps / {n} answers")
                if g.get("box"):
                    if any(a not in "ABCDEFGHIJ"[:len(g["box"])] for a in g["a"]) or len(set(g["a"])) != n or len(g["box"]) < n + 3:
                        err.append("summary box")
                else:
                    for a in g["a"]:
                        if not any(in_text(x, P) for x in alts(a)):
                            err.append(f"{t} answer not in passage: {a}")
                        if any(len(x.split()) > LIMIT[g["limit"]] for x in alts(a)):
                            err.append(f"{t} answer too long: {a}")
            elif t in ("completion", "short"):
                n = len(g["items"])
                for q in g["items"]:
                    if t == "completion" and q["q"].count("______") != 1:
                        err.append(f"completion gap: {q['q'][:30]}")
                    if not any(in_text(x, P) for x in alts(q["a"])):
                        err.append(f"{t} answer not in passage: {q['a']}")
                    if any(len(x.split()) > LIMIT[g["limit"]] for x in alts(q["a"])):
                        err.append(f"{t} answer too long: {q['a']}")
            else:
                err.append(f"unknown type {t}")
                n = 0
            total += n
        if total != 13:
            err.append(f"{total} questions")
        bad += bool(err)
        print(f"{f.name} {u['topic']:<17} {wc} words  {' + '.join(types)}  {err or 'OK'}")
    rep = {w: c for w, c in allw.items() if c > 1}
    print("repeated vocab:", rep or "none", "| total words:", sum(allw.values()))
    return 1 if bad or rep else 0


if __name__ == "__main__":
    raise SystemExit(main())
