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
Check `assets/jd/` for target JD files (supported extensions: `.html`, `.htm`, `.txt`, `.pdf`, `.md`).
Run the parser script to extract clean text:
```bash
python3 skills/cv-tuning/scripts/parse_jd.py "assets/jd/<jd_file>" --json
```

### Step 2: Read Base CV
Extract the full candidate history and details from `assets/cv_base.pdf`:
```bash
python3 skills/cv-tuning/scripts/extract_cv.py "assets/cv_base.pdf"
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
Create a `.typ` file in `/tmp/` or `output/` using the `#import` of `skills/cv-tuning/resources/harvard_cv.typ`:

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
Run `compile_cv.py` to compile the `.typ` file into PDF inside `output/`:
```bash
python3 skills/cv-tuning/scripts/compile_cv.py "/tmp/tuned_cv.typ" "output/CV_<Candidate_Name>_<Company>_<Role>.pdf"
```

### Step 6: Verify and Report Output
1. Check that the PDF was written successfully to `output/`.
2. Report the generated file location to the user and summarize key adjustments made to match the target JD.
