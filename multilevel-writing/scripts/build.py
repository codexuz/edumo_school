"""Build "A Complete Guide to Multilevel Writing" as a single HTML document.

Usage: python3 scripts/build.py   ->  dist/multilevel-writing.html

The book is: cover · how to use · the Uzbek guide to the paper · band
descriptors · a marked sample · Exercises 1-10 (task page, three lined
answer pages, sample answers and vocabulary) · a closing checklist.
Data lives in data/*.json; the design tokens are in scripts/style.css.
"""
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

SCHOOL = "Impulse Learning Center"
TITLE = "A Complete Guide to Multilevel Writing"

e = html.escape
LOGO = "data:image/png;base64," + base64.b64encode(
    (ROOT / "assets" / "impulse-logo.png").read_bytes()).decode()

guide = json.loads((ROOT / "data" / "guide.json").read_text(encoding="utf-8"))
descriptors = json.loads((ROOT / "data" / "descriptors.json").read_text(encoding="utf-8"))
worked = json.loads((ROOT / "data" / "worked-sample.json").read_text(encoding="utf-8"))
exercises = [json.loads(p.read_text(encoding="utf-8"))
             for p in sorted((ROOT / "data").glob("exercise-*.json"))]

cover = []
out = []
add = out.append


def page(body, cls=""):
    add(f'<section class="page {cls}">{body}</section>')


def ptitle(title, kicker=""):
    k = f"<small>{e(kicker)}</small>" if kicker else ""
    return f'<div class="ptitle"><h2>{e(title)}</h2><div class="bar"></div>{k}</div>'


def lines(n):
    return '<div class="lines">' + '<div></div>' * n + '</div>'


def brand(light=True):
    ring = "border:2px solid #fff;" if light else ""
    return (f'<div class="brand"><img src="{LOGO}" width="38" height="38" alt="" '
            f'style="display:block;border-radius:50%;{ring}">'
            f'<div><div class="name">IMPULSE</div><div class="sub">LEARNING CENTER</div></div></div>')


# ---------------------------------------------------------------- cover
cover.append(f'''<section class="cover">
<div class="grid"></div><div class="glow g1"></div><div class="glow g2"></div>
{brand()}
<div style="height:24mm"></div>
<span class="kicker">MULTILEVEL · CEFR B1–C1</span>
<h1>A Complete Guide to<span>Multilevel Writing</span></h1>
<p class="tag">The writing paper explained part by part, with official band descriptors,
a marked script and ten full practice exercises — each with model answers and
an English–Uzbek word list.</p>
<div class="chips"><span>10 exercises</span><span>30 model answers</span>
<span>400 words &amp; phrases</span><span>Band descriptors</span><span>Uzbek support</span></div>
<div class="spacer"></div>
<div class="card">
  <div class="top">WHAT YOU WRITE</div>
  <div class="q">One situation, two emails — then an online discussion post.</div>
  <div class="parts">
    <div><b>TASK 1.1</b><i>50</i><em>words · informal</em></div>
    <div><b>TASK 1.2</b><i>120–150</i><em>words · formal</em></div>
    <div><b>TASK 2</b><i>180–200</i><em>words · discussion</em></div>
  </div>
</div>
<div class="foot"><span>{e(SCHOOL)}</span><span>Writing · 17 marks</span></div>
</section>''')

