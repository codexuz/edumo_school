# A Complete Guide to Multilevel Writing

The Uzbek Multilevel (CEFR) writing paper, trained part by part: the paper explained in Uzbek,
the official band descriptors, an examiner-marked script, then ten full practice exercises with
model answers and English–Uzbek word lists. A4 portrait, 74 pages, in the dodger-blue design of
the Impulse vocabulary books (`--blue:#1E90FF` / `--blue-d:#0B63CE` / `--navy:#0A2A5E`, Inter).

Rebuilt from `A Complete Guide to Multilevel Writing` (the source PDF in `src/`).

## Contents

| Pages | Section |
|---|---|
| 1 | Cover |
| 2 | How to use this book · marks at a glance |
| 3–5 | Yozma ish: tuzilma va talablar — the paper, the language functions and the marking, in Uzbek |
| 6–9 | Band descriptors for Part 1.1, Part 1.2 and Part 2, with the target bands tinted |
| 10–12 | A marked script: three responses with their marks and the examiner's comments |
| 13–73 | Exercises 1–10 — six pages each: tasks · three lined answer pages · model answers + 20 words for Part 1 · model answer + 20 words for Part 2 |
| 74 | Before you hand it in — final checklist and useful language |

Each exercise gives one situation and three tasks: Task 1.1 (informal email, ~50 words, 5 marks),
Task 1.2 (formal email, 120–150 words, 6 marks) and Task 2 (discussion post, 180–200 words, 6 marks).

## Build

```
./build.sh     # -> dist/Multilevel_Writing_Guide.pdf
```

`build.sh` runs `scripts/check.py` first, so the build fails if any model answer falls outside its
word band or a vocabulary list is not exactly 20 complete pairs. `scripts/render.js` warns about
any page whose content would overflow A4.

- Content: `data/*.json` — format in `SCHEMA.md`. Nothing in `scripts/` needs editing to change text.
- Design: `scripts/style.css`. `scripts/build.py` emits `dist/cover.html` + `dist/body.html`;
  the cover is printed separately so the running header and page number stay off it.

## Changes made to the source material

### Model answers

Every one of the 30 model answers was rewritten so that it sits inside the word band its own task
asks for. In the source, most Task 1.2 answers ran 150–210 words against a 120–150 ceiling and
most Part 2 answers ran 205–220 against 180–200 — a model answer that breaks the rubric teaches
the wrong lesson. They are now 51–56 / 122–137 / 185–200 words.

Specific faults fixed:

- **Exercise 1, Task 1.1** — the letter was addressed "Hi Alex" and signed "Alex", so the writer
  and the recipient were the same person. It also answered only half the task: it gave feelings
  but suggested visiting a coffee shop instead of saying what the library should do. Rewritten.
- **Exercise 6, Task 1.1** — ended "Talk soon," with no name. Signature added.
- **Exercise 8, Task 1.1** — contained "Let's discuss about this", which a model answer should
  not teach. Rewritten.
- **Exercise 9, Task 1.2** — opened "Dear The Manager". Now addressed to a named manager.
- **Sign-offs** — made to follow one rule throughout: a named person or title-holder takes
  *Yours sincerely*, a role or department with no name takes *Dear Sir or Madam* / *Yours
  faithfully*. Exercises 3, 5 and 7 changed accordingly, and the rule is stated on page 74.

### Task prompts

- Exercise 9: "you are unemployment" → "you are currently unemployed".
- Exercise 8, Part 2: "Should students not be allowed to use smartphones at schools?" → "Should
  students be banned from using smartphones at school?" (the double negative made the stance
  impossible to state cleanly).
- Exercise 10, Part 2: the question was ungrammatical ("…or traditional subjects like math and
  science are important?") and has been rewritten as a straight either/or.
- Exercise 4, Part 2: "impacts" → "impact".
- Exercises 5, 7, 8 and 10: the prompt letter and the tasks were printed run together in one
  block; they are now separate elements. Exercise 8's prompt letter was also lightly corrected
  ("your disturbance made some inconveniences for me").
- British spelling used consistently (neighbourhood, centre, organise). US spellings are kept
  verbatim where they appear inside the official band descriptors and Exercise 1's prompt letter.

### Vocabulary lists

Standardised at exactly 20 English–Uzbek pairs per task, drawn from the model answers.

- Many source entries had lost their spaces in the PDF (`Bestregards-Engyaxshitilaklarbilan`,
  `Welcomeexperience-Qarshiolishtajribasi`); all re-spaced.
- Exercise 3 listed 30 items with "Onboarding process" twice; Exercise 6 had 10 items plus a
  separate 9-item "Phrases/Collocations" block. Both merged and trimmed to 20.
- Mistranslations corrected: "Perceive — ishonmoq" (to believe → *idrok qilmoq*), "Relaxed
  opportunity — Noyob imkoniyat" (*noyob* = rare), "Eager to discuss — Muhozakaga intilish"
  (*Muhokamaga*).

### Guide and apparatus

- The Uzbek guide had several paragraphs with their spaces lost in the PDF
  (`Bubo'limdanomzodumumiyqiziqishuyg'otadiganmavzuasosida`); all restored.
- Marked script, Task 2: the examiner's comment read "The response is relevant, but the stance is
  clear"; the contrastive "but" is a slip and is printed as "and".
- The band descriptor tables are reproduced in full. The source highlighted rows in green without
  a stated meaning; here the tint marks the bands the book trains you to reach, and the key says so.
