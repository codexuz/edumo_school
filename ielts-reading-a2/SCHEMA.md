# Unit file: data/units/NN.json (A2 IELTS-style reading unit, original content)

Write ORIGINAL texts and questions (no copying from published books). Level: CEFR A2. Use short sentences,
the past simple, present simple and continuous, and going to/will. Use common words. The 12 vocabulary items
may be slightly harder (A2+/B1), because they are the words being taught. Use British spelling.

```jsonc
{
  "n": 1,
  "topic": "Daily life",                 // 1–3 words, shown on the unit banner; its SVG icon is mapped in scripts/icons.py
  "title": "A Day in the Life of a Baker", // passage title
  "intro": "One sentence that introduces the text, e.g. 'You are going to read about a man who bakes bread every night.'",
  "vocab": [                              // exactly 12, every word appears in the passage (any form)
    {"word": "early", "pos": "adj", "uz": "erta", "ex": "I get up early on weekdays."}
  ],
  "passage": [                            // exactly 5 paragraphs, labelled A–E, 280–330 words in total
    "Paragraph A text…", "Paragraph B…", "Paragraph C…", "Paragraph D…", "Paragraph E…"
  ],
  "tfng": [                               // Questions 1–5: TRUE / FALSE / NOT GIVEN; use at least one of each
    {"q": "Tom starts work at 3 a.m.", "a": "TRUE"}
  ],
  "mcq": [                                // Questions 6–8: 3 options A–C, one correct
    {"q": "Why did Tom become a baker?", "options": ["…", "…", "…"], "a": "B"}
  ],
  "which_para": [                         // Questions 9–10: "Which paragraph contains…?" answer A–E
    {"q": "a description of a typical morning", "a": "C"}
  ],
  "completion": [                         // Questions 11–13: complete the sentence with ONE WORD ONLY from the passage
    {"q": "Tom puts the bread in the ______ at 4 a.m.", "a": "oven"}
  ],
  "vocab_match": [                        // 6 of the vocab words with simple English meanings (for a matching exercise)
    {"word": "early", "meaning": "before the usual time"}
  ],
  "gapfill": [                            // 6 NEW sentences (not from the passage); answer is one of the 12 vocab words
    {"s": "My grandmother gets up ______ every morning.", "a": "early"}
  ]
}
```
Exactly: 12 vocab, 5 paragraphs, 5 tfng, 3 mcq, 2 which_para, 3 completion, 6 vocab_match, 6 gapfill.
Completion answers must be ONE word that appears exactly in the passage. NOT GIVEN items must not be inferable from the text.
Uzbek ("uz") is Latin script, using ʻ/’ correctly (oʻ, gʻ written as o‘, g‘). Validate the file with python json.load.
