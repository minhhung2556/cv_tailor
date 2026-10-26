"""Workspace paths and contribution record shaping for CV evidence."""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT = Path("assets/github_contributions.json")

REPO_RECORD_KEYS = (
    "name_with_owner",
    "url",
    "private",
    "description",
    "primary_language",
    "topics",
    "role",
    "stars",
    "commit_count",
    "first_commit",
    "last_commit",
)

ROLE_OWNER = "owner"
ROLE_COLLABORATOR = "collaborator"
ROLE_ORG_MEMBER = "org_member"
ROLE_CONTRIBUTOR = "contributor"

ROLE_RANK = {
    ROLE_OWNER: 4,
    ROLE_COLLABORATOR: 3,
    ROLE_ORG_MEMBER: 2,
    ROLE_CONTRIBUTOR: 1,
}

_CV_IO_PATH = (
    Path(__file__).resolve().parent.parent.parent / "cv-tailor" / "scripts" / "cv_io.py"
)


def _load_cv_io():
    if not _CV_IO_PATH.is_file():
        return None
    spec = importlib.util.spec_from_file_location("cv_io_for_contributions", _CV_IO_PATH)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_workspace_root(start: Path | None = None) -> Path:
    cv_io = _load_cv_io()
    if cv_io is not None:
        return cv_io.find_workspace_root(start)
    if start is None:
        start = Path.cwd()
    current = start.resolve()
    skill_scripts = Path(__file__).resolve().parent
    if skill_scripts.name == "scripts" and skill_scripts.parent.name == "github-contributions":
        return skill_scripts.parent.parent.parent
    return current


def resolve_output_path(path_str: str | None, workspace: Path) -> Path:
    if path_str:
        path = Path(path_str)
        if path.is_absolute():
            return path.resolve()
        return (workspace / path).resolve()
    return (workspace / DEFAULT_OUTPUT).resolve()


def strip_private(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if not k.startswith("_")}


def empty_repo_record(name_with_owner: str, url: str, *, private: bool, role: str) -> dict[str, Any]:
    return {
        "name_with_owner": name_with_owner,
        "url": url,
        "private": private,
        "description": None,
        "primary_language": None,
        "topics": [],
        "role": role,
        "stars": None,
        "commit_count": None,
        "first_commit": None,
        "last_commit": None,
    }


MERGE_FILL_KEYS = ("description", "primary_language", "topics", "stars")


def repo_stub(
    name_with_owner: str,
    url: str,
    *,
    private: bool,
    role: str,
    description: Any = None,
    primary_language: Any = None,
    topics: list[Any] | None = None,
    stars: Any = None,
    is_fork: bool = False,
) -> dict[str, Any]:
    return {
        **empty_repo_record(name_with_owner, url, private=private, role=role),
        "description": description,
        "primary_language": primary_language,
        "topics": list(topics or []),
        "stars": stars,
        "_fork": is_fork,
    }


def merge_repo_metadata(existing: dict[str, Any], stub: dict[str, Any]) -> None:
    existing["role"] = merge_roles(existing["role"], stub["role"])
    for key in MERGE_FILL_KEYS:
        if key == "stars":
            if existing.get(key) is None and stub.get(key) is not None:
                existing[key] = stub[key]
        elif not existing.get(key) and stub.get(key):
            existing[key] = stub[key]


def normalize_repo_record(record: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in REPO_RECORD_KEYS:
        if key not in record:
            raise ValueError(f"Missing key {key!r} in repo record")
        out[key] = record[key]
    if out["topics"] is None:
        out["topics"] = []
    if not isinstance(out["topics"], list):
        raise ValueError("topics must be a list")
    if out["role"] not in ROLE_RANK:
        raise ValueError(f"Invalid role: {out['role']}")
    return out


def merge_roles(existing: str, new: str) -> str:
    if ROLE_RANK.get(new, 0) > ROLE_RANK.get(existing, 0):
        return new
    return existing


def should_include_repo(record: dict[str, Any]) -> bool:
    """Include repos with a description or at least one authored commit; skip the rest."""
    description = (record.get("description") or "").strip()
    commit_count = record.get("commit_count")
    commits = commit_count if commit_count is not None else 0
    if description or commits > 0:
        return True
    return False


def _format_date(iso: str | None) -> str | None:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%B %Y")
    except ValueError:
        return None


def build_project_bullets(record: dict[str, Any]) -> list[str]:
    bullets: list[str] = []
    description = (record.get("description") or "").strip()
    if description:
        bullets.append(description)
    language = record.get("primary_language")
    topics = record.get("topics") or []
    stack_parts: list[str] = []
    if language:
        stack_parts.append(str(language))
    for topic in topics[:8]:
        if topic and topic not in stack_parts:
            stack_parts.append(str(topic))
    if stack_parts:
        bullets.append("Stack: " + ", ".join(stack_parts))
    commit_count = record.get("commit_count")
    if commit_count is not None and commit_count > 0:
        bullets.append(f"Authored {commit_count} commit(s) on the default branch.")
    return bullets


def _escape_typst_string(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def format_typst_cv_experience(record: dict[str, Any]) -> str:
    """Render one #cv_experience block using only JSON fields (for tests and agent reference)."""
    name = record["name_with_owner"]
    url = record.get("url") or ""
    first = _format_date(record.get("first_commit"))
    last = _format_date(record.get("last_commit"))
    dates = ""
    if first and last:
        dates = f"{first} – {last}" if first != last else first
    elif last:
        dates = last
    elif first:
        dates = first
    bullets = build_project_bullets(record)
    bullet_lines = ",\n    ".join(
        f'"{_escape_typst_string(b)}"' for b in bullets
    )
    company = name
    if url:
        company = f"{name} ({url})"
    lines = [
        "#cv_experience(",
        f'  company: "{_escape_typst_string(company)}",',
        '  location: "",',
        '  role: "Open source",',
        f'  dates: "{_escape_typst_string(dates)}",',
        f"  bullets: ({bullet_lines})",
        ")",
    ]
    return "\n".join(lines)


def build_payload(
    viewer: dict[str, Any],
    repos: list[dict[str, Any]],
) -> dict[str, Any]:
    normalized = [normalize_repo_record(r) for r in repos]
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "viewer": {
            "login": viewer.get("login"),
            "id": viewer.get("node_id") or str(viewer.get("id", "")),
        },
        "repos": normalized,
    }


def write_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def repo_name_from_typst_company(company_field: str) -> str:
    """Match existing CV entries by repository name (before optional URL in parentheses)."""
    text = company_field.strip()
    if " (" in text:
        return text.split(" (", 1)[0].strip()
    return text
