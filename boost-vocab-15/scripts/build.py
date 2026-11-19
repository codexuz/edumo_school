"""Build the 'Boost Your Vocabulary – Cambridge IELTS 15' article + vocabulary book interior -> dist/mock.html.

Data: data/lessons.json (made by scripts/prep.py). Each lesson = one half of a Test 1 reading passage:
the article with its key words highlighted, a word box (synonyms / opposites / definitions + Uzbek) and
five exercises. Back matter: answer key and an A–Z word list.
"""
import json
import random
import re

from blocks import DIST, ROOT, e
from icons import icon, topic_icon

L = "ABCDEFGHIJ"
RUN = "Boost Your Vocabulary · Cambridge IELTS 15"


def kw(t):
    return re.sub(r"\[\[(.+?)\]\]", r'<b class="kw">\1</b>', e(t, quote=False))


def part_head(pill, right, cls=""):
    return f'<div class="phead"><span class="pill {cls}">{pill}</span><span class="qr">{right}</span></div>'


def exhead(n, ic, title, sub):
    return (f'<div class="exh"><span class="exn">{n}</span><span class="exi">{icon(ic)}</span>'
            f'<div><b>{title}</b><small>{sub}</small></div></div>')


def article(les):
    head = part_head("READING", f'Passage {les["passage"]} · part {les["part"]} of 2 · {les["count"]} words')
    title = (f'<h3 class="atitle">{e(les["title"])}</h3>' if les["part"] == 1 else
             f'<h3 class="atitle">{e(les["title"])} <span class="cont">(continued)</span></h3>')
    ins = (f'<div class="ins"><span class="aud">{icon("book")}</span><p>Read the text. The <b class="kw">highlighted</b> words '
           'are explained in the <b>Word box</b>. Try to guess their meaning from the context first.</p></div>')
    if les["letters"]:
        paras = "".join(f'<p class="pp"><b class="pl">{l}</b><span>{kw(p)}</span></p>' for l, p in zip(les["letters"], les["paras"]))
    else:
        paras = "".join(f'<p class="pp np">{kw(p)}</p>' for p in les["paras"])
    return f'<div class="part">{head}{ins}{title}<div class="split art">{paras}</div></div>'


def word_box(les):
    rows = []
    for w in les["words"]:
        if w["syn"]:
            body = f'<span class="eq">=</span> {e(w["main"])}'
        else:
            body = f'<i>{e(w["main"])}</i>'
        ant = f' <span class="ne">≠ {e(", ".join(w["ant"]))}</span>' if w["ant"] else ""
        rows.append(f'<div class="wb"><div class="wt"><b>{e(w["term"])}</b><span class="uz">{e(w["uz"])}</span></div>'
                    f'<p>{body}{ant}</p></div>')
    return ('<div class="part">' + part_head("WORD BOX", f'{len(les["words"])} words · = synonyms · ≠ opposite', "teal")
            + f'<div class="split wbox">{"".join(rows)}</div></div>')


def shuffled(items, seed):
    out = list(items)
    random.Random(seed).shuffle(out)
    return out


def match_key(left, right_sorted):
    return [L[right_sorted.index(r)] for r in left]


