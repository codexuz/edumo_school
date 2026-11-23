"""Build the IELTS Listening Practice B1+ book interior -> dist/mock.html (render.js prints it to PDF).

Data: data/tests.json (from scripts/extract.py): 80 tests (Parts 1–4, 20 each) with their question lines, figures,
answers and audioscripts. Question groups are rendered three ways:
  * choice  – multiple choice / choose TWO / matching boxes: lettered options, structured
  * list    – sentence completion and short answers: numbered items with write-in lines
  * layout  – forms, tables and notes: the original alignment, in a monospaced font with styled gaps
Flow-charts become boxes with arrows; figures are inserted full width.
"""
import base64
import html
import json
import re
from pathlib import Path

from icons import icon

ROOT = Path(__file__).resolve().parent.parent
DIST, FIG = ROOT / "dist", ROOT / "assets" / "figures"
NAME = "IELTS Listening Practice · B1+"
e = html.escape
PART = {
    1: ("A conversation between two people in an everyday social situation", "forms, notes, tables, multiple choice", "1–10"),
    2: ("One person talking about a place, an event or a service", "maps and plans, multiple choice, matching, notes", "11–20"),
    3: ("A conversation between students and a tutor about their studies", "multiple choice, matching, flow-charts, notes", "21–30"),
    4: ("A talk or lecture on an academic subject", "note, table, sentence and summary completion", "31–40"),
}
FLOW = {41: "27"}                                   # "notes" drawn as a flow-chart in the source
FIGTEXT = {"p066_1.png": ["Next steps", "Get approval from 27 ……………", ""]}   # figures that only hold text
HEAD = re.compile(r"\s*Questions?\s+(\d{1,2})(?:\s*(?:-|–|and)\s*(\d{1,2}))?\s*$")
INSTR = re.compile(r"^(Complete|Write|Choose|Circle|Label|Answer|Match|List|Which|What|Who|Where|How|Why|NB)\b")
OPT = re.compile(r"^\s{0,14}([A-I])\s{1,}(\S.*)$")
ITEM = re.compile(r"^\s{0,8}(\d{1,2})\s+(\S.*)$")
DOTS = re.compile(r"(?:…[…\.]+|[…\.]{3,})(?:[ …\.]*[…\.])?")


def gap_html(s, n=None):
    """Escape and turn dotted gaps into write-in lines; '12 ……' becomes a numbered gap."""
    s = re.sub(r"(?<=[…\.]) (?=…)|(?<=…) (?=[…\.])", "", e(s))         # "… ………" is one gap
    s = re.sub(r"(\d{1,2})(\s*(?:£|\$)?\s*)(" + DOTS.pattern + ")", lambda m: f'<b class="gn">{m.group(1)}</b>{m.group(2)}<span class="gp"></span>', s)
    return DOTS.sub('<span class="gp"></span>', s)


def pre_line(s):
    """Monospaced layout line: keep every character cell, style numbers before gaps and the dots themselves."""
    s = e(s)
    s = re.sub(r"(\d{1,2})(\s*(?:£|\$)?\s*)(" + DOTS.pattern + ")",
               lambda m: f'<b class="gn">{m.group(1)}</b>{m.group(2)}<span class="pd">{m.group(3)}</span>', s)
    return re.sub(r"(?<!>)(" + DOTS.pattern + r")(?![^<]*</span>)", r'<span class="pd">\1</span>', s)


def fig(name):
    data = base64.b64encode((FIG / name).read_bytes()).decode()
    return f'<figure class="fig"><img src="data:image/png;base64,{data}" alt=""></figure>'


def groups(lines):
    out, cur = [], None
    for ln in lines:
        m = HEAD.match(ln)
        if m:
            a = int(m.group(1)); b = int(m.group(2) or a)
            cur = {"a": a, "b": b, "lines": []}
            out.append(cur)
        elif cur is not None:
            cur["lines"].append(ln)
    return out


def split_instructions(g):
    ins, rest, k = [], g["lines"], 0
    while k < len(rest) and rest[k].strip() and not rest[k].startswith(("  ", "\t")) and not rest[k].startswith("[[FIG") \
            and not ITEM.match(rest[k]) and not OPT.match(rest[k]) and not DOTS.search(rest[k]) \
            and not re.search(r"\S\s{4,}\S", rest[k].strip()):
        ins.append(rest[k].strip())
        k += 1
    body = rest[k:]
    # instruction sentences that appear later (e.g. after a figure) stay instructions
    return ins, body


