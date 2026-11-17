"""Build the IELTS-style A2 Reading Practice book interior (A4, two columns, Mock-book design) -> dist/mock.html.

Per unit (data/units/NN.json): vocabulary preview, a 5-paragraph passage (A–E), Questions 1–13 in IELTS formats
(TRUE/FALSE/NOT GIVEN, multiple choice, which paragraph, one-word completion), then two vocabulary exercises.
Back matter: answer key and an A–Z word list.
"""
import json
import random

from blocks import DIST, EMOJI, ROOT, e

UNITS = sorted((ROOT / "data" / "units").glob("*.json"))
L = "ABCDEFGH"


def part_head(pill, right, cls=""):
    return f'<div class="phead"><span class="pill {cls}">{pill}</span><span class="qr">{right}</span></div>'


def vocab_preview(u):
    rows = "".join(f'<div class="vrow"><b>{e(v["word"])}</b><i>{e(v["pos"])}</i><span class="uz">{e(v["uz"])}</span>'
                   f'<p>{e(v["ex"])}</p></div>' for v in u["vocab"])
    return ('<div class="part">' + part_head("VOCABULARY", "12 key words")
            + f'<div class="vlist">{rows}</div></div>')


def passage(u):
    words = sum(len(p.split()) for p in u["passage"])
    paras = "".join(f'<p class="pp"><b class="pl">{L[i]}</b>{e(p)}</p>' for i, p in enumerate(u["passage"]))
    return ('<div class="part">' + part_head("READING", f"{words} words")
            + '<div class="ins"><span class="aud">⏱</span><p>You should spend about 20 minutes on <b>Questions 1–13</b>, '
              'which are based on the reading passage below.</p></div>'
            + f'<p class="intro">{e(u["intro"])}</p><h3 class="atitle">{e(u["title"])}</h3>'
            + f'<div class="split art">{paras}</div></div>')


def questions(u):
    out = ['<div class="part">' + part_head("QUESTIONS 1–13", "IELTS-style tasks")]
    out.append('<h4 class="subt">Questions 1–5</h4><div class="ins"><p>Do the following statements agree with the information in the passage? Write</p></div>'
               '<div class="tfkey"><span><b>TRUE</b> if the statement agrees with the information</span>'
               '<span><b>FALSE</b> if the statement contradicts the information</span>'
               '<span><b>NOT GIVEN</b> if there is no information on this</span></div>')
    out += [f'<div class="qq"><b class="qn">{i}</b><p>{e(q["q"])}</p><span class="ab"></span></div>' for i, q in enumerate(u["tfng"], 1)]
    out.append('<h4 class="subt">Questions 6–8</h4><div class="ins"><p>Choose the correct letter, <b>A</b>, <b>B</b> or <b>C</b>.</p></div>')
    for i, q in enumerate(u["mcq"], 6):
        opts = "".join(f"<li><b>{L[k]}</b> {e(o)}</li>" for k, o in enumerate(q["options"]))
        out.append(f'<div class="qq mc"><b class="qn">{i}</b><div><p>{e(q["q"])}</p><ul>{opts}</ul></div></div>')
    out.append('<h4 class="subt">Questions 9–10</h4><div class="ins"><p>The passage has five paragraphs, <b>A–E</b>. '
               'Which paragraph contains the following information? Write the correct letter, <b>A–E</b>.</p></div>')
    out += [f'<div class="qq"><b class="qn">{i}</b><p>{e(q["q"])}</p><span class="ab sm"></span></div>' for i, q in enumerate(u["which_para"], 9)]
    out.append('<h4 class="subt">Questions 11–13</h4><div class="ins"><p>Complete the sentences. Choose <b>ONE WORD ONLY</b> from the passage for each answer.</p></div>')
    out += [f'<div class="qq"><b class="qn">{i}</b><p>{e(q["q"]).replace("______", f"<span class=gapn>{i}</span>")}</p></div>'
            for i, q in enumerate(u["completion"], 11)]
    out.append("</div>")
    return "".join(out)


