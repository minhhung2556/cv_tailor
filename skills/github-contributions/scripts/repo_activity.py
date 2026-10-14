#!/usr/bin/env python3
"""Fetch per-repository commit activity for the authenticated viewer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import github_api as gh

BATCH_SIZE = 15


def _split_name(name_with_owner: str) -> tuple[str, str]:
    if "/" not in name_with_owner:
        raise ValueError(f"Invalid name_with_owner: {name_with_owner}")
    owner, name = name_with_owner.split("/", 1)
    return owner, name


def _activity_query_chunk(
    repos: list[str],
    viewer_id: str,
    start_index: int,
) -> tuple[str, dict[str, str]]:
    var_decls: list[str] = ["$viewerId: ID!"]
    variables: dict[str, str] = {"viewerId": viewer_id}
    field_parts: list[str] = []
    for i, full_name in enumerate(repos):
        owner, name = _split_name(full_name)
        alias = f"r{start_index + i}"
        owner_var = f"owner_{alias}"
        name_var = f"name_{alias}"
        variables[owner_var] = owner
        variables[name_var] = name
        var_decls.append(f"${owner_var}: String!")
        var_decls.append(f"${name_var}: String!")
        field_parts.append(
            f"""
  {alias}: repository(owner: ${owner_var}, name: ${name_var}) {{
    defaultBranchRef {{
      target {{
        ... on Commit {{
          history(first: 1, author: {{ id: $viewerId }}) {{
            totalCount
            nodes {{ committedDate }}
          }}
        }}
      }}
    }}
  }}"""
        )
    query = "query (" + ", ".join(var_decls) + ") {\n" + "\n".join(field_parts) + "\n}"
    return query, variables


def _oldest_commit_iso(owner: str, name: str, author_login: str) -> str | None:
    """Oldest authored commit on the default listing (author filter, page 1 is newest)."""
    path = f"repos/{owner}/{name}/commits?author={author_login}&per_page=1"
    raw = gh._run_gh(["api", "-i", "--method", "GET", path])
    last_page = 1
    for line in raw.splitlines():
        if line.lower().startswith("link:"):
            for part in line.split(","):
                if 'rel="last"' in part:
                    marker = "page="
                    idx = part.find(marker)
                    if idx >= 0:
                        digits = []
                        for ch in part[idx + len(marker) :]:
                            if ch.isdigit():
                                digits.append(ch)
                            else:
                                break
                        if digits:
                            last_page = int("".join(digits))
    body_path = path if last_page == 1 else f"{path}&page={last_page}"
    body = gh._run_gh(["api", "--method", "GET", body_path])
    commits = json.loads(body)
    if isinstance(commits, list) and commits:
        commit = commits[-1].get("commit") or {}
        author = commit.get("author") or {}
        return author.get("date")
    return None


def _fill_oldest_commits(results: dict[str, dict[str, Any]], viewer_login: str) -> None:
    if not viewer_login:
        return
    for full_name, row in results.items():
        if not row.get("_needs_oldest"):
            continue
        owner, name = _split_name(full_name)
        try:
            row["first_commit"] = _oldest_commit_iso(owner, name, viewer_login)
        except gh.GhError:
            row["first_commit"] = None


def fetch_activity_for_repos(
    name_with_owners: list[str],
    viewer_node_id: str,
    viewer_login: str = "",
) -> dict[str, dict[str, Any]]:
    """Map repo full name to commit_count, first_commit, last_commit (ISO strings or null)."""
    results: dict[str, dict[str, Any]] = {}
    if not viewer_node_id:
        return results
    for batch_start in range(0, len(name_with_owners), BATCH_SIZE):
        batch = name_with_owners[batch_start : batch_start + BATCH_SIZE]
        query, variables = _activity_query_chunk(batch, viewer_node_id, batch_start)
        data = gh.gh_graphql(query, variables)
        for i, full_name in enumerate(batch):
            alias = f"r{batch_start + i}"
            repo_data = data.get(alias) or {}
            branch = repo_data.get("defaultBranchRef") or {}
            target = branch.get("target") or {}
            history = target.get("history") or {}
            total = history.get("totalCount")
            newest_nodes = history.get("nodes") or []
            last_commit = newest_nodes[0].get("committedDate") if newest_nodes else None
            results[full_name] = {
                "commit_count": total if total is not None else 0,
                "first_commit": last_commit if total == 1 else None,
                "last_commit": last_commit,
                "_needs_oldest": bool(total and total > 1),
            }
    _fill_oldest_commits(results, viewer_login)
    for row in results.values():
        row.pop("_needs_oldest", None)
    return results


def enrich_repos_with_activity(
    repos: list[dict[str, Any]],
    viewer: dict[str, Any],
) -> list[dict[str, Any]]:
    node_id = viewer.get("node_id")
    if not node_id:
        data = gh.gh_graphql("query { viewer { id login } }")
        node_id = (data.get("viewer") or {}).get("id")
    names = [r["name_with_owner"] for r in repos]
    activity = fetch_activity_for_repos(
        names,
        node_id or "",
        viewer.get("login") or "",
    )
    enriched: list[dict[str, Any]] = []
    for repo in repos:
        act = activity.get(repo["name_with_owner"], {})
        updated = dict(repo)
        updated["commit_count"] = act.get("commit_count")
        updated["first_commit"] = act.get("first_commit")
        updated["last_commit"] = act.get("last_commit")
        enriched.append(updated)
    return enriched


def main() -> None:
    gh.configure_utf8_stdio()
    parser = argparse.ArgumentParser(
        description="Add commit activity fields to repo JSON (stdin or file)."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="JSON file with {viewer, repos}; default reads stdin",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    args = parser.parse_args()
    try:
        if args.input:
            raw = Path(args.input).read_text(encoding="utf-8")
        else:
            raw = sys.stdin.read()
        payload = json.loads(raw)
        viewer = payload.get("viewer") or gh.ensure_authenticated()
        repos = payload.get("repos") or []
        enriched = enrich_repos_with_activity(repos, viewer)
        out = {"viewer": viewer, "repos": enriched}
    except (gh.GhError, json.JSONDecodeError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    if args.json or not args.input:
        clean_repos = [{k: v for k, v in r.items() if not k.startswith("_")} for r in out["repos"]]
        print(json.dumps({"viewer": out["viewer"], "repos": clean_repos}, ensure_ascii=False, indent=2))
    else:
        for r in out["repos"]:
            print(
                f"{r['name_with_owner']}: {r.get('commit_count')} commits "
                f"({r.get('first_commit')} .. {r.get('last_commit')})"
            )


if __name__ == "__main__":
    main()