def render_flow(body):
    boxes, cur, title = [], [], None
    body = [x for ln in body for x in (FIGTEXT.get(ln.strip()[6:-2], [ln]) if ln.strip().startswith("[[FIG") else [ln])]
    for ln in body + [""]:
        t = ln.strip()
        if not t:
            if cur:
                boxes.append(" ".join(cur)); cur = []
            continue
        if title is None:
            title = t; continue
        cur.append(re.sub(r"\s{2,}", " ", t))
    inner = "".join(f'<div class="fbox">{gap_html(b)}</div>' + ('<div class="farr">▼</div>' if i < len(boxes) - 1 else "")
                    for i, b in enumerate(boxes))
    return f'<div class="fchart"><h5>{e(title or "")}</h5>{inner}</div>'


def body_mode(g, body):
    content = [l for l in body if l.strip() and not l.startswith("[[FIG")]
    opts = [l for l in content if OPT.match(l) and not DOTS.search(l)]
    if len(opts) >= 2:
        return "choice"
    cols = any(re.search(r"\S\s{3,}\S", re.sub(r"^\s*\d{1,2}\s+", "", l)) for l in content)
    indent = any(len(l) - len(l.lstrip()) >= 6 for l in content)
    return "layout" if cols or indent else "list"


def render_choice(g, body):
    out, stem = [], None
    for ln in body:
        t = ln.strip()
        if not t:
            continue
        if t.startswith("[[FIG"):
            out.append(fig(t[6:-2])); continue
        mo, mi = OPT.match(ln), ITEM.match(ln)
        if mo and not DOTS.search(ln) and not (mi and g["a"] <= int(mi.group(1)) <= g["b"]):
            out.append(f'<div class="op"><b>{mo.group(1)}</b><span>{gap_html(mo.group(2).strip())}</span></div>')
        elif mi and g["a"] <= int(mi.group(1)) <= g["b"]:
            out.append(f'<div class="qi"><b class="qn">{mi.group(1)}</b><p>{gap_html(mi.group(2).strip())}</p></div>')
        elif INSTR.match(t) and t.endswith((".", "?")) and len(t) > 25:
            out.append(f'<p class="ins2">{e(t)}</p>')
        elif out and out[-1].startswith('<div class="op">') and len(ln) - len(ln.lstrip()) >= 4:
            out[-1] = out[-1].replace("</span></div>", f" {gap_html(t)}</span></div>")
        elif out and out[-1].startswith('<div class="qi">') and len(ln) - len(ln.lstrip()) >= 3:
            out[-1] = out[-1].replace("</p></div>", f" {gap_html(t)}</p></div>")
        else:
            out.append(f'<p class="sub">{gap_html(t)}</p>')
    return f'<div class="choice">{"".join(out)}</div>'


def render_list(g, body):
    out = []
    for ln in body:
        t = ln.strip()
        if not t:
            continue
        if t.startswith("[[FIG"):
            out.append(fig(t[6:-2])); continue
        mi = ITEM.match(ln)
        if mi and g["a"] <= int(mi.group(1)) <= g["b"]:
            out.append(f'<div class="qi"><b class="qn">{mi.group(1)}</b><p>{gap_html(mi.group(2).strip())}</p></div>')
        elif INSTR.match(t):
            out.append(f'<p class="ins2">{e(t)}</p>')
        elif out and out[-1].startswith('<div class="qi">'):
            out[-1] = out[-1].replace("</p></div>", f" {gap_html(t)}</p></div>")
        else:
            out.append(f'<p class="sub">{gap_html(t)}</p>')
    return "".join(out)


def is_title(t):
    """A centred heading line inside a form or table (not a bullet, a label, a value or a wrapped fragment)."""
    return (len(t) > 3 and not t[:1].islower() and t[:1] not in "-–•(0123456789" and not t.rstrip().endswith((":", "-"))
            and not re.search(r"\w:\s", t) and t.count("(") == t.count(")") and not DOTS.search(t) and t not in ("Yes", "No"))


