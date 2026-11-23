# IELTS Listening Practice · B1+

A practice book of 80 IELTS Listening tests, 20 for each part of the exam. It is for classroom practice only and is not for sale. The tests and recordings are adapted from Cambridge IELTS 7, 8 and 9 and *The Official Cambridge Guide to IELTS* (Cambridge University Press).

The book uses the Mock-book design (A4) and the Impulse cover, in teal so it stands apart from the Reading book. The tests are set in one column. The book has four sections:

- **How to use this book:** tips, a contents table with page numbers, and an 80-box scoreboard.
- **Parts 1–4 (tests 1–80):** each test has a header bar showing the test number, the part and questions, the audio track and a score box, followed by its question groups. Tables are drawn cell by cell from the source PDF (black ruled grid, bold header). Forms and notes keep their source layout in a plain box. Maps, plans and diagrams are cropped from the source.
- **Answer key:** all 800 answers, with alternative answers and notes such as "in either order".
- **Synonyms & vocabulary:** for each test, a table of how the wording in the questions is paraphrased in the audio, and 6 key words with part of speech and Uzbek meaning.
- **Audioscripts:** all 80 scripts.

## Files
- `data/tests.json`: the 80 tests, extracted by `scripts/extract.py <tests.pdf> <scripts.pdf>`. Each test has its question lines, its answers (`q`, `a`, `note`) and its script. Running headers, footers and page numbers from the source are removed.
- `data/tables.json`: the ruled tables of the tests PDF, read with pdfplumber by `scripts/tables.py <tests.pdf>`. `build.py` matches each one to its test by content.
- `data/extras.json`: per test, `syn` (pairs of question wording → audio wording, checked against the scripts) and `vocab` (word, part of speech, Uzbek).
- `assets/figures/`: the maps, plans and diagrams (200 dpi).
- `assets/brand/`: logos and the cover hero image.

## Build
Run `./build.sh`. It writes `dist/IELTS_Listening_Practice_B1plus.pdf` (cover, 134 interior pages, back cover) and `dist/IELTS_Listening_B1plus_Cover_spread_A4.pdf`. It needs Python with qrcode, pypdf, Pillow and pdfplumber, Playwright with Chromium, and poppler-utils (used only by `extract.py`).
