---
name: cv-tuning
description: Tune and tailor candidate CVs against Job Descriptions (JD) in assets/jd to generate Harvard-style PDFs in /output. Load this skill when asked to tune a CV, match a resume to a job description, update a CV for a target role, or process job descriptions from assets/jd.
---

# CV Tuning Skill

This skill automates the process of tailoring a candidate's base resume (`assets/cv_base.typ`, or `assets/cv_base.pdf` when present) to match specific Job Description (JD) requirements found in `assets/jd/`, generating a clean, Harvard-style PDF in `output/`.

## When to load this skill

Load this skill whenever the user asks to:
- "tune my CV for a job description"
- "match my resume to a JD"
- "create a customized CV from assets/cv_base.pdf"
- "generate a targeted CV for a job in assets/jd"

---

## Workflow & Step-by-Step Instructions

### Step 1: Detect and Parse Job Description(s)
Check `assets/jd/` for target JD files (supported extensions: `.html`, `.htm`, `.txt`, `.pdf`, `.md`).
The parser keeps job text inside HTML `<header>` and removes nav, footer, scripts, and styles. Unsupported extensions raise an error instead of being read as plain text.
Run the parser script to extract clean text:
```bash
python skills/cv-tuning/scripts/parse_jd.py "assets/jd/<jd_file>" --json
```

### Step 2: Read Base CV and personal evidence
Extract the full candidate history and details from `assets/cv_base.typ` (preferred) or `assets/cv_base.pdf`:
```bash
python skills/cv-tuning/scripts/extract_cv.py "assets/cv_base.typ"
```

After extraction, read each **personal product and profile URL** listed under Reference Links in the base CV (at minimum `https://hooemi.com` and `https://romanticdeveloper.com`). Treat verified facts from those pages as additional evidence alongside the base CV. Do not invent dates, metrics, or scope not stated in the base CV or those pages.

### Step 3: Analyze Requirements & Map Accomplishments
0. **Evidence inventory** (before tailoring):
   - List every employer, founder or independent product, credential, and named skill from the base CV plus verified personal-site facts.
   - The tuned CV must retain each item. Reorder and rephrase for the JD; do not drop an evidenced employer, product, credential, or skill category to save space.
   - If a product appears only as a URL in Reference Links but the candidate built it (e.g. Hooemi), include a short **Experience** or **Projects** entry with truthful bullets from public product pages.
   - If an item must be omitted (e.g. page limit), name it in the Step 6 report with reason.

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

### Writing (CV prose)

Governs Professional Summary, Core Competencies, and experience bullets only. Does not change chat style, scripts, or Harvard Typst layout.

**Truth and structure**

- Facts only from the base CV. Reframe order and emphasis. Do not invent scope, titles, or metrics.
- One claim per bullet. Lead with a verb and a concrete result (what shipped, what changed, a number only if the base CV has one).

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
Create a `.typ` file under `output/` (or another writable path). Use an absolute import from the repo root. `compile_cv.py` sets `--root` to the repo, so this path works from `output/`:

```typst
#import "/skills/cv-tuning/resources/harvard_cv.typ": cv, cv_section, cv_experience, cv_entry, cv_url

#show: cv.with(
  name: "LUONG DO MINH HUNG",
  title: "<TARGET_ROLE_TITLE>",
  contact: "minhhung2556@gmail.com · (+84) 775005110 · Ho Chi Minh City, Vietnam",
)

#cv_section("Professional Summary")
<Tuned Professional Summary text tailored to the JD requirements...>

#cv_section("Core Competencies")
<Tuned Core Competencies bullet list or inline categories...>

#cv_section("Experience")

#cv_experience(
  company: "EmbedIT Vietnam (EmbedIT s.r.o., Czech Republic)",
  location: "Ho Chi Minh City",
  role: "Mobile Technical Lead / Senior Software Engineer",
  dates: "April 2022 – Present",
  bullets: (
    [<Tuned bullet point emphasizing JD responsibilities...>],
    [<Tuned bullet point...>],
  )
)

// Add remaining experience entries, Credentials, Reference Links, Technical Skills, and Education...
```

### Step 5: Compile PDF to Output Directory
Relative paths passed to `compile_cv.py` (Typst source and output PDF) are resolved from the repository root, not the shell working directory.
Run `compile_cv.py` to compile the `.typ` file into PDF inside `output/`:
```bash
python skills/cv-tuning/scripts/compile_cv.py "output/tuned_cv.typ" "output/CV_<Candidate_Name>_<Company>_<Role>.pdf"
```

### Agent skill path
`.agent/skills/cv-tuning` is a junction to `skills/cv-tuning` (not a second copy). After clone, recreate it with:
```bash
python skills/cv-tuning/scripts/link_agent_skill.py
```

### Step 6: Verify and Report Output
1. Check that the PDF was written successfully to `output/` and note the page count printed by `compile_cv.py`.
2. Report the generated file location to the user, summarize key adjustments made to match the target JD, include the JD keyword lists (used vs skipped), and list any evidenced employers, products, credentials, or skills omitted from the tuned CV (with reason).