def table_block(block):
    """Rebuild an aligned text block as a table.
    Columns come from the header row (the first row with 3+ cells) or from where cells start.
    A table row printed over several lines (rows separated by blank lines) is merged column by column."""
    CELL = r"\S(?:.*?\S)?(?=\s{2,}|$)"
    raw = [[(m.start(), m.group(0)) for m in re.finditer(CELL, ln)] for ln in block]
    hdr = next((r for r in raw if 3 <= len(r) <= 5 and all(len(t) <= 22 and ":" not in t and not DOTS.search(t)
                                                          and not re.search(r"\d", t) for _, t in r)), None)
    if hdr:
        anchors = [0] + [c[0] for c in hdr[1:]]
    else:
        anchors = []
        for x in sorted(c[0] for r in raw for c in r):
            if not anchors or x - anchors[-1] > 3:
                anchors.append(x)
        while len(anchors) > 4:                       # merge the two closest anchors
            k = min(range(1, len(anchors)), key=lambda i: anchors[i] - anchors[i - 1])
            anchors.pop(k)
        anchors[0] = 0
    ncol = len(anchors)

    def col_of(x):
        f = max(i for i, a in enumerate(anchors) if a <= x + 1) if x + 1 >= anchors[0] else 0
        if f + 1 < ncol and anchors[f + 1] - x < x - anchors[f]:
            f += 1
        return f

    def split_cell(x, t):
        """Split a cell where one of its words starts exactly on a later column's edge."""
        parts = [[x, []]]
        for m in re.finditer(r"\S+", t):
            wx = x + m.start()
            if parts[-1][1] and any(abs(wx - a) <= 1 and i > col_of(parts[-1][0]) for i, a in enumerate(anchors)):
                parts.append([wx, []])
            parts[-1][1].append(m.group(0))
        return [(px, " ".join(w)) for px, w in parts]

    rows = [[p for x, t in r for p in split_cell(x, t)] for r in raw]
    # groups of lines between blank lines
    groups, cur = [], []
    for r in rows:
        if r:
            cur.append(r)
        elif cur:
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    blanks = len(groups) > 2 and ncol >= 3

    merged = []                                   # (kind, {col: text})
    for gi, g in enumerate(groups):
        if gi:
            merged.append(("sp", {}))
        while hdr and len(g) > 1 and len(g[0]) == 1 and len(g[1]) >= 3 and is_title(g[0][0][1]):
            merged.append(("ti", {0: g[0][0][1]}))            # table title above the header row
            g = g[1:]
        if blanks and 2 <= len(g) <= 5 and any(len(r) > 1 for r in g):
            cols = {}
            for r in g:
                for x, t in r:
                    c = col_of(x)
                    cols[c] = (cols[c] + " " + t) if c in cols else t
            merged.append(("row", cols))
            continue
        for r in g:
            text = " ".join(t for _, t in r)
            mo = re.match(r"^([A-I])\s+(\S.*)$", text)
            if mo and not DOTS.search(text):
                merged.append(("opt", {0: mo.group(1), 1: mo.group(2)}))    # a lettered option in a box
                continue
            if (len(r) == 1 or (not merged and text.upper() == text)) and is_title(text) and (not merged or r[0][0] > 12) and len(text) < 60 and ncol > 1:
                merged.append(("ti", {0: text}))
                continue
            cols = {}
            for x, t in r:
                c = col_of(x)
                cols[c] = (cols[c] + " " + t) if c in cols else t
            if 0 not in cols and merged and merged[-1][0] == "row" and len(r) == 1 and not hdr:
                prev = merged[-1][1]                      # continuation line of the row above
                c = next(iter(cols))
                joint = " " if c in prev and cols[c][:1].islower() and not DOTS.search(prev[c][-4:]) else "<br>"
                prev[c] = (prev[c] + joint + cols[c]) if c in prev else cols[c]
                continue
            merged.append(("row", cols))

    html_rows = []
    for kind, cols in merged:
        if kind == "sp":
            html_rows.append(f'<tr class="sp"><td colspan="{ncol}"></td></tr>')
        elif kind == "opt":
            html_rows.append(f'<tr class="lo"><td colspan="{ncol}"><b class="tl">{cols[0]}</b>{e(cols[1])}</td></tr>')
        elif kind == "ti":
            html_rows.append(f'<tr class="ti"><td colspan="{ncol}">{e(cols[0])}</td></tr>')
        else:
            tds, pos, keys = [], 0, sorted(cols)
            for i, c in enumerate(keys):
                nxt = keys[i + 1] if i + 1 < len(keys) else ncol
                if hdr:
                    nxt = c + 1                       # a real table keeps its columns
                if c > pos:
                    tds.append(f'<td colspan="{c - pos}"></td>')
                cell = "<br>".join(gap_html(x) for x in cols[c].split("<br>"))
                tds.append(f'<td{f" colspan={chr(34)}{nxt - c}{chr(34)}" if nxt - c > 1 else ""}>{cell}</td>')
                pos = nxt
            if pos < ncol:
                tds.append(f'<td colspan="{ncol - pos}"></td>')
            html_rows.append("<tr>" + "".join(tds) + "</tr>")
    while html_rows and html_rows[-1].startswith('<tr class="sp"'):
        html_rows.pop()
    return f'<table class="lay c{ncol}{" grid" if hdr else ""}">{"".join(html_rows)}</table>'


