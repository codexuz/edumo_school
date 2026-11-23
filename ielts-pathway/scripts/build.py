"""Build an IELTS Pathway book (Student's Book or Workbook) for one level -> <level>/dist/<book>.html.

Usage: python3 scripts/build.py a1 sb [--units 1,2] [--title "Pilot"]
Reads <level>/data/<book>-unit-NN.json, writes HTML; scripts/render.js turns it into a PDF.
Order: title page, units, audioscripts, answer key.
"""
import argparse
import html
import json
import re
from functools import lru_cache
from pathlib import Path

from icons import icon

ROOT = Path(__file__).resolve().parent.parent
L = "ABCDEFGHIJ"
BOOK = {"sb": "Student's Book", "wb": "Workbook"}
SECTION = {  # kind -> (label, icon)
    "vocabulary": ("VOCABULARY", "book"), "grammar": ("GRAMMAR", "list"), "listening": ("LISTENING", "headphones"),
    "reading": ("READING", "news"), "speaking": ("SPEAKING", "chat"), "writing": ("WRITING", "pen"), "exam": ("EXAM PRACTICE", "check"), "check": ("SELF-CHECK", "check"),
}
CLOSED = {"short", "gap", "choose", "mcq", "tf", "match", "order", "correct", "form"}
e = html.escape


def md(s):
    s = e(str(s), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)


GAP = re.compile(r"_{4,}")


def gapline(s, cls="gl"):
    return GAP.sub(f'<span class="{cls}"></span>', md(s))


@lru_cache(maxsize=None)
def qr_svg(url):
    import qrcode
    import qrcode.image.svg
    return qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=1).to_string(encoding="unicode")


# ---------- exercises ----------
class Num:
    def __init__(self):
        self.n = 0

    def next(self):
        self.n += 1
        return self.n


def items_of(ex):
    return ex.get("items", [])


def numbered(ex, i):
    return ex.get("start", 1) + i


def ex_body(ex):
    k, its = ex["kind"], items_of(ex)
    rows = []
    if k in ("short", "order", "correct"):
        for i, it in enumerate(its):
            q = f'<i>{md(it["q"])}</i>' if k == "order" else md(it["q"])
            rows.append(f'<li><b class="n">{numbered(ex, i)}</b><span class="q">{q}</span><span class="wl"></span></li>')
        return f'<ol class="xl {k}">{"".join(rows)}</ol>'
    if k == "gap":
        for i, it in enumerate(its):
            rows.append(f'<li><b class="n">{numbered(ex, i)}</b><span class="q">{gapline(it["q"])}</span></li>')
        return f'<ol class="xl gap">{"".join(rows)}</ol>'
    if k == "choose":
        def opts(m):
            parts = [p.strip() for p in m.group(1).split("/")]
            return '<span class="ch">' + '<i>/</i>'.join(f"<span>{e(p)}</span>" for p in parts) + "</span>"
        for i, it in enumerate(its):
            q = re.sub(r"\(([^()]*/[^()]*)\)", opts, e(it["q"], quote=False))
            rows.append(f'<li><b class="n">{numbered(ex, i)}</b><span class="q">{q}</span></li>')
        return f'<ol class="xl choose">{"".join(rows)}</ol>'
    if k == "mcq":
        for i, it in enumerate(its):
            op = "".join(f"<li><b>{L[j]}</b> {md(o)}</li>" for j, o in enumerate(it["options"]))
            inline = " inl" if all(len(o) <= 14 for o in it["options"]) else ""
            rows.append(f'<li><b class="n">{numbered(ex, i)}</b><div><p>{gapline(it["q"])}</p><ul class="{inline}">{op}</ul></div></li>')
        return f'<ol class="xl mcq">{"".join(rows)}</ol>'
    if k == "tf":
        for i, it in enumerate(its):
            rows.append(f'<li><b class="n">{numbered(ex, i)}</b><span class="q">{md(it["q"])}</span><span class="ab"></span></li>')
        return f'<ol class="xl tf">{"".join(rows)}</ol>'
    if k == "match":
        left = "".join(f'<li><b class="n">{i + 1}</b><span>{md(x)}</span><span class="ab sm"></span></li>' for i, x in enumerate(ex["left"]))
        right = "".join(f"<li><b>{L[i]}</b> {md(x)}</li>" for i, x in enumerate(ex["right"]))
        return f'<div class="mt"><ol>{left}</ol><ol class="r">{right}</ol></div>'
    if k == "form":
        out = []
        for label, val in ex["rows"]:
            v = md(val)
            v = re.sub(r"\((\d{1,2})\)\s*", r'<b class="fn">\1</b>', v)
            v = GAP.sub('<span class="fgap"></span>', v)
            v = v.replace("(Example)", '<em class="exm">Example</em>')
            out.append(f'<div class="frow"><span>{e(label)}</span><b>{v}</b></div>')
        return f'<div class="form"><h4>{e(ex["title"])}</h4>{"".join(out)}</div>'
    if k == "speak":
        return '<ul class="sq">' + "".join(f"<li>{md(q)}</li>" for q in its) + "</ul>"
    if k == "frames":
        for i, it in enumerate(its):
            rows.append(f'<li><b class="n">{i + 1}</b><div><p><b>{md(it["q"])}</b></p><p class="fr">{md(it["frame"])}</p>'
                        f'<span class="wl full"></span></div></li>')
        return f'<ol class="xl frames">{"".join(rows)}</ol>'
    if k == "write":
        out = ""
        if ex.get("fields"):
            out += '<div class="form wf">' + "".join(f'<div class="frow"><span>{e(f)}</span><b><span class="fgap w"></span></b></div>'
                                                      for f in ex["fields"]) + "</div>"
        if ex.get("lines"):
            out += '<div class="lines">' + '<i></i>' * ex["lines"] + "</div>"
        if ex.get("checklist"):
            out += checklist({"title": "Check your writing", "items": ex["checklist"]})
        return out
    raise ValueError(f"unknown exercise kind {k}")


