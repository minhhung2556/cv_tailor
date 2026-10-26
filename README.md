# CV Tailor

[![skills.sh](https://skills.sh/b/minhhung2556/cv_tailor)](https://skills.sh/minhhung2556/cv_tailor)

Tailor your base CV to a job description, compile a Harvard-style PDF or Word file, and optionally draft a one-page English cover letter. The agent rephrases and reorders only what is already in your files: the base CV, `assets/github_contributions.json` when present, and verified pages from Reference Links in the extract. It does not invent employers, dates, or metrics. Personal data stays under `assets/` and `output/` on your machine (both gitignored). Source and clone path: GitHub repository `minhhung2556/cv_tailor`.

Agent workflows live in [skills/](skills/):

- [skills/cv-tailor/SKILL.md](skills/cv-tailor/SKILL.md): parse JDs, tune the CV against the posting, compile PDF or `.docx` (one claim per bullet, two-page target, JD keywords only with evidence).
- [skills/github-contributions/SKILL.md](skills/github-contributions/SKILL.md): collect GitHub repo metadata into `assets/github_contributions.json`, then merge a **Projects** section into `assets/cv_base.typ`.
- [skills/cv-section-audit/SKILL.md](skills/cv-section-audit/SKILL.md): keep product and outcome in Experience and libraries in Technical Skills before tailoring.
- [skills/cover-letter/SKILL.md](skills/cover-letter/SKILL.md): write English Markdown at `output/Cover_Letter_<Candidate>_<Company>_<Role>.md` (about 250–350 words); does not edit the CV or compile a PDF.

## What this solves

- Job descriptions arrive as HTML, PDF, Word (`.docx`), Markdown, or plain text. Legacy `.doc` is not supported; convert it first. One parser normalizes supported formats for the agent.
- PDF extraction is lossy on multi-column layouts. Keep `assets/cv_base.typ` as the source of truth; if you also have a PDF, the tools prefer the sibling `.typ`.
- Harvard layout comes from a Typst template copied next to your tuned file at compile time.
- No Typst on your machine? Render from JSON to `.docx`, then convert to PDF with Word or LibreOffice.
- Open-source work is easy to understate until you run the GitHub collector (`gh auth login`, no tokens in the repo). It writes `assets/github_contributions.json` and can fold repos into **Projects** on the base CV.
- Summary, competencies, experience, and skills often repeat the same claim. The section-audit skill separates product copy from the stack.
- A generic CV does not match the employer's wording, and screening looks for those keywords. Tailoring reorders and rephrases with JD terms only where the base CV already supports them (one claim per bullet, two-page target).
- Need a letter with the application? The cover-letter skill is separate: Markdown under `output/`, same evidence rules, CV unchanged unless you ask.

## Quick start

1. `pip install -r requirements.txt`
2. Install [Typst](https://typst.app/) and put `typst` on `PATH` if you want the Typst PDF route.
3. After clone, link agent skills: `python skills/cv-tailor/scripts/link_agent_skill.py`
4. Add `assets/cv_base.typ` and one or more files under `assets/jd/`.
5. Ask your agent to tune the CV for a job in `assets/jd/`.
6. When you want a letter, ask for a cover letter for that job. Output is `output/Cover_Letter_*.md`; the tuned CV is not edited.

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
gh skill install minhhung2556/cv_tailor
```

That installs all four skills (`cv-tailor`, `github-contributions`, `cv-section-audit`, `cover-letter`) for Cursor and Claude Code. To install one skill only:

```powershell
npx skills add minhhung2556/cv_tailor --skill cv-tailor -a cursor -a claude-code -g -y
npx skills add minhhung2556/cv_tailor --skill github-contributions -a cursor -a claude-code -g -y
npx skills add minhhung2556/cv_tailor --skill cv-section-audit -a cursor -a claude-code -g -y
npx skills add minhhung2556/cv_tailor --skill cover-letter -a cursor -a claude-code -g -y
gh skill install minhhung2556/cv_tailor cv-tailor
gh skill install minhhung2556/cv_tailor github-contributions
gh skill install minhhung2556/cv_tailor cv-section-audit
gh skill install minhhung2556/cv_tailor cover-letter
```

Browse installs and skill pages on [skills.sh/minhhung2556/cv_tailor](https://skills.sh/minhhung2556/cv_tailor).

**Cursor:** import `https://github.com/minhhung2556/cv_tailor` from Plugins (manifest: [.cursor-plugin/marketplace.json](.cursor-plugin/marketplace.json)).

**Claude Code:** `/plugin marketplace add minhhung2556/cv_tailor` then `/plugin install cv-tailor@cv-tailor`.

Other install paths (local clone, one agent, single skill): [skills/cv-tailor/SKILL.md](skills/cv-tailor/SKILL.md).

## Tests

```powershell
python -m unittest discover -s tests
```

## References

Writing and tailoring rules in the skills come from these guides (applied with facts-only evidence; see the skill docs for full constraints).

- [CIH: 11 tips for writing the perfect CV](https://www.cih.org/blogs/11-tips-for-writing-the-perfect-cv/) — **Tailor and adapt your CV** is the reason to match each posting: review the skills and experience the employer asks for, emphasise what you already have, and reuse the employer's wording. Organisations scan for those keywords; a generic CV does not stand out. The skills use JD phrases only where the base CV supports them. The same page informs the two-page cap, language check, opening profile, and honest gaps (no invented roles or metrics).
- [Harvard FAS: Create a Strong Resume](https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/) — Tailor the resume to the role so it shows skills that employer would value; add job-description keywords to your draft rather than a generic AI profile. Applied as skim-first bullets, active verbs, no `I`/`we`, reverse chronological order, no photo, and a cover letter that opens from the reader's need and cites skills from the posting (also cited in [skills/cv-tailor/SKILL.md](skills/cv-tailor/SKILL.md)).

## License

[MIT License](LICENSE)