# ---------------------------------------------------------------- how to use
add(f'''<section class="page">
{ptitle("How to use this book", "START HERE")}
<p class="lead">Every exercise follows the same six-page cycle. Work through it in order — the
model answers only help once you have written your own.</p>
<div class="panel"><ol style="list-style:none">
<li style="margin:7px 0"><b style="color:var(--blue-d)">1 · Read the situation.</b>
One prompt letter sets up all three tasks. Underline what you are being asked to do —
most lost marks come from missing a question, not from weak English.</li>
<li style="margin:7px 0"><b style="color:var(--blue-d)">2 · Write Task 1.1 (about 50 words).</b>
A message to a friend. Informal, warm, and it must still answer the task.</li>
<li style="margin:7px 0"><b style="color:var(--blue-d)">3 · Write Task 1.2 (120–150 words).</b>
The same situation in a formal email. Keep the register consistent from first line to signature.</li>
<li style="margin:7px 0"><b style="color:var(--blue-d)">4 · Write Task 2 (180–200 words).</b>
An online discussion post: take a clear position, support it, and close it properly.</li>
<li style="margin:7px 0"><b style="color:var(--blue-d)">5 · Compare with the model answers.</b>
Do not copy them. Look at how each one is organised and what language carries the argument.</li>
<li style="margin:7px 0"><b style="color:var(--blue-d)">6 · Learn the word list.</b>
Twenty words and phrases per task, with Uzbek translations, taken from the models themselves.</li>
</ol></div>
<div class="cols2" style="margin-top:12px">
  <div class="note"><b>Word count</b>Examiners do not reward extra length. A 260-word
  Task 2 is not a better Task 2 — it is an unfinished one that ran out of control.</div>
  <div class="note"><b>Register</b>The single most common fault is a formal email that
  slips into chat ("Hi there", "Thanks a lot!") halfway through. Choose a register and hold it.</div>
</div>
<h4 class="sub">Marks at a glance</h4>
<div class="total">
  <div><b>TASK 1.1</b><i>5</i></div>
  <div><b>TASK 1.2</b><i>6</i></div>
  <div><b>TASK 2</b><i>6</i></div>
  <div><b>TOTAL</b><i>17</i></div>
</div>
</section>''')

# ---------------------------------------------------------------- the guide (Uzbek)
g = guide
b = [ptitle(g["title"], "YO'RIQNOMA"), f'<p class="lead">{e(g["intro"])}</p>',
     '<ul class="ticks">' + "".join(f"<li>{e(x)}</li>" for x in g["intro_list"]) + "</ul>"]
for sec in g["sections"]:
    b.append(f'<h3 class="sec"><span style="color:var(--blue)">{e(sec["kicker"])}:</span> {e(sec["title"])}</h3>')
    b.append(f'<p class="lead">{e(sec["lead"])}</p>')
    cards = []
    for c in sec["cards"]:
        facts = "".join(f"<tr><td>{e(k)}</td><td>{e(v)}</td></tr>" for k, v in c["facts"])
        req = "".join(f"<li>{e(x)}</li>" for x in c["req"])
        cards.append(f'''<div class="tcard"><div class="hd"><b>{e(c["label"])}</b><h4>{e(c["title"])}</h4></div>
<div class="bd"><table class="facts">{facts}</table>
<div class="req">{e(c["req_title"])}</div><ul class="ticks">{req}</ul></div></div>''')
    b.append(f'<div class="cols2">{"".join(cards)}</div>' if len(cards) > 1 else cards[0])
    if sec.get("note"):
        b.append(f'<div class="note"><b>{e(sec["note_title"])}</b>{e(sec["note"])}</div>')
    if sec.get("extra"):
        items = "".join(f"<li>{e(x)}</li>" for x in sec["extra"])
        b.append(f'<div class="panel"><h4 class="sub" style="margin-top:0">{e(sec["extra_title"])}</h4>'
                 f'<ul class="ticks">{items}</ul></div>')
    # one section per page: the two email cards alone fill an A4 page
    page("".join(b))
    b = [ptitle(g["title"] + " (davomi)", "YO'RIQNOMA")]

b = [ptitle(g["functions_title"], "TIL FUNKSIYALARI"), f'<p class="lead">{e(g["functions_lead"])}</p>',
     '<div class="panel"><ul class="ticks" style="columns:2;column-gap:16px">'
     + "".join(f"<li>{e(x)}</li>" for x in g["functions"]) + "</ul></div>"]