def practice(les):
    ex, n = les["ex"], les["n"]
    out = ['<div class="part">' + part_head("PRACTICE", "Use the new words", "gold")]
    # 1 synonyms
    syns = shuffled([x["syn"] for x in ex["syn"]], n * 7)
    left = "".join(f'<li><b>{i}</b> {e(x["word"])} <span class="ab sm"></span></li>' for i, x in enumerate(ex["syn"], 1))
    right = "".join(f"<li><b>{L[k]}</b> {e(s)}</li>" for k, s in enumerate(syns))
    out.append(exhead(1, "swap", "Synonyms", f'Match the words (1–{len(ex["syn"])}) with their synonyms (A–{L[len(syns) - 1]}).')
               + f'<div class="vmatch"><ol>{left}</ol><ol>{right}</ol></div>')
    # 2 opposites
    opps = shuffled([x["opp"] for x in ex["opp"]], n * 11)
    left = "".join(f'<li><b>{i}</b> {e(x["word"])} <span class="ab sm"></span></li>' for i, x in enumerate(ex["opp"], 1))
    right = "".join(f"<li><b>{L[k]}</b> {e(s)}</li>" for k, s in enumerate(opps))
    out.append(exhead(2, "repeat", "Opposites", f'Match the words (1–{len(ex["opp"])}) with their opposites (A–{L[len(opps) - 1]}).')
               + f'<div class="vmatch opp"><ol>{left}</ol><ol>{right}</ol></div>')
    # 3 gap fill
    bank = sorted({g["a"] for g in ex["gap"]}, key=str.lower)
    gaps = "".join(f'<div class="qq"><b class="qn">{i}</b><p>{e(g["s"]).replace("______", "<span class=gapl></span>")}</p></div>'
                   for i, g in enumerate(ex["gap"], 1))
    out.append(exhead(3, "pen", "Complete the sentences", "Use a word from the box. Try first without looking at the text!")
               + '<div class="wbank">' + "".join(f"<span>{e(w)}</span>" for w in bank) + "</div>" + gaps)
    # 4 find the word
    finds = "".join(f'<div class="qq fw"><b class="qn">{i}</b><div><p>{e(f["def"])}</p><span class="hint">{e(f["h"])}</span></div></div>'
                    for i, f in enumerate(ex["find"], 1))
    out.append(exhead(4, "search", "Find the word", "Find a word or phrase in the text with this meaning. The first letters help you.") + finds)
    # 5 Uzbek -> English
    uzs = "".join(f'<div class="qq fw uzq"><b class="qn">{i}</b><div><p>{e(u["uz"])}</p><span class="hint">{e(u["h"])}</span></div></div>'
                  for i, u in enumerate(ex["uz"], 1))
    out.append(exhead(5, "chat", "O‘zbekcha → English", "Write the English word from the text.") + f'<div class="uzgrid">{uzs}</div>')
    out.append("</div>")
    return "".join(out)


def lesson_section(les):
    banner = (f'<div class="banner"><div class="girih"></div><div class="bl"><small>PASSAGE {les["passage"]} · PART {les["part"]}</small>'
              f'<h1>LESSON {les["n"]}</h1></div><div class="br"><b>{topic_icon(les["topic"], "ico bi")} {e(les["title"])}</b>'
              f'<span>{e(les["topic"])}</span></div></div>')
    body = article(les) + word_box(les) + practice(les)
    return (f'<section class="page flow first" data-run="Lesson {les["n"]}">{banner}<div class="cols"><div class="col">{body}</div>'
            f'<div class="col"></div></div><footer><span>{RUN} · Lesson {les["n"]}</span><span class="pno"></span></footer></section>')


def how_page(lessons):
    total = sum(len(l["words"]) for l in lessons)
    tips = [("book", "1 · Read the article", "Read like a newspaper. Guess the meaning of the highlighted words from the context."),
            ("list", "2 · Check the Word box", "Synonyms (=), opposites (≠), short definitions and the Uzbek meaning of every key word."),
            ("swap", "3 · Synonyms and opposites", "IELTS Reading often uses synonyms (paraphrase). Learn word pairs, not single words."),
            ("pen", "4 · Use the words", "Complete sentences from the text without looking, then check with the article."),
            ("search", "5 · Find and translate", "Find words from their definitions and from Uzbek – this is how you remember them."),
            ("check", "6 · Check and repeat", f"Check the answer key. Read the article again after 2–3 days. All {total} words are in the A–Z list.")]
    cards = "".join(f'<div class="tip"><span class="tipi">{icon(i)}</span><div><b>{t}</b><p>{d}</p></div></div>' for i, t, d in tips)
    rows = "".join(f'<tr><td>{l["n"]}</td><td class="tic">{topic_icon(l["topic"])} {e(l["title"])}</td>'
                   f'<td>Passage {l["passage"]} · part {l["part"]}</td><td>{len(l["words"])}</td></tr>' for l in lessons)
    return ('<section class="page howpage"><div class="banner"><div class="girih"></div><div class="bl"><small>CAMBRIDGE IELTS 15 · TEST 1</small>'
            f'<h1>HOW TO USE THIS BOOK</h1></div><div class="br"><b>{len(lessons)} lessons</b><span>Article + vocabulary + exercises</span></div></div>'
            '<p class="lead">This book turns the three <b>Academic Reading passages of Cambridge IELTS 15, Test 1</b> into six vocabulary lessons. '
            'Each lesson has the original article with the key academic words highlighted, a <b>Word box</b> with synonyms, opposites, '
            f'definitions and <b>Uzbek translations</b>, and <b>five exercises</b> to practise the words — {total} words in total.</p>'
            f'<div class="tips">{cards}</div>'
            f'<table class="plan"><tr><th>Lesson</th><th>Article</th><th>Part</th><th>Words</th></tr>{rows}</table>'
            '<p class="src">Reading passages: <i>Cambridge IELTS 15 Academic</i>, Test 1 (Cambridge University Press). '
            'Vocabulary notes based on <i>Boost Your Vocabulary – Cambridge IELTS 15</i>.</p>'
            f'<footer><span>{RUN}</span><span class="pno"></span></footer></section>')


