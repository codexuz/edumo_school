# Unit file: data/units/NN.json (B1 IELTS-style reading unit, original content)

Write ORIGINAL texts and questions (no copying from published books). Level: CEFR B1. The texts should read like
real IELTS General/Academic passages, made easier: clear paragraphs, some complex sentences (relative clauses,
passive voice, present perfect, first and second conditionals), real facts used carefully (avoid exact claims you
are unsure of), and interesting details. The 15 vocabulary items are B1/B2 words taught by the unit. Use British spelling.

```jsonc
{
  "n": 1,
  "topic": "Work",                          // must be one of the topic names listed for your units
  "title": "The Four-Day Week",             // passage title
  "intro": "One sentence that introduces the text.",
  "vocab": [                                // exactly 15, every word appears in the passage (any form)
    {"word": "productive", "pos": "adj", "uz": "samarali", "ex": "I'm most productive in the morning."}
  ],
  "passage": [                              // exactly 6 paragraphs, labelled A–F, 450–520 words in total
    "Paragraph A…", "B…", "C…", "D…", "E…", "F…"
  ],
  "tfng": [                                 // Questions 1–5: TRUE / FALSE / NOT GIVEN; use each answer at least once
    {"q": "…", "a": "TRUE"}
  ],
  "mcq": [                                  // Questions 6–8: 3 options A–C, one correct; test understanding, not word-matching
    {"q": "…", "options": ["…", "…", "…"], "a": "B"}
  ],
  "which_para": [                           // Questions 9–10: "Which paragraph contains…?" answer A–F
    {"q": "an example of a company that changed its working hours", "a": "C"}
  ],
  "completion": [                           // Questions 11–13: NO MORE THAN TWO WORDS from the passage
    {"q": "Workers at the company took fewer ______ during the trial.", "a": "sick days"}
  ],
  "vocab_match": [                          // 6 of the vocab words with simple English meanings
    {"word": "productive", "meaning": "doing or achieving a lot"}
  ],
  "gapfill": [                              // 6 NEW sentences (not from the passage); each answer is one of the 15 vocab words
    {"s": "She is much more ______ when she works from home.", "a": "productive"}
  ]
}
```
Exactly: 15 vocab, 6 paragraphs, 5 tfng, 3 mcq, 2 which_para, 3 completion, 6 vocab_match, 6 gapfill.
Completion answers are 1–2 words that appear exactly (same form) in the passage. NOT GIVEN items must not be inferable.
Mix the MCQ answer letters. Uzbek ("uz") in Latin script with o‘ / g‘ (use the ‘ character). Validate with python json.load.
