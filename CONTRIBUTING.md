# Contributing

Thanks for helping improve cv_tailor.

## Getting started

1. Fork the repository and create a branch from `main`.
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Install [Typst](https://typst.app/) if you need to compile PDFs (`typst` on `PATH`).
4. After clone, recreate agent skill junctions:

   ```powershell
   python skills/cv-tailor/scripts/link_agent_skill.py
   ```

   Use `--force` if a real directory already exists at an agent skill path.

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
