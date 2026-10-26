# Talk Time! — Teen2Teen speaking books for kids

A5, playful design in the style of "Speak Up! A2" (colour emoji, sticker headers). Two books, 12 units and
120 questions each, taken verbatim from the speaking-question documents in `src/`.

| Book | Course | Level | Source | PDF |
|------|--------|-------|--------|-----|
| Talk Time! 1 | Teen2Teen 1 | A1 | `src/teen2teen1.txt` | `dist/Talk_Time_1.pdf` |
| Talk Time! 2 | Teen2Teen 2 | A1–A2 | `src/teen2teen2.txt` | `dist/Talk_Time_2.pdf` |

Book 2 is the speaking companion to "Read Time! 2" and covers the same Teen2Teen 2 grammar: present continuous,
*there is/are* with count and non-count nouns, present simple and frequency, *by* + transport, third-person jobs,
*should* for advice, object pronouns, *can* for permission, and comparatives.

Each unit has 4 pages and 7 steps:
1. **Word Bank** – 12 picture cards (emoji, English, Uzbek) + "Point & say" pair game
2. **Grammar Helper** – the unit's grammar pattern with examples and a tip
3. **Talk Time** – questions 1–5 with answer starters
4. **More Talk** – questions 6–10 with starters + 3 example answers
5. **Class Survey** – ask 4 classmates
6. **Game Time** – find someone who / dice / board game / spinner / guess who / bingo
7. **My Mini Talk** – a 4-step plan, a model and 3 tries, then "Now I can" stars

## Build
```
./build.sh            # both books
./build.sh 2          # just Talk Time! 2
```
or step by step:
```
python3 scripts/check.py 2    # validate data/units-2/*.json against SCHEMA.md
python3 scripts/build.py 2    # -> dist/talk-time-2.html
node scripts/render.js 2      # -> dist/Talk_Time_2.pdf (A5, warns about overflowing pages)
```
Book 1 lives in `data/units/`, book 2 in `data/units-2/`; pass `1` or `2` to every script (default `1`).

Unit data format: `SCHEMA.md`. Styles: `scripts/style.css` (shared with Speak Up!) + `scripts/kids.css`.

`scripts/check.py` enforces the per-unit counts (12 word cards with no repeated picture, 10 starters, 3 samples,
3 can-dos, the right number of game items for the game type) and — importantly — that the ten questions match
`src/teen2teen<N>.txt` character for character, so an edited question in a unit file is caught before printing.
Each sample answer must also answer one of that unit's own ten questions.
