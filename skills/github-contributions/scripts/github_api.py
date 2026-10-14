"""GitHub access via the authenticated ``gh`` CLI (REST pagination and GraphQL)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from typing import Any

GH_INSTALL_MSG = (
    "GitHub CLI (gh) is required. Install from https://cli.github.com/ and run: gh auth login"
)
GH_AUTH_MSG = "gh is not authenticated. Run: gh auth login"


class GhError(RuntimeError):
    pass


def configure_utf8_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def _require_gh() -> str:
    gh = shutil.which("gh")
    if not gh:
        raise GhError(GH_INSTALL_MSG)
    return gh


def _run_gh(args: list[str], *, input_text: str | None = None) -> str:
    gh = _require_gh()
    try:
        proc = subprocess.run(
            [gh, *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            input=input_text,
            check=False,
        )
    except OSError as e:
        raise GhError(GH_INSTALL_MSG) from e
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        if "not logged in" in err.lower() or "401" in err:
            raise GhError(GH_AUTH_MSG)
        raise GhError(err or f"gh exited with code {proc.returncode}")
    return proc.stdout


def ensure_authenticated() -> dict[str, Any]:
    """Return the authenticated viewer from ``GET /user``."""
    raw = _run_gh(["api", "user"])
    try:
        user = json.loads(raw)
    except json.JSONDecodeError as e:
        raise GhError(f"Invalid JSON from gh api user: {e}") from e
    if not user.get("login"):
        raise GhError(GH_AUTH_MSG)
    return user


def gh_api_paginated(path: str, *, params: dict[str, str] | None = None) -> list[Any]:
    """Paginate a GitHub REST endpoint (gh api --paginate).

    Query parameters go on the path. ``gh api -f`` sends a POST body, which
    turns ``user/repos`` into a create-repository call.
    """
    if params:
        from urllib.parse import urlencode

        separator = "&" if "?" in path else "?"
        path = f"{path}{separator}{urlencode(params)}"
    args = ["api", "--paginate", "--method", "GET", path]
    raw = _run_gh(args)
    items: list[Any] = []
    for chunk in raw.strip().split("\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        page = json.loads(chunk)
        if isinstance(page, list):
            items.extend(page)
        else:
            items.append(page)
    return items


def gh_graphql(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"query": query}
    if variables:
        payload["variables"] = variables
    raw = _run_gh(
        ["api", "graphql", "--input", "-"],
        input_text=json.dumps(payload),
    )
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise GhError(f"Invalid GraphQL response: {e}") from e
    if data.get("errors"):
        messages = "; ".join(
            str(err.get("message", err)) for err in data["errors"]
        )
        raise GhError(messages)
    return data.get("data") or {}


def gh_graphql_paginated(
    build_query: str,
    connection_path: list[str],
    *,
    page_size: int = 100,
    max_pages: int = 50,
) -> list[dict[str, Any]]:
    """
    Walk a GraphQL connection using ``first`` / ``after``.

    ``build_query`` must contain placeholders ``__FIRST__`` and ``__AFTER__``
    and return a connection with ``nodes`` and ``pageInfo``.
    """
    nodes: list[dict[str, Any]] = []
    cursor: str | None = None
    for _ in range(max_pages):
        after_part = f', after: "{cursor}"' if cursor else ""
        query = build_query.replace("__FIRST__", str(page_size)).replace(
            "__AFTER__", after_part
        )
        data = gh_graphql(query)
        conn: Any = data
        for key in connection_path:
            conn = conn[key]
        page_nodes = conn.get("nodes") or []
        nodes.extend(page_nodes)
        page_info = conn.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break
    return nodes
