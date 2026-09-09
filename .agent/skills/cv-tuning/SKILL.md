---
name: cv-tuning
description: Tune and tailor candidate CVs against Job Descriptions (JD) in assets/jd to generate Harvard-style PDFs in /output. Load this skill when asked to tune a CV, match a resume to a job description, update a CV for a target role, or process job descriptions from assets/jd.
---

# CV Tuning Skill

This skill automates the process of tailoring a candidate's base resume (`assets/cv_base.pdf`) to match specific Job Description (JD) requirements found in `assets/jd/`, generating a clean, Harvard-style PDF in `output/`.

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
Legacy `.doc` (old binary Word) is NOT supported — convert it to `.docx` (or export as PDF/text) first.
Run the parser script to extract clean text:
```bash
python skills/cv-tuning/scripts/parse_jd.py "assets/jd/<jd_file>" --json
```

### Step 2: Read Base CV
Extract the full candidate history and details from `assets/cv_base.pdf`:
```bash
python skills/cv-tuning/scripts/extract_cv.py "assets/cv_base.pdf"
```

### Step 3: Analyze Requirements & Map Accomplishments
1. **Identify Target Parameters**:
   - Role Title & Level (e.g. Senior Flutter Engineer, Mobile Architect)
   - Hiring Company & Location
   - Top 5-7 Required Qualifications & Key Responsibilities
   - Target Domain/Tech Stack Keywords (e.g., Flutter rendering pipeline, custom widgets, CI/CD, state management)

2. **Tailor CV Content Truthfully**:
   - **Professional Summary**: Rewrite in English to emphasize years of experience and achievements directly relevant to the target role.
   - **Core Competencies**: Highlight key domains and principles matching the JD.
   - **Experience**: Reorder and reframe bullet points under each employer to prioritize relevant projects, metrics, and accomplishments matching the target JD. *Do not fabricate unverified experience.*
   - **Technical Skills**: Rearrange skill categories so the target technology stack is featured first.

### Step 4: Write Harvard-Style Typst Document
Create a `.typ` file in `output/` using the `#import` of `skills/cv-tuning/resources/harvard_cv.typ`:

```typst
#import "skills/cv-tuning/resources/harvard_cv.typ": cv, cv_section, cv_experience, cv_entry

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
  company: "EmbedIT Vietnam",
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
Run `compile_cv.py` to compile the `.typ` file into PDF inside `output/`. **Requires the
`typst` CLI** — if it is not installed, use the Word route in Step 5-ALT instead.
```bash
python skills/cv-tuning/scripts/compile_cv.py "output/tuned_cv.typ" "output/CV_<Candidate_Name>_<Company>_<Role>.pdf"
```

### Step 5-ALT: Export as Word (.docx) instead of / in addition to PDF
When the user wants an editable Word document (or has no Typst installed), skip the Typst
route and render the tuned CV from a JSON spec. The JSON schema mirrors the Typst helpers
one-to-one (see `skills/cv-tuning/resources/cv_spec.example.json`):

- `type: "text"` → a paragraph (like `cv_section` + prose)
- `type: "bullets"` → a bulleted list (Core Competencies, Technical Skills)
- `type: "experience"` → `cv_experience` entries (company/location/role/dates/bullets)
- `type: "entries"` → `cv_entry` items (title/subtitle/dates/details) for Education, Credentials

Write the tuned spec (e.g. to `output/<name>.json`), then render:
```bash
python skills/cv-tuning/scripts/build_docx_cv.py "output/<name>.json" "output/CV_<Candidate_Name>_<Company>_<Role>.docx"
```
The `.docx` reproduces the Harvard layout (A4, Times New Roman, centered header, ruled
section headings, right-aligned dates) purely with `python-docx` — no Typst required.

To also produce a PDF from that `.docx` without Typst (via MS Word on Windows, or
LibreOffice if `soffice` is on PATH):
```bash
python skills/cv-tuning/scripts/docx_to_pdf.py "output/CV_<Candidate_Name>_<Company>_<Role>.docx" "output/CV_<Candidate_Name>_<Company>_<Role>.pdf"
```

### Step 6: Verify and Report Output
1. Check that the PDF (and/or `.docx`) was written successfully to `output/`.
2. Report the generated file location to the user and summarize key adjustments made to match the target JD.

> Environment notes:
> - Commands use `python` (on some machines `python3` is not on PATH, e.g. Windows).
> - Dependencies: `pip install -r requirements.txt` (beautifulsoup4, pypdf, python-docx).
> - **Typst PDF route** (`compile_cv.py`) needs the `typst` CLI installed separately.
> - **Word route** (`build_docx_cv.py` → `docx_to_pdf.py`) needs no Typst; PDF conversion
>   uses MS Word (`pywin32`, Windows) or LibreOffice (`soffice` on PATH).
> - After editing this skill, run `python sync_skills.py` to mirror it to `.agent/skills/`.