b.append(f'<h3 class="sec">{e(g["marking_title"])}</h3>')
marks = []
for m in g["marking"]:
    bands = "".join(f'<div class="band"><b>{e(k)}</b><span>{e(v)}</span></div>' for k, v in m["bands"])
    crit = "".join(f"<li>{e(x)}</li>" for x in m["criteria"])
    marks.append(f'''<div class="mark"><div class="hd"><h4>{e(m["title"])}</h4><span>{e(m["range"])}</span></div>
<div class="bd">{bands}<div class="req" style="margin-top:8px;font-size:8pt;font-weight:800;color:var(--navy);
letter-spacing:.1em;text-transform:uppercase">{e(m["criteria_title"])}</div>
<ul class="ticks">{crit}</ul></div></div>''')
b.append(f'<div class="cols2">{"".join(marks)}</div>')
b.append(f'<h3 class="sec">{e(g["conclusion_title"])}</h3><p class="lead">{e(g["conclusion_lead"])}</p>')
b.append('<ul class="ticks">' + "".join(f"<li>{e(x)}</li>" for x in g["conclusion_list"]) + "</ul>")
b.append(f'<p style="margin-top:6px">{e(g["conclusion_tail"])}</p>')
b.append(f'<div class="note"><b>{e(g["success_title"])}</b>'
         + " · ".join(e(x) for x in g["success"]) + "</div>")
page("".join(b))

# ---------------------------------------------------------------- band descriptors
add(f'''<section class="page divider">
<div class="num">01</div><h2>Band descriptors</h2><div class="rule"></div>
<p>The official scale each part of the paper is marked against. The tinted rows are the
bands this book trains you to reach — read them before you write, not after.</p>
</section>''')

for d in descriptors:
    rows = []
    for band in d["bands"]:
        tgt = ' class="tgt"' if band["band"].isdigit() and int(band["band"]) in d["target"] else ""
        lvl = f'<em>{e(band["level"])}</em>' if band["level"] else ""
        pts = ("<ul>" + "".join(f"<li>{e(p)}</li>" for p in band["points"]) + "</ul>") if band["points"] else ""
        rows.append(f'<tr{tgt}><td class="b"><strong>{e(band["band"])}</strong>{lvl}</td>'
                    f'<td>{e(band["lead"])}{pts}</td></tr>')
    page(ptitle(d["part"], "BAND DESCRIPTORS")
         + f'<p class="lead">{e(d["subtitle"])}</p>'
         + '<table class="bands"><thead><tr><th>Band</th><th>Description</th></tr></thead>'
         + "<tbody>" + "".join(rows) + "</tbody></table>"
         + '<div class="tgt-key"><i></i> Bands this book trains you to reach</div>')

# ---------------------------------------------------------------- worked sample
add(f'''<section class="page divider">
<div class="num">02</div><h2>A marked script</h2><div class="rule"></div>
<p>{e(worked["intro"])}</p>
</section>''')

b = [ptitle(worked["title"], "EXAMINER'S MARKS")]
for t in worked["tasks"]:
    resp = "".join(f"<p>{e(p)}</p>" for p in t["response"])
    cmt = "".join(f"<p>{e(p)}</p>" for p in t["comment"])
    b.append(f'''<div class="ws"><div class="hd"><b>{e(t["label"])}</b>
<span class="score">{t["mark"]} / {t["max"]}</span></div>
<div class="body"><div class="resp">{resp}</div>
<div class="cmt"><b>Examiner's comment</b>{cmt}</div></div></div>''')
    if t["label"] == "Task 1.2":
        page("".join(b))
        b = [ptitle(worked["title"] + " (continued)", "EXAMINER'S MARKS")]
o = worked["overall"]
b.append(f'''<div class="total"><div><b>OVERALL SCORE</b><i>{o["score"]} / {o["max"]}</i></div>
<div><b>STANDARD SCORE</b><i>{o["standard"]}</i></div>
<div><b>LEVEL</b><i>{e(o["level"])}</i></div></div>''')
b.append('<h4 class="sub">What this script teaches you</h4><ul class="ticks">'
         + "".join(f"<li>{e(x)}</li>" for x in worked["takeaways"]) + "</ul>")
page("".join(b))

