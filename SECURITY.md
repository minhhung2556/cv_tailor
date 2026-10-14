# Security

## Reporting a vulnerability

Please report security issues through [GitHub private security advisories](https://github.com/minhhung2556/cv_tailor/security/advisories/new) for this repository. Do not open public issues for exploits or leaked secrets.

Include steps to reproduce, affected components, and impact if known.

## Scope

This policy covers the Python scripts and agent skills in this repository (for example under `skills/` and `tests/`).

## Local data

The tooling is designed to keep personal data on your machine:

- Base CV, job descriptions, compiled PDFs, and `github_contributions.json` belong under `assets/` and `output/` and are gitignored.
- GitHub access uses the [GitHub CLI](https://cli.github.com/) (`gh auth login`); do not store tokens in the repo.

If you accidentally commit sensitive data, rotate any exposed credentials and contact the maintainers through a private advisory.
