# Contributing

Thanks for helping improve CV Tailor.

## Getting started

1. Fork the repository and create a branch from `main`.
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Install [Typst](https://typst.app/) if you need to compile PDFs (`typst` on `PATH`).
4. Install the published skills globally, or link a local clone:

   ```powershell
   gh skill install minhhung2556/cv_tailor
   npx skills add minhhung2556/cv_tailor -a cursor -a claude-code -g -y
   python skills/cv-tailor/scripts/link_agent_skill.py
   ```

   Use `--force` on `link_agent_skill.py` if a real directory already exists at an agent skill path.

   After changes to `skills/` land on `main`, cut a release with `gh skill publish --tag <version>` so `gh skill` search and install pick up the new tag.

## Making changes

- Edit skills under [`skills/`](skills/). Do not commit `.agents/skills/` or `.claude/skills/`; those are local junctions.
- Do not commit personal data: `assets/`, `output/`, `.env`, or GitHub credentials.
- Keep changes focused and match existing style in the files you touch.

## Tests

Before opening a pull request:

```powershell
python -m unittest discover -s tests
```

## Pull requests

1. Open a PR against `main` with a clear description of what changed and why.
2. Confirm tests pass locally (CI runs the same unittest suite on pull requests).

`main` and `develop` are protected: changes must go through a pull request, CI (`unittest` on Python 3.12 and 3.14) must pass, and conversation threads must be resolved. Force pushes and branch deletion are disabled.