def match_order(u):
    items = u["vocab_match"]
    meanings = [m["meaning"] for m in items]
    random.Random(u["n"] * 31).shuffle(meanings)
    key = [L[meanings.index(m["meaning"])] for m in items]
    return items, meanings, key


def vocab_practice(u):
    items, meanings, _ = match_order(u)
    left = "".join(f'<li><b>{i}</b> {e(m["word"])} <span class="ab sm"></span></li>' for i, m in enumerate(items, 1))
    right = "".join(f"<li><b>{L[k]}</b> {e(m)}</li>" for k, m in enumerate(meanings))
    bank = sorted({g["a"] for g in u["gapfill"]} | {v["word"] for v in u["vocab"][:8]}, key=str.lower)
    gaps = "".join(f'<div class="qq"><b class="qn">{i}</b><p>{e(g["s"]).replace("______", "<span class=gapl></span>")}</p></div>'
                   for i, g in enumerate(u["gapfill"], 1))
    return ('<div class="part">' + part_head("VOCABULARY PRACTICE", "Use the new words", "gold")
            + '<h4 class="subt">A · Match the words (1–6) with their meanings (A–F).</h4>'
            + f'<div class="vmatch"><ol>{left}</ol><ol>{right}</ol></div>'
            + '<h4 class="subt">B · Complete the sentences with a word from the box.</h4>'
            + '<div class="wbank">' + "".join(f"<span>{e(w)}</span>" for w in bank) + "</div>" + gaps + "</div>")


def unit_section(u):
    banner = (f'<div class="banner"><div class="girih"></div><div class="bl"><small>IELTS READING · A2</small>'
              f'<h1>UNIT {u["n"]}</h1></div><div class="br"><b>{u["emoji"]} {e(u["topic"])}</b><span>{e(u["title"])}</span></div></div>')
    body = vocab_preview(u) + passage(u) + questions(u) + vocab_practice(u)
    return (f'<section class="page flow first" data-run="Unit {u["n"]}">{banner}<div class="cols"><div class="col">{body}</div>'
            f'<div class="col"></div></div><footer><span>IELTS Reading Practice · A2 · Unit {u["n"]}</span><span class="pno"></span></footer></section>')


def how_page(units):
    tips = [("📖", "Before you read", "Learn the 12 words in the vocabulary box. Say them aloud and read the examples."),
            ("⏱", "Read in 20 minutes", "Like the real IELTS test: read the passage and answer Questions 1–13 in about 20 minutes."),
            ("✅", "TRUE / FALSE / NOT GIVEN", "FALSE means the passage says the opposite. NOT GIVEN means the passage does not say."),
            ("🔤", "One word only", "In sentence completion, copy one word from the passage. Check the spelling!"),
            ("🔁", "Practise the words", "Do the two vocabulary exercises, then check all answers in the key at the back."),
            ("📚", "Word list", "All 144 words with their Uzbek meanings are in the A–Z word list at the end of the book.")]
    cards = "".join(f'<div class="tip"><span>{i}</span><div><b>{t}</b><p>{d}</p></div></div>' for i, t, d in tips)
    rows = "".join(f'<tr><td>{u["n"]}</td><td>{u["emoji"]} {e(u["topic"])}</td><td>{e(u["title"])}</td></tr>' for u in units)
    return ('<section class="page howpage"><div class="banner"><div class="girih"></div><div class="bl"><small>IELTS READING · A2</small>'
            f'<h1>HOW TO USE THIS BOOK</h1></div><div class="br"><b>{len(units)} units</b><span>Reading + vocabulary</span></div></div>'
            f'<p class="lead">This book helps you start preparing for <b>IELTS Reading</b> at <b>A2 level</b>. Every unit has an interesting text, '
            f'the same question types as the real IELTS test, and <b>12 new words</b> with Uzbek translations.</p>'
            f'<div class="tips">{cards}</div>'
            f'<table class="plan"><tr><th>Unit</th><th>Topic</th><th>Reading passage</th></tr>{rows}</table>'
            '<footer><span>IELTS Reading Practice · A2</span><span class="pno"></span></footer></section>')


