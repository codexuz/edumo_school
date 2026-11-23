# IELTS Listening Practice · B1+

A practice book of 80 IELTS Listening tests, 20 for each part of the exam. It is for classroom practice only and is not for sale. The tests and recordings are adapted from Cambridge IELTS 7, 8 and 9 and *The Official Cambridge Guide to IELTS* (Cambridge University Press).

The book uses the Mock-book design (A4) and the Impulse cover, in teal so it stands apart from the Reading book. The tests are set in one column. The book has four sections:

- **How to use this book:** tips, a contents table with page numbers, and an 80-box scoreboard.
- **Parts 1–4 (tests 1–80):** each test has a header bar showing the test number, the part and questions, the audio track and a score box, followed by its question groups. Tables are drawn cell by cell from the source PDF (black ruled grid, bold header). Forms and notes are rebuilt from the word positions in the source PDF (label and value columns, indents, bold titles, dividing lines) in a plain black box. Maps, plans and diagrams are cropped from the source.
- **Answer key:** all 800 answers, with alternative answers and notes such as "in either order".
- **Synonyms & vocabulary:** for each test, a table of how the wording in the questions is paraphrased in the audio, and 6 key words with part of speech and Uzbek meaning.
- **Audioscripts:** all 80 scripts.

## Files
- `data/tests.json`: the 80 tests, extracted by `scripts/extract.py <tests.pdf> <scripts.pdf>`. Each test has its question lines, its answers (`q`, `a`, `note`) and its script. Running headers, footers and page numbers from the source are removed.
- `data/tables.json` and `data/lines.json`: written by `scripts/tables.py <tests.pdf>` (pdfplumber). The first holds the ruled tables, cell for cell. The second holds every text line with word positions and fonts, plus the horizontal rules. `build.py` matches each table and form to its test by content.
- `data/extras.json`: per test, `syn` (pairs of question wording → audio wording, checked against the scripts) and `vocab` (word, part of speech, Uzbek).
- `assets/figures/`: the maps, plans and diagrams (200 dpi).
- `assets/brand/`: logos and the cover hero image.

## Build
Run `./build.sh`. It writes `dist/IELTS_Listening_Practice_B1plus.pdf` (cover, 137 interior pages, back cover) and `dist/IELTS_Listening_B1plus_Cover_spread_A4.pdf`. It needs Python with qrcode, pypdf, Pillow and pdfplumber, Playwright with Chromium, and poppler-utils (used only by `extract.py`).
