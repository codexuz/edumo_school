"""Build the B1 Preliminary (PET) Listening Practice book interior (A4, two columns, Mock-book design) -> dist/mock.html.

Data: data/pet_b1_listening_tests.json (36 tests, 4 parts each, answers and audioscripts).
Pictures for Part 1: assets/pics/tNN-qN.jpg. Each part gets a QR code that opens its recording.
Order: how to use + contents, Tests 1–36 (each starts on a new page), answer key, audioscripts.
"""
import base64
import html
import json
import re
from functools import lru_cache
from pathlib import Path

import qrcode
import qrcode.image.svg

from icons import icon

ROOT = Path(__file__).resolve().parent.parent
DIST, PICS = ROOT / "dist", ROOT / "assets" / "pics"
DATA = ROOT / "data" / "pet_b1_listening_tests.json"
CHANNEL = "t.me/multilevel_express"
NAME = "B1 Preliminary Listening Practice"
KICKER = "B1 PRELIMINARY · LISTENING"
L = "ABCDEFGH"
e = html.escape


@lru_cache(maxsize=None)
def qr_svg(url):
    return qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=1).to_string(encoding="unicode")


def uri(p):
    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode()


def dash(r):
    return r.replace("-", "–")


GAP = re.compile(r"\s*[.…]{3,}\s*")


def gaps(s):
    """'(6) £……… per day' -> numbered badge + a write-in line."""
    s = e(s)
    s = re.sub(r"\((\d{1,2})\)\s*", r'<b class="fn">\1</b>', s)
    return GAP.sub(' <span class="fgap"></span> ', s).strip()


# ---------- parts ----------
def part_head(p):
    qrange = dash(p["questions"])
    audio = (f'<div class="qrs">{qr_svg(p["audio"])}</div>' if p.get("audio") else "")
    return (f'<div class="phead"><span class="pill">PART {p["part"]}</span><span class="qr">Questions {qrange}</span></div>'
            f'<div class="audrow">{audio}<div><p>{e(p["instruction"])}</p>'
            f'<small>{icon("scan")} Scan to listen · you hear it twice</small></div></div>')


def part1(p, t):
    out = []
    for it in p["items"]:
        img = PICS / f"t{t:02d}-q{it['n']}.jpg"
        out.append(f'<div class="p1q"><div class="qq"><b class="qn">{it["n"]}</b><p>{e(it["question"])}</p></div>'
                   f'<img src="{uri(img)}" alt="Question {it["n"]}: pictures A, B and C"></div>')
    return "".join(out)


def part2(p):
    lines = p["form"]
    title, rest = lines[0], lines[1:]
    rows, k = [], 0
    while k < len(rest):
        ln = rest[k].strip()
        if ln.endswith(":") and k + 1 < len(rest) and not rest[k + 1].strip().endswith(":"):
            rows.append(f'<div class="frow"><span>{e(ln)}</span><b>{gaps(rest[k + 1].strip())}</b></div>')
            k += 2
        else:
            rows.append(f'<div class="fline">{gaps(ln)}</div>')
            k += 1
    return f'<div class="form"><h4>{e(title)}</h4>{"".join(rows)}</div>'


def mcq(p):
    out = []
    for it in p["items"]:
        opts = "".join(f"<li><b>{L[k]}</b> {e(o)}</li>" for k, o in enumerate(it["options"]))
        lead = f'<div class="lead4">{e(it["context"])}</div>' if it.get("context") else ""
        out.append(f'<div class="qq mc"><b class="qn">{it["n"]}</b><div>{lead}<p>{e(it["question"])}</p><ul>{opts}</ul></div></div>')
    return "".join(out)


def part_block(p, t):
    body = {1: lambda: part1(p, t), 2: lambda: mcq(p), 3: lambda: part2(p), 4: lambda: mcq(p)}[p["part"]]()
    ctx = f'<p class="ctx">{e(p["context"])}</p>' if p.get("context") else ""
    return f'<div class="part">{part_head(p)}{ctx}{body}</div>'


