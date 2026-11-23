"""Build the IELTS Listening Practice B1+ book interior -> dist/mock.html (render.js prints it to PDF).

Data:
  data/tests.json   80 tests (Parts 1–4, 20 each) with answers and audioscripts (scripts/extract.py)
  data/snips.json   crops of each test's question pages from the source PDF (scripts/snips.py), in assets/snips/
  data/extras.json  per test: synonym pairs (question wording -> audio wording) and key vocabulary with Uzbek
Each test is a header bar (test number, part, audio track, score) followed by its crops, in one column.
"""
import base64
import html
import json
import re
from pathlib import Path

from icons import icon

ROOT = Path(__file__).resolve().parent.parent
DIST, SNIP = ROOT / "dist", ROOT / "assets" / "snips"
NAME = "IELTS Listening Practice · B1+"
e = html.escape
PART = {
    1: ("A conversation between two people in an everyday social situation", "forms, notes, tables, multiple choice", "1–10"),
    2: ("One person talking about a place, an event or a service", "maps and plans, multiple choice, matching, notes", "11–20"),
    3: ("A conversation between students and a tutor about their studies", "multiple choice, matching, flow-charts, notes", "21–30"),
    4: ("A talk or lecture on an academic subject", "note, table, sentence and summary completion", "31–40"),
}
SNIPS = {int(k): v for k, v in json.loads((ROOT / "data" / "snips.json").read_text(encoding="utf-8")).items()}


def snip(f):
    b64 = base64.b64encode((SNIP / f["file"]).read_bytes()).decode()
    return f'<div class="snip"><img src="data:image/png;base64,{b64}" alt=""></div>'


def test_html(t):
    n, part = t["n"], t["part"]
    a, b = PART[part][2].split("–")
    bar = (f'<div class="th"><span class="tn">TEST {n}</span><span class="tp">Part {part} · Questions {a}–{b}</span>'
           f'<span class="ta">{icon("headphones")} Audio: Test {n}</span><span class="sc">Score <i></i> / 10</span></div>')
    return f'<div class="test" id="t{n}">{bar}{"".join(snip(f) for f in SNIPS[n])}</div>'


def part_section(part, tests):
    desc, tasks, qs = PART[part]
    banner = (f'<div class="banner"><div class="girih"></div><div class="bl"><small>IELTS LISTENING · B1+</small><h1>PART {part}</h1></div>'
              f'<div class="br"><b>{icon("headphones", "ico bi")} Tests {tests[0]["n"]}–{tests[-1]["n"]}</b><span>Questions {qs}</span></div></div>'
              f'<p class="pdesc"><b>Part {part}:</b> {e(desc)}. <span>Typical tasks: {e(tasks)}.</span></p>')
    body = "".join(test_html(t) for t in tests)
    return (f'<section class="page flow first" id="part{part}">{banner}<div class="cols one"><div class="col">{body}</div></div>'
            f'<footer><span>{NAME} · Part {part}</span><span class="pno"></span></footer></section>')


def how_page(tests):
    tips = [("book", "Read first", "Use the time before each recording to read the questions. Decide what kind of answer each gap needs: a name, a number, a date, a noun?"),
            ("headphones", "Listen once", "In the real test you hear each recording only once. Play it once, answer, then listen again with the audioscript to check."),
            ("type", "Spelling counts", "Names and words that are spelled out must be written correctly. Check plurals and word limits."),
            ("repeat", "Paraphrase", "The words you hear are often different from the words in the question. Study the synonym tables at the back.")]
    cards = "".join(f'<div class="tip"><span class="tipi">{icon(i)}</span><div><b>{h}</b><p>{d}</p></div></div>' for i, h, d in tips)
    parts = "".join(f'<tr><td>Part {p}</td><td>{e(PART[p][0])}</td><td>Tests {(p - 1) * 20 + 1}–{p * 20}</td>'
                    f'<td class="pg"><i data-ref="part{p}"></i></td></tr>' for p in PART) + "".join(
        f'<tr><td colspan="3"><b>{h}</b></td><td class="pg"><i data-ref="{r}"></i></td></tr>'
        for h, r in (("Answer key", "key"), ("Synonyms &amp; vocabulary", "syn"), ("Audioscripts", "scripts")))
    return ('<section class="page howpage"><div class="banner"><div class="girih"></div><div class="bl"><small>IELTS LISTENING · B1+</small>'
            f'<h1>HOW TO USE THIS BOOK</h1></div><div class="br"><b>{len(tests)} tests</b><span>Answer key + audioscripts</span></div></div>'
            '<p class="lead">This book has <b>80 practice tests</b> for the <b>IELTS Listening</b> paper: 20 tests for each of the four parts. '
            'Each test has <b>10 questions</b>. At the back of the book are the <b>answer key</b>, a <b>synonym table</b> and a '
            '<b>vocabulary list</b> (with Uzbek meanings) for every test, and all the <b>audioscripts</b>.</p>'
            f'<div class="tips">{cards}</div>'
            f'<table class="plan"><tr><th>Part</th><th>What you hear</th><th>Tests</th><th>Page</th></tr>{parts}</table>'
            '<p class="src">For classroom practice only. Not for sale. Tests and recordings adapted from Cambridge IELTS 7, 8 and 9 and '
            '<i>The Official Cambridge Guide to IELTS</i> (Cambridge University Press).</p>'
            f'<footer><span>{NAME}</span><span class="pno"></span></footer></section>')


