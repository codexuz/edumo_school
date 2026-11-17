# IELTS Reading Practice · B1

An original IELTS-style reading book for B1 learners. It uses the Mock book design: an A4 two-column layout and the Impulse cover with a 3D hero image. Each unit fills one two-page spread.

There are 12 units: Work, Education, Health, City life, History, Media, Tourism, Food, Space, Psychology, Inventions and Languages. Each unit has:
- a vocabulary preview of 15 B1/B2 words, each with part of speech, Uzbek meaning and an example
- a reading passage of about 470–520 words in six paragraphs, A–F
- Questions 1–13:
  - Questions 1–5: TRUE / FALSE / NOT GIVEN
  - Questions 6–8: multiple choice (A–C)
  - Questions 9–10: which paragraph
  - Questions 11–13: sentence completion with NO MORE THAN TWO WORDS
- vocabulary practice A (matching) and B (gap-fill with a word box)

The back of the book has an answer key and an A–Z word list of 180 different words with Uzbek meanings.

## Files
- `data/units/NN.json`: unit content (the format is described in `SCHEMA.md`).
- `assets/brand/`: the logos and the cover hero image.

## Build
Run `./build.sh`. It produces `dist/IELTS_Reading_Practice_B1.pdf` (cover, 30 interior pages, back cover) and `dist/IELTS_Reading_B1_Cover_spread_A4.pdf`. The build needs the Python packages qrcode, pypdf and Pillow, plus Playwright with Chromium.
