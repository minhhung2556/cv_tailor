---
name: cover-letter
description: >-
  Write a one-page English cover letter from assets/cv_base.typ and a job
  description in assets/jd/, saved as Markdown under output/. Use when asked
  for a cover letter, application letter, or a letter for a job in assets/jd.
---

# Cover letter

Write one English cover letter per target job. Reuse the JD parser and CV extract from [cv-tailor](../cv-tailor/SKILL.md). Do not compile PDF or edit the CV unless the user asks.

**Paths:** JD and base CV live in the workspace (`assets/jd/`, `assets/cv_base.typ`, `output/`). Run scripts from the workspace root. Script paths are under this skill's sibling `cv-tailor`, for example `skills/cv-tailor/scripts/` in this repo or `.agents/skills/cv-tailor/scripts/` after install.

## When to load this skill

Load when the user asks to:

- write a cover letter for a job in `assets/jd/`
- draft an application letter for a role
- produce a letter to send with a tailored CV

---

## Workflow

### Step 1: Pick one job description

Use the file the user names under `assets/jd/`. If several files exist and none is named, ask which JD to use before writing.

Supported extensions match the CV tailor parser: `.html`, `.htm`, `.txt`, `.pdf`, `.md`, `.docx`.

### Step 2: Parse the JD

```bash
python <cv-tailor-scripts>/parse_jd.py "assets/jd/<jd_file>" --json
```

Record company name, role title, and top requirements from the parsed text.

### Step 3: Extract candidate facts

```bash
python <cv-tailor-scripts>/extract_cv.py "assets/cv_base.typ" --json
```

Use only facts from that extract, from `assets/github_contributions.json` when present, and verified content from **Reference Links** in the extract. Do not invent employers, dates, metrics, salary, or availability.

**Optional emphasis from a tuned CV:** If `output/` contains a `.typ` whose filename includes the parsed company and role (for example `output/vng_senior_fullstack_and_agentic.typ`), read it and match emphasis only. Ignore PDFs, `output/jobs/`, and `output/assets/cv_base.typ`. If no matching `.typ` exists, ignore `output/`.

### Step 4: Write the letter

Save to:

`output/Cover_Letter_<Candidate>_<Company>_<Role>.md`

Use the candidate name from the extract for `<Candidate>`. Sanitize `<Company>` and `<Role>` for filenames (spaces to underscores, drop characters unsafe on disk).

**Language:** English only. A Vietnamese JD or a user message in another language still produces an English letter.

**Length:** About 250–350 words, one page.

**Structure:**

1. Name and contact from the extract
2. Session date (today's date in the conversation)
3. Company and role (from the JD)
4. Greeting: named contact only if the JD names one; otherwise `Dear Hiring Team,`
5. Opening: state the role and company from the reader’s need (what the hire must deliver), then one evidenced reason this candidate fits. Do not open with a generic enthusiasm line.
6. Two short body paragraphs: two or three proofs from the extract, tied to JD requirements. One proof per sentence. Each proof uses an action verb and a result or scope from the extract. A result clause may sit in the same sentence. Do not restate the CV bullet list. Vary sentence openings; do not start every sentence with `I`.
7. Closing paragraph and sign-off with the candidate name

### Step 5: Report

Tell the user the output path. Summarize which JD requirements you addressed and which proofs you used. Do not edit `assets/cv_base.typ` or tuned CV files unless the user asks.

---

## Prose rules

**Plain English, no dash pauses**

- Short sentences. Do not join clauses with an em dash (U+2014), en dash between words, horizontal bar (U+2015), spaced hyphen pause (` - `), or double hyphen pause (`--`).
- Date ranges and numeric spans may use an en dash (for example `April 2022 – Present`, `20–50%`).
- When a sentence would use a dash, split into two sentences, or use a comma, colon, or parentheses.
- Before finalizing, scan letter prose for U+2014, U+2013, and U+2015 in clause positions and rewrite any hit (except allowed date or range fields).

**Reader-first proofs**

- Put yourself in the reader’s shoes: each paragraph should show readiness for this role, not a biography.
- Numbers in the letter only when the extract or verified Reference Links already have them.

**Avoid AI and JD echo**

- Do not copy JD slogans or stock AI lines. Avoid: leveraged, spearheaded, robust, passionate, results-driven, proven track record, cutting-edge, delve, foster, and vague intensifiers without numbers (for example significantly boosting).
- Prefer plain verbs from the candidate record: shipped, led, cut, fixed, built.
- Do not mirror dash-heavy or slogan wording from the JD. State the same fact in plain sentences.

**Exceptions**

- Keep dashes only in code, stack names, string literals, and verbatim quotations from the JD or CV.

---

## Install

```bash
npx skills add minhhung2556/cv_tailor -a cursor -a claude-code -g -y
```

More install paths and junction setup: [cv-tailor](../cv-tailor/SKILL.md) (Install and agent discovery).
