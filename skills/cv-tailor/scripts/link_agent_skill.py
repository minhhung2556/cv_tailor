#!/usr/bin/env python3
"""
Ensure agent skill paths are directory junctions (Windows) or symlinks to skills/*.

Creates .agents/skills/<name> (Cursor) and .claude/skills/<name> (Claude Code)
for each skill directory under skills/ that contains SKILL.md.
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

SKILLS_DIR = Path("skills")
CURSOR_SKILLS_ROOT = Path(".agents/skills")
CLAUDE_SKILLS_ROOT = Path(".claude/skills")


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


def _ensure_skill_junction_at(
    repo_root: Path,
    agent_rel: Path,
    skills: Path,
    *,
    force: bool = False,
) -> Path:
    agent = repo_root / agent_rel

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


def discover_skill_names(repo_root: Path) -> list[str]:
    skills_root = repo_root / SKILLS_DIR
    if not skills_root.is_dir():
        raise RuntimeError(f"Missing skills directory: {skills_root}")

    names: list[str] = []
    for child in sorted(skills_root.iterdir()):
        if not child.is_dir():
            continue
        if (child / "SKILL.md").is_file():
            names.append(child.name)
    if not names:
        raise RuntimeError(f"No skills with SKILL.md found under {skills_root}")
    return names


def ensure_agent_skill_junction(
    repo_root: Path | None = None,
    *,
    force: bool = False,
) -> list[Path]:
    if repo_root is None:
        repo_root = cv_io.find_workspace_root(Path(__file__).resolve().parent)

    linked: list[Path] = []
    for name in discover_skill_names(repo_root):
        source = (repo_root / SKILLS_DIR / name).resolve()
        if not source.is_dir():
            raise RuntimeError(f"Missing skill source directory: {source}")
        for agent_root in (CURSOR_SKILLS_ROOT, CLAUDE_SKILLS_ROOT):
            agent_rel = agent_root / name
            linked.append(_ensure_skill_junction_at(repo_root, agent_rel, source, force=force))
    return linked


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete a real directory at an agent skill path before linking",
    )
    args = parser.parse_args()
    root = cv_io.find_workspace_root(Path(__file__).resolve().parent)
    for path in ensure_agent_skill_junction(root, force=args.force):
        print(f"Linked {path} -> {path.resolve()}")


if __name__ == "__main__":
    main()
