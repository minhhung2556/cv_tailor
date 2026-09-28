#!/usr/bin/env python3
"""
Ensure .agent/skills/cv-tuning is a directory junction (Windows) or symlink to skills/cv-tuning.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HARVARD_TEMPLATE = Path("skills/cv-tuning/resources/harvard_cv.typ")
AGENT_SKILL = Path(".agent/skills/cv-tuning")
SKILL_SOURCE = Path("skills/cv-tuning")


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / HARVARD_TEMPLATE).is_file():
            return candidate
    raise RuntimeError(
        f"Could not locate repo root (missing {HARVARD_TEMPLATE}) starting from {start}"
    )


def _is_reparse_point(path: Path) -> bool:
    if not path.exists():
        return False
    if path.is_symlink():
        return True
    if sys.platform == "win32":
        import stat

        try:
            return bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
        except (AttributeError, OSError):
            return path.resolve() != path.absolute()
    return False


def ensure_agent_skill_junction(repo_root: Path | None = None) -> Path:
    if repo_root is None:
        repo_root = find_repo_root(Path(__file__).resolve().parent)

    agent = repo_root / AGENT_SKILL
    skills = (repo_root / SKILL_SOURCE).resolve()
    if not skills.is_dir():
        raise RuntimeError(f"Missing skill source directory: {skills}")

    if agent.exists():
        try:
            if agent.resolve() == skills:
                return agent
        except OSError:
            pass
        if _is_reparse_point(agent):
            if agent.is_dir():
                agent.rmdir()
            else:
                agent.unlink()
        else:
            import shutil

            shutil.rmtree(agent)

    agent.parent.mkdir(parents=True, exist_ok=True)

    if sys.platform == "win32":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(agent), str(skills)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(f"Failed to create junction {agent} -> {skills}: {detail}")
    else:
        agent.symlink_to(skills, target_is_directory=True)

    return agent


def main() -> None:
    root = find_repo_root(Path(__file__).resolve().parent)
    path = ensure_agent_skill_junction(root)
    print(f"Linked {path} -> {(root / SKILL_SOURCE).resolve()}")


if __name__ == "__main__":
    main()
