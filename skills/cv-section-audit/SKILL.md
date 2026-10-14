---
name: cv-section-audit
description: >-
  Audit a Harvard-style CV as a hiring manager and rewrite it so product and
  outcome stay in Experience, libraries stay in Technical Skills, and the
  summary, competencies, experience, and skills do not repeat the same fact.
  Use when asked to audit a CV, separate product copy from the tech stack,
  remove duplicated claims across summary, competencies, and skills, or clean
  assets/cv_base.typ before tailoring.
---

# CV section audit

Hiring-manager pass on a base CV (default `assets/cv_base.typ`). Each section has one job. A product name, feature, or library appears in only one of Professional Summary, Core Competencies, Experience (including Side Projects), and Technical Skills.

Facts only. Do not invent metrics, titles, or scope. Do not drop an evidenced employer, product, credential, skill category, or education line. Rephrase and move, do not delete evidence.

## When a first pass fails

- **Broken punctuation.** Contact, dates, competency separators, or currency render as mojibake (often `ï¿½` for `·`, `–`, or `€`). Restore real characters. Save the file as UTF-8. Date ranges and numeric spans may use an en dash (`April 2022 – Present`, `20–50%`). Do not join prose clauses with an em dash, en dash, spaced hyphen, or `--`.
- **Product and stack share a sentence.** A bullet names what shipped and then lists libraries (`FastAPI`, `PyTorch`, `Playwright`, `OSV-Scanner`). A reader cannot see the product.
- **The same claim is repeated.** Summary, competencies, experience, and Technical Skills all carry the same product, feature, or tool.

Leave title, short contracts, missing side-project dates, and education timing unless the user asks. Those are signals, not this rewrite.

## Section jobs

**Professional Summary.** Years, leadership span, and quantified results already in the file. One short clause for a current independent product is enough. No employer story, no feature list, no tool names. Named products belong in Experience.

**Core Competencies.** Practices only: governance, hiring, release standards, cross-market delivery, vendor and cost decisions, mentoring. No product names, no feature lists, no libraries. Labels that restate the summary or name a tool move out.

**Experience and Side Projects.** One claim per bullet. Lead with the product or the decision. Keep markets, features, team scale, and results already in the file. Do not name libraries, CLIs, model runtimes, or package names in the bullet.

**Technical Skills.** The only place a library or platform name appears. Group by use: mobile, APIs and web, delivery, AI, security. Fold design tools (`UML`, `Figma`, `OpenAPI`) into the API or delivery line. Drop a category that only repeats product features already stated in Experience (payments flows, super-app feature lists). Every tool removed from a bullet must land here. Do not drop a skill category that still has evidenced tools; rename or merge it.

Credentials, reference links, and education stay in their sections. Do not use them to restate the skills inventory.

## Move, do not drop

| Leave in the bullet | Move to Technical Skills |
| --- | --- |
| What shipped, for whom, what changed | Library, CLI, scanner, model runtime, package name |
| Markets, features, team size, money or size result already in the file | Framework used to build it (`Flutter`, `React Native`, `FastAPI`, `PyTorch`) |
| Open-source outcome (version, pull request, download count) | Manifest, hook, and toolchain nouns |

Examples: a CI line keeps "publishes dependency vulnerability reports"; `Azure Pipelines` and `OSV-Scanner` go to skills. A super-app line keeps payments, flash sales, and travel; `Flutter` goes to skills. A recognition line keeps document-image extraction; `PyTorch`, `OpenCV`, and `VietOCR` go to skills. A package publisher line keeps count and download or star figures; package names go to skills.

## Finish

1. Edit the CV source only. Leave the Harvard template import and section order unchanged.
2. Scan Summary, Competencies, Experience, Side Projects, and Technical Skills. Confirm no product name, feature, or library appears in more than one of them.
3. Confirm every employer, product, credential, skill that left a bullet, and education line is still present.

## Install

Install with the other CV skills from the repository root (not from `skills/cv-tailor` alone):

```bash
npx skills add minhhung2556/cv_tailor -a cursor -a claude-code -g -y
npx skills add . -a cursor -a claude-code -g -y
```

After clone, recreate in-repo junctions for every skill:

```bash
python skills/cv-tailor/scripts/link_agent_skill.py
```
