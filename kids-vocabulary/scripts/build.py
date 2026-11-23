"""Build "Word Time! 2" — kids' vocabulary book for Teen2Teen 2 (A5, playful; companion to Talk Time! and Read Time!)
-> dist/word-time.html (render.js prints it to dist/Word_Time_2.pdf).

Each unit (4 pages), built on the unit's vocabulary list (src/teen2teen2-vocabulary.txt):
  1 Word Bank (picture cards: SVG icon, English, Uzbek)
  2 Match · 3 Spell It · 4 Odd One Out
  5 Fill the Gaps · 6 Word Power (the unit's grammar / word focus) · 7 Say It! (social language)
  8 Word Search · 9 About Me · Now I can
Answer key and an A–Z word list with Uzbek at the end. Icons: data/icons.json (scripts/icons.py).
"""
import html
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNITS = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "data" / "units").glob("*.json"))]
ICONS = json.loads((ROOT / "data" / "icons.json").read_text(encoding="utf-8"))
BOOK = "Word Time! 2"
e = html.escape

SECTIONS = {
    "bank": (1, "Word Bank", "Rasmlarga qarang, so‘zlarni o‘qing va takrorlang.", "c-green", "mdi:cards-outline"),
    "match": (2, "Match", "So‘zni uning ma’nosi bilan bog‘lang.", "c-purple", "mdi:link-variant"),
    "spell": (3, "Spell It", "Tushib qolgan harflarni yozing.", "c-orange", "mdi:alphabetical-variant"),
    "odd": (4, "Odd One Out", "Ortiqcha so‘zni aylana ichiga oling.", "c-pink", "mdi:help-circle"),
    "gaps": (5, "Fill the Gaps", "So‘zlar qutisidan foydalanib gaplarni to‘ldiring.", "c-teal", "mdi:pencil"),
    "power": (6, "Word Power", "Qoidani o‘qing va javobni yozing.", "c-blue", "mdi:lightning-bolt"),
    "say": (7, "Say It!", "Juftlikda o‘qing va o‘zingizning so‘zlaringiz bilan aytib ko‘ring.", "c-yellow", "mdi:chat"),
    "search": (8, "Word Search", "8 ta so‘zni toping va belgilang.", "c-yellow", "mdi:magnify"),
    "me": (9, "About Me", "O‘zingiz haqingizda yangi so‘zlar bilan bitta gap yozing.", "c-blue", "mdi:account-edit"),
}


def svg(ident, cls="ico"):
    ic = ICONS[ident]
    return (f'<svg class="{cls}" viewBox="0 0 {ic["w"]} {ic["h"]}" xmlns="http://www.w3.org/2000/svg" '
            f'fill="currentColor" aria-hidden="true">{ic["body"]}</svg>')


def section(key):
    n, title, uz, cls, ico = SECTIONS[key]
    return (f'<div class="sec {cls}"><div class="sechead"><span class="secno">{n}</span><h2>{title}</h2>'
            f'<span class="secico">{svg(ico)}</span></div><p class="secuz">{e(uz)}</p></div>')


def page(inner, n, unit=None, cls=""):
    tab = f'<span class="tab {unit["color"]}">{unit["n"]}</span>' if unit else ""
    ucls = unit["color"] if unit else ""
    return (f'<section class="page {ucls} {cls}">{tab}<div class="content">{inner}</div>'
            f'<footer><span>{BOOK} · Teen2Teen 2</span><span class="pno">{n}</span></footer></section>')


def bare(word):
    """'an apple' -> 'apple' (for sorting and for finding a word's icon)."""
    return re.sub(r"^(a|an|the)\s+", "", word.strip(), flags=re.I)


def icon_for(u, word):
    w = word.lower()
    for en, _, ico in u["words"]:
        if bare(en).lower() == w or w in en.lower().split():
            return ico
    for en, _, ico in u["words"]:
        if w in en.lower():
            return ico
    return u["icon"]


