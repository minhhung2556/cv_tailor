---
name: github-contributions
description: Collect GitHub repository contributions (public and private) via the authenticated gh CLI, write assets/github_contributions.json, and merge Projects entries into assets/cv_base.typ. Use when syncing GitHub activity into a CV, refreshing open-source evidence, or researching the user's repositories for resume facts.
license: MIT
---

# GitHub Contributions into the CV

Collect repository metadata and authored-commit activity through the logged-in [GitHub CLI](https://cli.github.com/) (`gh`). No tokens are stored in the repo. Output is [`assets/github_contributions.json`](../../assets/github_contributions.json) (gitignored). Merge truthful **Projects** lines into [`assets/cv_base.typ`](../../assets/cv_base.typ).

**Paths:** Run scripts from the **workspace** root (project with `assets/`). Scripts live under this skill's `scripts/` directory.

## When to load this skill

- Sync GitHub repos into the CV or base Typst file
- Refresh open-source / side-project evidence before tailoring
- Research all repositories the user can see (owner, collaborator, org member, contributor)

---

## Step 1: Authenticate

Verify `gh` sees the viewer:

```bash
gh api user
```

If this fails, stop and tell the user to run `gh auth login`. Do not store or commit tokens.

## Step 2: Collect evidence JSON

```bash
python <skill-scripts>/collect_contributions.py
```

Optional output path:

```bash
python <skill-scripts>/collect_contributions.py -o assets/github_contributions.json
```

Reusable pieces (same auth requirements):

```bash
python <skill-scripts>/list_repos.py --json
python <skill-scripts>/repo_activity.py path/to/list_output.json --json
```

Each repo record includes: `name_with_owner`, `url`, `private`, `description`, `primary_language`, `topics`, `role` (`owner`, `collaborator`, `org_member`, `contributor`), `stars`, `commit_count`, `first_commit`, `last_commit`. Missing values stay `null`.

**Scope:** Repositories from affiliations (including private) plus `repositoriesContributedTo` with commit contributions. Metadata only; no clone and no file contents.

**Filtering:** By default, repos with a non-empty description or `commit_count > 0` are kept. Repos with no description and no authored commits are skipped. Use `--include-all` on `collect_contributions.py` to retain everything.

## Step 3: Merge into `assets/cv_base.typ`

1. If `assets/cv_base.typ` is missing, stop and ask the user to add a base CV.
2. Read `assets/github_contributions.json`.
3. Add or update `#cv_section("Projects")` using `#cv_experience` from the Harvard template ([`skills/cv-tailor/resources/harvard_cv.typ`](../cv-tailor/resources/harvard_cv.typ)).
4. One `#cv_experience` per included repo. Match existing entries by repository name (`name_with_owner`, ignoring an optional URL in the company field).
5. **Bullets:** Use only `description`, `primary_language`, `topics`, and `commit_count` when present. **Dates:** `first_commit` / `last_commit` formatted as month year, or omit if null.
6. Do not invent impact, employers, or metrics. Follow the same plain-prose rules as [cv-tailor](../cv-tailor/SKILL.md) (no dash pauses between clauses).

When generating Typst, use `scripts/contributions_io.py` (`build_project_bullets`, `format_typst_cv_experience`) so bullets stay limited to JSON fields.

## Step 4: Report

Summarize how many repos were collected, how many were written to the JSON file, and which **Projects** entries were added or updated in `cv_base.typ`. Remind the user that private repo names appear only in local gitignored files.

## Integration with CV Tailor

After merging Projects, run [cv-tailor](../cv-tailor/SKILL.md) to tune against a JD. Tailoring must treat `assets/github_contributions.json` as allowed evidence alongside the base CV extract.

## Install

```bash
npx skills add minhhung2556/cv_tailor -a cursor -a claude-code -g -y
gh skill install minhhung2556/cv_tailor github-contributions
```

More install paths and junction setup: [cv-tailor](../cv-tailor/SKILL.md) (Install and agent discovery).