def answer_box(t):
    cols = ""
    for p in t["parts"]:
        cells = "".join(f'<li><b>{k}</b><i></i></li>' for k in p["answers"])
        cols += f'<div class="ycol p{p["part"]}"><h5>Part {p["part"]}</h5><ol>{cells}</ol></div>'
    return ('<div class="part"><div class="phead"><span class="pill gold">YOUR ANSWERS</span>'
            f'<span class="qr">Test {t["test"]}</span></div><div class="yans">{cols}</div>'
            '<div class="yscore">Score <i></i> / 25</div></div>')


def banner(small, title, rb, rs, cls=""):
    return (f'<div class="banner {cls}"><div class="girih"></div><div class="bl"><small>{small}</small><h1>{title}</h1></div>'
            f'<div class="br"><b>{rb}</b><span>{rs}</span></div></div>')


def test_section(t):
    n = t["test"]
    head = banner(KICKER, f"TEST {n}", f'{icon("headphones", "ico bi")} 25 questions', "4 parts · about 30 minutes")
    body = "".join(part_block(p, n) for p in t["parts"]) + answer_box(t)
    return (f'<section class="page flow first" id="t{n}" data-run="Test {n}">{head}<div class="cols"><div class="col">{body}</div>'
            f'<div class="col"></div></div><footer><span>{NAME} · Test {n}</span><span class="pno"></span></footer></section>')


# ---------- front and back matter ----------
def how_page(tests):
    fmt = [("Part 1", "1–7", "Seven short recordings", "Choose the right picture: A, B or C."),
           ("Part 2", "8–13", "Six short conversations", "Choose the right answer: A, B or C."),
           ("Part 3", "14–19", "One person gives information", "Write one or two words, a number, a date or a time in each gap."),
           ("Part 4", "20–25", "A longer interview", "Choose the right answer: A, B or C.")]
    rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in fmt)
    tips = [("headphones", "Listen twice", "You hear every recording two times. Use the first time to find the answer and the second time to check it."),
            ("book", "Read first", "Before you listen, read the questions and look at the pictures. Think about the words you might hear."),
            ("pen", "Spell carefully", "In Part 3, spelling must be correct. Names are often spelled for you: listen for each letter."),
            ("check", "Check the key", "Check your answers in the key, then read the audioscript and find the words that give each answer.")]
    cards = "".join(f'<div class="tip"><span class="tipi">{icon(i)}</span><div><b>{h}</b><p>{d}</p></div></div>' for i, h, d in tips)
    toc = "".join(f'<a href="#t{t["test"]}"><b>Test {t["test"]}</b><i data-ref="t{t["test"]}"></i></a>' for t in tests)
    toc += ('<a class="x" href="#key"><b>Answer key</b><i data-ref="key"></i></a>'
            '<a class="x" href="#scripts"><b>Audioscripts</b><i data-ref="scripts"></i></a>')
    return ('<section class="page howpage">' + banner(KICKER, "HOW TO USE THIS BOOK", f"{len(tests)} tests", "Answers + audioscripts")
            + f'<p class="lead">This book has <b>{len(tests)} practice tests</b> in the format of the <b>B1 Preliminary (PET) Listening</b> paper. '
              'Each test has <b>4 parts</b> and <b>25 questions</b> and takes about <b>30 minutes</b>. '
              'The answer key and the audioscripts of every recording are at the back of the book.</p>'
            + f'<table class="fmt"><tr><th>Part</th><th>Questions</th><th>What you hear</th><th>What you do</th></tr>{rows}</table>'
            + f'<div class="tips">{cards}</div>'
            + f'<div class="audio"><div class="qrc">{qr_svg("https://" + CHANNEL)}</div><div><b>Audio for every part</b>'
              '<p>Each part of every test has its own QR code next to the instructions. Scan it with your phone camera to play the recording. '
              'For news and help, join our Telegram channel.</p>'
              f'<span>{CHANNEL}</span></div></div>'
            + f'<h3 class="sect">Contents</h3><div class="toc">{toc}</div>'
            + '<p class="src">Tests, pictures and recordings: englishpracticetest.net (Practice PET B1 Listening Tests).</p>'
            + f'<footer><span>{NAME}</span><span class="pno"></span></footer></section>')


