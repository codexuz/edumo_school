"""Build the IELTS Reading Practice B1+ book interior (A4, two columns, Mock-book design) -> dist/mock.html.

Per unit (data/units/NN.json): vocabulary preview, a 7-paragraph passage (A–G), Questions 1–13 in three IELTS task groups
(any of: matching headings, T/F/NG, Y/N/NG, multiple choice, matching information / features, sentence endings,
summary / sentence / note completion, short answers), then two vocabulary exercises.
Back matter: answer key and an A–Z word list.
"""
import html
import json
import random
import re
from pathlib import Path

from icons import icon, topic_icon

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
UNITS = sorted((ROOT / "data" / "units").glob("*.json"))
NAME = "IELTS Reading Practice · B1+"
L = "ABCDEFGHIJ"
ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"]
e = html.escape
GAP = re.compile(r"_{4,}")


def md(s):
    s = e(str(s), quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def part_head(pill, right, cls=""):
    return f'<div class="phead"><span class="pill {cls}">{pill}</span><span class="qr">{right}</span></div>'


def vocab_preview(u):
    rows = "".join(f'<div class="vrow"><b>{e(v["word"])}</b><i>{e(v["pos"])}</i><span class="uz">{e(v["uz"])}</span>'
                   f'<p>{e(v["ex"])}</p></div>' for v in u["vocab"])
    return '<div class="part">' + part_head("VOCABULARY", "15 key words") + f'<div class="vlist">{rows}</div></div>'


def passage(u):
    words = sum(len(p.split()) for p in u["passage"])
    paras = "".join(f'<p class="pp"><b class="pl">{L[i]}</b>{e(p)}</p>' for i, p in enumerate(u["passage"]))
    return ('<div class="part">' + part_head("READING PASSAGE", f"{words} words")
            + f'<div class="ins"><span class="aud">{icon("timer")}</span><p>You should spend about 20 minutes on <b>Questions 1–13</b>, '
              'which are based on the reading passage below.</p></div>'
            + f'<p class="intro">{e(u["intro"])}</p><h3 class="atitle">{e(u["title"])}</h3>'
            + f'<div class="split art">{paras}</div></div>')


# ---------- question groups ----------
def count(g):
    t = g["type"]
    if t == "headings":
        return len(g["paras"])
    if t in ("summary", "notes"):
        return len(g["a"])
    return len(g["items"])


def rng(a, b):
    return f"Question {a}" if a == b else f"Questions {a}–{b}"


def ins(text):
    return f'<div class="ins"><p>{text}</p></div>'


def ab(sm=False):
    return f'<span class="ab{" sm" if sm else ""}"></span>'


def numbered_gaps(text, start):
    k = [start]

    def rep(_):
        n = k[0]
        k[0] += 1
        return f'<span class="gapn">{n}</span>'
    return GAP.sub(rep, md(text))


def group_html(g, s, last):
    t, head = g["type"], f'<h4 class="subt">{rng(s, last)}</h4>'
    out = [head]
    if t == "headings":
        out.append(ins(f'The reading passage has seven paragraphs, <b>A–G</b>. Choose the correct heading for paragraphs '
                       f'<b>{g["paras"][0]}–{g["paras"][-1]}</b> from the list of headings below. Write the correct number, '
                       f'<b>i–{ROMAN[len(g["options"]) - 1]}</b>.'))
        opts = "".join(f'<li><b>{ROMAN[i]}</b> {md(o)}</li>' for i, o in enumerate(g["options"]))
        out.append(f'<div class="hbox"><h5>List of Headings</h5><ul>{opts}</ul></div>')
        out += [f'<div class="qq"><b class="qn">{s + i}</b><p>Paragraph <b>{p}</b></p>{ab()}</div>' for i, p in enumerate(g["paras"])]
    elif t in ("tfng", "ynng"):
        if t == "tfng":
            out.append(ins('Do the following statements agree with the information given in the reading passage? Write'))
            key = [("TRUE", "if the statement agrees with the information"), ("FALSE", "if the statement contradicts the information"),
                   ("NOT GIVEN", "if there is no information on this")]
        else:
            out.append(ins('Do the following statements agree with the views of the writer? Write'))
            key = [("YES", "if the statement agrees with the views of the writer"), ("NO", "if the statement contradicts the views of the writer"),
                   ("NOT GIVEN", "if it is impossible to say what the writer thinks about this")]
        out.append('<div class="tfkey">' + "".join(f"<span><b>{a}</b> {b}</span>" for a, b in key) + "</div>")
        out += [f'<div class="qq"><b class="qn">{s + i}</b><p>{md(q["q"])}</p>{ab()}</div>' for i, q in enumerate(g["items"])]
    elif t == "mcq":
        out.append(ins('Choose the correct letter, <b>A</b>, <b>B</b>, <b>C</b> or <b>D</b>.'))
        for i, q in enumerate(g["items"]):
            opts = "".join(f"<li><b>{L[k]}</b> {md(o)}</li>" for k, o in enumerate(q["options"]))
            out.append(f'<div class="qq mc"><b class="qn">{s + i}</b><div><p>{md(q["q"])}</p><ul>{opts}</ul></div></div>')
    elif t == "matching_info":
        out.append(ins('The reading passage has seven paragraphs, <b>A–G</b>. Which paragraph contains the following information? '
                       'Write the correct letter, <b>A–G</b>.<br><i>NB You may use any letter more than once.</i>'))
        out += [f'<div class="qq"><b class="qn">{s + i}</b><p>{md(q["q"])}</p>{ab(True)}</div>' for i, q in enumerate(g["items"])]
    elif t == "matching_features":
        n = len(g["features"])
        out.append(ins(f'{md(g.get("instruction", "Match each statement with the correct person"))}, <b>A–{L[n - 1]}</b>. '
                       f'Write the correct letter, <b>A–{L[n - 1]}</b>.<br><i>NB You may use any letter more than once.</i>'))
        out.append(f'<div class="hbox"><h5>{e(g.get("box_title", "List of People"))}</h5><ul>'
                   + "".join(f"<li><b>{L[i]}</b> {md(f)}</li>" for i, f in enumerate(g["features"])) + "</ul></div>")
        out += [f'<div class="qq"><b class="qn">{s + i}</b><p>{md(q["q"])}</p>{ab(True)}</div>' for i, q in enumerate(g["items"])]
    elif t == "sentence_endings":
        n = len(g["endings"])
        out.append(ins(f'Complete each sentence with the correct ending, <b>A–{L[n - 1]}</b>, below. Write the correct letter, <b>A–{L[n - 1]}</b>.'))
        out += [f'<div class="qq"><b class="qn">{s + i}</b><p>{md(q["q"])}</p>{ab(True)}</div>' for i, q in enumerate(g["items"])]
        out.append('<div class="hbox ends"><ul>' + "".join(f"<li><b>{L[i]}</b> {md(x)}</li>" for i, x in enumerate(g["endings"])) + "</ul></div>")
    elif t == "summary":
        if g.get("box"):
            n = len(g["box"])
            out.append(ins(f'Complete the summary using the list of words, <b>A–{L[n - 1]}</b>, below. Write the correct letter, <b>A–{L[n - 1]}</b>.'))
        else:
            out.append(ins(f'Complete the summary below. Choose <b>{g["limit"]}</b> from the passage for each answer.'))
        out.append(f'<div class="sumbox"><h5>{e(g["title"])}</h5><p>{numbered_gaps(g["text"], s)}</p></div>')
        if g.get("box"):
            out.append('<div class="wbank lettered">' + "".join(f"<span><b>{L[i]}</b> {e(w)}</span>" for i, w in enumerate(g["box"])) + "</div>")
    elif t in ("completion", "short"):
        if t == "completion":
            out.append(ins(f'Complete the sentences below. Choose <b>{g["limit"]}</b> from the passage for each answer.'))
            out += [f'<div class="qq"><b class="qn">{s + i}</b><p>{GAP.sub(f"<span class=gapn>{s + i}</span>", md(q["q"]))}</p></div>'
                    for i, q in enumerate(g["items"])]
        else:
            out.append(ins(f'Answer the questions below. Choose <b>{g["limit"]}</b> from the passage for each answer.'))
            out += [f'<div class="qq sa"><b class="qn">{s + i}</b><p>{md(q["q"])}</p><span class="aline"></span></div>'
                    for i, q in enumerate(g["items"])]
    elif t == "notes":
        out.append(ins(f'Complete the notes below. Choose <b>{g["limit"]}</b> from the passage for each answer.'))
        k = [s]

        def line(x):
            h = numbered_gaps(x, k[0])
            k[0] += x.count("______")
            return f'<li>{h}</li>'
        out.append(f'<div class="sumbox notes"><h5>{e(g["title"])}</h5><ul>{"".join(line(x) for x in g["lines"])}</ul></div>')
    else:
        raise ValueError(t)
    return "".join(out)


def questions(u):
    out, s = ['<div class="part">' + part_head("QUESTIONS 1–13", "IELTS Academic tasks")], 1
    for g in u["groups"]:
        n = count(g)
        out.append(group_html(g, s, s + n - 1))
        s += n
    out.append("</div>")
    return "".join(out)


def answers(u):
    res, s = [], 1
    for g in u["groups"]:
        t = g["type"]
        if t == "headings":
            vals = g["a"]
        elif t in ("summary", "notes"):
            vals = g["a"]
        else:
            vals = [q["a"] for q in g["items"]]
        if t == "summary" and g.get("box"):
            vals = [f'{v} ({g["box"][L.index(v)]})' for v in vals]
        res += [(s + i, v) for i, v in enumerate(vals)]
        s += len(vals)
    return res


def match_order(u):
    items = u["vocab_match"]
    meanings = [m["meaning"] for m in items]
    random.Random(u["n"] * 37).shuffle(meanings)
    return items, meanings, [L[meanings.index(m["meaning"])] for m in items]


def vocab_practice(u):
    items, meanings, _ = match_order(u)
    left = "".join(f'<li><b>{i}</b> {e(m["word"])} <span class="ab sm"></span></li>' for i, m in enumerate(items, 1))
    right = "".join(f"<li><b>{L[k]}</b> {e(m)}</li>" for k, m in enumerate(meanings))
    used = {g["a"] for g in u["gapfill"]} | {m["word"] for m in u["vocab_match"]}
    extra = [v["word"] for v in u["vocab"] if v["word"] not in used][:2]     # two distractors
    bank = sorted({g["a"] for g in u["gapfill"]} | set(extra), key=str.lower)
    gaps = "".join(f'<div class="qq"><b class="qn">{i}</b><p>{e(g["s"]).replace("______", "<span class=gapl></span>")}</p></div>'
                   for i, g in enumerate(u["gapfill"], 1))
    return ('<div class="part">' + part_head("VOCABULARY PRACTICE", "Use the new words", "gold")
            + '<h4 class="subt">A · Match the words (1–6) with their meanings (A–F).</h4>'
            + f'<div class="vmatch"><ol>{left}</ol><ol>{right}</ol></div>'
            + '<h4 class="subt">B · Complete the sentences with a word from the box.</h4>'
            + '<div class="wbank">' + "".join(f"<span>{e(w)}</span>" for w in bank) + "</div>" + gaps + "</div>")


TYPE_NAME = {"headings": "Matching headings", "tfng": "True / False / Not Given", "ynng": "Yes / No / Not Given",
             "mcq": "Multiple choice", "matching_info": "Matching information", "matching_features": "Matching features",
             "sentence_endings": "Sentence endings", "summary": "Summary completion", "completion": "Sentence completion",
             "short": "Short answers", "notes": "Note completion"}


def unit_section(u):
    tasks = " · ".join(TYPE_NAME[g["type"]] for g in u["groups"])
    banner = (f'<div class="banner unitb"><div class="girih"></div><div class="bl"><small>IELTS READING · B1+</small>'
              f'<h1>UNIT {u["n"]}</h1></div><div class="br"><b>{topic_icon(u["topic"], "ico bi")} {e(u["topic"])}</b>'
              f'<span>{e(u["title"])}</span></div></div><p class="tasks"><b>Task types:</b> {tasks}</p>')
    body = vocab_preview(u) + passage(u) + questions(u) + vocab_practice(u)
    return (f'<section class="page flow first" id="u{u["n"]}">{banner}<div class="cols"><div class="col">{body}</div>'
            f'<div class="col"></div></div><footer><span>{NAME} · Unit {u["n"]}</span><span class="pno"></span></footer></section>')


def how_page(units):
    tips = [("book", "Learn the words first", "Study the 15 key words with their Uzbek meanings before you read. They all appear in the passage."),
            ("timer", "20 minutes per passage", "The real test has three passages in 60 minutes. Practise reading a 630-word passage and answering 13 questions in 20 minutes."),
            ("list", "Skim, then scan", "Read the title and the first lines of each paragraph for the main ideas. Then scan for names, numbers and key words."),
            ("check", "TRUE / FALSE / NOT GIVEN", "FALSE: the passage says the opposite. NOT GIVEN: the passage does not say. YES / NO / NOT GIVEN asks about the writer's opinions."),
            ("type", "Watch the word limit", "\"NO MORE THAN TWO WORDS\" means one or two words. Copy them from the passage and spell them correctly."),
            ("repeat", "Look for paraphrase", "Questions rarely use the same words as the passage. Look for synonyms: rise = increase, a few = a small number.")]
    cards = "".join(f'<div class="tip"><span class="tipi">{icon(i)}</span><div><b>{t}</b><p>{d}</p></div></div>' for i, t, d in tips)
    rows = "".join(f'<tr><td>{u["n"]}</td><td class="tic">{topic_icon(u["topic"])} {e(u["topic"])}</td><td>{e(u["title"])}</td>'
                   f'<td class="tt">{" · ".join(TYPE_NAME[g["type"]] for g in u["groups"])}</td><td class="pg"><i data-ref="u{u["n"]}"></i></td></tr>'
                   for u in units)
    return ('<section class="page howpage"><div class="banner"><div class="girih"></div><div class="bl"><small>IELTS READING · B1+</small>'
            f'<h1>HOW TO USE THIS BOOK</h1></div><div class="br"><b>{len(units)} units</b><span>{13 * len(units)} questions</span></div></div>'
            '<p class="lead">This book takes you from B1 towards the level of the real <b>IELTS Academic Reading</b> test. Each unit has a '
            '<b>passage of about 630 words</b> and <b>13 questions</b> in three IELTS task types, so you practise every task type in the test several times, '
            'plus <b>15 key words</b> with Uzbek translations.</p>'
            f'<div class="tips">{cards}</div>'
            f'<table class="plan"><tr><th>Unit</th><th>Topic</th><th>Passage</th><th>Task types</th><th>Page</th></tr>{rows}</table>'
            f'<footer><span>{NAME}</span><span class="pno"></span></footer></section>')


def answer_key(units):
    body = ""
    for u in units:
        r = "  ".join(f"<span><b>{n}</b> {e(a)}</span>" for n, a in answers(u))
        _, _, key = match_order(u)
        va = "  ".join(f"<span><b>{i}</b> {k}</span>" for i, k in enumerate(key, 1))
        vb = "  ".join(f"<span><b>{i}</b> {e(g['a'])}</span>" for i, g in enumerate(u["gapfill"], 1))
        body += (f'<div class="kmock"><h3>Unit {u["n"]} · {e(u["title"])}</h3><table>'
                 f'<tr><th>Reading</th><td>{r}</td></tr><tr><th>Vocabulary A</th><td>{va}</td></tr>'
                 f'<tr><th>Vocabulary B</th><td>{vb}</td></tr></table></div>')
    return ('<section class="page flow first" id="key"><div class="banner small"><div class="girih"></div><div class="bl">'
            '<small>ALL UNITS</small><h1>ANSWER KEY</h1></div><div class="br"><span>Reading 1–13 · Vocabulary A and B</span></div></div>'
            f'<div class="cols"><div class="col"><div class="split keys">{body}</div></div><div class="col"></div></div>'
            f'<footer><span>{NAME} · Answer key</span><span class="pno"></span></footer></section>')


def word_list(units):
    words = sorted(((v["word"], v["pos"], v["uz"], u["n"]) for u in units for v in u["vocab"]), key=lambda x: x[0].lower())
    rows, cur = "", ""
    for w, p, uz, n in words:
        if w[0].upper() != cur:
            cur = w[0].upper()
            rows += f'<h4 class="wl">{cur}</h4>'
        rows += f'<div class="wrow"><b>{e(w)}</b><i>{e(p)}</i><span>{e(uz)}</span><em>U{n}</em></div>'
    return ('<section class="page flow first" id="words"><div class="banner small"><div class="girih"></div><div class="bl">'
            f'<small>{len(words)} WORDS</small><h1>WORD LIST A–Z</h1></div><div class="br"><span>English · part of speech · O‘zbekcha · unit</span></div></div>'
            f'<div class="cols"><div class="col"><div class="split">{rows}</div></div><div class="col"></div></div>'
            f'<footer><span>{NAME} · Word list</span><span class="pno"></span></footer></section>')


def build():
    units = [json.loads(p.read_text(encoding="utf-8")) for p in UNITS]
    pages = [how_page(units)] + [unit_section(u) for u in units] + [answer_key(units), word_list(units)]
    css = "".join((ROOT / "scripts" / f).read_text(encoding="utf-8") for f in ("style.css", "reading.css", "plus.css"))
    fonts = ('<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700;800'
             '&family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&display=block" rel="stylesheet">')
    DIST.mkdir(exist_ok=True)
    (DIST / "mock.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>IELTS Reading Practice B1+</title>'
                                    f'{fonts}<style>{css}</style></head><body>{"".join(pages)}</body></html>', encoding="utf-8")
    print("units:", len(units))


if __name__ == "__main__":
    build()
