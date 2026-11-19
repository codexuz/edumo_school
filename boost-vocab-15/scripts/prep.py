"""Turn the extracted source (src/passages_raw.json, src/glossary_raw.json) into data/lessons.json.

- fixes extraction errors in the three Cambridge IELTS 15 Test 1 passages and their glossaries
- splits every passage into two lessons (text + its glossary words)
- adds Uzbek meanings (data/uz.json) and builds five exercises per lesson (deterministic shuffles)
"""
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DATA = ROOT / "src", ROOT / "data"

TITLES = {1: ("Nutmeg – a valuable spice", "History · trade"),
          2: ("Driverless cars", "Technology · transport"),
          3: ("What is exploration?", "Travel · discovery")}

TEXT_FIX = [  # extraction / typing errors (checked against the page images and the Cambridge original)
    ("‘[[a]] ril’", "‘[[aril]]’"), ("[[groves.]]", "[[groves]]."), ("[[nutmeg]]- producing", "[[nutmeg]]-producing"),
    ("[[uncontacted]] [[tr]] ibes", "[[uncontacted tribes]]"), ("[[self-discovery.]]", "[[self-discovery]]."),
    ("[[campaigner on]] [[behalf of remote so-]]called", "[[campaigner]] [[on behalf of]] [[remote]] [[so-called]]"),
    ("on the sweets of London", "on the streets of London"), ("and how even less about", "and know even less about"),
    ("only 31cm long", "only 3 km long"), ("[[the]] [[unknown]]", "[[the unknown]]"),
    ("[[played an]] [[important part]]", "[[played an important part]]"), ("[[have]] [[responsibility for]]", "[[have responsibility for]]"),
    ("[[fell]] [[under]]", "[[fell under]]"), ("[[arrived]] [[at a compromise settlement]]", "[[arrived at a compromise settlement]]"),
    ("[[flexible in]] [[response to]]", "[[flexible in response to]]"), ("[[the]] [[workings of]]", "[[the workings of]]"),
    ("[[spices nutmeg]]", "[[spices]] [[nutmeg]]"), ("[[as if exploration peaked somehow]]", "[[as if]] [[exploration]] [[peaked]] [[somehow]]"),
    ("[[merchants based in Venice]]", "[[merchants]] [[based in]] Venice"), ("[[Indeed]]", "[[indeed]]"),
]
GLOSS_FIX = {
    "unprotected": "defenceless, insecure, vulnerable", "proper": "appropriate, suitable, apt",
    "grove": "plantation, copse, orchard", "conquere": None, "suit": "fit, match, go well with, be appropriate",
    "prompt": "stimulate, encourage, motivate #prevent", "respond": "react, reply, answer #ignore",
    "specialized": "trained, designed or developed for a particular purpose",
    "astronomer": "a scientist who studies the stars and planets", "quest": "search, hunt, seek #find",
    "yonder": "over there – used to show where something or someone is",
    "camel": "a large desert animal with a long neck and one or two humps on its back",
    "either one or two humps (": None, "continental": "relating to a large mass of land (a continent)",
    "voyage": "journey, trip, expedition", "bring back": "return with, carry back",
    "uncontacted tribes": "communities who live without contact with the rest of the world",
    "crawl over": "to move slowly across something, close to the ground", "landscape#2": "situation, circumstances",
    "penny - pennies (plural)": None, "monopoly": "complete control of a business or trade, so that nobody else can compete",
    "indeed#3": None, "valuable#2": None, "merchant#1b": None,
}
ADD = {2: [("conquer", "defeat, overcome, beat")], 3: [("border", "edge, limit, boundary, margin")],
       1: [("penny", "a small unit of British money (plural: pennies)")]}
SKIP_TERMS = {"implementation#2"}  # printed twice in the source
# the first glossary term of the second lesson of each passage, and the first paragraph of that lesson
SPLIT = {1: ("merchant", 3), 2: ("implement", 3), 3: ("surface", 3)}


