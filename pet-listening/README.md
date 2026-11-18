# B1 Preliminary (PET) Listening Practice

A listening practice book with 36 tests in the B1 Preliminary (PET) format. It uses the Mock book design: an A4 two-column layout and the Impulse cover with the headphones-and-checklist hero image.

Each test fills one two-page spread and has 4 parts, 25 questions in all:
- Part 1 (1–7): choose the picture (A, B or C) for seven short recordings
- Part 2 (8–13): multiple choice on six short conversations
- Part 3 (14–19): complete the notes (one or two words, a number, a date or a time)
- Part 4 (20–25): multiple choice on a longer interview

Each part has a QR code next to its instructions that opens the recording. Each test ends with a "Your answers" box (25 boxes and a score).

The front of the book has a how-to page with the test format and a contents list with page numbers. The back has the answer key for all tests and the audioscripts of every recording, with each question shown above its recording.

Tests, pictures and recordings: englishpracticetest.net (Practice PET B1 Listening Tests 1–36). The QR codes link to the MP3 files on that site.

Source fixes made while parsing: Test 15, Question 8 "How will hear…" → "You will hear…" (question and audioscript); Test 30, Part 3 key "15 Town Hall" → "14 Town Hall".
Test 1, Part 4 has explanations on the site; they are kept in the JSON (`explanations`) but not printed, because they name the speaker "Ellie" instead of Andrea.

## Files
- `data/pet_b1_listening_tests.json`: the 36 tests (questions, options, answers, audioscripts, audio and picture links).
- `audio/testNN-partN.mp3`: local copies of all 144 recordings (659 MB, about 16 hours). In the JSON, each part's `audio_file` gives its local file and `audio` gives the online link that the QR code opens.
- `assets/pics/tNN-qN.jpg`: the Part 1 pictures (greyscale, 1000 px wide).
- `assets/brand/`: the logos and the cover hero image.

## Build
Run `./build.sh`. It produces `dist/B1_Preliminary_Listening_Practice.pdf` (cover, 140 interior pages, back cover) and `dist/B1_Preliminary_Listening_Cover_spread_A4.pdf` (the print spread). The build needs the Python packages qrcode, pypdf and Pillow, plus Playwright with Chromium. Set the spine width for the printer in `SPINE_MM` in `scripts/cover.py`.
