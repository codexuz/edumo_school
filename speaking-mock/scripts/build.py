"""Build the Multilevel Speaking Mock book interior (A4, two columns, Mock-book design) -> dist/mock.html.

One flowing section per test: Part 1.1, Part 1.2 (two pictures), Part 2 (cue card + picture), Part 3 (for/against table),
then the C1 model answers for that test. Data: data/questions_and_sample_answers.json, pictures: assets/img/.
"""
import json
from collections import defaultdict

from blocks import CHANNEL, DIST, EMOJI, ROOT, e, qr_svg

DATA = ROOT / "data" / "questions_and_sample_answers.json"
SET_ORDER = {"ra": 0, "rb": 1, "mb": 2}
SET_NAME = {"ra": "Real Exam 2026 · Set A", "rb": "Real Exam 2026 · Set B", "mb": "Speaking Mock Book"}
PART_INFO = {"1.1": ("PART 1.1", "Personal questions"), "1.2": ("PART 1.2", "Compare two pictures"),
             "2": ("PART 2", "Long turn"), "3": ("PART 3", "Discussion")}


def secs(n):
    return f"{n // 60} min" if n >= 60 and n % 60 == 0 else f"{n} s"


def timer(q):
    return f'<span class="tm">⏱ {secs(q["preparation_seconds"])} · 🎙 {secs(q["speaking_seconds"])}</span>'


def img(path, cls="pic"):
    return f'<img class="{cls}" src="../assets{path}" alt="">'


def question(n, q):
    return f'<div class="sq"><b class="qn">{n}</b><p>{e(q["question_or_statement"])}</p>{timer(q)}</div>'


def phead(part, extra=""):
    pill, name = PART_INFO[part]
    return f'<div class="phead"><span class="pill">{pill}</span><span class="qr">{name}{extra}</span></div>'


def test_section(num, tid, title, topics, qs):
    by = defaultdict(list)
    for q in qs:
        by[q["part"]].append(q)
    p11, p12, p2, p3 = by["1.1"], by["1.2"], by["2"][0], by["3"][0]
    html = []
    # Part 1.1
    html.append('<div class="part">' + phead("1.1")
                + '<div class="ins"><span class="aud">🎙</span><p>Answer the questions about yourself. Speak for about 30 seconds each.</p></div>'
                + "".join(question(i, q) for i, q in enumerate(p11, 1)) + "</div>")
    # Part 1.2
    pics = "".join(img(p) for p in p12[0]["images"])
    html.append('<div class="part">' + phead("1.2")
                + '<div class="ins"><span class="aud">🖼</span><p>Look at the two pictures and answer the questions.</p></div>'
                + f'<div class="pics">{pics}</div>'
                + "".join(question(i, q) for i, q in enumerate(p12, 4)) + "</div>")
    # Part 2
    bullets = (p2.get("prompts_or_table") or {}).get("bullets") or [p2["question_or_statement"]]
    pic2 = img(p2["images"][0], "pic wide") if p2.get("images") else ""
    html.append('<div class="part">' + phead("2")
                + '<div class="ins"><span class="aud">🗣</span><p>Look at the picture and talk about the topic. You have 1 minute to prepare and 2 minutes to speak.</p></div>'
                + f'<div class="cue">{pic2}<div class="cuebox"><h4>Talk about:</h4><ul>'
                + "".join(f"<li>{e(b)}</li>" for b in bullets) + f"</ul>{timer(p2)}</div></div></div>")
    # Part 3
    t = p3.get("prompts_or_table") or {}
    pros, cons = t.get("for", []), t.get("against", [])
    rows = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in
                   zip(pros + [""] * (len(cons) - len(pros)), cons + [""] * (len(pros) - len(cons))))
    html.append('<div class="part">' + phead("3")
                + '<div class="ins"><span class="aud">⚖️</span><p>Give a balanced argument for and against the statement, then give your own opinion. 1 minute to prepare, 2 minutes to speak.</p></div>'
                + f'<div class="stmt">“{e(t.get("statement") or p3["question_or_statement"])}”</div>'
                + f'<table class="fa"><tr><th>FOR</th><th>AGAINST</th></tr>{rows}</table>{timer(p3)}</div>')
    # Model answers
    src = "C1 model answers" if qs[0].get("sample_source") != "book" else "C1 model answers · book"
    ans = [f'<div class="split mahead"><div class="phead"><span class="pill gold">MODEL ANSWERS</span><span class="qr">{src}</span></div></div>']
    labels = [("1.1", i + 1, q) for i, q in enumerate(p11)] + [("1.2", i + 4, q) for i, q in enumerate(p12)] + [("2", 7, p2), ("3", 8, p3)]
    for part, n, q in labels:
        head = f'<h5><span class="mn">{n}</span><i>{PART_INFO[part][0].title()}</i> {e(q["question_or_statement"])}</h5>'
        paras = "".join(f"<p>{e(x.strip())}</p>" for x in q["sample_answer"].split("\n") if x.strip())
        ans.append(f'<div class="split ma">{head}{paras}</div>')
    html.append("".join(ans))
    banner = (f'<div class="banner"><div class="girih"></div><div class="bl"><small>MULTILEVEL · SPEAKING</small>'
              f'<h1>TEST {num}</h1></div><div class="br"><b>{e(SET_NAME[tid[:2]])}</b>'
              f'<span class="topics">{e(topics)}</span></div></div>')
    return (f'<section class="page flow first" data-run="Test {num}">{banner}'
            f'<div class="cols"><div class="col">{"".join(html)}</div><div class="col"></div></div>'
            f'<footer><span>Multilevel Speaking Mock Tests · Test {num}</span><span class="pno"></span></footer></section>')