# ---------------- word search ----------------
def word_search(words, seed, size=10):
    rnd = random.Random(seed)
    for _ in range(50):
        grid = [[""] * size for _ in range(size)]
        dirs = [(0, 1), (1, 0), (1, 1)]
        ok = True
        for w in sorted(words, key=len, reverse=True):
            for _ in range(800):
                dr, dc = rnd.choice(dirs)
                if len(w) > size:
                    break
                r = rnd.randrange(size - (len(w) - 1) * dr)
                c = rnd.randrange(size - (len(w) - 1) * dc)
                if all(grid[r + i * dr][c + i * dc] in ("", ch) for i, ch in enumerate(w)):
                    for i, ch in enumerate(w):
                        grid[r + i * dr][c + i * dc] = ch
                    break
            else:
                ok = False
                break
        if ok:
            letters = "ABCDEFGHIKLMNOPRSTUWY"
            return [[ch or rnd.choice(letters) for ch in row] for row in grid]
    raise ValueError(f"cannot place {words}")


def shuffled(n, seed):
    rnd = random.Random(seed)
    order = list(range(n))
    while any(i == k for i, k in enumerate(order)):
        rnd.shuffle(order)
    return order


def hidden(word, n):
    """Positions of the letters to leave out in Spell It (about 40%, never the first letter)."""
    idx = [i for i, ch in enumerate(word) if ch.isalpha() and i > 0]
    rnd = random.Random(n * 31 + len(word))
    k = max(2, round(len(idx) * 0.4))
    return set(rnd.sample(idx, min(k, len(idx))))


# ---------------- unit pages ----------------
def p_bank(u):
    k = len(u["words"])
    cols = 3 if k <= 12 else 4
    cards = "".join(f'<li><span class="wic">{svg(ico)}</span><b>{e(en)}</b><small>{e(uz)}</small></li>' for en, uz, ico in u["words"])
    tip = ('<div class="pairgame"><span>' + svg("mdi:account-voice") + '</span><div><b>Point &amp; say!</b>'
           '<small>Juftlikda: biringiz rasmni ko‘rsating, ikkinchingiz so‘zni ayting.</small></div></div>') if k <= 16 else ""
    return (f'<div class="uhead {u["color"]}"><div class="utitle"><small>UNIT {u["n"]} · VOCABULARY LIST {u["n"]}</small>'
            f'<h1>{e(u["title"])}</h1><p class="utopic">{e(u["topic"])}</p></div><span class="uico">{svg(u["icon"])}</span></div>'
            f'{section("bank")}<ul class="vcards c{cols} n{k}">{cards}</ul>{tip}')


def p_practice(u):
    order = shuffled(6, u["n"] * 11)
    left = "".join(f'<li><span class="mn">{i}</span><b>{e(w)}</b><i class="dot"></i></li>' for i, (w, _) in enumerate(u["match"], 1))
    right = "".join(f'<li><i class="dot"></i><span class="ml">{"abcdef"[j]}</span>{e(u["match"][k][1])}</li>' for j, k in enumerate(order))
    spell = ""
    for i, w in enumerate(u["spell"], 1):
        hide = hidden(w, u["n"])
        boxes = "".join(f'<i class="{"h" if j in hide else ""}">{"" if j in hide else e(ch)}</i>' for j, ch in enumerate(w))
        spell += f'<li><span class="qn">{i}</span><span class="sic">{svg(icon_for(u, w))}</span><span class="letters">{boxes}</span></li>'
    odd = "".join(f'<li><span class="qn">{i}</span>' + "".join(f"<span>{e(x)}</span>" for x in ws) + "</li>"
                  for i, (ws, _) in enumerate(u["odd"], 1))
    return (f'{section("match")}<div class="vmatch"><ul>{left}</ul><ul class="r">{right}</ul></div>'
            f'{section("spell")}<ol class="spell">{spell}</ol>'
            f'{section("odd")}<ol class="odd">{odd}</ol>')


