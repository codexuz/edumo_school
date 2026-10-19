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
  "vocab_task1":  [["library", "библиотека", "kutubxona"], …],  // exactly 20 triples
  "vocab_part2":  [["flexibility", "гибкость", "moslashuvchanlik"], …]
}
```

In `samples`, a first entry shorter than 40 characters is styled as a greeting and
either of the last two is styled as a sign-off; everything else is a body paragraph.

Each word list is exactly 20 `[English, Russian, Uzbek]` triples.

`scripts/check.py` enforces the word bands (Task 1.1 45–60, Task 1.2 120–150,
Task 2 180–200), the 20 complete triples, and that the practice tasks build.
`build.sh` runs it first, so a sample outside its band fails the build.

## `data/sentences.json`

The hand-written sentence-transformation task (practice task D), keyed by
exercise number:

```jsonc
{
  "1": {
    "lead": "Rewrite each line so that it would fit Task 1.2 …",
    "items": [["Thanks a lot for telling us about the works.",
               "Thank you for letting us know about the upcoming renovations."], …]
  }
}
```

The first element is printed as the prompt; the second is the suggested answer
and appears only in the answer key. Five items per exercise.

## Practice tasks

Only task D is written by hand. `scripts/practice.py` derives the other three
from the exercise's own data, so editing a word list or a model answer changes
the practice and the answer key with it:

- **A — Complete the sentence**: eight sentences taken from the unit's model
  answers, each with one word-list term blanked out.
- **B — Match English to Uzbek**: eight terms, the Uzbek column shuffled.
- **C — Choose the English word**: six Russian prompts with three English options.

The shuffling is seeded on the exercise number, so the same book is produced
on every build.

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