def exercise(ex, num, sec):
    n = num.next()
    ex["_n"] = n
    bank = ""
    if ex.get("bank"):
        bank = '<div class="bank">' + "".join(f"<span>{e(w)}</span>" for w in ex["bank"]) + "</div>"
    example = f'<p class="exl"><b>Example:</b> {md(ex["example"])}</p>' if ex.get("example") else ""
    note = f'<p class="exl">{md(ex["note"])}</p>' if ex.get("note") else ""
    tag = '<span class="etag">IELTS</span>' if ex.get("exam") else ""
    aud = f'<span class="atag">{icon("headphones")} {ex["audio"]}</span>' if ex.get("audio") else ""
    return (f'<div class="ex k-{ex["kind"]}" id="{ex["id"]}"><div class="xhead"><b class="xn">{n}</b><p>{md(ex["instruction"])}{tag}{aud}</p></div>'
            f'{example}{note}{bank}{ex_body(ex)}</div>')


# ---------- other blocks ----------
def checklist(b):
    return (f'<div class="ck"><h5>{e(b.get("title", "Checklist"))}</h5><ul>'
            + "".join(f"<li><i></i>{md(x)}</li>" for x in b["items"]) + "</ul></div>")


def box(b):
    st = b.get("style", "tip")
    ic = {"exam": "check", "tip": "bulb", "errors": "type"}[st]
    if st == "errors":
        inner = "".join(f'<div class="er"><p><span class="w">✗ {e(x["wrong"])}</span><span class="r">✓ {e(x["right"])}</span></p>'
                        f'<p class="uz">{e(x["uz"])}</p></div>' for x in b["items"])
    else:
        inner = "<ul>" + "".join(f"<li>{md(x)}</li>" for x in b["items"]) + "</ul>"
    return f'<div class="bx {st}"><h5>{icon(ic)} {e(b["title"])}</h5>{inner}</div>'