def p_use(u):
    rnd = random.Random(u["n"] * 5)
    bank = [a for _, a in u["gaps"]]
    rnd.shuffle(bank)
    gaps = "".join(f'<li>{e(s).replace("___", "<span class=gapline></span>")}</li>' for s, _ in u["gaps"])
    pw = u["power"]
    items = "".join(f'<li><span class="qn">{i}</span><span class="pq">{e(q).replace("___", "<span class=gapline></span>")}</span>'
                    + ("" if "___" in q else '<span class="arr">→</span><span class="gapline long"></span>') + "</li>"
                    for i, (q, _) in enumerate(pw["items"], 1))
    say = "".join(f'<li class="{"a" if i % 2 else "b"}"><b>{e(en)}</b><small>{e(uz)}</small></li>' for i, (en, uz) in enumerate(u["phrases"]))
    return (f'{section("gaps")}<div class="bank">{"".join(f"<span>{e(w)}</span>" for w in bank)}</div><ol class="gaps">{gaps}</ol>'
            f'{section("power")}<div class="power"><h3>{e(pw["title"])} <small>{e(pw["uz"])}</small></h3><ul>{items}</ul></div>'
            f'{section("say")}<ul class="say">{say}</ul>'
            '<div class="drawit"><p>' + svg("mdi:pencil") + ' Draw it! <small>Ikkita yangi so‘zning rasmini chizing va so‘zni yozing.</small></p>'
            '<div class="frames"><div><i></i></div><div><i></i></div></div></div>')


def p_play(u):
    grid = word_search(u["search"], u["n"])
    cells = "".join("<tr>" + "".join(f"<td>{ch}</td>" for ch in row) + "</tr>" for row in grid)
    words = "".join(f'<li><i class="box"></i>{w.lower()}</li>' for w in u["search"])
    me = "".join(f'<li><p>{i}. {e(q)}</p><i class="wline"></i></li>' for i, q in enumerate(u["you"], 1))
    star = svg("mdi:star", "st")
    can = "".join(f'<li><span>{e(c)}</span><span class="stars">{star * 3}</span></li>' for c in u["can"])
    return (f'{section("search")}<div class="wsearch"><table>{cells}</table><ul>{words}</ul></div>'
            f'{section("me")}<ul class="you">{me}</ul>'
            f'<div class="cando"><h3>{svg("mdi:trophy")} Now I can … <small>Yulduzlarni bo‘yang!</small></h3><ul>{can}</ul></div>')


# ---------------- back matter ----------------
def answer_key():
    out = []
    for u in UNITS:
        order = shuffled(6, u["n"] * 11)
        match = "  ".join(f"{i + 1} {'abcdef'[order.index(i)]}" for i in range(6))
        spell = ", ".join(u["spell"])
        odd = ", ".join(f"{i} {ws[k]}" for i, (ws, k) in enumerate(u["odd"], 1))
        gaps = "  ".join(f"{i} {a}" for i, (_, a) in enumerate(u["gaps"], 1))
        power = "  ".join(f"{i} {a}" for i, (_, a) in enumerate(u["power"]["items"], 1))
        out.append(f'<div class="kunit {u["color"]}"><h3><span>{u["n"]}</span>{e(u["title"])}</h3>'
                f'<p><b>Match:</b> {match}</p><p><b>Spell It:</b> {e(spell)}</p><p><b>Odd One Out:</b> {e(odd)}</p>'
                f'<p><b>Gaps:</b> {e(gaps)}</p><p><b>Word Power:</b> {e(power)}</p></div>')
    return out


def word_list():
    rows = sorted(((bare(en).lower(), en, uz, u["n"]) for u in UNITS for en, uz, _ in u["words"]), key=lambda r: r[0])
    out, letter = [], ""
    for key, en, uz, n in rows:
        first = key[0].upper()
        if first != letter:
            letter = first
            out.append(f'<li class="let">{letter}</li>')
        out.append(f'<li><b>{e(en)}</b><span>{e(uz)}</span><i>{n}</i></li>')
    return out


