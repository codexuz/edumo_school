# IELTS Reading Practice · B1+

An original IELTS-style reading book for learners moving from B1 towards IELTS Academic Reading. It uses the Mock-book design (A4, two columns) and the Impulse cover, in violet so it stands apart from the A2 and B1 books.

There are 12 units, and each one fills a single two-page spread (the passage and its questions are visible together):
- 15 key words, each with part of speech, Uzbek meaning and an example
- an original passage of 610–645 words in seven paragraphs, A–G
- 13 questions in three IELTS Academic task groups
- vocabulary practice A (matching) and B (gap-fill with a word box)

The back of the book has the answer key and an A–Z word list of 180 different words with Uzbek meanings.

| Unit | Topic | Passage | Task types |
|---|---|---|---|
| 1 | Wildlife | The Return of the Wolves | Matching headings · T/F/NG · Summary (from the passage) |
| 2 | Memory | Why We Forget | Multiple choice · T/F/NG · Sentence completion |
| 3 | Environment | A Wall of Trees Across Africa | Matching information · T/F/NG · Summary (word box) |
| 4 | Business | Lines in the Sand | Matching features · Short answers · T/F/NG |
| 5 | Animal behaviour | Finding the Way | Matching headings · Multiple choice · Sentence endings |
| 6 | Work | Working from Anywhere | Y/N/NG · Matching information · Summary (word box) |
| 7 | Transport | The Age of the Bullet Train | T/F/NG · Note completion · Multiple choice |
| 8 | Water | The Disappearing Sea (the Aral Sea) | Matching headings · Sentence completion · T/F/NG |
| 9 | Music | Music and the Brain | Y/N/NG · Multiple choice · Sentence endings |
| 10 | Health | The Forgotten Medicine | Matching information · T/F/NG · Short answers |
| 11 | Insects | The Language of Bees | Sentence completion · T/F/NG · Summary (word box) |
| 12 | Technology | Are Electric Cars the Answer? | Matching headings · Y/N/NG · Multiple choice |

## Files
- `data/units/NN.json`: unit content (format in `SCHEMA.md`).
- `scripts/check.py`: checks every unit (counts, passage length, vocabulary in the passage, answer letters and labels, completion answers copied exactly from the passage within the word limit, 13 questions, no repeated vocabulary).
- `assets/brand/`: logos and the cover hero image.

## Build
Run `python3 scripts/check.py`, then `./build.sh`. The build writes `dist/IELTS_Reading_Practice_B1plus.pdf` (cover, 30 interior pages, back cover) and `dist/IELTS_Reading_B1plus_Cover_spread_A4.pdf`. It needs the Python packages qrcode, pypdf and Pillow, plus Playwright with Chromium.
