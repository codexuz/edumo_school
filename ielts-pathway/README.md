# IELTS Pathway A1–B2

An exam-focused course in four levels (A1, A2, B1, B2), each with a **Student's Book** and a **Workbook**. Every unit teaches grammar and vocabulary, then applies them in IELTS-format Listening, Reading, Speaking and Writing tasks at the right difficulty for the level.

* `SERIES_SPEC.md`: the source of truth. It replaces the four General English "English Pathway" guides; section 1 explains what changed and why.
* `levels/a1.md` … `levels/b2.md`: 12-unit course maps with grammar, vocabulary and the IELTS task for each skill.
* `TRACKER.md`: what is done. `OPEN_QUESTIONS.md`: decisions for the owner.
* `a1/data/sb-unit-01.json`, `a1/data/wb-unit-01.json`: the pilot unit (content as JSON).
* `a1/dist/sb.pdf`, `a1/dist/wb.pdf`: the rendered pilot.

## Build
```
./build.sh a1                      # validate, then build both books for A1
./build.sh a1 sb --title "Units 1-3"
python3 scripts/validate.py a1     # checks only
```
The build needs the Python packages qrcode, pypdf and Pillow, plus Playwright with Chromium (the same as the repo's other books).

## Photos
Photos come from Unsplash. The access key is read from the `UNSPLASH_ACCESS_KEY` environment variable and is never stored in the repo.
```
export UNSPLASH_ACCESS_KEY=...                                  # your Unsplash access key
python3 scripts/unsplash.py search "students in a classroom" --sheet /tmp/choices.jpg
python3 scripts/unsplash.py get <photo_id> a1-u02-opener          # -> assets/photos/a1-u02-opener.jpg + credits.json
```
Use a photo in a unit with `"photo": "<name>"` (the unit opener), a `{"type": "photo", "name": "<name>", "h": 34}` block, or `"photo": "<name>"` on a passage. The credit lines are added automatically.

## Unit file format
A unit is a list of `sections` (vocabulary, grammar, listening, reading, speaking, writing, exam or check), each with a `title` and a `goal`. Each section holds `blocks`:
`text`, `table`, `box` (exam / tip / errors), `vocab`, `audio`, `photo`, `passage`, `model`, `checklist`, `score`, `cando`, `selfcheck`, and `ex` (exercise).
Exercise kinds: `short`, `gap`, `choose`, `mcq`, `tf`, `match`, `order`, `correct`, `form`, `speak`, `frames`, `write`.
Answers live with each item (`a`), so the answer key is generated and always matches. Audio scripts live in `scripts` at the end of the unit, and the build prints them at the back of the book.
