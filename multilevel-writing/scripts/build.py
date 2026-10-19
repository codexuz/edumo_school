"""Build "A Complete Guide to Multilevel Writing" as HTML sheets.

Usage: python3 scripts/build.py   ->  dist/body.html (the interior)

Every page is a fixed 210x297mm `.sheet` carrying its own running header and
footer, with the flowing content in a two-column `.cols` box — the page model
of the Multilevel Practice Book, in the dodger-blue palette of the vocabulary
books. The cover is written to its own document so that no running header or
page number is printed over it.

Content comes from data/*.json (see SCHEMA.md); the practice tasks are derived
from each exercise's own word lists and model answers by scripts/practice.py.
"""
import base64
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import practice  # noqa: E402

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

out = []


def sheet(body, right="", cls="", one=False):
    """One printed page: running header, two-column body, footer."""
    n = len(out) + 2                      # the cover is page 1
    out.append(
        f'<section class="sheet {cls}">'
        f'<div class="rhead"><span>IMPULSE <i>LEARNING CENTER</i></span>'
        f'<span class="r">{right or "MULTILEVEL WRITING"}</span></div>'
        f'<div class="cols{" one" if one else ""}">{body}</div>'
        f'<footer><span>© {e(SCHOOL)}</span><span class="pno">{n}</span></footer>'
        "</section>")


def ptitle(title, kicker=""):
    k = f"<small>{e(kicker)}</small>" if kicker else ""
    return f'<div class="ptitle span"><h2>{e(title)}</h2><div class="bar"></div>{k}</div>'


def lines(n):
    return '<div class="lines">' + "<div></div>" * n + "</div>"


# ---------------------------------------------------------------- how to use
sheet(f'''{ptitle("How to use this book", "START HERE")}
<p class="lead span">Every exercise follows the same eight-page cycle. Work through it in order —
the model answers only help once you have written your own.</p>
<div class="panel"><h4 class="sub" style="margin-top:0">The cycle</h4>
<ol style="list-style:none">
<li style="margin:1.4mm 0"><b style="color:var(--blue-d)">1 · Read the situation.</b>
One prompt letter sets up all three tasks. Underline what you are asked to do — most lost
marks come from missing a question, not from weak English.</li>
<li style="margin:1.4mm 0"><b style="color:var(--blue-d)">2 · Task 1.1, about 50 words.</b>
A message to a friend: informal, warm, and still an answer to the task.</li>
<li style="margin:1.4mm 0"><b style="color:var(--blue-d)">3 · Task 1.2, 120–150 words.</b>
The same situation in a formal email. Hold the register from first line to signature.</li>
<li style="margin:1.4mm 0"><b style="color:var(--blue-d)">4 · Task 2, 180–200 words.</b>
A discussion post: take a position, support it, close it properly. Two pages are given.</li>
<li style="margin:1.4mm 0"><b style="color:var(--blue-d)">5 · Compare with the models.</b>
Do not copy them. Look at how each is organised and what language carries the argument.</li>
<li style="margin:1.4mm 0"><b style="color:var(--blue-d)">6 · Learn the word list.</b>
Twenty words per task, with Russian and Uzbek, taken from the models themselves.</li>
<li style="margin:1.4mm 0"><b style="color:var(--blue-d)">7 · Do the practice page.</b>
Four tasks on that unit's language. The answer key is at the back of the book.</li>
</ol></div>
<div class="note"><b>Word count</b>Examiners do not reward extra length. A 260-word Task 2
is not a better Task 2 — it is an unfinished one that ran out of control.</div>
<div class="note"><b>Register</b>The commonest fault is a formal email that slips into chat
("Hi there", "Thanks a lot!") halfway through. Choose a register and hold it.</div>
<div class="note"><b>Sign-offs</b>A named person or title-holder takes <b
style="display:inline">Yours sincerely</b>; a role or department with no name takes
<b style="display:inline">Dear Sir or Madam</b> and <b style="display:inline">Yours faithfully</b>.</div>
<h4 class="sub span">Marks at a glance</h4>
<div class="total span">
  <div><b>TASK 1.1</b><i>5</i></div><div><b>TASK 1.2</b><i>6</i></div>
  <div><b>TASK 2</b><i>6</i></div><div><b>TOTAL</b><i>17</i></div>
</div>''', right="HOW TO USE THIS BOOK")