SRC_TABLES = [t for t in json.loads((ROOT / "data" / "tables.json").read_text(encoding="utf-8")) if t["page"] > 3] \
    if (ROOT / "data" / "tables.json").exists() else []
WORD = re.compile(r"[A-Za-z£$0-9][A-Za-z0-9’'\-]*")


def words(s):
    return {w.lower() for w in WORD.findall(s)}


def grid_table(rows):
    """Draw a source table cell for cell (None = merged with the cell on its left)."""
    ncol = max(len(r) for r in rows)
    rows = [r + [None] * (ncol - len(r)) for r in rows]
    # column groups come from the rows that merge cells; header cells drawn inside a group are joined
    merged_rows = [r for r in rows if None in r[1:] and sum(c is not None for c in r) > 1]
    starts = sorted({k for r in merged_rows for k, c in enumerate(r) if c is not None} | {0}) if merged_rows else list(range(ncol))
    bounds = starts + [ncol]
    clean = []
    for r in rows:
        out = []
        for i in range(len(starts)):
            seg = r[bounds[i]:bounds[i + 1]]
            if seg[0] is None and out:
                out.append(None)                                       # merged with the cell on the left
            else:
                out.append("\n".join(c for c in seg if c))
        clean.append(out)
    rows, ncol = clean, len(starts)
    first_data = next((i for i, r in enumerate(rows) if sum(c is not None for c in r) > 1), len(rows)) + 1   # titles + one header row
    if first_data < len(rows) and any(c and DOTS.search(c) for c in rows[first_data - 1]):
        first_data -= 1
    out = []
    for i, r in enumerate(rows):
        r = r + [None] * (ncol - len(r))
        cells, k = [], 0
        while k < ncol:
            span = 1
            while k + span < ncol and r[k + span] is None:
                span += 1
            txt = r[k] or ""
            cell = "<br>".join(gap_html(x) for x in txt.split("\n"))
            tag = "th" if i < first_data else "td"
            cells.append(f'<{tag}{f" colspan={chr(34)}{span}{chr(34)}" if span > 1 else ""}>{cell}</{tag}>')
            k += span
        title = len(cells) == 1 and ncol > 1
        out.append(f'<tr{" class=" + chr(34) + "tt" + chr(34) if title else ""}>{"".join(cells)}</tr>')
    return f'<table class="src">{"".join(out)}</table>'


def match_table(lines):
    """The source table whose words best cover this block of lines, with the lines it covers."""
    bw = words(" ".join(lines))
    best, score = None, 0
    for t in SRC_TABLES:
        tw = words(" ".join(c or "" for r in t["rows"] for c in r))
        if not tw or not bw:
            continue
        sc = len(bw & tw) / len(tw)
        if sc > score and len(bw & tw) / len(bw) > 0.3:
            best, score = t, sc
    if not best or score < 0.85:
        return None
    tw = words(" ".join(c or "" for r in best["rows"] for c in r))
    cov = [i for i, l in enumerate(lines) if l.strip() and len(words(l) & tw) >= 0.7 * len(words(l) or {1})]
    return best, cov[0], cov[-1]