def answer_key(tests):
    body = ""
    for t in tests:
        rows = "".join(f'<tr><th>Part {p["part"]}</th><td>' + " ".join(f"<span><b>{k}</b>{e(v)}</span>" for k, v in p["answers"].items())
                       + "</td></tr>" for p in t["parts"])
        body += f'<div class="kt"><h3>Test {t["test"]}</h3><table>{rows}</table></div>'
    return ('<section class="page flow first" id="key" data-run="Answer key">'
            + banner(f"TESTS 1–{len(tests)}", "ANSWER KEY", "25 answers per test", "Part 3: correct spelling is needed", "small")
            + f'<div class="cols"><div class="col"><div class="split">{body}</div></div><div class="col"></div></div>'
            f'<footer><span>{NAME} · Answer key</span><span class="pno"></span></footer></section>')


SPEAKER = re.compile(r"^([A-Z][\w’'.]*(?: [A-Z0-9][\w’'.]*){0,2}):\s*(.*)$")


def script_lines(lines, items=()):
    """Bare question numbers ('8') get the question text from the test page (context + question)."""
    label = {str(it["n"]): " ".join(x for x in (it.get("context"), it["question"]) if x) for it in items}
    out = []
    for ln in lines:
        ln = ln.strip()
        if re.fullmatch(r"\d{1,2}", ln):
            ln = f"{ln}   {label.get(ln, '')}".rstrip()
        m = re.match(r"^(\d{1,2})\s+(.*)$", ln) or re.match(r"^(\d{1,2})()$", ln)
        if m:
            out.append(f'<p class="sq"><i>{m.group(1)}</i>{e(m.group(2))}</p>')
            continue
        m = SPEAKER.match(ln)
        out.append(f"<p><b>{e(m.group(1))}:</b> {e(m.group(2))}</p>" if m else f"<p>{e(ln)}</p>")
    return "".join(out)


def scripts(tests):
    body = ""
    for t in tests:
        body += f'<h3 class="sh3">Test {t["test"]}</h3>'
        for p in t["parts"]:
            body += f'<h4 class="sh4">Part {p["part"]}</h4>' + script_lines(p["audioscript"], p.get("items", []))
    return ('<section class="page flow first" id="scripts" data-run="Audioscripts">'
            + banner(f"TESTS 1–{len(tests)}", "AUDIOSCRIPTS", "Every recording", "Read after you check your answers", "small")
            + f'<div class="cols"><div class="col"><div class="split script">{body}</div></div><div class="col"></div></div>'
            f'<footer><span>{NAME} · Audioscripts</span><span class="pno"></span></footer></section>')


def build():
    tests = json.loads(DATA.read_text(encoding="utf-8"))["tests"]
    pages = [how_page(tests)] + [test_section(t) for t in tests] + [answer_key(tests), scripts(tests)]
    css = (ROOT / "scripts" / "style.css").read_text(encoding="utf-8") + (ROOT / "scripts" / "listening.css").read_text(encoding="utf-8")
    fonts = ('<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700;800'
             '&family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&display=block" rel="stylesheet">')
    DIST.mkdir(exist_ok=True)
    (DIST / "mock.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{NAME}</title>'
                                    f'{fonts}<style>{css}</style></head><body>{"".join(pages)}</body></html>', encoding="utf-8")
    print("tests:", len(tests))


if __name__ == "__main__":
    build()