def cover():
    stickers = "".join(f'<span class="{cls}">{svg(ico)} {title}</span>' for _, title, _, cls, ico in SECTIONS.values())
    floats = "".join(f"<span>{svg(i)}</span>" for i in ("mdi:book-alphabet", "mdi:star", "mdi:lightbulb-on", "mdi:pencil", "mdi:puzzle"))
    return (f'<section class="page cover wcover"><div class="dots"></div><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div>'
            f'<div class="floaters">{floats}</div>'
            '<div class="ctitle"><span class="kicker">TEEN2TEEN 2 · VOCABULARY</span><h1>Word<br>Time! <span class="two">2</span></h1>'
            '<p>12 vocabulary lists · 200+ words · <b>puzzles &amp; games!</b></p>'
            '<p class="uz">Rasmli so‘zlar, mashqlar va boshqotirmalar bilan yangi so‘zlarni o‘rganamiz!</p></div>'
            f'<div class="cstick">{stickers}</div>'
            '<div class="cfoot">For young learners · A1+ · Uzbek support · Answer key + word list</div></section>')


def how_page():
    rows = "".join(f'<li class="{cls}"><span class="secno">{n}</span><div><b>{svg(ico)} {title}</b><small>{e(uz)}</small></div></li>'
                   for n, title, uz, cls, ico in SECTIONS.values())
    units = "".join(f'<li class="{u["color"]}"><span>{u["n"]}</span>{e(u["topic"])}</li>' for u in UNITS)
    return (f'<section class="page"><div class="content"><div class="howhead"><h1>How to use<br>this book</h1><span>{svg("mdi:map-marker-path")}</span></div>'
            '<p class="howintro">Every unit is one <b>vocabulary list</b> from Teen2Teen 2: 4 pages and 9 steps. Learn the words, practise, then play!'
            '<span>Har bir unit Teen2Teen 2 dagi bitta so‘zlar ro‘yxati: 4 sahifa va 9 bosqich. So‘zlarni o‘rganing, mashq qiling, keyin o‘ynang!</span></p>'
            f'<ol class="howlist">{rows}</ol><ul class="ulist">{units}</ul>'
            '<p class="credits">Icons: Material Design Icons (Apache 2.0), game-icons.net by Lorc, Delapouite &amp; contributors (CC BY 3.0), '
            'Healthicons (MIT), Hugeicons (MIT).</p>'
            f'</div><footer><span>{BOOK} · Teen2Teen 2</span><span class="pno">2</span></footer></section>')


def build():
    pages, n = [cover(), how_page()], 3
    for u in UNITS:
        for make in (p_bank, p_practice, p_use, p_play):
            pages.append(page(make(u), n, u))
            n += 1
    keys = answer_key()
    for k in (0, 6):
        head = f'<div class="howhead"><h1>Answer key</h1><span>{svg("mdi:key-variant")}</span></div>' if k == 0 else ""
        pages.append(page(f'{head}<div class="keygrid">{"".join(keys[k:k + 6])}</div>', n, cls="keypage"))
        n += 1
    wl, per = word_list(), 70
    for k in range(0, len(wl), per):
        head = (f'<div class="howhead"><h1>Word list A–Z</h1><span>{svg("mdi:format-list-bulleted")}</span></div>'
                '<p class="wlnote">So‘z · o‘zbekcha · unit</p>') if k == 0 else ""
        pages.append(page(f'{head}<ul class="wlist">{"".join(wl[k:k + per])}</ul>', n, cls="wlpage"))
        n += 1
    css = "".join((ROOT / "scripts" / f).read_text(encoding="utf-8") for f in ("style.css", "kids.css", "reading.css", "vocab.css"))
    fonts = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700'
             '&family=Nunito:ital,wght@0,500;0,700;0,800;0,900;1,500;1,700&display=block">')
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{BOOK}</title>{fonts}<style>{css}</style></head>'
           f'<body>{"".join(pages)}</body></html>')
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist" / "word-time.html").write_text(doc, encoding="utf-8")
    print("pages:", len(pages), "words:", sum(len(u["words"]) for u in UNITS))


if __name__ == "__main__":
    build()
