#!/usr/bin/env python3
"""Mirror skills/cv-tuning -> .agent/skills/cv-tuning.

`skills/cv-tuning` is the source of truth; `.agent/skills/cv-tuning` is a generated
copy kept for the runtime that loads skills from `.agent/`. Run this after editing
the skill so the two copies never drift. `__pycache__` / compiled files are skipped.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "skills" / "cv-tuning"
DST = ROOT / ".agent" / "skills" / "cv-tuning"


def main():
    if not SRC.is_dir():
        raise SystemExit(f"Source not found: {SRC}")
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"Synced {SRC} -> {DST}")


if __name__ == "__main__":
    main()
