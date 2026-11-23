# IELTS Listening Practice · B1+

A practice book of 80 IELTS Listening tests, 20 for each part of the exam. It is for classroom practice only and is not for sale. The tests and recordings are adapted from Cambridge IELTS 7, 8 and 9 and *The Official Cambridge Guide to IELTS* (Cambridge University Press).

The book uses the Mock-book design (A4) and the Impulse cover, in teal so it stands apart from the Reading book. The tests are set in one column. The book has four sections:

- **How to use this book:** tips and a contents table with page numbers.
- **Parts 1–4 (tests 1–80):** each test has a header bar showing the test number, the part and questions, the audio track and a score box. Below it are crops of that test's question pages from the source PDF, without the source's running header and page numbers. The crops are cut at every "Questions …" heading so they flow across the pages.
- **Answer key:** all 800 answers, with alternative answers and notes such as "in either order".
- **Synonyms & vocabulary:** for each test, a table of how the wording in the questions is paraphrased in the audio, and 6 key words with part of speech and Uzbek meaning.
- **Audioscripts:** all 80 scripts.

## Files
- `data/tests.json`: the 80 tests, extracted by `scripts/extract.py <tests.pdf> <scripts.pdf>`. Each test has its answers (`q`, `a`, `note`) and its script. Running headers, footers and page numbers from the source are removed.
- `data/snips.json` and `assets/snips/`: the page crops for each test, made by `scripts/snips.py <tests.pdf>` (pdfplumber + pdftoppm, 150 dpi).
- `data/extras.json`: per test, `syn` (pairs of question wording → audio wording, checked against the scripts) and `vocab` (word, part of speech, Uzbek).
- `assets/brand/`: logos and the cover hero image.

## Build
Run `./build.sh`. It writes `dist/IELTS_Listening_Practice_B1plus.pdf` (cover, 170 interior pages, back cover) and `dist/IELTS_Listening_B1plus_Cover_spread_A4.pdf`. It needs Python with qrcode, pypdf, Pillow and pdfplumber, Playwright with Chromium, and poppler-utils (pdftoppm, pdftotext).
