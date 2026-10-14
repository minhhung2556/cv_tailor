# cv_tuning

Tailor a base CV against a job description and compile a Harvard-style PDF. Put the base CV at `assets/cv_base.typ`. If that path is a PDF and a sibling `.typ` exists, extraction uses the Typst file. Put job descriptions in `assets/jd/`. The agent writes the PDF under `output/`. Agent steps live in [skills/cv-tuning/SKILL.md](skills/cv-tuning/SKILL.md).

## Layout

- `assets/cv_base.typ`: base CV. Gitignored.
- `assets/jd/`: job descriptions (`.html`, `.htm`, `.txt`, `.pdf`, `.md`). Gitignored.
- `output/`: compiled PDFs. Gitignored.
- `skills/cv-tuning/`: skill instructions, scripts, and the Harvard Typst template.
- `.agents/skills/cv-tuning`: junction to `skills/cv-tuning`, created after clone so Cursor loads the in-repo skill. Gitignored.
- `.claude/skills/cv-tuning`: junction to `skills/cv-tuning`, for Claude Code. Gitignored.



## Install

Recommended for Cursor and Claude Code, installed globally from GitHub:

```powershell
npx skills add minhhung2556/cv_tuning -a cursor -a claude-code -g -y
```

For one agent only:

```powershell
npx skills add minhhung2556/cv_tuning -a cursor -g -y
npx skills add minhhung2556/cv_tuning -a claude-code -g -y
```

From a local clone, pass that repository path. Use an absolute path, `.`, or `..`. A bare folder name is treated as a GitHub repository, not a local directory.

```powershell
npx skills add E:\projects\cv_tuning -a cursor -a claude-code -g -y
npx skills add . -a claude-code -g -y
npx skills add .\skills\cv-tuning -a claude-code -g -y
```

The same CLI accepts an HTTPS URL or an SSH URL:

```powershell
npx skills add https://github.com/minhhung2556/cv_tuning.git -a claude-code -g -y
npx skills add git@github.com:minhhung2556/cv_tuning.git -a claude-code -g -y
```

Omit `-g` to install into the current project (`.agents/skills/` for Cursor, `.claude/skills/` for Claude Code). Private repositories use git credentials already configured for that URL. If Windows refuses the symlink, add `--copy`.

**Cursor:** import `https://github.com/minhhung2556/cv_tuning` from Cursor Customize, Plugins. The manifest is [.cursor-plugin/marketplace.json](.cursor-plugin/marketplace.json).

**Claude Code:** in a Claude Code session:

```text
/plugin marketplace add minhhung2556/cv_tuning
/plugin install cv-tuning@cv-tuning
```

From a local clone: `/plugin marketplace add E:\projects\cv_tuning` (or your path). Catalog file: [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json).

## Setup in this repo

```powershell
pip install -r requirements.txt
```

`typst` must be on `PATH` (`typst compile`).

After clone, recreate the Cursor and Claude Code skill junctions:

```powershell
python skills/cv-tuning/scripts/link_agent_skill.py
```

`--force` replaces a real directory at `.agents/skills/cv-tuning` or `.claude/skills/cv-tuning`. A junction is recreated without that flag.

## Use

1. Add `assets/cv_base.typ` and one or more files under `assets/jd/`.
2. Ask the agent to tune the CV for a job in `assets/jd/`.

Scripts run from the workspace root, under `skills/cv-tuning/scripts/`:

- `parse_jd.py`: plain text from a job description. Optional `--json`.
- `extract_cv.py`: text from the base CV. Defaults to `assets/cv_base.typ`. Optional `--json`.
- `compile_cv.py`: compiles a `.typ` file to PDF and prints the page count. It copies `harvard_cv.typ` next to the source. If you omit the PDF path, the PDF is written beside the `.typ` file with the same name.



## Tests

```powershell
python -m unittest discover -s tests
```