# ---------------------------------------------------------------- exercises
add(f'''<section class="page divider">
<div class="num">03</div><h2>Exercises 1–10</h2><div class="rule"></div>
<p>Ten complete writing papers. Each one gives you a situation, three tasks, lined pages
to write on, model answers and the vocabulary those answers are built from.</p>
<ul>''' + "".join(
    f'<li><b>Exercise {x["n"]}</b> — {e(x["topic"])} · <span style="color:var(--muted)">{e(x["part2_question"])}</span></li>'
    for x in exercises) + '</ul></section>')


def letter_html(L):
    paras = "".join(f"<p>{e(p)}</p>" for p in L["paragraphs"])
    return (f'<div class="letter"><div class="greet">{e(L["greeting"])}</div>{paras}'
            f'<div class="sign">{e(L["signoff"])}<b>{e(L["signer"])}</b></div></div>')


def sample_html(label, words, paras):
    body = []
    for i, p in enumerate(paras):
        cls = ""
        if i == 0 and len(p) < 40:
            cls = ' class="greet"'
        elif i >= len(paras) - 2 and len(p) < 40:
            cls = ' class="sign"'
        body.append(f"<p{cls}>{e(p)}</p>")
    return (f'<div class="sample"><div class="hd"><b>{e(label)}</b><span>{e(words)}</span></div>'
            f'<div class="bd">{"".join(body)}</div></div>')


def vocab_html(title, items):
    half = (len(items) + 1) // 2
    tables = []
    for start, chunk in ((0, items[:half]), (half, items[half:])):
        rows = "".join(
            f'<tr><td class="n">{start + i + 1}</td><td class="en">{e(en)}</td><td class="uz">{e(uz)}</td></tr>'
            for i, (en, uz) in enumerate(chunk))
        tables.append('<table><thead><tr><th></th><th>English</th><th>O‘zbekcha</th></tr></thead>'
                      f"<tbody>{rows}</tbody></table>")
    return (f'<div class="voc"><h4 class="sub">{e(title)}</h4>'
            f'<div class="pair">{"".join(tables)}</div></div>')


TASKS = [("Task 1.1", "about 50 words", "task11"),
         ("Task 1.2", "120–150 words", "task12"),
         ("Task 2", "180–200 words", "part2")]

for x in exercises:
    head = (f'<div class="ex-head"><div class="n"><b>EXERCISE</b><i>{x["n"]}</i></div>'
            f'<div><h2>{e(x["topic"])}</h2><p>Part 1 · two emails &nbsp;·&nbsp; Part 2 · discussion post</p></div></div>')
    # task page
    b = [head,
         '<div class="scenario">'
         f'<div class="ctx"><b style="color:var(--blue-d)">PART 1 &nbsp;</b>{e(x["context"])}</div>'
         + letter_html(x["letter"]) + "</div>"]
    for label, words, key in TASKS[:2]:
        b.append(f'<div class="task"><div class="hd"><b>{label}</b><span>{words}</span></div>'
                 f'<div class="bd">{e(x["task11"] if key == "task11" else x["task12"])}</div></div>')
    b.append('<div class="scenario" style="margin-top:12px">'
             '<div class="ctx"><b style="color:var(--blue-d)">PART 2 &nbsp;</b>'
             'You are taking part in an online discussion for language learners.</div>'
             f'<div class="letter"><p>The question is: <b>“{e(x["part2_question"])}”</b></p>'
             '<p>Post your response, giving reasons and examples.</p></div></div>'
             '<div class="task"><div class="hd"><b>Task 2</b><span>180–200 words</span></div>'
             '<div class="bd">Write your post. Take a clear position, support it with reasons and '
             'examples, and finish with a conclusion.</div></div>')
    page("".join(b))

    # three lined answer pages
    for label, words, key in TASKS:
        prompt = {"task11": x["task11"], "task12": x["task12"],
                  "part2": f'“{x["part2_question"]}” — post your response, giving reasons and examples.'}[key]
        page(ptitle(label, f"EXERCISE {x['n']} · YOUR ANSWER")
             + f'<div class="prompt"><b>{label}:</b> {e(prompt)}</div>'
             + lines(24)
             + f'<div class="wc">Target length <span>{words}</span>'
               '<span>Words used: &nbsp; &nbsp; &nbsp;</span></div>', cls="answer")

    # sample answers + vocabulary
    page(ptitle(f"Exercise {x['n']} · Model answers", "PART 1")
         + '<p class="lead">Read these after you have written your own. Notice the structure '
           'and the linking language, not just the ideas.</p>'
         + sample_html("Task 1.1 · informal", "about 50 words", x["samples"]["task11"])
         + sample_html("Task 1.2 · formal", "120–150 words", x["samples"]["task12"])
         + vocab_html("Words and phrases from Part 1", x["vocab_task1"]))

    page(ptitle(f"Exercise {x['n']} · Model answer", "PART 2")
         + f'<p class="lead">“{e(x["part2_question"])}”</p>'
         + sample_html("Task 2 · discussion post", "180–200 words", x["samples"]["part2"])
         + vocab_html("Words and phrases from Part 2", x["vocab_part2"]))