LINES = json.loads((ROOT / "data" / "lines.json").read_text(encoding="utf-8")) if (ROOT / "data" / "lines.json").exists() else []
SEQ = [(pg["page"], ln) for pg in LINES for ln in pg["lines"]]           # every source line, in reading order
RULES = {pg["page"]: pg["rules"] for pg in LINES}
SPAN, CUR = {}, {"n": 0}
for _i, (_p, _ln) in enumerate(SEQ):
    _m = re.fullmatch(r"TEST\s*(\d+)", " ".join(w[2] for w in _ln["w"]))
    if _m:
        SPAN[int(_m.group(1))] = _i
NORM = re.compile(r"[a-z0-9£$]+")


def toks(s):
    return [t for t in NORM.findall(s.lower()) if t]


def locate(lines, n):
    """The run of source lines (inside test n) that holds this block: best matched words minus extras."""
    if n not in SPAN:
        return None
    ends = sorted(SPAN.values())
    a = SPAN[n]
    b = next((x for x in ends if x > a), len(SEQ))
    want = {}
    for t in toks(" ".join(lines)):
        want[t] = want.get(t, 0) + 1
    total = sum(want.values())
    best, cur, start, bi = (0, 0, 0), 0, a, None
    for i in range(a, b):
        ws = toks(" ".join(w[2] for w in SEQ[i][1]["w"]))
        m = sum(1 for t in ws if t in want)
        sc = m - 2 * (len(ws) - m)
        if cur <= 0:
            cur, start = 0, i
        cur += sc
        if cur > best[0]:
            best = (cur, start, i)
    if not total or best[0] < 0.6 * total:
        return None
    return [SEQ[i] for i in range(best[1], best[2] + 1)]


def box_html(region):
    """Rebuild a form / notes box from source word positions: title lines, label and value columns, dividing rules."""
    rows = []                                    # (page, top, [(x0, x1, text, flags)] segments)
    for pg, ln in region:
        segs = []
        for x0, x1, t, f in ln["w"]:
            if segs and x0 - segs[-1][1] < 9:
                segs[-1] = (segs[-1][0], x1, segs[-1][2] + " " + t, "".join(c for c in "bih" if c in segs[-1][3] and c in f))
            else:
                segs.append((x0, x1, t, f))
        if rows and rows[-1][0] == pg and ln["top"] - rows[-1][1] < 9 and " ".join(x[2] for x in rows[-1][2]) in ("•", "-", "–", "▪", "●"):
            segs = rows.pop()[2] + segs                  # a bullet glyph sits a little higher than its text
        rows.append((pg, ln["top"], segs))
    left = min(r[2][0][0] for r in rows)
    right = max(r[2][-1][1] for r in rows)
    mid = (left + right) / 2
    starts = sorted(sg[0] for r in rows for sg in r[2][1:] if len(r[2]) > 1)
    anchors = [left]
    groups = []
    for x in starts:
        if groups and x - groups[-1][-1] <= 14:
            groups[-1].append(x)
        else:
            groups.append([x])
    anchors += [min(gp) for gp in groups if len(gp) >= 2 or len(starts) <= 2]
    anchors = sorted(set(anchors))[:4]
    ncol = len(anchors)

    def col(x):
        return max(i for i, a in enumerate(anchors) if a <= x + 10) if x + 10 >= anchors[0] else 0
    html_rows, prev = [], None
    for pg, top, segs in rows:
        if prev and prev[0] == pg and any(prev[1] + 6 < r < top - 2 for r in RULES.get(pg, [])):
            html_rows.append(f'<tr class="rl"><td colspan="{ncol}"></td></tr>')
        prev = (pg, top)
        text = " ".join(sg[2] for sg in segs)
        x0, x1 = segs[0][0], segs[-1][1]
        bold = all("b" in sg[3] for sg in segs) and not DOTS.search(text)
        on_col = any(abs(x0 - a) <= 12 for a in anchors[1:])
        centred = len(segs) == 1 and x0 > left + 40 and abs((x0 + x1) / 2 - mid) < 12 and not on_col
        if centred or (bold and len(segs) == 1 and x0 > left + 25 and (not on_col or ":" not in text)):
            cls = "ti" if bold else "ce"
            html_rows.append(f'<tr class="{cls}"><td colspan="{ncol}">{gap_html(text)}</td></tr>')
            continue
        cells, pad = {}, {}
        for sg in segs:
            c = col(sg[0])
            while c in cells and c + 1 < ncol:
                c += 1
            if c not in cells and sg[0] - anchors[c] > 6:              # keep the source indent
                pad[c] = (sg[0] - anchors[c]) / (max(right, anchors[-1] + 60) - left) * 186
            h = gap_html(sg[2])
            if "i" in sg[3] and "b" in sg[3]:
                h = f"<em>{h}</em>"
            elif "h" in sg[3]:
                h = f'<span class="hw">{h}</span>'
            cells[c] = (cells[c] + " " + h) if c in cells else h
        tds, pos, keys = [], 0, sorted(cells)
        for i, c in enumerate(keys):
            nxt = keys[i + 1] if i + 1 < len(keys) else ncol
            if c > pos:
                tds.append(f'<td colspan="{c - pos}"></td>')
            sty = f' style="padding-left:{pad[c] + 2:.1f}mm"' if c in pad else ""
            tds.append(f'<td{f" colspan={chr(34)}{nxt - c}{chr(34)}" if nxt - c > 1 else ""}{sty}>{cells[c]}</td>')
            pos = nxt
        html_rows.append("<tr>" + "".join(tds) + "</tr>")
    width = max(right, anchors[-1] + 60) - left
    cols = "".join(f'<col style="width:{100 * ((anchors[i + 1] if i + 1 < ncol else left + width) - anchors[i]) / width:.1f}%">'
                   for i in range(ncol))
    return f'<table class="box c{ncol}"><colgroup>{cols}</colgroup>{"".join(html_rows)}</table>'


