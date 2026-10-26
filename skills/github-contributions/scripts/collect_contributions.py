#!/usr/bin/env python3
"""Collect GitHub repository evidence into assets/github_contributions.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import contributions_io as cio
import github_api as gh
import list_repos
import repo_activity


def collect(
    *,
    workspace: Path | None = None,
    output: Path | None = None,
    include_all: bool = False,
) -> Path:
    workspace = workspace or cio.find_workspace_root()
    out_path = output or cio.resolve_output_path(None, workspace)
    viewer = gh.ensure_authenticated()
    listed = list_repos.list_repositories(viewer)
    enriched = repo_activity.enrich_repos_with_activity(listed["repos"], listed["viewer"])
    filtered: list[dict] = []
    for repo in enriched:
        if include_all or cio.should_include_repo(repo):
            filtered.append(cio.strip_private(repo))
    payload = cio.build_payload(listed["viewer"], filtered)
    cio.write_payload(out_path, payload)
    return out_path


def main() -> None:
    gh.configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Collect GitHub contributions JSON.")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help=f"Output path (default: {cio.DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Include repos with no description and no authored commits",
    )
    args = parser.parse_args()
    workspace = cio.find_workspace_root()
    out = cio.resolve_output_path(args.output, workspace)
    try:
        written = collect(workspace=workspace, output=out, include_all=args.include_all)
    except gh.GhError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print(written)


if __name__ == "__main__":
    main()