# ---------------------------------------------------------------- the guide (Uzbek)
g = guide
b = [ptitle(g["title"], "YO'RIQNOMA"), f'<p class="lead span">{e(g["intro"])}</p>',
     '<ul class="ticks">' + "".join(f"<li>{e(x)}</li>" for x in g["intro_list"]) + "</ul>"]
for sec in g["sections"]:
    b.append(f'<h3 class="sec span"><span style="color:var(--blue)">{e(sec["kicker"])}:</span> '
             f'{e(sec["title"])}</h3>')
    b.append(f'<p class="lead span">{e(sec["lead"])}</p>')
    for c in sec["cards"]:
        facts = "".join(f"<tr><td>{e(k)}</td><td>{e(v)}</td></tr>" for k, v in c["facts"])
        req = "".join(f"<li>{e(x)}</li>" for x in c["req"])
        b.append(f'''<div class="tcard"><div class="hd"><b>{e(c["label"])}</b><h4>{e(c["title"])}</h4></div>
<div class="bd"><table class="facts">{facts}</table>
<div class="req">{e(c["req_title"])}</div><ul class="ticks">{req}</ul></div></div>''')
    if sec.get("note"):
        b.append(f'<div class="note"><b>{e(sec["note_title"])}</b>{e(sec["note"])}</div>')
    if sec.get("extra"):
        items = "".join(f"<li>{e(x)}</li>" for x in sec["extra"])
        b.append(f'<div class="panel"><h4 class="sub" style="margin-top:0">{e(sec["extra_title"])}</h4>'
                 f'<ul class="ticks">{items}</ul></div>')
    sheet("".join(b), right="YOZMA ISH · YO'RIQNOMA")
    b = [ptitle(g["title"] + " (davomi)", "YO'RIQNOMA")]

b = [ptitle(g["functions_title"], "TIL FUNKSIYALARI"), f'<p class="lead span">{e(g["functions_lead"])}</p>',
     '<div class="panel"><ul class="ticks">'
     + "".join(f"<li>{e(x)}</li>" for x in g["functions"]) + "</ul></div>",
     f'<h3 class="sec">{e(g["marking_title"])}</h3>']
for m in g["marking"]:
    bands = "".join(f'<div class="band"><b>{e(k)}</b><span>{e(v)}</span></div>' for k, v in m["bands"])
    crit = "".join(f"<li>{e(x)}</li>" for x in m["criteria"])
    b.append(f'''<div class="mark"><div class="hd"><h4>{e(m["title"])}</h4><span>{e(m["range"])}</span></div>
<div class="bd">{bands}<div class="req" style="margin-top:1.6mm;font-size:7.2pt;font-weight:800;
color:var(--navy);letter-spacing:.1em;text-transform:uppercase">{e(m["criteria_title"])}</div>
<ul class="ticks">{crit}</ul></div></div>''')
b.append(f'<h3 class="sec">{e(g["conclusion_title"])}</h3><p class="lead">{e(g["conclusion_lead"])}</p>')
b.append('<ul class="ticks">' + "".join(f"<li>{e(x)}</li>" for x in g["conclusion_list"]) + "</ul>")
b.append(f'<p style="margin-top:1.4mm">{e(g["conclusion_tail"])}</p>')
b.append(f'<div class="note"><b>{e(g["success_title"])}</b>' + " · ".join(e(x) for x in g["success"]) + "</div>")
sheet("".join(b), right="BAHOLASH MEZONLARI")


def divider(num, title, text, extra=""):
    sheet(f'<div class="num">{num}</div><h2>{e(title)}</h2><div class="rule"></div>'
          f"<p>{e(text)}</p>{extra}", right=title.upper(), cls="divider", one=True)


# ---------------------------------------------------------------- band descriptors
divider("01", "Band descriptors",
        "The official scale each part of the paper is marked against. The tinted rows are the "
        "bands this book trains you to reach — read them before you write, not after.")

for d in descriptors:
    rows = []
    for band in d["bands"]:
        tgt = ' class="tgt"' if band["band"].isdigit() and int(band["band"]) in d["target"] else ""
        lvl = f'<em>{e(band["level"])}</em>' if band["level"] else ""
        pts = ("<ul>" + "".join(f"<li>{e(p)}</li>" for p in band["points"]) + "</ul>") if band["points"] else ""
        rows.append(f'<tr{tgt}><td class="b"><strong>{e(band["band"])}</strong>{lvl}</td>'
                    f'<td>{e(band["lead"])}{pts}</td></tr>')
    sheet(ptitle(d["part"], "BAND DESCRIPTORS")
          + f'<p class="lead">{e(d["subtitle"])}</p>'
          + '<table class="bands"><thead><tr><th>Band</th><th>Description</th></tr></thead>'
          + "<tbody>" + "".join(rows) + "</tbody></table>"
          + '<div class="tgt-key"><i></i> Bands this book trains you to reach</div>',
          right=f"BAND DESCRIPTORS · {d['part'].upper()}", one=True)