# ---------------------------------------------------------------- closing checklist
add('''<section class="page">
<div class="ptitle"><h2>Before you hand it in</h2><div class="bar"></div><small>FINAL CHECK</small></div>
<p class="lead">Ninety seconds with this list is worth more than another two sentences.</p>
<div class="cols2">
<div class="panel"><h4 class="sub" style="margin-top:0">Every task</h4><ul class="ticks">
<li>Have I answered <b>every</b> question in the prompt?</li>
<li>Am I inside the word count?</li>
<li>Is the register the same from the first word to the signature?</li>
<li>Have I checked the verb endings, articles and plurals?</li>
<li>Does each paragraph hold one idea?</li></ul></div>
<div class="panel"><h4 class="sub" style="margin-top:0">Task 2 only</h4><ul class="ticks">
<li>Is my position clear in the first paragraph?</li>
<li>Does every argument have a reason <b>and</b> an example?</li>
<li>Have I answered the other side of the argument?</li>
<li>Does the conclusion add a judgement, not just a summary?</li>
<li>Have I used linking expressions rather than repeating "and"?</li></ul></div>
</div>
<h4 class="sub">Useful language</h4>
<div class="cols2">
<div class="panel"><b style="color:var(--blue-d)">Opening a position</b>
<p style="margin-top:5px">In my view … · I would argue that … · Having experienced both, …
· It seems to me that … · I am firmly in favour of …</p></div>
<div class="panel"><b style="color:var(--blue-d)">Conceding and contrasting</b>
<p style="margin-top:5px">On the other hand, … · I do accept that … · However, the opposite is
equally common. · There is no denying that … · Of course, this has a price.</p></div>
<div class="panel"><b style="color:var(--blue-d)">Giving evidence</b>
<p style="margin-top:5px">For instance, … · Research has repeatedly linked … · A good example
of this is … · This is particularly true where …</p></div>
<div class="panel"><b style="color:var(--blue-d)">Opening and closing a formal email</b>
<p style="margin-top:5px">Named person or title-holder (<i>Dear Mr Edward, Dear Head Teacher</i>)
&rarr; <b>Yours sincerely</b>. A role or department with no name (<i>Dear Sir or Madam,
Dear HR Department</i>) &rarr; <b>Yours faithfully</b>. Never <i>Best</i> or <i>Thanks</i>
in Task 1.2.</p></div>
<div class="panel"><b style="color:var(--blue-d)">Concluding</b>
<p style="margin-top:5px">Overall, I believe … · In the end, the choice depends on …
· For that reason, … · The answer, therefore, is not to choose but to combine.</p></div>
</div>
<div class="note" style="margin-top:12px"><b>Remember</b>Band 4 and band 5 scripts still
contain small mistakes. What separates them from band 2 is coverage, organisation and
register — not perfection.</div>
</section>''')

css = (ROOT / "scripts" / "style.css").read_text(encoding="utf-8")


def document(sections):
    return (f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{e(TITLE)}</title><style>{css}</style></head><body>'''
            + "".join(sections) + "</body></html>")


(DIST / "cover.html").write_text(document(cover), encoding="utf-8")
(DIST / "body.html").write_text(document(out), encoding="utf-8")
print(f"dist/cover.html + dist/body.html  ({len(out) + 1} pages)")
