# cv_tailor

Tailor your base CV to a job description and compile a Harvard-style PDF. The agent rephrases and reorders only what is already in your files. It does not invent employers, dates, or metrics. Personal data stays under `assets/` and `output/` on your machine (both gitignored).

Agent workflows live in [skills/](skills/):

- [skills/cv-tailor/SKILL.md](skills/cv-tailor/SKILL.md): parse JDs, tune the CV, compile PDF or Word.
- [skills/github-contributions/SKILL.md](skills/github-contributions/SKILL.md): collect GitHub repo evidence into the base CV.
- [skills/cv-section-audit/SKILL.md](skills/cv-section-audit/SKILL.md): clean section overlap before tailoring.

## What this solves

- Job descriptions arrive as HTML, PDF, Word, Markdown, or plain text. One parser normalizes them for the agent.
- PDF extraction is lossy on multi-column layouts. Keep `assets/cv_base.typ` as the source of truth; if you also have a PDF, the tools prefer the sibling `.typ`.
- Harvard layout comes from a Typst template copied next to your tuned file at compile time.
- No Typst on your machine? Render from JSON to `.docx`, then convert to PDF with Word or LibreOffice.
- Open-source work is easy to understate until you run the GitHub collector (`gh auth login`, no tokens in the repo).
- Summary, competencies, experience, and skills often repeat the same claim. The section-audit skill separates product copy from the stack.

## Quick start

1. `pip install -r requirements.txt`
2. Install [Typst](https://typst.app/) and put `typst` on `PATH` if you want the Typst PDF route.
3. After clone, link agent skills: `python skills/cv-tailor/scripts/link_agent_skill.py`
4. Add `assets/cv_base.typ` and one or more files under `assets/jd/`.
5. Ask your agent to tune the CV for a job in `assets/jd/`.

Run scripts from the workspace root (paths below are under `skills/`):

```powershell
python skills/cv-tailor/scripts/parse_jd.py "assets/jd/<file>" --json
python skills/cv-tailor/scripts/extract_cv.py "assets/cv_base.typ" --json
python skills/cv-tailor/scripts/compile_cv.py "output/tuned.typ" "output/CV_Name_Company_Role.pdf"
python skills/cv-tailor/scripts/build_docx_cv.py "output/spec.json" "output/CV.docx"
python skills/cv-tailor/scripts/docx_to_pdf.py "output/CV.docx" "output/CV.pdf"
python skills/github-contributions/scripts/collect_contributions.py
```

## Install agent skills

Global install for Cursor and Claude Code:

```powershell
npx skills add minhhung2556/cv_tailor -a cursor -a claude-code -g -y
```

**Cursor:** import `https://github.com/minhhung2556/cv_tailor` from Plugins (manifest: [.cursor-plugin/marketplace.json](.cursor-plugin/marketplace.json)).

**Claude Code:** `/plugin marketplace add minhhung2556/cv_tailor` then `/plugin install cv-tailor@cv-tailor`.

Other install paths (local clone, one agent, single skill): [skills/cv-tailor/SKILL.md](skills/cv-tailor/SKILL.md).

## Tests

```powershell
python -m unittest discover -s tests
```

## License

[MIT License](LICENSE)
