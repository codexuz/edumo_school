# Multilevel Speaking Mock Tests

This book uses the Multilevel Mock Tests design: an A4 two-column layout, a blue banner for each test, and the Impulse cover with a microphone hero image.

It contains 34 speaking tests:
- Tests 1–10: Real Exam 2026, Set A
- Tests 11–20: Real Exam 2026, Set B
- Tests 21–34: Speaking Mock Book

Each test has four parts, followed by the C1 model answers for all 8 answers:
- Part 1.1: three personal questions
- Part 1.2: two pictures and three questions
- Part 2: a cue card and a picture
- Part 3: a statement with a for and against table

## Sources
- `data/questions_and_sample_answers.json`: the questions, timings and model answers.
- `assets/img/`: the Part 1.2 and Part 2 pictures (`/img/...` paths in the JSON).
- `assets/brand/`: the logos and the cover hero image.

## Build
Run `./build.sh`. It produces `dist/Multilevel_Speaking_Mock_Tests.pdf` and `dist/Speaking_Cover_spread_A4.pdf`.