def block(b, ctx):
    t = b["type"]
    if t == "text":
        return f'<p class="tx">{md(b["text"])}</p>'
    if t == "table":
        head = "".join(f"<th>{md(h)}</th>" for h in b["head"]) if any(b["head"]) else ""
        rows = "".join("<tr>" + "".join(f"<td>{md(c)}</td>" for c in r) + "</tr>" for r in b["rows"])
        return f'<table class="gt">{f"<tr>{head}</tr>" if head else ""}{rows}</table>'
    if t == "box":
        return box(b)
    if t == "vocab":
        rows = "".join(f'<div class="vrow"><b>{e(v["word"])}</b><i>{e(v["pos"])}</i><span class="uz">{e(v["uz"])}</span>'
                       f'<p>{md(v["ex"])}</p></div>' for v in b["items"])
        return f'<div class="vlist split">{rows}</div>'
    if t == "audio":
        s = ctx["scripts"].get(b["id"], {})
        return (f'<div class="audio-b"><span class="qrph">QR</span><div><b>{icon("headphones")} Audio {b["id"]}</b>'
                f'<span>{e(s.get("title", ""))} · scan after recording</span></div></div>')
    if t == "passage":
        paras = "".join((f'<p class="pp"><b class="who">{e(p["head"])}</b>' if p.get("head") else '<p class="pp">') + f'{md(p["text"])}</p>'
                        for p in b["paras"])
        words = sum(len(p["text"].split()) for p in b["paras"])
        intro = f'<p class="pin">{md(b["intro"])}</p>' if b.get("intro") else ""
        return (f'<div class="psg split"><h4 class="ptitle">{e(b["title"])}<small>{words} words</small></h4>{intro}{paras}</div>')
    if t == "model":
        if b.get("lines"):
            inner = "".join(f'<p><b>{e(w)}:</b> {md(x)}</p>' for w, x in b["lines"])
        else:
            inner = f'<p>{md(b["text"])}</p>'
        return f'<div class="model"><h5>{icon("chat")} {e(b["title"])}</h5>{inner}</div>'
    if t == "ex":
        return exercise(b, ctx["num"], ctx["sec"])
    if t == "checklist":
        return checklist(b)
    if t == "score":
        return f'<div class="score">Your score <i></i> / {b["total"]}</div>'
    if t == "cando":
        return checklist({"title": "I can …", "items": ctx["unit"]["goals"]})
    if t == "selfcheck":
        rows = "".join(f'<tr><td>{SECTION[k][0].title()}</td><td><i></i> / {n}</td></tr>' for k, n in ctx["counts"].items() if n)
        return f'<table class="selfc"><tr><th>Section</th><th>My score</th></tr>{rows}</table>'
    raise ValueError(f"unknown block {t}")


def closed_count(ex):
    if ex["kind"] == "form":
        return len(ex["answers"])
    if ex["kind"] == "match":
        return len(ex["a"])
    return len(items_of(ex)) if ex["kind"] in CLOSED else 0


def unit_html(u, book):
    num = Num()
    scripts = {s["id"]: s for s in u.get("scripts", [])}
    counts = {}
    for s in u["sections"]:
        for b in s["blocks"]:
            if b["type"] == "ex" and s["kind"] != "exam":
                counts[s["kind"]] = counts.get(s["kind"], 0) + closed_count(b)
    ctx = {"num": num, "scripts": scripts, "unit": u, "counts": counts}
    lvl, n = u["level"], u["unit"]
    banner = (f'<div class="banner"><div class="girih"></div><div class="bl"><small>IELTS PATHWAY {lvl} · {BOOK[book].upper()}</small>'
              f'<h1>UNIT {n} · {e(u["title"].upper())}</h1></div><div class="br"><b>{e(u["topic"])}</b><span>IELTS foundations</span></div></div>')
    opener = ""
    if book == "sb":
        focus = "".join(f"<li>{md(x)}</li>" for x in u["exam_focus"])
        goals = "".join(f"<li>{md(x)}</li>" for x in u["goals"])
        warm = "".join(f"<li>{md(x)}</li>" for x in u["warmup"])
        opener = (f'<div class="part op"><div class="opx"><h5>{icon("check")} Exam focus</h5><ul>{focus}</ul></div>'
                  f'<div class="opg"><h5>In this unit I can …</h5><ul>{goals}</ul></div>'
                  f'<div class="opw"><h5>{icon("chat")} Warm-up · Speaking Part 1</h5><ul>{warm}</ul></div></div>')
    body = opener
    for s in u["sections"]:
        ctx["sec"] = s["kind"]
        label, ic = SECTION[s["kind"]]
        inner = "".join(block(b, ctx) for b in s["blocks"])
        body += (f'<div class="part sec s-{s["kind"]}"><div class="shead"><span class="spill">{icon(ic)} {label}</span>'
                 f'<span class="stitle">{e(s["title"])}</span></div>{inner}</div>')
    return (f'<section class="page flow first" id="u{n}">{banner}<div class="cols"><div class="col">{body}</div><div class="col"></div></div>'
            f'<footer><span>IELTS Pathway {lvl} · {BOOK[book]} · Unit {n}</span><span class="pno"></span></footer></section>')