def how_page(count, sets):
    tips = [("⏱", "Use a timer", "Keep to the real timings: 5–10 s to prepare in Part 1, 1 minute in Parts 2 and 3."),
            ("📱", "Record yourself", "Record every answer on your phone, then listen back. Check your fluency, grammar and range of vocabulary."),
            ("⭐", "Compare with the model", "Each test is followed by C1 model answers. Note the useful phrases and try to use them next time."),
            ("🔁", "Repeat", "Answer the same test again a few days later and compare the two recordings."),
            ("🎧", "Examiner audio", "Listen to the examiner questions in our Telegram channel and answer in real time.")]
    cards = "".join(f'<div class="tip"><span>{i}</span><div><b>{t}</b><p>{d}</p></div></div>' for i, t, d in tips)
    plan = [("1.1", "Personal questions", "3", "5 s", "30 s"), ("1.2", "Two pictures: describe and compare", "3", "5–10 s", "30–45 s"),
            ("2", "Long turn with a cue card", "1", "1 min", "2 min"), ("3", "For and against discussion", "1", "1 min", "2 min")]
    rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{f}</td></tr>" for a, b, c, d, f in plan)
    setrows = "".join(f"<tr><td>{e(n)}</td><td>Tests {a}–{b}</td></tr>" for n, a, b in sets)
    return (f'<section class="page howpage"><div class="banner"><div class="girih"></div><div class="bl"><small>MULTILEVEL · CEFR</small>'
            f'<h1>HOW TO USE THIS BOOK</h1></div><div class="br"><b>{count} speaking tests</b><span>Questions + C1 model answers</span></div></div>'
            f'<p class="lead">This book contains <b>{count} complete Multilevel speaking tests</b> in the real exam format, each followed by '
            f'<b>C1-level model answers</b>. Practise like the real exam: set a timer, speak out loud and record yourself.</p>'
            f'<div class="tips">{cards}</div>'
            f'<div class="audio"><div class="qrc">{qr_svg("https://" + CHANNEL)}</div><div><b>🎧 Examiner audio</b>'
            f'<p>Scan the QR code to open our Telegram channel.</p><span>{CHANNEL}</span></div></div>'
            f'<table class="plan"><tr><th>Part</th><th>Task</th><th>Questions</th><th>Preparation</th><th>Speaking</th></tr>{rows}</table>'
            f'<table class="plan sets"><tr><th>Test set</th><th>Tests</th></tr>{setrows}</table>'
            '<footer><span>Multilevel Speaking Mock Tests</span><span class="pno"></span></footer></section>')


def build():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    tests = sorted(d["tests"], key=lambda t: (SET_ORDER[t["id"][:2]], t["id"]))
    qa = defaultdict(list)
    for q in d["all_questions_and_answers"]:
        qa[q["test_id"]].append(q)
    sets, pages = [], []
    for n, t in enumerate(tests, 1):
        pages.append(test_section(n, t["id"], t["title"], t["topics"], sorted(qa[t["id"]], key=lambda q: q["step_key"])))
        name = SET_NAME[t["id"][:2]]
        if sets and sets[-1][0] == name:
            sets[-1] = (name, sets[-1][1], n)
        else:
            sets.append((name, n, n))
    pages.insert(0, how_page(len(tests), sets))
    css = (ROOT / "scripts" / "style.css").read_text(encoding="utf-8") + (ROOT / "scripts" / "speaking.css").read_text(encoding="utf-8")
    fonts = ('<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700;800'
             '&family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&display=block" rel="stylesheet">')
    body = EMOJI.sub(r'<span class="em">\1</span>', "".join(pages))
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Multilevel Speaking Mock Tests</title>{fonts}'
           f'<style>{css}</style></head><body>{body}</body></html>')
    DIST.mkdir(exist_ok=True)
    (DIST / "mock.html").write_text(doc, encoding="utf-8")
    print("tests:", len(tests), "sets:", sets)


if __name__ == "__main__":
    build()
