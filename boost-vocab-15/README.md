# Boost Your Vocabulary – Cambridge IELTS 15 (Test 1)

Article + vocabulary workbook in the Impulse mock-book design (A4, two columns).

- **6 lessons**: each Academic Reading passage of Cambridge IELTS 15 Test 1 is split into two parts
  (1 Nutmeg – a valuable spice · 2 Driverless cars · 3 What is exploration?).
- Each lesson: the article with key words highlighted → **Word box** (synonyms `=`, opposites `≠`, definitions,
  Uzbek) → **5 exercises**: synonyms, opposites, sentence completion from the text, find the word, O‘zbekcha → English.
- Answer key and an A–Z word list (347 words with Uzbek).

## Files
- `src/` – text and glossary extracted from *Boost Your Vocabulary – Cambridge IELTS 15* (PyMuPDF; bold = key word).
- `data/uz.json` – Uzbek meanings (please have a teacher check them).
- `scripts/prep.py` – fixes extraction errors, splits lessons, generates exercises → `data/lessons.json`.
- `scripts/build.py`, `vocab.css` – interior HTML; `render.js` paginates; `cover.py` cover; `merge.py` final PDFs.

Build: `bash build.sh` (needs `pip install pymupdf qrcode pypdf`, Playwright Chromium) →
`dist/Boost_Your_Vocabulary_Cambridge_IELTS_15.pdf` and `dist/Boost_Your_Vocabulary_15_Cover_spread_A4.pdf`.
