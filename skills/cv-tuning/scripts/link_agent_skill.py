#!/usr/bin/env python3
"""
Ensure .agents/skills/cv-tuning is a directory junction (Windows) or symlink to skills/cv-tuning.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cv_io

AGENT_SKILL = Path(".agents/skills/cv-tuning")
SKILL_SOURCE = Path("skills/cv-tuning")


def _is_reparse_point(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
    except OSError:
        pass
    if sys.platform == "win32":
        import stat

        try:
            return bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
        except (AttributeError, OSError):
            return False
    return False


def _remove_reparse_point(agent: Path) -> None:
    if agent.is_dir():
        agent.rmdir()
    else:
        agent.unlink(missing_ok=True)


def ensure_agent_skill_junction(
    repo_root: Path | None = None,
    *,
    force: bool = False,
) -> Path:
    if repo_root is None:
        repo_root = cv_io.find_workspace_root(Path(__file__).resolve().parent)

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
            _remove_reparse_point(agent)
        elif agent.is_file():
            agent.unlink()
        elif agent.is_dir():
            if not force:
                raise RuntimeError(
                    f"{agent} is a real directory, not a junction. "
                    "Remove it manually or pass --force to delete and recreate."
                )
            import shutil

            shutil.rmtree(agent)
    elif _is_reparse_point(agent):
        _remove_reparse_point(agent)

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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete a real directory at the agent skill path before linking",
    )
    args = parser.parse_args()
    root = cv_io.find_workspace_root(Path(__file__).resolve().parent)
    path = ensure_agent_skill_junction(root, force=args.force)
    print(f"Linked {path} -> {(root / SKILL_SOURCE).resolve()}")


if __name__ == "__main__":
    main()