# ---------------------------------------------------------------- worked sample
divider("02", "A marked script", worked["intro"])

b = [ptitle(worked["title"], "EXAMINER'S MARKS")]
for t in worked["tasks"]:
    resp = "".join(f"<p>{e(p)}</p>" for p in t["response"])
    cmt = "".join(f"<p>{e(p)}</p>" for p in t["comment"])
    b.append(f'''<div class="ws"><div class="hd"><b>{e(t["label"])}</b>
<span class="score">{t["mark"]} / {t["max"]}</span></div>
<div class="resp">{resp}</div><div class="cmt"><b>Examiner's comment</b>{cmt}</div></div>''')
o = worked["overall"]
b.append(f'''<div class="total span"><div><b>OVERALL SCORE</b><i>{o["score"]} / {o["max"]}</i></div>
<div><b>STANDARD SCORE</b><i>{o["standard"]}</i></div>
<div><b>LEVEL</b><i>{e(o["level"])}</i></div></div>''')
b.append('<h4 class="sub span">What this script teaches you</h4><ul class="ticks">'
         + "".join(f"<li>{e(x)}</li>" for x in worked["takeaways"]) + "</ul>")
sheet("".join(b), right="A MARKED SCRIPT")

# ---------------------------------------------------------------- exercises
divider("03", f"Exercises 1–{len(exercises)}",
        "Complete writing papers. Each gives you a situation, three tasks, lined pages to write "
        "on, model answers, a trilingual word list and a practice page.",
        '<div class="list">' + "".join(
            f'<div><b>{x["n"]} · {e(x["topic"])}</b><br><span>{e(x["part2_question"])}</span></div>'
            for x in exercises) + "</div>")


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


def sample_flow_html(label, words, paras):
    """A model answer that flows across both columns, with a full-width header."""
    body = "".join(f"<p>{e(p)}</p>" for p in paras)
    return (f'<div class="sflow-hd span"><b>{e(label)}</b><span>{e(words)}</span></div>'
            f'<div class="sflow">{body}</div>')


def vocab_html(title, items):
    rows = "".join(
        f'<tr><td class="n">{i + 1}</td><td class="en">{e(en)}</td>'
        f'<td class="ru">{e(ru)}</td><td class="uz">{e(uz)}</td></tr>'
        for i, (en, ru, uz) in enumerate(items))
    return (f'<div class="voc span"><h4 class="sub">{e(title)}</h4><table>'
            '<thead><tr><th></th><th>English</th><th>Русский</th><th>O‘zbekcha</th></tr></thead>'
            f"<tbody>{rows}</tbody></table></div>")


def practice_html(ex, pr):
    gaps = "".join(f"<li>{e(g['q'])}</li>" for g in pr["gapfill"])
    left = "".join(f'<div><span class="k">{i + 1}</span><span class="box"></span>'
                   f"<span>{e(t)}</span></div>" for i, t in enumerate(pr["match"]["left"]))
    right = "".join(f'<div><span class="k">{chr(65 + i)}</span><span>{e(t)}</span></div>'
                    for i, t in enumerate(pr["match"]["right"]))
    choice = "".join(
        f'<li>{e(c["ru"])}<br><span class="opts">'
        + "  ".join(f'<b>{"ABC"[j]}</b> {e(o)}' for j, o in enumerate(c["options"]))
        + "</span></li>" for c in pr["choice"])
    rw = "".join(f'<li><i>{e(a)}</i><span class="to"></span></li>'
                 for a, _ in pr["rewrite"]["items"])
    return f'''{ptitle(f"Exercise {ex['n']} · Practice", "VOCABULARY & SENTENCES")}
<p class="lead span">Four tasks on the language of this unit. Answers at the back of the book.</p>
<div class="pr"><div class="hd"><i>A</i><b>Complete the sentence</b></div><div class="bd">
<p class="i">Each sentence comes from a model answer in this unit. Write the missing word or phrase.</p>
<ol>{gaps}</ol></div></div>
<div class="pr"><div class="hd"><i>B</i><b>Match English to Uzbek</b></div><div class="bd">
<p class="i">Write the letter of the Uzbek translation next to each English word.</p>
<div class="mgrid"><div style="display:block">{left}</div><div style="display:block">{right}</div></div>
</div></div>
<div class="pr"><div class="hd"><i>C</i><b>Choose the English word</b></div><div class="bd">
<p class="i">Circle the English word or phrase that matches the Russian.</p>
<ol>{choice}</ol></div></div>
<div class="pr"><div class="hd"><i>D</i><b>Make it formal</b></div><div class="bd">
<p class="i">{e(pr["rewrite"]["lead"])}</p>
<ol class="rw">{rw}</ol></div></div>'''


