# Data format

All content lives in `data/`. Nothing in `scripts/` needs editing to change the book's text.

## `data/exercise-NN.json`

One complete writing paper. `scripts/build.py` picks up every `exercise-*.json` in
filename order, so adding `exercise-11.json` adds Exercise 11 to the book.

```jsonc
{
  "n": 1,                       // exercise number, printed in the banner
  "topic": "A library closure", // banner title
  "context": "You are a member of a local community library. …",
  "letter": {                   // the prompt letter the candidate receives
    "greeting": "Dear Member,",
    "paragraphs": ["…", "…"],
    "signoff": "Best regards,",
    "signer": "The Head Librarian"
  },
  "task11": "Write a letter to your friend, …",   // about 50 words
  "task12": "Write a letter to the head librarian, …", // 120–150 words
  "part2_question": "What are the advantages and disadvantages of online learning …?",
  "samples": {                  // model answers, one array entry per paragraph
    "task11": ["Hi Jack,", "…", "Best,", "Alex"],
    "task12": ["Dear Head Librarian,", "…", "Yours sincerely,", "Alex"],
    "part2":  ["…", "…"]
  },
  "vocab_task1":  [["library", "kutubxona"], …],  // exactly 20 [English, Uzbek] pairs
  "vocab_part2":  [["flexibility", "moslashuvchanlik"], …]
}
```

In `samples`, a first entry shorter than 40 characters is styled as a greeting and
either of the last two is styled as a sign-off; everything else is a body paragraph.

`scripts/check.py` enforces the word bands (Task 1.1 45–60, Task 1.2 120–150,
Task 2 180–200) and that each vocabulary list holds exactly 20 complete pairs.
`build.sh` runs it first, so a sample outside its band fails the build.

## `data/guide.json`

The Uzbek explanation of the paper: `intro`/`intro_list`, two `sections` (each with
`cards` describing a task, an optional `note` and an optional `extra` list),
`functions`, `marking` (one entry per part, with `bands` and `criteria`) and the
closing `conclusion_*` / `success` blocks. Each section prints on its own page.

## `data/descriptors.json`

A list of three parts. Each has `part`, `subtitle`, `target` (the band numbers
tinted as "what this book trains you to reach") and `bands`, where each band is
`{band, level, lead, points}`.

## `data/worked-sample.json`

The official examiner-marked script: `tasks` (each with `label`, `mark`, `max`,
`response` paragraphs and `comment` paragraphs), the `overall` scores, and
`takeaways`. The page breaks after Task 1.2.
