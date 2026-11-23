"""Build an IELTS Pathway book (Student's Book or Workbook) for one level -> <level>/dist/<book>.html.

Usage: python3 scripts/build.py a1 sb [--units 1,2] [--title "Pilot"]
Reads <level>/data/<book>-unit-NN.json, writes HTML; scripts/render.js turns it into a PDF.
Order: title page, units (lettered lessons, each from a new page in the SB), grammar reference, audioscripts, answer key.
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
PHOTOS = ROOT / "assets" / "photos"
USED_PHOTOS = []


@lru_cache(maxsize=None)
def credits():
    f = PHOTOS / "credits.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def photo_uri(name):
    import base64
    if name not in USED_PHOTOS:
        USED_PHOTOS.append(name)
    return "data:image/jpeg;base64," + base64.b64encode((PHOTOS / f"{name}.jpg").read_bytes()).decode()


def credit(name):
    c = credits().get(name)
    return f"Photo: {e(c['photographer'])} / Unsplash" if c else ""


def photo(name, h=36, cls="ph"):
    alt = e(credits().get(name, {}).get("alt", ""))
    return (f'<figure class="{cls}"><img src="{photo_uri(name)}" alt="{alt}" style="height:{h}mm">'
            f'<figcaption>{credit(name)}</figcaption></figure>')


def md(s):
    s = e(str(s), quote=False)
    s = re.sub(r"~~(.+?)~~", r"<s>\1</s>", s)
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
        two = " two" if k == "short" and len(its) >= 4 and all(len(it["q"]) <= 14 for it in its) else ""
        if k in ("order", "correct") and all(len(it["q"]) <= 32 for it in its):
            two = " inl"
        return f'<ol class="xl {k}{two}">{"".join(rows)}</ol>'
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
        two = " two" if len(its) >= 4 and all(len(it["q"]) <= 16 for it in its) else ""
        return f'<ol class="xl choose{two}">{"".join(rows)}</ol>'
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
            out += checkwork(ex["checklist"])
        return out
    raise ValueError(f"unknown exercise kind {k}")


SKILL = {k: v[0] for k, v in SECTION.items()}


def bubbles(items):
    if not items:
        return ""
    return '<div class="bubs">' + "".join(f'<span class="bub b{i % 2}">{md(t)}</span>' for i, t in enumerate(items)) + "</div>"


def exercise(ex, num, ctx):
    n = num.next()
    ex["_n"], ex["_code"] = n, ctx["code"]
    bank = '<p class="bank">' + "".join(f"<span>{e(w)}</span>" for w in ex["bank"]) + "</p>" if ex.get("bank") else ""
    example = f'<p class="exl"><b>Example:</b> {md(ex["example"])}</p>' if ex.get("example") else ""
    note = f'<p class="exl">{md(ex["note"])}</p>' if ex.get("note") else ""
    chips = f'<span class="chip">{e(ex["chip"])}</span>' if ex.get("chip") else ""
    if ex.get("audio"):
        chips = f'<span class="trk">{icon("headphones")} {ctx["tracks"].get(ex["audio"], ex["audio"])}</span>' + chips
    body = f'{example}{note}{bank}{ex_body(ex)}{bubbles(ex.get("bubbles"))}'
    if ex.get("task"):                                           # exam-practice page: task box only
        return (f'<div class="ex" id="{ex["id"]}"><div class="xhead"><b class="xn">{n}</b><p>{chips}Do the exam task.</p></div>'
                f'<div class="task"><h5>{e(ex["task"].upper())} exam task</h5><div class="tb"><p class="ti">{md(ex["instruction"])}</p>{body}</div></div></div>')
    if ex.get("exam"):
        kind = SKILL.get(ctx["kind"], "IELTS")
        return (f'<div class="ex" id="{ex["id"]}"><div class="xhead"><b class="xn">{n}</b><p>{chips}Do the IELTS task.</p></div>'
                f'<div class="task"><h5>{e(ex.get("label") or f"IELTS {kind.title()} task")}</h5><div class="tb"><p class="ti">{md(ex["instruction"])}</p>{body}</div></div></div>')
    return (f'<div class="ex k-{ex["kind"]}" id="{ex["id"]}"><div class="xhead"><b class="xn">{n}</b><p>{chips}{md(ex["instruction"])}</p></div>'
            f'{body}</div>')


# ---------- other blocks ----------
def checklist(b):
    return (f'<div class="ck"><h5>{e(b.get("title", "Checklist"))}</h5><ul>'
            + "".join(f"<li><i></i>{md(x)}</li>" for x in b["items"]) + "</ul></div>")


def checkwork(items):
    return ('<div class="cw"><h5>Check your work</h5><ul>' + "".join(f"<li><i></i>{md(x)}</li>" for x in items) + "</ul></div>")


def box(b):
    st = b.get("style", "tip")
    if st == "errors":
        inner = "".join(f'<div class="er"><p><span class="w">✗ {e(x["wrong"])}</span><span class="r">✓ {e(x["right"])}</span></p>'
                        f'<p class="uz">{e(x["uz"])}</p></div>' for x in b["items"])
        return f'<div class="side errs"><span class="slab">Common errors</span><div class="sbody">{inner}</div></div>'
    items = "<ul>" + "".join(f"<li>{md(x)}</li>" for x in b["items"]) + "</ul>"
    title = re.sub(r"^Exam skill:\s*", "", b["title"])
    if st == "exam":
        return f'<div class="strat"><h5>IELTS strategy<span>{e(title)}</span></h5><div class="sb">{items}</div></div>'
    return f'<div class="look"><h5>Look out!<span>{e(title)}</span></h5>{items}</div>'


def block(b, ctx):
    t = b["type"]
    if t == "text":
        return f'<p class="tx">{md(b["text"])}</p>'
    if t == "subhead":
        return f'<h4 class="subh">{e(b["text"])}</h4>'
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
        return ""                                   # tracks are shown in the lesson header and on each exercise
    if t == "passage":
        paras = "".join((f'<p class="pp"><b class="who">{e(p["head"])}</b>' if p.get("head") else '<p class="pp">') + f'{md(p["text"])}</p>'
                        for p in b["paras"])
        intro = f'<p class="pin">{md(b["intro"])}</p>' if b.get("intro") else ""
        pic = photo(b["photo"], b.get("photo_h", 30), "ph in") if b.get("photo") else ""
        return f'<div class="psg split">{pic}<h4 class="ptitle">{e(b["title"])}</h4>{intro}{paras}</div>'
    if t == "photo":
        return photo(b["name"], b.get("h", 36))
    if t == "model":
        inner = "".join(f'<p><b>{e(w)}</b> {md(x)}</p>' for w, x in b["lines"]) if b.get("lines") else f'<p>{md(b["text"])}</p>'
        return f'<div class="model"><h5>{e(b["title"])}</h5>{inner}</div>'
    if t == "ex":
        return exercise(b, ctx["num"], ctx)
    if t == "checklist":
        return checklist(b)
    if t == "xref":
        return f'<p class="xref">›››&nbsp; GRAMMAR REFERENCE {b["ref"]}: PAGE <i data-ref="gr-{b["ref"]}"></i> &nbsp;‹‹‹</p>'
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


def section_tracks(s, tracks):
    ids = [b["id"] for b in s["blocks"] if b["type"] == "audio"]
    nums = [tracks[i] for i in ids if i in tracks]
    if not nums:
        return ""
    return nums[0] if len(nums) == 1 else f"{nums[0]}–{nums[-1]}"


def footer(label):
    return f'<footer><span class="pno"></span><span class="fl">{e(label)}</span></footer>'


def lesson_header(code, kind, title, goal, trk, compact=False):
    can = f'<p class="lcan">I can {md(goal)}.</p>' if goal else ""
    aud = (f'<div class="laud"><span class="qrph">QR</span><span>{icon("headphones")} {trk}</span></div>' if trk else "")
    cls = "lhc" if compact else "lh"
    return (f'<div class="{cls}"><div class="lcode">{code}</div><div class="lbar"><p><span class="ltag">{SKILL[kind]}</span>'
            f'<span class="ltitle">{e(title)}</span></p>{can}</div>{aud}</div>')


def unit_header(u, book):
    if book == "wb":
        return (f'<div class="uh wb"><div class="unum">{u["unit"]}</div><div><small>WORKBOOK</small><h1>{e(u["title"])}</h1></div>'
                f'<div class="uinc"><p>Extra practice for Student\'s Book Unit {u["unit"]}: new texts, new recordings and IELTS tasks.</p></div></div>')
    inc = "".join(f'<p><b>{k}</b> ' + " ".join(f"▪ {md(x)}" for x in v) + "</p>" for k, v in u.get("includes", {}).items())
    return (f'<div class="uh"><div class="unum">{u["unit"]}</div><h1>{e(u["title"])}</h1>'
            f'<div class="uinc"><h5>This unit includes</h5>{inc}</div></div>')


def unit_html(u, book):
    scripts = {s["id"]: s for s in u.get("scripts", [])}
    tracks = {sid: f'{u["unit"]}.{i:02d}' for i, sid in enumerate(scripts, 1)}
    u["_tracks"] = tracks
    counts = {}
    for s in u["sections"]:
        for b in s["blocks"]:
            if b["type"] == "ex" and s["kind"] not in ("exam", "check"):
                counts[s["kind"]] = counts.get(s["kind"], 0) + closed_count(b)
    n, label = u["unit"], f'Unit {u["unit"]} · {u["title"]}'
    ctx = {"scripts": scripts, "unit": u, "counts": counts, "tracks": tracks}
    out, letter, wb_body = [], 0, ""
    for i, s in enumerate(u["sections"]):
        kind = s["kind"]
        if kind in ("exam", "check"):
            code = "E" if kind == "exam" else ""
        else:
            code = f"{n}{L[letter]}"
            letter += 1
        s["_code"] = code
        ctx.update(num=Num(), code=code, kind=kind)
        inner = "".join(block(b, ctx) for b in s["blocks"])
        trk = section_tracks(s, tracks)
        if book == "wb":
            head = (f'<h3 class="ehc">{icon("check")} {e(s["title"])}</h3>' if kind == "check"
                    else lesson_header(code, kind, s["title"], s.get("goal"), trk, compact=True))
            wb_body += f'<div class="part sec s-{kind}">{head}{inner}</div>'
            continue
        if kind == "exam":
            head = (f'<div class="lh eh"><div class="lcode">{n}</div><div class="lbar"><p><span class="ltitle">IELTS Exam Practice</span></p>'
                    f'<p class="lcan">Unit {n} · {e(u["title"])} · {e(s.get("goal", ""))}</p></div>'
                    f'{f"""<div class="laud"><span class="qrph">QR</span><span>{icon("headphones")} {trk}</span></div>""" if trk else ""}</div>')
            out.append(f'<section class="page flow first exam s-exam" id="u{n}-exam">{head}<div class="cols"><div class="col">'
                       f'<div class="part">{inner}</div></div><div class="col"></div></div>{footer(f"IELTS Exam Practice {n}")}</section>')
            continue
        top = unit_header(u, book) if i == 0 else ""
        out.append(f'<section class="page flow first s-{kind}" id="u{n}-{code}">{top}{lesson_header(code, kind, s["title"], s.get("goal"), trk)}'
                   f'<div class="cols"><div class="col"><div class="part">{inner}</div></div><div class="col"></div></div>{footer(label)}</section>')
    if book == "wb":
        out.append(f'<section class="page flow first" id="u{n}">{unit_header(u, book)}<div class="cols"><div class="col">{wb_body}</div>'
                   f'<div class="col"></div></div>{footer(label)}</section>')
    return "".join(out)


def key_items(ex):
    k = ex["kind"]
    if k == "form":
        return [(n, a) for n, a in ex["answers"].items()]
    if k == "match":
        return [(i + 1, a) for i, a in enumerate(ex["a"])]
    return [(numbered(ex, i), it["a"]) for i, it in enumerate(items_of(ex))]


def grammar_reference(units):
    body = ""
    for u in units:
        for g in u.get("grammar_ref", []):
            gid = f'gr-{g["code"]}'
            first = gid not in body
            body += f'<h3 class="grh"{f" id={chr(34)}{gid}{chr(34)}" if first else ""}><span class="gcode">{g["code"]}</span>{md(g["title"])}</h3>'
            for pt in g["points"]:
                body += f'<div class="grp"><b class="gn">{pt["n"]}</b>'
                if pt.get("text"):
                    body += f'<p>{md(pt["text"])}</p>'
                if pt.get("table"):
                    t = pt["table"]
                    body += ('<table class="gt">' + "<tr>" + "".join(f"<th>{md(h)}</th>" for h in t["head"]) + "</tr>"
                             + "".join("<tr>" + "".join(f"<td>{md(c)}</td>" for c in r) + "</tr>" for r in t["rows"]) + "</table>")
                body += "".join(f'<p class="gex">{md(x)}</p>' for x in pt.get("ex", [])) + "</div>"
    return body


def back_matter(units, book):
    scripts, keys = "", ""
    for u in units:
        tracks = u["_tracks"]
        scripts += f'<h3 class="sh3">Unit {u["unit"]} · {e(u["title"])}</h3>'
        for s in u.get("scripts", []):
            scripts += f'<h4 class="sh4">{icon("headphones")} {tracks[s["id"]]} · {e(s["title"])}<small>{s["id"]}</small></h4>'
            scripts += "".join(f'<p>{f"<b>{e(w)}:</b> " if w else ""}{e(x)}</p>' for w, x in s["lines"])
            scripts += f'<p class="rn">Recording notes: {e(s["notes"])}</p>'
        keys += f'<h3 class="sh3">Unit {u["unit"]} · {e(u["title"])}</h3>'
        for sec in u["sections"]:
            exs = [b for b in sec["blocks"] if b["type"] == "ex"]
            if not exs:
                continue
            code = sec["_code"]
            keys += f'<h4 class="kh"><span class="gcode">{code}</span>{e("IELTS Exam Practice" if sec["kind"] == "exam" else sec["title"])}</h4>'
            for b in exs:
                ans = ("  ".join(f'<span><b>{n}</b> {md(a)}</span>' for n, a in key_items(b)) if b["kind"] in CLOSED
                       else "<span>Students' own answers.</span>")
                keys += f'<div class="krow"><b class="xn">{b["_n"]}</b><div>{ans}</div></div>'
    if USED_PHOTOS:
        keys += '<h3 class="sh3">Photo credits</h3><p class="cr">All photos from Unsplash (unsplash.com).</p>'
        keys += "".join(f'<p class="cr"><b>{e(credits()[n]["photographer"])}</b> '
                        f'<span>{e(credits()[n]["photo"].split("?")[0])}</span></p>' for n in USED_PHOTOS if n in credits())

    def sec(i, title, inner, cls):
        return (f'<section class="page flow first back {cls}" id="{i}"><div class="bh"><h1>{title}</h1></div>'
                f'<div class="cols"><div class="col"><div class="split {cls}">{inner}</div></div><div class="col"></div></div>{footer(title)}</section>')
    gr = grammar_reference(units)
    return ((sec("grammar", "Grammar Reference", gr, "gref") if gr else "")
            + sec("scripts", "Audioscripts", scripts, "script") + sec("key", "Answer Key", keys, "keys"))


def title_page(level, book, title):
    return (f'<section class="page tpage"><div class="tp"><small>IELTS PATHWAY</small><h1>{level.upper()}</h1><h2>{BOOK[book]}</h2>'
            f'<p>{e(title)}</p><p class="sub">Grammar · Vocabulary · Listening · Reading · Speaking · Writing<br>From the first words to IELTS</p></div>'
            f'{footer(f"IELTS Pathway {level.upper()} · {BOOK[book]}")}</section>')


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