def key_items(ex):
    k = ex["kind"]
    if k == "form":
        return [(n, a) for n, a in ex["answers"].items()]
    if k == "match":
        return [(i + 1, a) for i, a in enumerate(ex["a"])]
    return [(numbered(ex, i), it["a"]) for i, it in enumerate(items_of(ex))]


def back_matter(units, book):
    lvl = units[0]["level"]
    scripts, keys = "", ""
    for u in units:
        scripts += f'<h3 class="sh3">Unit {u["unit"]} · {e(u["title"])}</h3>'
        for s in u.get("scripts", []):
            scripts += f'<h4 class="sh4">{icon("headphones")} {s["id"]} · {e(s["title"])}</h4>'
            scripts += "".join(f'<p>{f"<b>{e(w)}:</b> " if w else ""}{e(x)}</p>' for w, x in s["lines"])
            scripts += f'<p class="rn">Recording notes: {e(s["notes"])}</p>'
        keys += f'<h3 class="sh3">Unit {u["unit"]} · {e(u["title"])}</h3>'
        for sec in u["sections"]:
            for b in sec["blocks"]:
                if b["type"] != "ex":
                    continue
                if b["kind"] in CLOSED:
                    ans = "  ".join(f'<span><b>{n}</b> {md(a)}</span>' for n, a in key_items(b))
                else:
                    ans = "<span>Students' own answers.</span>"
                keys += f'<div class="krow"><b class="xn">{b["_n"]}</b><div>{ans}</div></div>'
    foot = lambda t: f'<footer><span>IELTS Pathway {lvl} · {BOOK[book]} · {t}</span><span class="pno"></span></footer>'
    sec = lambda i, title, sub, inner, cls: (
        f'<section class="page flow first" id="{i}"><div class="banner small"><div class="girih"></div><div class="bl"><small>{BOOK[book].upper()}</small>'
        f'<h1>{title}</h1></div><div class="br"><span>{sub}</span></div></div>'
        f'<div class="cols"><div class="col"><div class="split {cls}">{inner}</div></div><div class="col"></div></div>{foot(title.title())}</section>')
    return (sec("scripts", "AUDIOSCRIPTS", "Read after you answer the questions", scripts, "script")
            + sec("key", "ANSWER KEY", "Accept other correct answers where shown with /", keys, "keys"))


def title_page(level, book, title):
    return (f'<section class="page tpage"><div class="tp"><small>IELTS PATHWAY</small><h1>{level.upper()}</h1><h2>{BOOK[book]}</h2>'
            f'<p>{e(title)}</p><p class="sub">Grammar · Vocabulary · Listening · Reading · Speaking · Writing<br>From the first words to IELTS</p></div>'
            f'<footer><span>IELTS Pathway {level.upper()} · {BOOK[book]}</span><span class="pno"></span></footer></section>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("level")
    ap.add_argument("book", choices=["sb", "wb"])
    ap.add_argument("--units", default="")
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    data = ROOT / a.level / "data"
    files = sorted(data.glob(f"{a.book}-unit-*.json"))
    if a.units:
        want = {int(x) for x in a.units.split(",")}
        files = [f for f in files if int(f.stem.split("-")[-1]) in want]
    units = [json.loads(f.read_text(encoding="utf-8")) for f in files]
    body = title_page(a.level, a.book, a.title) + "".join(unit_html(u, a.book) for u in units) + back_matter(units, a.book)
    css = "".join((ROOT / "scripts" / f).read_text(encoding="utf-8") for f in ("style.css", "pathway.css"))
    fonts = ('<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700;800'
             '&family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&display=block" rel="stylesheet">')
    dist = ROOT / a.level / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    out = dist / f"{a.book}.html"
    out.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>IELTS Pathway {a.level.upper()} {BOOK[a.book]}</title>'
                   f'{fonts}<style>{css}</style></head><body>{body}</body></html>', encoding="utf-8")
    print(f"{out.relative_to(ROOT)}: {len(units)} unit(s)")


if __name__ == "__main__":
    main()
