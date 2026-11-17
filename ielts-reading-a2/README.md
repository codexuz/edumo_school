# IELTS Reading Practice · A2

An original IELTS-style reading book for A2 learners. It uses the Mock book design: an A4 two-column layout and the Impulse cover with a book-and-magnifier hero image.

There are 12 units. Each unit has:
- a vocabulary preview of 12 words, each with part of speech, Uzbek meaning and an example
- a reading passage of about 300–350 words in five paragraphs, A–E
- Questions 1–13:
  - Questions 1–5: TRUE / FALSE / NOT GIVEN
  - Questions 6–8: multiple choice
  - Questions 9–10: which paragraph
  - Questions 11–13: sentence completion with ONE WORD ONLY
- vocabulary practice A (matching) and B (gap-fill with a word box)

The back of the book has an answer key and an A–Z word list of 144 words with Uzbek meanings.

## Files
- `data/units/NN.json`: unit content (the format is described in `SCHEMA.md`).
- `assets/brand/`: the logos and the cover hero image.

## Build
Run `./build.sh`. It produces `dist/IELTS_Reading_Practice_A2.pdf` and `dist/IELTS_Reading_A2_Cover_spread_A4.pdf`. The build needs the Python packages qrcode, pypdf and Pillow, plus Playwright with Chromium.