def clean_entries(P, raw):
    seen, out = {}, []
    for term, val in raw:
        term = term.strip().lower()
        key = term
        if term in seen and term == "implementation":  # printed twice in a row
            continue
        seen[term] = seen.get(term, 0) + 1
        fx = GLOSS_FIX.get(f"{term}#{P}", GLOSS_FIX.get(term, val))
        if term == "landscape" and P == 3:
            fx = "scenery, land, site, scene"
        if term == "astronomer":
            out.append({"term": "astronomer", "val": GLOSS_FIX["astronomer"]})
            out.append({"term": "border", "val": "edge, limit, boundary, margin"})
            continue
        if fx is None:
            if term == "conquere":
                out.append({"term": "conquer", "val": "defeat, overcome, beat"})
            elif term.startswith("penny"):
                out.append({"term": "penny", "val": "a small unit of British money (plural: pennies)"})
            continue
        out.append({"term": key, "val": re.sub(r"\s+,", ",", fx).strip()})
    return out


def parse(val):
    main, *ants = val.split("#")
    ant = [a.strip(" ,") for a in ",".join(ants).split(",") if a.strip(" ,")]
    items = [s.strip() for s in main.split(",") if s.strip()]
    is_syn = len(items) >= 2 and all(len(s.split()) <= 3 for s in items) and not re.search(r"\b(sth|someone|something)\b", main)
    if len(items) == 1 and len(items[0].split()) <= 2:
        is_syn = True
    return main.strip(" ,"), items, ant, is_syn


def plain(t):
    return t.replace("[[", "").replace("]]", "")


def core(term):
    t = re.sub(r"\(.*?\)|\b(sth|sb|sb/sth)\b", " ", term)
    t = t.split("/")[0]
    t = re.sub(r"\s+", " ", t).strip()
    return {"come to do": "come to"}.get(t, re.sub(r" (to do|doing)$", "", t))