def render_layout(g, body):
    out, block = [], []

    def flush():
        while block and not block[-1].strip():
            block.pop()
        while block and not block[0].strip():
            block.pop(0)
        if block:
            ind = min(len(l) - len(l.lstrip()) for l in block if l.strip())
            lines, prev_blank = [], False
            for l in block:
                if not l.strip():
                    if not prev_blank:
                        lines.append("")
                    prev_blank = True
                else:
                    lines.append(l[ind:]); prev_blank = False
            m = match_table(lines)
            if m:
                t, a, b = m
                pre = [x for x in lines[:a] if x.strip()]
                if len(pre) == 1:
                    out.append(f'<p class="ins2">{e(pre[0].strip())}</p>')
                elif pre:
                    out.append(table_block(lines[:a]))
                out.append(grid_table(t["rows"]))
                if any(x.strip() for x in lines[b + 1:]):
                    out.append(table_block(lines[b + 1:]))
            else:
                region = locate(lines, CUR["n"])
                out.append(box_html(region) if region else table_block(lines))
        block.clear()
    for ln in body:
        t = ln.strip()
        if t.startswith("[[FIG"):
            flush(); out.append(fig(t[6:-2]))
        elif INSTR.match(t) and not ln.startswith(" ") and t.endswith(".") and len(t) > 25 and not DOTS.search(t):
            flush(); out.append(f'<p class="ins2">{e(t)}</p>')
        else:
            block.append(ln.rstrip())
    flush()
    return "".join(out)


def test_html(t):
    n, part = t["n"], t["part"]
    CUR["n"] = n
    out = []
    for g in groups(t["lines"]):
        ins, body = split_instructions(g)
        rng = f'Question {g["a"]}' if g["a"] == g["b"] else f'Questions {g["a"]}–{g["b"]}'
        head = f'<h4 class="qh">{rng}</h4>' + "".join(
            f'<p class="{"ins" if INSTR.match(x) else "ins2"}">{e(x)}</p>' for x in ins)
        if FLOW.get(n) == str(g["a"]) or any("flow-chart" in x for x in ins) and not any(l.startswith("[[FIG") for l in body):
            # keep a list of options (A–G) above the flow-chart
            opts = [l for l in body if OPT.match(l)]
            rest = [l for l in body if not OPT.match(l)]
            optbox = ('<div class="choice obox">' + "".join(f'<div class="op"><b>{OPT.match(l).group(1)}</b><span>{e(OPT.match(l).group(2).strip())}</span></div>'
                                                         for l in opts) + "</div>") if opts else ""
            inner = optbox + render_flow(rest)
        else:
            mode = body_mode(g, body)
            inner = {"choice": render_choice, "list": render_list, "layout": render_layout}[mode](g, body)
        out.append(f'<div class="qgrp">{head}{inner}</div>')
    a, b = PART[part][2].split("–")
    bar = (f'<div class="th"><span class="tn">TEST {n}</span><span class="tp">Part {part} · Questions {a}–{b}</span>'
           f'<span class="ta">{icon("headphones")} Audio: Test {n}</span><span class="sc">Score <i></i> / 10</span></div>')
    return f'<div class="test" id="t{n}">{bar}{"".join(out)}</div>'


