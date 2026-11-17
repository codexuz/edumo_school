# A2 Key (KET) Listening Practice

A listening practice book with 44 tests in the A2 Key (KET) format. It uses the Mock book design: an A4 two-column layout and the Impulse cover with the headphones hero image.

Each test fills one two-page spread and has 5 parts, 25 questions in all:
- Part 1 (1–5): choose the picture (A, B or C)
- Part 2 (6–10): complete the notes
- Part 3 (11–15): multiple choice on a longer conversation
- Part 4 (16–20): multiple choice on five short recordings
- Part 5 (21–25): match each person to a letter, A–H

Each part has a QR code next to its instructions that opens the recording. Each test ends with a "Your answers" box (25 boxes and a score).

The front of the book has a how-to page with the test format and a contents list with page numbers. The back has the answer key for all tests and the audioscripts of every recording.

Tests, pictures and recordings: englishpracticetest.net (Practice KET A2 Listening Tests 1–44). The QR codes link to the MP3 files on that site.

## Files
- `data/ket_a2_listening_tests.json`: the 44 tests (questions, options, answers, audioscripts, audio and picture links).
- `audio/testNN-partN.mp3`: local copies of all 220 recordings (591 MB, about 14 hours). In the JSON, each part's `audio_file` gives its local file and `audio` gives the online link that the QR code opens.
- `assets/pics/tNN-qN.jpg`: the Part 1 pictures (greyscale, 1000 px wide).
- `assets/brand/`: the logos and the cover hero image.

## Build
Run `./build.sh`. It produces `dist/A2_Key_Listening_Practice.pdf` (cover, 149 interior pages, back cover) and `dist/A2_Key_Listening_Cover_spread_A4.pdf` (the print spread). The build needs the Python packages qrcode, pypdf and Pillow, plus Playwright with Chromium. Set the spine width for the printer in `SPINE_MM` in `scripts/cover.py`.
