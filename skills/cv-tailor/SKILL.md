---
name: cv-tailor
description: Tune and tailor candidate CVs against Job Descriptions (JD) in assets/jd to generate Harvard-style PDFs in /output. Load this skill when asked to tune a CV, match a resume to a job description, update a CV for a target role, or process job descriptions from assets/jd.
---

# CV Tailor Skill

This skill automates the process of tailoring a candidate's base resume (`assets/cv_base.typ`, or `assets/cv_base.pdf` when present) to match specific Job Description (JD) requirements found in `assets/jd/`, generating a clean, Harvard-style PDF in `output/`.

**Paths:** CV and JD files live in the **workspace** (the project you are tuning, usually the repo root with `assets/` and `output/`). Scripts live under this skill directory (`SKILL.md` and `scripts/`). Run them with the workspace as the shell working directory. Use the path to `scripts/parse_jd.py` (and siblings) from wherever this skill is installed, for example `skills/cv-tailor/scripts/` in this repo, `.agents/skills/cv-tailor/scripts/` after Cursor install, or `.claude/skills/cv-tailor/scripts/` after Claude Code install.

## When to load this skill

Load this skill whenever the user asks to:
- "tune my CV for a job description"
- "match my resume to a JD"
- "create a customized CV from assets/cv_base.pdf"
- "generate a targeted CV for a job in assets/jd"

---

## Workflow & Step-by-Step Instructions