def part_section(part, tests):
    desc, tasks, qs = PART[part]
    banner = (f'<div class="banner"><div class="girih"></div><div class="bl"><small>IELTS LISTENING · B1+</small><h1>PART {part}</h1></div>'
              f'<div class="br"><b>{icon("headphones", "ico bi")} Tests {tests[0]["n"]}–{tests[-1]["n"]}</b><span>Questions {qs}</span></div></div>'
              f'<p class="pdesc"><b>Part {part}:</b> {e(desc)}. <span>Typical tasks: {e(tasks)}.</span></p>')
    body = "".join(test_html(t) for t in tests)
    return (f'<section class="page flow first" id="part{part}">{banner}<div class="cols one"><div class="col">{body}</div></div>'
            f'<footer><span>{NAME} · Part {part}</span><span class="pno"></span></footer></section>')


def how_page(tests):
    tips = [("book", "Read first", "Use the time before each recording to read the questions. Decide what kind of answer each gap needs: a name, a number, a date, a noun?"),
            ("headphones", "Listen once", "In the real test you hear each recording only once. Play it once, answer, then listen again with the audioscript to check."),
            ("type", "Spelling counts", "Names and words that are spelled out must be written correctly. Check plurals and word limits."),
            ("repeat", "Paraphrase", "The words you hear are often different from the words in the question. Study the synonym tables at the back.")]
    cards = "".join(f'<div class="tip"><span class="tipi">{icon(i)}</span><div><b>{h}</b><p>{d}</p></div></div>' for i, h, d in tips)
    parts = "".join(f'<tr><td>Part {p}</td><td>{e(PART[p][0])}</td><td>Tests {(p - 1) * 20 + 1}–{p * 20}</td>'
                    f'<td class="pg"><i data-ref="part{p}"></i></td></tr>' for p in PART) + "".join(
        f'<tr><td colspan="3"><b>{h}</b></td><td class="pg"><i data-ref="{r}"></i></td></tr>'
        for h, r in (("Answer key", "key"), ("Synonyms &amp; vocabulary", "syn"), ("Audioscripts", "scripts")))
    score = "".join(f'<div class="sb"><b>{t["n"]}</b><i></i></div>' for t in tests)
    return ('<section class="page howpage"><div class="banner"><div class="girih"></div><div class="bl"><small>IELTS LISTENING · B1+</small>'
            f'<h1>HOW TO USE THIS BOOK</h1></div><div class="br"><b>{len(tests)} tests</b><span>Answer key + audioscripts</span></div></div>'
            '<p class="lead">This book has <b>80 practice tests</b> for the <b>IELTS Listening</b> paper: 20 tests for each of the four parts. '
            'Each test has <b>10 questions</b>. At the back of the book are the <b>answer key</b>, a <b>synonym table</b> and a '
            '<b>vocabulary list</b> (with Uzbek meanings) for every test, and all the <b>audioscripts</b>.</p>'
            f'<div class="tips">{cards}</div>'
            f'<table class="plan"><tr><th>Part</th><th>What you hear</th><th>Tests</th><th>Page</th></tr>{parts}</table>'
            f'<h3 class="sect">Scoreboard</h3><div class="score">{score}</div>'
            '<p class="src">For classroom practice only. Not for sale. Tests and recordings adapted from Cambridge IELTS 7, 8 and 9 and '
            '<i>The Official Cambridge Guide to IELTS</i> (Cambridge University Press).</p>'
            f'<footer><span>{NAME}</span><span class="pno"></span></footer></section>')


