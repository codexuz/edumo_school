"""Derive the practice tasks for one exercise from its own data.

Four tasks per unit, all built from the unit's word lists and model answers so
that the practice always reviews exactly what the unit taught:

  A  Complete the sentence   — a gap in a real sentence from the model answer
  B  Match English to Uzbek  — eight items from the two word lists
  C  Choose the right word   — Russian prompt, three English options
  D  Make it formal          — rewrite an informal line in Task 1.2 register

The sentence-level task D is hand-written per unit in data/sentences.json;
everything else is generated here, so a change to a word list flows straight
through to the practice and the answer key.
"""
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SENTENCES = json.loads((ROOT / "data" / "sentences.json").read_text(encoding="utf-8"))

GAP = "__________"


def _sentences(paras):
    """Split model-answer paragraphs into usable sentences."""
    out = []
    for p in paras:
        if len(p) < 45:          # greeting / sign-off
            continue
        for s in re.split(r"(?<=[.!?])\s+", p):
            if 55 <= len(s) <= 165:
                out.append(s.strip())
    return out


def _pick_gap(sentences, terms, rng, want):
    """Find sentences that contain a word-list term and blank that term out."""
    items, used = [], set()
    for s in sentences:
        for en, ru, uz in terms:
            if en in used or len(en) < 4:
                continue
            m = re.search(r"(?<![\w-])" + re.escape(en) + r"(?![\w-])", s, re.I)
            if m:
                items.append({"q": s[:m.start()] + GAP + s[m.end():], "a": m.group(0)})
                used.add(en)
                break
        if len(items) >= want:
            break
    return items


def build(ex):
    """Return the practice block for one exercise, plus its answer key."""
    rng = random.Random(ex["n"])          # deterministic: same book every build
    terms = ex["vocab_task1"] + ex["vocab_part2"]
    sents = _sentences(ex["samples"]["task12"]) + _sentences(ex["samples"]["part2"])

    # A — gap-fill from the model answers
    gaps = _pick_gap(sents, terms, rng, 8)

    # B — matching, eight terms with the Uzbek column shuffled
    pool = [t for t in terms if len(t[0]) < 26]
    chosen = rng.sample(pool, 8)
    shuffled = chosen[:]
    rng.shuffle(shuffled)
    match = {"left": [t[0] for t in chosen], "right": [t[2] for t in shuffled],
             "key": [shuffled.index(t) + 1 for t in chosen]}

    # C — Russian prompt, three English options
    choice = []
    for en, ru, uz in rng.sample([t for t in terms if t not in chosen], 6):
        wrong = rng.sample([t[0] for t in terms if t[0] != en], 2)
        opts = [en] + wrong
        rng.shuffle(opts)
        choice.append({"ru": ru, "options": opts, "a": "ABC"[opts.index(en)]})

    return {
        "gapfill": gaps,
        "match": match,
        "choice": choice,
        "rewrite": SENTENCES[str(ex["n"])],
    }