TASK_PAGES = [("Task 1.1", "about 50 words", "task11", 1),
              ("Task 1.2", "120–150 words", "task12", 1),
              ("Task 2", "180–200 words", "part2", 2)]
keys = {}

for x in exercises:
    rt = f"EXERCISE {x['n']}"
    pr = practice.build(x)
    keys[x["n"]] = pr

    # --- task page ---
    b = [f'<div class="ex-head span"><div class="n"><b>EXERCISE</b><i>{x["n"]}</i></div>'
         f'<div><h2>{e(x["topic"])}</h2><p>Part 1 · two emails &nbsp;·&nbsp; '
         f"Part 2 · discussion post</p></div></div>",
         '<div class="scenario"><div class="ctx"><b>PART 1</b> &nbsp;'
         + e(x["context"]) + "</div>" + letter_html(x["letter"]) + "</div>",
         f'<div class="task"><div class="hd"><b>Task 1.1</b><span>about 50 words</span></div>'
         f'<div class="bd">{e(x["task11"])}</div></div>',
         f'<div class="task"><div class="hd"><b>Task 1.2</b><span>120–150 words</span></div>'
         f'<div class="bd">{e(x["task12"])}</div></div>',
         # Part 2 and Task 2 are one card
         f'<div class="task"><div class="hd"><b>Part 2 · Task 2</b><span>180–200 words</span></div>'
         '<div class="bd">You are taking part in an online discussion for language learners.'
         f'<div class="q">The question is:<br><b>“{e(x["part2_question"])}”</b></div>'
         "Post your response, giving reasons and examples. Take a clear position, support it "
         "with reasons and examples, and finish with a conclusion.</div></div>",
         # planning box: the page has room, and planning is where marks are won
         '<div class="plan"><div class="hd"><b>Before you write · plan</b>'
         "<span>5 minutes</span></div><div class=\"bd\">"
         "<p class=\"i\">Note your ideas here in English before you start. A plan costs five "
         "minutes and saves you from the commonest fault: missing one of the questions.</p>"
         '<div class="row"><b>Task 1.1</b> Who am I writing to, and how do I feel?'
         '<span class="to"></span><span class="to"></span></div>'
         '<div class="row"><b>Task 1.2</b> What exactly am I asked for? List every question.'
         '<span class="to"></span><span class="to"></span></div>'
         '<div class="row"><b>Task 2</b> My position, two reasons, one example each, the other side.'
         '<span class="to"></span><span class="to"></span><span class="to"></span></div>'
         "</div></div>"]
    sheet("".join(b), right=rt)

    # --- lined answer pages ---
    for label, words, key, pages in TASK_PAGES:
        prompt = {"task11": x["task11"], "task12": x["task12"],
                  "part2": f'“{x["part2_question"]}” — post your response, giving reasons and examples.'}[key]
        for pg in range(1, pages + 1):
            of = f" ({pg} of {pages})" if pages > 1 else ""
            head = (f'<div class="prompt"><b>{label}:</b> {e(prompt)}</div>' if pg == 1
                    else f'<div class="prompt"><b>{label}</b> — continued.</div>')
            sheet(ptitle(label + of, f"EXERCISE {x['n']} · YOUR ANSWER") + head + lines(25)
                  + (f'<div class="wc">Target length <span>{words}</span>'
                     '<span>Words used: &nbsp; &nbsp;</span></div>' if pg == pages else ""),
                  right=rt, cls="answer", one=True)

    # --- model answers ---
    sheet(ptitle(f"Exercise {x['n']} · Model answers", "PART 1")
          + '<p class="lead span">Read these after you have written your own. Notice the structure '
            "and the linking language, not just the ideas.</p>"
          + sample_html("Task 1.1 · informal", "about 50 words", x["samples"]["task11"])
          + sample_html("Task 1.2 · formal", "120–150 words", x["samples"]["task12"])
          + vocab_html("Words and phrases from Part 1", x["vocab_task1"]),
          right=rt)

    sheet(ptitle(f"Exercise {x['n']} · Model answer", "PART 2")
          + f'<p class="lead span">“{e(x["part2_question"])}”</p>'
          + sample_flow_html("Task 2 · discussion post", "180–200 words", x["samples"]["part2"])
          + vocab_html("Words and phrases from Part 2", x["vocab_part2"]),
          right=rt)

    # --- practice ---
    sheet(practice_html(x, pr), right=rt)

