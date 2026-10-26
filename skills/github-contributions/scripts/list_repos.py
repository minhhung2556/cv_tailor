#!/usr/bin/env python3
"""List GitHub repositories visible to the authenticated viewer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import contributions_io as cio
import github_api as gh

CONTRIBUTED_REPOS_QUERY = """
query($first: Int!, $after: String) {
  viewer {
    repositoriesContributedTo(
      first: $first
      after: $after
      includeUserRepositories: true
      contributionTypes: [COMMIT]
    ) {
      nodes {
        nameWithOwner
        url
        isPrivate
        description
        primaryLanguage { name }
        repositoryTopics(first: 20) { nodes { topic { name } } }
        stargazerCount
        isFork
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""


def _role_from_rest(repo: dict[str, Any], viewer_login: str) -> str:
    owner = repo.get("owner") or {}
    owner_login = owner.get("login") or ""
    owner_type = owner.get("type") or ""
    if owner_login.lower() == viewer_login.lower():
        return cio.ROLE_OWNER
    if owner_type == "Organization":
        return cio.ROLE_ORG_MEMBER
    return cio.ROLE_COLLABORATOR


def _rest_repo_to_stub(repo: dict[str, Any], viewer_login: str) -> dict[str, Any]:
    name = repo.get("full_name") or repo.get("name") or ""
    return cio.repo_stub(
        name,
        repo.get("html_url") or f"https://github.com/{name}",
        private=bool(repo.get("private")),
        role=_role_from_rest(repo, viewer_login),
        description=repo.get("description"),
        primary_language=repo.get("language"),
        topics=list(repo.get("topics") or []),
        stars=repo.get("stargazers_count"),
        is_fork=bool(repo.get("fork")),
    )


def _fetch_affiliated_repos(viewer_login: str) -> dict[str, dict[str, Any]]:
    raw_repos = gh.gh_api_paginated(
        "user/repos",
        params={
            "visibility": "all",
            "affiliation": "owner,collaborator,organization_member",
            "per_page": "100",
            "sort": "updated",
        },
    )
    by_name: dict[str, dict[str, Any]] = {}
    for repo in raw_repos:
        if not isinstance(repo, dict):
            continue
        name = repo.get("full_name")
        if not name:
            continue
        by_name[name] = _rest_repo_to_stub(repo, viewer_login)
    return by_name


def _graphql_topics(node: dict[str, Any]) -> list[str]:
    return [
        t.get("topic", {}).get("name")
        for t in (node.get("repositoryTopics") or {}).get("nodes") or []
        if t.get("topic", {}).get("name")
    ]


def _fetch_contributed_repos() -> list[dict[str, Any]]:
    nodes = gh.gh_graphql_paginated(
        CONTRIBUTED_REPOS_QUERY,
        ["viewer", "repositoriesContributedTo"],
        page_size=100,
    )
    stubs: list[dict[str, Any]] = []
    for node in nodes:
        name = node.get("nameWithOwner") or ""
        if not name:
            continue
        lang = (node.get("primaryLanguage") or {}).get("name")
        stubs.append(
            cio.repo_stub(
                name,
                node.get("url") or f"https://github.com/{name}",
                private=bool(node.get("isPrivate")),
                role=cio.ROLE_CONTRIBUTOR,
                description=node.get("description"),
                primary_language=lang,
                topics=_graphql_topics(node),
                stars=node.get("stargazerCount"),
                is_fork=bool(node.get("isFork")),
            )
        )
    return stubs


def list_repositories(viewer: dict[str, Any] | None = None) -> dict[str, Any]:
    if viewer is None:
        viewer = gh.ensure_authenticated()
    login = viewer["login"]
    by_name = _fetch_affiliated_repos(login)
    for stub in _fetch_contributed_repos():
        name = stub["name_with_owner"]
        if name in by_name:
            cio.merge_repo_metadata(by_name[name], stub)
        else:
            by_name[name] = stub
    repos = sorted(by_name.values(), key=lambda r: r["name_with_owner"].lower())
    return {"viewer": viewer, "repos": repos}


def main() -> None:
    gh.configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="List GitHub repos for the authenticated user.")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    args = parser.parse_args()
    try:
        result = list_repositories()
    except gh.GhError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    if args.json:
        repos = [cio.strip_private(r) for r in result["repos"]]
        print(
            json.dumps(
                {"viewer_login": result["viewer"].get("login"), "repos": repos},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for r in result["repos"]:
            print(r["name_with_owner"])


if __name__ == "__main__":
    main()
