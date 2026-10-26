"""GitHub access via the authenticated ``gh`` CLI (REST pagination and GraphQL)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from typing import Any

GH_INSTALL_MSG = (
    "GitHub CLI (gh) is required. Install from https://cli.github.com/ and run: gh auth login"
)
GH_AUTH_MSG = "gh is not authenticated. Run: gh auth login"
GH_TIMEOUT_SECONDS = 120
GH_MAX_RATE_LIMIT_RETRIES = 3


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


def _is_rate_limited(stderr: str, returncode: int) -> bool:
    if returncode == 429:
        return True
    lower = stderr.lower()
    if "rate limit" in lower or "secondary rate limit" in lower:
        return True
    if returncode == 403 and ("rate" in lower or "abuse" in lower):
        return True
    return False


def _run_gh(args: list[str], *, input_text: str | None = None) -> str:
    gh = _require_gh()
    last_err = ""
    for attempt in range(GH_MAX_RATE_LIMIT_RETRIES):
        try:
            proc = subprocess.run(
                [gh, *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                input=input_text,
                check=False,
                timeout=GH_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as e:
            raise GhError(f"gh timed out after {GH_TIMEOUT_SECONDS} seconds") from e
        except OSError as e:
            raise GhError(GH_INSTALL_MSG) from e
        if proc.returncode == 0:
            return proc.stdout
        last_err = (proc.stderr or proc.stdout or "").strip()
        if _is_rate_limited(last_err, proc.returncode) and attempt < GH_MAX_RATE_LIMIT_RETRIES - 1:
            time.sleep(2 ** attempt)
            continue
        if "not logged in" in last_err.lower() or "401" in last_err:
            raise GhError(GH_AUTH_MSG)
        raise GhError(last_err or f"gh exited with code {proc.returncode}")
    raise GhError(last_err or "gh rate limit exceeded")


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


def viewer_node_id(viewer: dict[str, Any]) -> str:
    """Return the viewer GraphQL node id (REST ``node_id`` or GraphQL ``viewer.id``)."""
    node_id = viewer.get("node_id")
    if node_id:
        return str(node_id)
    data = gh_graphql("query { viewer { id } }")
    node_id = (data.get("viewer") or {}).get("id")
    if not node_id:
        raise GhError("Could not resolve viewer GraphQL id")
    return str(node_id)


def gh_api_get_with_headers(path: str) -> tuple[str, str]:
    """Run ``gh api -i`` and return ``(raw_headers_and_status, response_body)``."""
    raw = _run_gh(["api", "-i", "--method", "GET", path])
    parts = raw.split("\r\n\r\n", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    parts = raw.split("\n\n", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", raw.strip()


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
        try:
            page = json.loads(chunk)
        except json.JSONDecodeError as e:
            raise GhError(f"Invalid JSON in paginated gh response: {e}") from e
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
    query: str,
    connection_path: list[str],
    *,
    page_size: int = 100,
    max_pages: int = 50,
) -> list[dict[str, Any]]:
    """
    Walk a GraphQL connection using variables ``$first`` and ``$after``.

    ``query`` must declare ``$first: Int!`` and ``$after: String`` and return a
    connection with ``nodes`` and ``pageInfo``.
    """
    nodes: list[dict[str, Any]] = []
    cursor: str | None = None
    for _ in range(max_pages):
        variables: dict[str, Any] = {"first": page_size, "after": cursor}
        data = gh_graphql(query, variables)
        conn: Any = data
        try:
            for key in connection_path:
                conn = conn[key]
        except (KeyError, TypeError) as e:
            path = ".".join(connection_path)
            raise GhError(f"Missing GraphQL connection at {path}: {e}") from e
        page_nodes = conn.get("nodes") or []
        nodes.extend(page_nodes)
        page_info = conn.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break
    return nodes