# ---------------------------------------------------------------- checklist
sheet('''<div class="ptitle span"><h2>Before you hand it in</h2><div class="bar"></div>
<small>FINAL CHECK</small></div>
<p class="lead span">Ninety seconds with this list is worth more than another two sentences.</p>
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
<div class="panel"><b style="color:var(--blue-d)">Opening a position</b>
<p>In my view … · I would argue that … · Having experienced both, … · It seems to me that …
· I am firmly in favour of …</p></div>
<div class="panel"><b style="color:var(--blue-d)">Conceding and contrasting</b>
<p>On the other hand, … · I do accept that … · However, the opposite is equally common.
· There is no denying that … · Of course, this has a price.</p></div>
<div class="panel"><b style="color:var(--blue-d)">Giving evidence</b>
<p>For instance, … · Research has repeatedly linked … · A good example of this is …
· This is particularly true where …</p></div>
<div class="panel"><b style="color:var(--blue-d)">Opening and closing a formal email</b>
<p>Named person or title-holder (<i>Dear Mr Edward, Dear Head Teacher</i>) &rarr;
<b>Yours sincerely</b>. A role or department with no name (<i>Dear Sir or Madam</i>) &rarr;
<b>Yours faithfully</b>. Never <i>Best</i> or <i>Thanks</i> in Task 1.2.</p></div>
<div class="panel"><b style="color:var(--blue-d)">Concluding</b>
<p>Overall, I believe … · In the end, the choice depends on … · For that reason, …
· The answer is not to choose but to combine.</p></div>
<div class="note span"><b>Remember</b>Band 4 and band 5 scripts still contain small mistakes.
What separates them from band 2 is coverage, organisation and register — not perfection.</div>''',
      right="FINAL CHECK")

# ---------------------------------------------------------------- answer key
divider("04", "Answer key", "Answers to the practice page of every exercise.")

units = []
for x in exercises:
    pr = keys[x["n"]]
    a = "  ".join(f"<b>{i + 1}</b> {e(g['a'])}" for i, g in enumerate(pr["gapfill"]))
    bm = "  ".join(f"<b>{i + 1}</b> {chr(64 + k)}" for i, k in enumerate(pr["match"]["key"]))
    c = "  ".join(f"<b>{i + 1}</b> {ch['a']}" for i, ch in enumerate(pr["choice"]))
    d = "".join(f'<p><b>{i + 1}</b> {e(t)}</p>' for i, (_, t) in enumerate(pr["rewrite"]["items"]))
    units.append(f'<div class="u"><h5>Exercise {x["n"]} · {e(x["topic"])}</h5>'
                 f"<p><b>A</b> &nbsp;{a}</p><p><b>B</b> &nbsp;{bm}</p><p><b>C</b> &nbsp;{c}</p>"
                 f'<p style="margin-top:.8mm"><b>D</b> — suggested answers:</p>{d}</div>')

for i in range(0, len(units), 5):
    sheet(ptitle("Answer key" + ("" if i == 0 else " (continued)"), "PRACTICE PAGES")
          + '<div class="key">' + "".join(units[i:i + 5]) + "</div>", right="ANSWER KEY")

# ---------------------------------------------------------------- write
css = (ROOT / "scripts" / "style.css").read_text(encoding="utf-8")


def document(sections):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f"<title>{e(TITLE)}</title><style>{css}</style></head><body>"
            + "".join(sections) + "</body></html>")


(DIST / "body.html").write_text(document(out), encoding="utf-8")
print(f"dist/body.html  ({len(out)} interior pages)")