def answer_key(tests):
    body = ""
    for t in tests:
        items = "".join(f'<span><b>{e(a["q"])}</b> {e(a["a"])}{f" <em>({e(a["note"])})</em>" if a["note"] else ""}</span>' for a in t["answers"])
        body += f'<div class="ka"><h4>Test {t["n"]}</h4><p>{items}</p></div>'
    return ('<section class="page flow first" id="key"><div class="banner small"><div class="girih"></div><div class="bl"><small>TESTS 1–80</small>'
            '<h1>ANSWER KEY</h1></div><div class="br"><span>/ = other correct answers · ( ) = optional words</span></div></div>'
            f'<div class="cols"><div class="col"><div class="split">{body}</div></div><div class="col"></div></div>'
            f'<footer><span>{NAME} · Answer key</span><span class="pno"></span></footer></section>')


EXTRAS = {x["n"]: x for x in json.loads((ROOT / "data" / "extras.json").read_text(encoding="utf-8"))["tests"]}


def synonyms(tests):
    """Per test: how the question wording is paraphrased in the audio, plus key vocabulary with Uzbek meanings."""
    body = ""
    for t in tests:
        x = EXTRAS[t["n"]]
        syn = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in x["syn"])
        voc = "".join(f'<tr><td><b>{e(w)}</b> <i>{e(pos)}</i></td><td>{e(uz)}</td></tr>' for w, pos, uz in x["vocab"])
        body += (f'<div class="sx"><h4>Test {t["n"]} <span>Part {t["part"]}</span></h4><div class="sxr">'
                 f'<table class="syn"><tr><th>In the questions</th><th>In the audio</th></tr>{syn}</table>'
                 f'<table class="voc"><tr><th>Word</th><th>O‘zbekcha</th></tr>{voc}</table></div></div>')
    return ('<section class="page flow first" id="syn"><div class="banner small"><div class="girih"></div><div class="bl"><small>TESTS 1–80</small>'
            '<h1>SYNONYMS &amp; VOCABULARY</h1></div><div class="br"><span>question words → audio words · key words</span></div></div>'
            f'<div class="cols one"><div class="col">{body}</div></div>'
            f'<footer><span>{NAME} · Synonyms &amp; vocabulary</span><span class="pno"></span></footer></section>')


def paragraphs(text):
    s = re.split(r"(?<=[.?!])\s+(?=[A-Z‘'\"])", text)
    paras, cur = [], []
    for x in s:
        cur.append(x)
        if len(" ".join(cur)) > 520 or re.match(r"(Before you|Now listen|You now have|That is the end)", x):
            paras.append(" ".join(cur)); cur = []
    if cur:
        paras.append(" ".join(cur))
    return "".join(f"<p>{e(p)}</p>" for p in paras)


def scripts(tests):
    body = "".join(f'<h4 class="sh">Test {t["n"]}<small>Part {t["part"]}</small></h4>{paragraphs(t["script"])}' for t in tests)
    return ('<section class="page flow first" id="scripts"><div class="banner small"><div class="girih"></div><div class="bl"><small>TESTS 1–80</small>'
            '<h1>AUDIOSCRIPTS</h1></div><div class="br"><span>Read after you check your answers</span></div></div>'
            f'<div class="cols"><div class="col"><div class="split scr">{body}</div></div><div class="col"></div></div>'
            f'<footer><span>{NAME} · Audioscripts</span><span class="pno"></span></footer></section>')


def build():
    tests = json.loads((ROOT / "data" / "tests.json").read_text(encoding="utf-8"))["tests"]
    pages = [how_page(tests)] + [part_section(p, [t for t in tests if t["part"] == p]) for p in PART] + [answer_key(tests), synonyms(tests), scripts(tests)]
    css = "".join((ROOT / "scripts" / f).read_text(encoding="utf-8") for f in ("style.css", "listening.css"))
    fonts = ('<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700;800'
             '&family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&family=JetBrains+Mono:wght@400;700&display=block" rel="stylesheet">')
    DIST.mkdir(exist_ok=True)
    (DIST / "mock.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>IELTS Listening Practice B1+</title>'
                                    f'{fonts}<style>{css}</style></head><body>{"".join(pages)}</body></html>', encoding="utf-8")
    print("tests:", len(tests))


if __name__ == "__main__":
    build()