def stem(w):
    w = w.lower()
    for suf in ("ies", "ied", "ing", "ed", "es", "s", "e", "y"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def surface(term, text):
    """The form of a single-word term used inside a highlighted span of the lesson text (or None)."""
    c = core(term)
    if " " in c:
        return None
    for span in re.findall(r"\[\[(.+?)\]\]", text):
        for w in re.findall(r"[A-Za-z][A-Za-z-]*", span):
            if stem(w) == stem(c) and abs(len(w) - len(c)) <= 3:
                return w
    return None


def hint(phrase):
    return "   ".join(w[0] + " " + " ".join("_" for _ in w[1:]) if len(w) > 1 else w for w in phrase.split())


def exercises(n, text, ents, uz):
    rnd = random.Random(1500 + n)
    used = set()
    ambiguous = {"found", "free", "test", "model", "rule", "power", "trade", "hold", "past", "map", "cross", "park",
                 "aim", "own", "nature", "reach", "spread", "average", "fresh", "risk", "doubt", "root", "branch"}
    sents = [s.strip() for s in re.split(r"(?<=[.?!’])\s+(?=[A-Z‘])|(?<=;)\s+| — ", plain(text))]

    # 1 synonyms
    syn = [x for x in ents if x["syn"] and len(x["items"]) >= 2 and x["term"] not in ambiguous]
    rnd.shuffle(syn)
    ex1 = []
    for x in syn:
        if len(ex1) == 8:
            break
        opts = [s for s in x["items"] if core(x["term"]).split()[0] not in s.lower()][:2]
        if len(opts) < 2:
            continue
        ex1.append({"word": core(x["term"]), "syn": ", ".join(opts)})
        used.add(x["term"])
    # 2 opposites
    opp = [x for x in ents if x["ant"] and x["term"] not in used and x["term"] not in ("pale", "found")]
    rnd.shuffle(opp)
    ex2 = [{"word": core(x["term"]), "opp": x["ant"][0]} for x in opp[:6]]
    used |= {x["term"] for x in opp[:6]}
    # 3 gap-fill with sentences from the text
    ex3 = []
    cand = [x for x in ents if x["term"] not in used and x["term"] not in ambiguous]
    rnd.shuffle(cand)
    used_sents = set()
    for x in cand:
        if len(ex3) == 8:
            break
        w = surface(x["term"], text)
        if not w or w.lower() in {g["a"].lower() for g in ex3}:
            continue
        for i, s in enumerate(sents):
            ps = plain(s)
            if i in used_sents or not (7 <= len(ps.split()) <= 36):
                continue
            if not re.search(rf"\b{re.escape(w)}\b", ps):
                continue
            gap = re.sub(rf"\b{re.escape(w)}\b", "______", ps, count=1)
            if gap[0].islower() or gap.startswith("______") and i and not sents[i - 1].endswith((".", "?", "!", "’")):
                gap = "… " + gap
            gap = re.sub(r"[;,]$", " …", gap)
            if not gap.endswith(("…", ".", "?", "!", "’")):
                gap += " …"
            ex3.append({"s": gap, "a": w})
            used_sents.add(i)
            used.add(x["term"])
            break
    # 4 find the word that means … (definitions)
    defs = [x for x in ents if not x["syn"] and x["term"] not in used and len(x["main"]) < 110 and x["main"].count(",") < 3
            and x["term"] not in ("myristica fragrans", "middle ages", "nutmeg")]
    rnd.shuffle(defs)
    ex4 = [{"def": x["main"], "a": core(x["term"]), "h": hint(core(x["term"]))} for x in defs[:6]]
    used |= {x["term"] for x in defs[:6]}
    # 5 Uzbek -> English
    rest = [x for x in ents if x["term"] not in used and uz.get(x["term"]) and " " not in core(x["term"]) and x["term"] not in ambiguous
            and x["term"] not in ("myristica fragrans",)]
    rnd.shuffle(rest)
    ex5 = [{"uz": uz[x["term"]], "a": core(x["term"]), "h": hint(core(x["term"]))} for x in rest[:6]]
    return {"syn": ex1, "opp": ex2, "gap": ex3, "find": ex4, "uz": ex5}


def build():
    passages = json.loads((SRC / "passages_raw.json").read_text(encoding="utf-8"))
    gloss = json.loads((SRC / "glossary_raw.json").read_text(encoding="utf-8"))
    uz = json.loads((DATA / "uz.json").read_text(encoding="utf-8"))
    lessons, missing = [], []
    for P in (1, 2, 3):
        p = passages[P - 1]
        paras = []
        for t in p["paras"]:
            for a, b in TEXT_FIX:
                t = t.replace(a, b)
            paras.append(t)
        ents = clean_entries(P, gloss[str(P)])
        first, cut_para = SPLIT[P]
        idx = [i for i, x in enumerate(ents) if x["term"] == first][-1]
        halves = [ents[:idx], ents[idx:]]
        letters = p["letters"]
        for h, (lo, hi) in enumerate([(0, cut_para), (cut_para, len(paras))]):
            words = []
            for x in halves[h]:
                main, items, ant, is_syn = parse(x["val"])
                u = uz.get(x["term"], "")
                if not u:
                    missing.append(x["term"])
                words.append({"term": x["term"], "main": main, "items": items, "ant": ant, "syn": is_syn, "uz": u})
            n = len(lessons) + 1
            text = " ".join(paras[lo:hi])
            les = {"n": n, "passage": P, "part": h + 1, "title": TITLES[P][0], "topic": TITLES[P][1],
                   "paras": paras[lo:hi], "letters": letters[lo:hi] if letters else [], "words": words,
                   "count": sum(len(plain(t).split()) for t in paras[lo:hi])}
            les["ex"] = exercises(n, text, words, uz)
            lessons.append(les)
    (DATA / "lessons.json").write_text(json.dumps(lessons, ensure_ascii=False, indent=1), encoding="utf-8")
    for l in lessons:
        print(l["n"], l["title"], l["part"], l["count"], "words;", len(l["words"]), "glossary;",
              {k: len(v) for k, v in l["ex"].items()})
    if missing:
        print("NO UZBEK:", missing)


if __name__ == "__main__":
    build()