### Step 1: Detect and Parse Job Description(s)
Check `assets/jd/` for target JD files (supported extensions: `.html`, `.htm`, `.txt`, `.pdf`, `.md`, `.docx`).
Legacy `.doc` (old binary Word) is not supported. Convert it to `.docx` (or export as PDF/text) first.
The parser keeps HTML `<header>` and document `<title>` text, and removes nav, footer, scripts, and styles. Unsupported extensions raise an error instead of being read as plain text.
Run the parser script to extract clean text (replace `<skill-scripts>` with this skill's `scripts/` directory):
```bash
python <skill-scripts>/parse_jd.py "assets/jd/<jd_file>" --json
```

### Step 2: Read Base CV and personal evidence
Extract the full candidate history from the base CV path (default `assets/cv_base.typ`; `extract_cv.py` prefers a sibling `.typ` when you pass `.pdf`):
```bash
python <skill-scripts>/extract_cv.py "assets/cv_base.typ" --json
```

Use only facts from that extract, from `assets/github_contributions.json` when present (GitHub repo metadata and authored-commit counts from [github-contributions](../github-contributions/SKILL.md)), plus verified content from URLs listed under **Reference Links** in the extract. Do not invent dates, metrics, or scope. Prefer `.typ` over `.pdf` for extraction: PDF text order is lossy for multi-column layouts.

### Step 3: Analyze Requirements & Map Accomplishments
0. **Evidence inventory** (before tailoring):
   - List every employer, founder or independent product, credential, and named skill from the extract, from `assets/github_contributions.json` when present, plus verified facts from Reference Link pages.
   - The tuned CV must retain each item. Reorder and rephrase for the JD; do not drop an evidenced employer, product, credential, or skill category.
   - If a product appears only as a URL in Reference Links, include a short **Experience** or **Projects** entry with truthful bullets from those linked pages.

1. **Identify Target Parameters**:
   - Role Title & Level (e.g. Senior Flutter Engineer, Mobile Architect)
   - Hiring Company & Location
   - Top 5-7 Required Qualifications & Key Responsibilities
   - Target Domain/Tech Stack Keywords (e.g., Flutter rendering pipeline, custom widgets, CI/CD, state management)

2. **Extract and place JD keywords** (before rewriting sections):
   - From the parsed JD, build a keyword list: role title, must-have tools, domains, and repeated responsibility phrases. Keep the JD's exact wording. Cap at about 15 terms.
   - Place terms in the tuned CV only where the base CV already supports them. Priority: Professional Summary, Core Competencies, first bullets of the latest role, Technical Skills.
   - When the JD names a skill the candidate has under different wording, use the JD phrase (e.g. JD says `FastAPI`, base CV describes that work as Python APIs → use `FastAPI` in the tuned CV).
   - Do not add a keyword without evidence in the base CV or verified personal-site pages. In the Step 6 report, list keywords used and keywords skipped (no evidence).

3. **Tailor CV Content Truthfully**:
   - **Professional Summary**: Rewrite in English to emphasize years of experience and achievements directly relevant to the target role.
   - **Core Competencies**: Highlight key domains and principles matching the JD.
   - **Experience**: Reorder and reframe bullet points under each employer to prioritize relevant projects, metrics, and accomplishments matching the target JD. *Do not fabricate unverified experience.*
   - **Technical Skills**: Rearrange skill categories so the target technology stack is featured first.

Before rewriting a base CV whose bullets mix product with libraries, or whose summary, competencies, and skills repeat the same claim, follow [cv-section-audit](../cv-section-audit/SKILL.md). Tailoring still uses only facts from the extract.

### Writing (CV prose)

Governs Professional Summary, Core Competencies, and experience bullets only. Does not change chat style, scripts, or Harvard Typst layout. Aligns with [Harvard FAS resume guidance](https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/) (specific, active, fact-based, skim-friendly) and common CV best practices (short document, honest tailoring, personal profile up front).

**Truth and structure**

- Facts only from the extract and verified Reference Link pages. Reframe order and emphasis. Do not invent scope, titles, or metrics.
- One claim per bullet. Each experience bullet is one short sentence: **action verb**, then the **product or decision**, then an **evidenced result** (what shipped, what changed). Use a number only when the base CV or verified Reference Links already have it. When they do not, qualify with scope already in the extract (market, team size, users, what changed). Do not invent a percentage or statistic to sound impressive.
- **Skim-first.** Recruiters scan quickly. Put the bullets most relevant to the JD first within each role. Experience and Education stay reverse chronological.
- **Voice.** Active voice. No `I`, `we`, `my`, or `our` in the CV. No narrative paragraphs under a role. Do not start a bullet with a date; dates stay in the experience header. Past tense for past roles; present tense only for the current role.
- **Professional Summary (personal profile).** Three to four lines: years, industries, and the strongest evidenced results for this JD. No tool list (see [cv-section-audit](../cv-section-audit/SKILL.md)). If a sentence could describe any applicant for the role, replace it with a fact from the extract. Edit the candidate record; do not author a generic profile.
- **Length.** Target at most two pages in the compiled PDF. Keep every evidenced employer, product, credential, and education line. Shorten older roles to fewer bullets before dropping anything. If the PDF is still over two pages, say so in the Step 6 report instead of dropping evidence.
- **Gaps.** Do not invent a job or a “career break” sentence. If a credential, product, or side project in the extract falls between roles, place that entry so the timeline is readable. If nothing in the extract explains a gap, leave the dates as they are.

**Verbs**

- Prefer plain verbs from the candidate record: shipped, led, cut, fixed, built.
- When the extract supports it, specific Harvard-style verbs are fine: designed, engineered, launched, reduced, mentored, negotiated, documented, coordinated, improved.
- Do not use spearheaded, leveraged, utilized, or other banned stock lines below even if they appear on verb lists elsewhere.

**Language pass (before compile)**

- Spelling and grammar. No slang or colloquialisms.
- Spell out uncommon non-technical abbreviations. Keep JD keywords and standard technical abbreviations (`API`, `CI/CD`, `iOS`).
- No photo, age, gender, or “references available” line. **Reference Links** are portfolio or work URLs, not character references.
- Be consistent in formatting and section emphasis. Do not abbreviate employer names in ways the extract does not use.

**Plain prose (no dash pauses)**

- Short sentences. Do not join clauses with an em dash (U+2014), en dash between words, horizontal bar (U+2015), spaced hyphen pause (` - `), or double hyphen pause (`--`).
- Date ranges and numeric spans in Typst metadata are OK (e.g. `April 2022 – Present`, `20–50%`): en dash between numbers, not between prose clauses.
- When a sentence would use a dash, split into two sentences, or use a comma, colon, or parentheses. Do not replace one dash with another dash-like character.
- Before finalizing CV text, scan prose for U+2014, U+2013, and U+2015 in clause positions and rewrite any hit (except allowed date/range fields above).

**Avoid AI and JD echo**

- Do not copy JD slogans or stock AI lines into the CV. Avoid: leveraged, spearheaded, robust, passionate, results-driven, proven track record, cutting-edge, delve, foster, and vague intensifiers without numbers (e.g. significantly boosting).
- Prefer plain verbs from the candidate record: shipped, led, cut, fixed, built.
- Do not mirror dash-heavy or slogan wording from the JD. State the same fact in plain sentences.

**Exceptions**

- Keep dashes only in code, stack names, string literals, regex, Unicode escapes, and verbatim quotations.

### Step 4: Write Harvard-Style Typst Document
Create a `.typ` file under `output/` (or another writable path). Import the Harvard template by filename; `compile_cv.py` copies `harvard_cv.typ` next to your source and sets Typst `--root` to the workspace:

```typst
#import "harvard_cv.typ": cv, cv_section, cv_experience, cv_entry, cv_url

#show: cv.with(
  name: "<NAME_FROM_EXTRACT>",
  title: "<TARGET_ROLE_TITLE>",
  contact: "<CONTACT_FROM_EXTRACT>",
)

#cv_section("Professional Summary")
<Tuned summary from extract, aligned to JD...>

#cv_section("Core Competencies")
<Tuned competencies from extract...>

#cv_section("Experience")
<One #cv_experience(...) per employer/product in the extract; tuned bullets only, same entries as extract>

#cv_section("Selected Credentials and Speaking")
<One #cv_entry(...) per credential in the extract>

#cv_section("Reference Links")
<URLs from extract, same links as base CV>

#cv_section("Technical Skills")
<Skill categories from extract, reordered for JD>

#cv_section("Education")
<One #cv_entry(...) per education line in the extract>
```

### Step 5: Compile PDF to Output Directory
Relative paths passed to `compile_cv.py` (Typst source and output PDF) are resolved from the workspace root, not only the shell working directory.
If you omit the PDF path, `compile_cv.py` writes `<source>.pdf` beside the `.typ` file.
**Requires the `typst` CLI.** If Typst is not installed, use the Word route in Step 5-ALT instead.
Run `compile_cv.py` with an explicit destination for the tuned CV:
```bash
python <skill-scripts>/compile_cv.py "output/tuned_cv.typ" "output/CV_<Candidate_Name>_<Company>_<Role>.pdf"
```

### Step 5-ALT: Export as Word (.docx) instead of or in addition to PDF
When the user wants an editable Word document (or has no Typst installed), skip the Typst route and render the tuned CV from a JSON spec. The JSON schema mirrors the Typst helpers one-to-one (see `resources/cv_spec.example.json` in this skill):

- `type: "text"` → a paragraph (like `cv_section` + prose)
- `type: "bullets"` → a bulleted list (Core Competencies, Technical Skills)
- `type: "experience"` → `cv_experience` entries (company/location/role/dates/bullets)
- `type: "entries"` → `cv_entry` items (title/subtitle/dates/details) for Education, Credentials

Write the tuned spec (e.g. to `output/<name>.json`), then render:
```bash
python <skill-scripts>/build_docx_cv.py "output/<name>.json" "output/CV_<Candidate_Name>_<Company>_<Role>.docx"
```
The `.docx` reproduces the Harvard layout (A4, Times New Roman, centered header, ruled section headings, right-aligned dates) with `python-docx` only. No Typst required.

To also produce a PDF from that `.docx` without Typst (MS Word on Windows, or LibreOffice if `soffice` is on PATH):
```bash
python <skill-scripts>/docx_to_pdf.py "output/CV_<Candidate_Name>_<Company>_<Role>.docx" "output/CV_<Candidate_Name>_<Company>_<Role>.pdf"
```

### Install and agent discovery

This repository ships four agent skills under `skills/`: `cv-tailor`, `cover-letter`, `github-contributions`, and `cv-section-audit`. Repo-level install commands below add all of them. `./skills/cv-tailor` installs only this skill.

Install globally (GitHub shorthand). Use `-a cursor`, `-a claude-code`, or both:
```bash
npx skills add minhhung2556/cv_tailor -a cursor -a claude-code -g -y
npx skills add minhhung2556/cv_tailor -a claude-code -g -y
```

From a local clone, pass the repository path. Use an absolute path, `.`, or `..`. A bare folder name is treated as a GitHub repository, not a local directory.
```bash
npx skills add /path/to/cv_tailor -a claude-code -g -y
npx skills add . -a cursor -a claude-code -g -y
npx skills add ./skills/cv-tailor -a claude-code -g -y
```

From a git URL:
```bash
npx skills add https://github.com/minhhung2556/cv_tailor.git -a claude-code -g -y
npx skills add git@github.com:minhhung2556/cv_tailor.git -a cursor -g -y
npx skills add https://github.com/minhhung2556/cv_tailor/tree/main/skills/cv-tailor -a claude-code -g -y
```

Omit `-g` to install into the current project (`.agents/skills/<name>` for Cursor, `.claude/skills/<name>` for Claude Code). Private repos use the same commands with your configured git credentials. If Windows refuses the symlink, add `--copy`.

**Cursor:** import `https://github.com/minhhung2556/cv_tailor` in Cursor Plugins to load every skill from the repository marketplace manifest (`skills` in [.cursor-plugin/plugin.json](../../.cursor-plugin/plugin.json)).

**Claude Code:** register the marketplace, then install the plugin:
```text
/plugin marketplace add minhhung2556/cv_tailor
/plugin install cv-tailor@cv-tailor
```

In this repository, `.agents/skills/<name>` and `.claude/skills/<name>` are junctions to `skills/<name>` for each skill (not second copies). After clone, recreate them with:
```bash
python skills/cv-tailor/scripts/link_agent_skill.py
```
Use `--force` only to replace a real directory at an agent skill path (not a junction).

### Step 6: Verify and Report Output
1. Check that the PDF (and/or `.docx`) was written successfully (typically under `output/`). For the Typst route, note the page count from `compile_cv.py`. If the count exceeds two pages, report that and what was shortened (if anything).
2. Report the generated file location to the user, summarize key adjustments made to match the target JD, and include the JD keyword lists (used vs skipped). Confirm every employer, product, credential, skill category, and education entry from the extract appears in the tuned CV.
3. A cover letter is a separate step via [cover-letter](../cover-letter/SKILL.md). Do not write one unless the user asks.

> Environment notes:
> - Dependencies: `pip install -r requirements.txt` (beautifulsoup4, pypdf, python-docx).
> - **Typst PDF route** (`compile_cv.py`) needs the `typst` CLI installed separately.
> - **Word route** (`build_docx_cv.py` → `docx_to_pdf.py`) needs no Typst; PDF conversion uses MS Word (`pywin32`, Windows) or LibreOffice (`soffice` on PATH).
