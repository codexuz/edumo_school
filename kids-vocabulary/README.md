# Word Time! 2: Teen2Teen 2 vocabulary book for kids

An A5 book in the same playful style as "Talk Time!" and "Read Time!". It has 12 units, one for each Teen2Teen 2 **vocabulary list**: 203 words in total, every word with an SVG icon and its Uzbek meaning. The word lists come from the Teen2Teen 2 Workbook's "Review the Vocabulary" tables, and the unit focus comes from the course lesson plan (`src/teen2teen2-vocabulary.txt`). All exercises were written for this book.

Each unit has 4 pages and 9 steps:
1. **Word Bank**: picture cards for the whole vocabulary list (icon, English, Uzbek) and a "Point & say" pair game
2. **Match** (word ↔ meaning), 3. **Spell It** (missing letters), 4. **Odd One Out**
5. **Fill the Gaps** (word bank), 6. **Word Power** (the unit's grammar or word focus: -ing, plurals, containers, comparatives …),
7. **Say It!** (the unit's social language, with Uzbek) and a **Draw it!** picture-dictionary box
8. **Word Search** (generated 10×10), 9. **About Me** and **Now I can** stars

At the end are an answer key and an A–Z word list with Uzbek and unit numbers.

## Build
```
python3 scripts/icons.py <node_modules/@iconify-json>   # only when icons change -> data/icons.json
python3 scripts/build.py                                 # data/units/*.json -> dist/word-time.html
node scripts/render.js                                   # -> dist/Word_Time_2.pdf (A5, warns about overflowing pages)
```
`scripts/icons.py` reads the Iconify JSON packages `@iconify-json/mdi`, `game-icons`, `healthicons` and `hugeicons` (install them with npm). It also has 4 simple icons drawn by hand: onion, mango, wristband and shy. The icon licences are Material Design Icons (Apache 2.0), game-icons.net (CC BY 3.0, credited in the book), Healthicons (MIT) and Hugeicons (MIT).

The unit data format is visible in `data/units/01-people.json`: `words` holds [English, Uzbek, icon] triples, followed by `match`, `spell`, `odd`, `gaps`, `power`, `phrases`, `search`, `you` and `can`. Styles are in `scripts/style.css` and `scripts/kids.css` (shared), plus `scripts/reading.css` and `scripts/vocab.css`.