def answer_key(tests):
    body = ""
    for t in tests:
        items = "".join(f'<span><b>{e(a["q"])}</b> {e(a["a"])}{f" <em>({e(a["note"])})</em>" if a["note"] else ""}</span>' for a in t["answers"])
        body += f'<div class="ka"><h4>Test {t["n"]}</h4><p>{items}</p></div>'
    return ('<section class="page flow first" id="key"><div class="banner small"><div class="girih"></div><div class="bl"><small>TESTS 1–80</small>'
            '<h1>ANSWER KEY</h1></div><div class="br"><span>/ = other correct answers · ( ) = optional words</span></div></div>'
            f'<div class="cols"><div class="col"><div class="split">{body}</div></div><div class="col"></div></div>'
            f'<footer><span>{NAME} · Answer key</span><span class="pno"></span></footer></section>')


EXTRAS = {x["n"]: x for x in json.loads((ROOT / "data" / "extras.json").read_text(encoding="utf-8"))["tests"]}


def synonyms(tests):
    """Per test: how the question wording is paraphrased in the audio, plus key vocabulary with Uzbek meanings."""
    body = ""
    for t in tests:
        x = EXTRAS[t["n"]]
        syn = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in x["syn"])
        voc = "".join(f'<tr><td><b>{e(w)}</b> <i>{e(pos)}</i></td><td>{e(uz)}</td></tr>' for w, pos, uz in x["vocab"])
        body += (f'<div class="sx"><h4>Test {t["n"]} <span>Part {t["part"]}</span></h4><div class="sxr">'
                 f'<table class="syn"><tr><th>In the questions</th><th>In the audio</th></tr>{syn}</table>'
                 f'<table class="voc"><tr><th>Word</th><th>O‘zbekcha</th></tr>{voc}</table></div></div>')
    return ('<section class="page flow first" id="syn"><div class="banner small"><div class="girih"></div><div class="bl"><small>TESTS 1–80</small>'
            '<h1>SYNONYMS &amp; VOCABULARY</h1></div><div class="br"><span>question words → audio words · key words</span></div></div>'
            f'<div class="cols one"><div class="col">{body}</div></div>'
            f'<footer><span>{NAME} · Synonyms &amp; vocabulary</span><span class="pno"></span></footer></section>')


def paragraphs(text):
    s = re.split(r"(?<=[.?!])\s+(?=[A-Z‘'\"])", text)
    paras, cur = [], []
    for x in s:
        cur.append(x)
        if len(" ".join(cur)) > 520 or re.match(r"(Before you|Now listen|You now have|That is the end)", x):
            paras.append(" ".join(cur)); cur = []
    if cur:
        paras.append(" ".join(cur))
    return "".join(f"<p>{e(p)}</p>" for p in paras)


def scripts(tests):
    body = "".join(f'<h4 class="sh">Test {t["n"]}<small>Part {t["part"]}</small></h4>{paragraphs(t["script"])}' for t in tests)
    return ('<section class="page flow first" id="scripts"><div class="banner small"><div class="girih"></div><div class="bl"><small>TESTS 1–80</small>'
            '<h1>AUDIOSCRIPTS</h1></div><div class="br"><span>Read after you check your answers</span></div></div>'
            f'<div class="cols"><div class="col"><div class="split scr">{body}</div></div><div class="col"></div></div>'
            f'<footer><span>{NAME} · Audioscripts</span><span class="pno"></span></footer></section>')


def build():
    tests = json.loads((ROOT / "data" / "tests.json").read_text(encoding="utf-8"))["tests"]
    pages = [how_page(tests)] + [part_section(p, [t for t in tests if t["part"] == p]) for p in PART] + [answer_key(tests), synonyms(tests), scripts(tests)]
    css = "".join((ROOT / "scripts" / f).read_text(encoding="utf-8") for f in ("style.css", "listening.css"))
    fonts = ('<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700;800'
             '&family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&family=JetBrains+Mono:wght@400;700&display=block" rel="stylesheet">')
    DIST.mkdir(exist_ok=True)
    (DIST / "mock.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>IELTS Listening Practice B1+</title>'
                                    f'{fonts}<style>{css}</style></head><body>{"".join(pages)}</body></html>', encoding="utf-8")
    print("tests:", len(tests))


if __name__ == "__main__":
    build()
