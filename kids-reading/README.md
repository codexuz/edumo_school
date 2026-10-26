# Read Time! — kids reading comprehension books (Teen2Teen topics)

A5, playful and colourful, companion to "Talk Time!". Two books, 12 units each, every unit an original text
(email, blog, chat, diary, story, poster, letter, article, interview, quiz), Uzbek instructions, answer key at the end.

| Book | Course | Level | Units | PDF |
|------|--------|-------|-------|-----|
| Read Time! 1 | Teen2Teen 1 | A1 | 12 | `dist/Read_Time_1.pdf` |
| Read Time! 2 | Teen2Teen 2 | A1–A2 | 12 | `dist/Read_Time_2.pdf` |

Book 2 follows the Teen2Teen 2 units: present continuous (uniforms, homework, this school year), *there is/are*
with count and non-count nouns (food shopping), daily routines, transport, parents' jobs, health, object pronouns,
*can* for permission with devices, and comparatives.

Each unit has 4 pages and 9 steps:
1. **Before You Read** – 6 picture word cards + a guessing question
2. **Read** – the text in a styled "window" for its text type, key words highlighted
3. **True or False?** · 4. **Choose the Answer** · 5. **Match** (word ↔ picture)
6. **Fill the Gaps** (word bank) · 7. **Word Search** (generated 10×10 puzzle) · fun fact
8. **About You** · 9. **Draw & Write** · "How did I do?" faces

## Build
```
./build.sh            # both books
./build.sh 2          # just Read Time! 2
```
or step by step:
```
python3 scripts/check.py 2    # validate data/units-2/*.json against SCHEMA.md
python3 scripts/build.py 2    # -> dist/read-time-2.html
node scripts/render.js 2      # -> dist/Read_Time_2.pdf (A5, warns about overflowing pages)
```
Book 1 lives in `data/units/`, book 2 in `data/units-2/`; pass `1` or `2` to every script (default `1`).

Unit data format: `SCHEMA.md`. Styles: `scripts/style.css` + `scripts/kids.css` (shared) + `scripts/reading.css`.
Sources: `../kids-speaking/src/teen2teen1.txt` and `teen2teen2.txt` (each unit's title, topic and grammar).

`scripts/check.py` enforces the per-unit counts (6 word cards, 5 true/false, 4 questions, 5 match, 5 gaps,
8 word-search words, 3 about-you questions), the 120–185-word text, and that the word-search words are A–Z only.
A page that would overflow A5 is reported by `render.js` — the A5 text window fits about 4–5 short paragraphs.