def answer_key(lessons):
    body = ""
    for les in lessons:
        ex, n = les["ex"], les["n"]
        k1 = match_key([x["syn"] for x in ex["syn"]], shuffled([x["syn"] for x in ex["syn"]], n * 7))
        k2 = match_key([x["opp"] for x in ex["opp"]], shuffled([x["opp"] for x in ex["opp"]], n * 11))
        fmt = lambda xs: "  ".join(f"<b>{i}</b> {e(x)}" for i, x in enumerate(xs, 1))
        body += (f'<div class="kmock"><h3>Lesson {n} · {e(les["title"])}</h3><table>'
                 f'<tr><th>1 Synonyms</th><td>{fmt(k1)}</td></tr><tr><th>2 Opposites</th><td>{fmt(k2)}</td></tr>'
                 f'<tr><th>3 Sentences</th><td>{fmt([g["a"] for g in ex["gap"]])}</td></tr>'
                 f'<tr><th>4 Find the word</th><td>{fmt([f["a"] for f in ex["find"]])}</td></tr>'
                 f'<tr><th>5 O‘zbekcha</th><td>{fmt([u["a"] for u in ex["uz"]])}</td></tr></table></div>')
    return ('<section class="page flow" data-run="Answer key"><div class="banner small"><div class="girih"></div><div class="bl">'
            '<small>ALL LESSONS</small><h1>ANSWER KEY</h1></div><div class="br"><span>Exercises 1–5</span></div></div>'
            f'<div class="cols"><div class="col"><div class="split keys">{body}</div></div><div class="col"></div></div>'
            f'<footer><span>{RUN} · Answer key</span><span class="pno"></span></footer></section>')


def word_list(lessons):
    seen = {}
    for l in lessons:
        for w in l["words"]:
            k = (w["term"], w["uz"])
            seen.setdefault(k, []).append(str(l["n"]))
    words = sorted(((t, uz, ", ".join(dict.fromkeys(ns))) for (t, uz), ns in seen.items()), key=lambda x: x[0].lower())
    rows, cur = "", ""
    for w, uz, n in words:
        if w[0].upper() != cur:
            cur = w[0].upper()
            rows += f'<h4 class="wl">{cur}</h4>'
        rows += f'<div class="wrow"><b>{e(w)}</b><i></i><span>{e(uz)}</span><em>L{n}</em></div>'
    return ('<section class="page flow" data-run="Word list"><div class="banner small"><div class="girih"></div><div class="bl">'
            f'<small>{len(words)} WORDS</small><h1>WORD LIST A–Z</h1></div><div class="br"><span>English · O‘zbekcha · lesson</span></div></div>'
            f'<div class="cols"><div class="col"><div class="split">{rows}</div></div><div class="col"></div></div>'
            f'<footer><span>{RUN} · Word list</span><span class="pno"></span></footer></section>')


def build():
    lessons = json.loads((ROOT / "data" / "lessons.json").read_text(encoding="utf-8"))
    pages = [how_page(lessons)] + [lesson_section(l) for l in lessons] + [answer_key(lessons), word_list(lessons)]
    css = "".join((ROOT / "scripts" / f).read_text(encoding="utf-8") for f in ("style.css", "reading.css", "vocab.css"))
    fonts = ('<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700;800'
             '&family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&display=block" rel="stylesheet">')
    DIST.mkdir(exist_ok=True)
    (DIST / "mock.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Boost Your Vocabulary – Cambridge IELTS 15</title>'
                                    f'{fonts}<style>{css}</style></head><body>{"".join(pages)}</body></html>', encoding="utf-8")
    print("lessons:", len(lessons))


if __name__ == "__main__":
    build()
