# cv_tuning

Tailors a candidate's base résumé to a specific Job Description (JD) and produces a
clean, **Harvard-style** CV as **PDF and/or Word (.docx)**. The logic lives in a
Claude Code skill under [`skills/cv-tuning`](skills/cv-tuning/SKILL.md).

## Layout

| Path | Purpose |
|------|---------|
| `assets/cv_base.pdf` | Base résumé (source of truth for the candidate's history) |
| `assets/jd/` | Input job descriptions (`.txt`, `.md`, `.html`, `.pdf`, `.docx`) |
| `skills/cv-tuning/` | The skill: `SKILL.md`, scripts, and the Typst template |
| `.agent/skills/cv-tuning/` | Generated mirror of the above (see *Sync* below) |
| `output/` | Generated CVs (`.typ` / `.json` sources + built `.pdf` / `.docx`) |

## Setup

```bash
pip install -r requirements.txt
```

Use `python` (on this machine `python3` is not on PATH).

### Producing a PDF — two paths
- **Typst route** (`compile_cv.py`): needs the [`typst`](https://typst.app) CLI installed
  separately (not a pip package).
- **Word route** (`build_docx_cv.py` + `docx_to_pdf.py`): needs no Typst. Renders a
  `.docx`, then converts to PDF via Microsoft Word (`pywin32`, Windows) or LibreOffice
  (`soffice` on PATH).

## Usage

```bash
# 1. Parse the JD
python skills/cv-tuning/scripts/parse_jd.py "assets/jd/<jd_file>" --json

# 2. Read the base CV
python skills/cv-tuning/scripts/extract_cv.py "assets/cv_base.pdf"

# 3. Tune the content (see SKILL.md), then EITHER:

# 3a. Typst -> PDF
python skills/cv-tuning/scripts/compile_cv.py "output/<name>.typ" "output/<name>.pdf"

# 3b. Word: JSON spec -> .docx  (schema: resources/cv_spec.example.json)
python skills/cv-tuning/scripts/build_docx_cv.py "output/<name>.json" "output/<name>.docx"
#     ...and optionally .docx -> PDF without Typst:
python skills/cv-tuning/scripts/docx_to_pdf.py "output/<name>.docx" "output/<name>.pdf"
```

See [`skills/cv-tuning/SKILL.md`](skills/cv-tuning/SKILL.md) for the full step-by-step workflow.

## Sync

`skills/cv-tuning` is the source of truth. After editing it, mirror the copy the
`.agent/` runtime uses:

```bash
python sync_skills.py
```