def answer_key(units):
    body = ""
    for u in units:
        r = ([f"<b>{i}</b> {q['a']}" for i, q in enumerate(u["tfng"], 1)] + [f"<b>{i}</b> {q['a']}" for i, q in enumerate(u["mcq"], 6)]
             + [f"<b>{i}</b> {q['a']}" for i, q in enumerate(u["which_para"], 9)] + [f"<b>{i}</b> {e(q['a'])}" for i, q in enumerate(u["completion"], 11)])
        _, _, key = match_order(u)
        va = "  ".join(f"<b>{i}</b> {k}" for i, k in enumerate(key, 1))
        vb = "  ".join(f"<b>{i}</b> {e(g['a'])}" for i, g in enumerate(u["gapfill"], 1))
        body += (f'<div class="kmock"><h3>Unit {u["n"]} · {e(u["topic"])}</h3><table>'
                 f'<tr><th>Reading</th><td>{"  ".join(r)}</td></tr><tr><th>Vocabulary A</th><td>{va}</td></tr>'
                 f'<tr><th>Vocabulary B</th><td>{vb}</td></tr></table></div>')
    return ('<section class="page flow" data-run="Answer key"><div class="banner small"><div class="girih"></div><div class="bl">'
            '<small>ALL UNITS</small><h1>ANSWER KEY</h1></div><div class="br"><span>Reading 1–13 · Vocabulary A and B</span></div></div>'
            f'<div class="cols"><div class="col"><div class="split keys">{body}</div></div><div class="col"></div></div>'
            '<footer><span>IELTS Reading Practice · A2 · Answer key</span><span class="pno"></span></footer></section>')


def word_list(units):
    words = sorted(((v["word"], v["pos"], v["uz"], u["n"]) for u in units for v in u["vocab"]), key=lambda x: x[0].lower())
    rows, cur = "", ""
    for w, p, uz, n in words:
        if w[0].upper() != cur:
            cur = w[0].upper()
            rows += f'<h4 class="wl">{cur}</h4>'
        rows += f'<div class="wrow"><b>{e(w)}</b><i>{e(p)}</i><span>{e(uz)}</span><em>U{n}</em></div>'
    return ('<section class="page flow" data-run="Word list"><div class="banner small"><div class="girih"></div><div class="bl">'
            f'<small>{len(words)} WORDS</small><h1>WORD LIST A–Z</h1></div><div class="br"><span>English · part of speech · O‘zbekcha · unit</span></div></div>'
            f'<div class="cols"><div class="col"><div class="split">{rows}</div></div><div class="col"></div></div>'
            '<footer><span>IELTS Reading Practice · A2 · Word list</span><span class="pno"></span></footer></section>')


def build():
    units = [json.loads(p.read_text(encoding="utf-8")) for p in UNITS]
    pages = [how_page(units)] + [unit_section(u) for u in units] + [answer_key(units), word_list(units)]
    css = (ROOT / "scripts" / "style.css").read_text(encoding="utf-8") + (ROOT / "scripts" / "reading.css").read_text(encoding="utf-8")
    fonts = ('<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700;800'
             '&family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&display=block" rel="stylesheet">')
    body = EMOJI.sub(r'<span class="em">\1</span>', "".join(pages))
    DIST.mkdir(exist_ok=True)
    (DIST / "mock.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>IELTS Reading Practice A2</title>'
                                    f'{fonts}<style>{css}</style></head><body>{body}</body></html>', encoding="utf-8")
    print("units:", len(units))


if __name__ == "__main__":
    build()
