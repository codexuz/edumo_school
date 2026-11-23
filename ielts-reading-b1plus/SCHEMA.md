# Unit file: data/units/NN.json (B1+ IELTS-style reading unit, original content)

Write ORIGINAL texts and questions (nothing copied from published books or websites). Level: CEFR B1+ (moving towards B2).
Texts read like IELTS Academic passages, a little easier: a clear argument across 7 paragraphs, some abstract ideas, the passive,
relative clauses, conditionals, reported views ("Some researchers argue that…"), and careful use of real facts (no invented
statistics; keep claims general when unsure). British spelling.

```jsonc
{
  "n": 1,
  "topic": "Nature",
  "title": "The Return of the Wolves",
  "intro": "One sentence that introduces the text.",
  "vocab": [                       // exactly 15 B1+/B2 words; each appears in the passage (any form)
    {"word": "predator", "pos": "n", "uz": "yirtqich", "ex": "The fox is a predator of rabbits and mice."}
  ],
  "passage": ["A…", "B…", "C…", "D…", "E…", "F…", "G…"],   // exactly 7 paragraphs, 600–790 words
  "groups": [ … ],                 // 3 question groups, 13 questions in total, numbered automatically 1–13
  "vocab_match": [{"word": "…", "meaning": "…"}],             // 6 vocab words with simple English meanings
  "gapfill": [{"s": "… ______ …", "a": "word"}]              // 6 NEW sentences; each answer is one of the 15 words, exact form
}
```

## Question groups
| type | fields | notes |
|---|---|---|
| `headings` | `paras` (letters), `options` (headings), `a` (one roman numeral per paragraph) | 2–3 more headings than paragraphs |
| `tfng` / `ynng` | `items: [{q, a}]` | a = TRUE/FALSE/NOT GIVEN or YES/NO/NOT GIVEN; every answer used at least once. YES/NO/NG is about the **writer's views** |
| `mcq` | `items: [{q, options[4], a}]` | 4 options A–D; mix the answer letters |
| `matching_info` | `items: [{q, a}]` | "Which paragraph contains…" a = A–G; may repeat |
| `matching_features` | `features` (list), `items: [{q, a}]` | a = letter of the feature; letters may repeat |
| `sentence_endings` | `endings` (list), `items: [{q, a}]` | 2–3 more endings than items |
| `summary` | `title`, `text` with `______` gaps, `a` (list), `limit` **or** `box` (word list) | without a box, answers are copied exactly from the passage |
| `completion` / `short` | `items: [{q, a}]`, `limit` | completion uses `______`; answers copied exactly from the passage |
| `notes` | `title`, `lines` with `______`, `a` (list), `limit` | answers copied exactly from the passage |

`limit` examples: "ONE WORD ONLY", "NO MORE THAN TWO WORDS", "NO MORE THAN THREE WORDS AND/OR A NUMBER".
Alternative answers: "6 / six". Uzbek in Latin script with o‘ / g‘ (‘ character). Check with `python3 scripts/check.py`.
