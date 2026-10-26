import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
GH_SCRIPTS = REPO_ROOT / "skills" / "github-contributions" / "scripts"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, GH_SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


cio = _load("contributions_io", "contributions_io.py")
gh = _load("github_api", "github_api.py")


def _sample_record(**overrides):
    base = {
        "name_with_owner": "acme/widget",
        "url": "https://github.com/acme/widget",
        "private": False,
        "description": "A widget library",
        "primary_language": "Python",
        "topics": ["api"],
        "role": "owner",
        "stars": 12,
        "commit_count": 5,
        "first_commit": "2024-01-15T10:00:00Z",
        "last_commit": "2024-06-01T12:00:00Z",
    }
    base.update(overrides)
    return base


class RecordShapeTests(unittest.TestCase):
    def test_normalize_requires_all_keys(self):
        with self.assertRaises(ValueError):
            cio.normalize_repo_record({"name_with_owner": "a/b"})

    def test_normalize_accepts_full_record(self):
        rec = cio.normalize_repo_record(_sample_record())
        self.assertEqual(rec["name_with_owner"], "acme/widget")
        self.assertEqual(rec["topics"], ["api"])


class ShouldIncludeTests(unittest.TestCase):
    def test_includes_with_description(self):
        self.assertTrue(
            cio.should_include_repo(_sample_record(description="x", commit_count=0))
        )

    def test_includes_with_commits_only(self):
        self.assertTrue(
            cio.should_include_repo(_sample_record(description=None, commit_count=3))
        )

    def test_skips_empty_repo(self):
        self.assertFalse(
            cio.should_include_repo(_sample_record(description=None, commit_count=0))
        )


class RepoStubMergeTests(unittest.TestCase):
    def test_repo_stub_sets_internal_fork_flag(self):
        stub = cio.repo_stub(
            "o/r",
            "https://github.com/o/r",
            private=False,
            role=cio.ROLE_OWNER,
            is_fork=True,
        )
        self.assertEqual(stub["_fork"], True)
        self.assertEqual(stub["topics"], [])

    def test_merge_repo_metadata_fills_empty_fields(self):
        existing = cio.repo_stub(
            "o/r",
            "https://github.com/o/r",
            private=False,
            role=cio.ROLE_OWNER,
            description=None,
            stars=None,
        )
        incoming = cio.repo_stub(
            "o/r",
            "https://github.com/o/r",
            private=False,
            role=cio.ROLE_CONTRIBUTOR,
            description="from contrib",
            primary_language="Go",
            topics=["cli"],
            stars=3,
        )
        cio.merge_repo_metadata(existing, incoming)
        self.assertEqual(existing["role"], cio.ROLE_OWNER)
        self.assertEqual(existing["description"], "from contrib")
        self.assertEqual(existing["primary_language"], "Go")
        self.assertEqual(existing["topics"], ["cli"])
        self.assertEqual(existing["stars"], 3)


class ViewerNodeIdTests(unittest.TestCase):
    def test_uses_rest_node_id(self):
        self.assertEqual(gh.viewer_node_id({"node_id": "N_rest"}), "N_rest")

    def test_fetches_when_missing(self):
        with mock.patch.object(
            gh, "gh_graphql", return_value={"viewer": {"id": "N_gql"}}
        ):
            self.assertEqual(gh.viewer_node_id({"login": "dev"}), "N_gql")


class GhApiPaginatedTests(unittest.TestCase):
    def test_merges_list_pages_and_singleton_chunks(self):
        raw = '[{"id": 1}]\n{"id": 2}\n'
        with mock.patch.object(gh, "_run_gh", return_value=raw):
            items = gh.gh_api_paginated("user/repos")
        self.assertEqual(items, [{"id": 1}, {"id": 2}])


class GraphqlPaginatedTests(unittest.TestCase):
    _QUERY = "query($first: Int!, $after: String) { conn { nodes pageInfo } }"
    _PATH = ["conn"]

    def test_after_null_first_page_then_cursor_with_quote(self):
        calls: list[dict] = []

        def fake_graphql(_query, variables=None):
            calls.append(dict(variables or {}))
            if len(calls) == 1:
                return {
                    "conn": {
                        "nodes": [{"n": 1}],
                        "pageInfo": {
                            "hasNextPage": True,
                            "endCursor": 'end"cursor',
                        },
                    }
                }
            return {
                "conn": {
                    "nodes": [{"n": 2}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }

        with mock.patch.object(gh, "gh_graphql", side_effect=fake_graphql):
            nodes = gh.gh_graphql_paginated(
                self._QUERY, self._PATH, page_size=50, max_pages=5
            )
        self.assertEqual(len(nodes), 2)
        self.assertIsNone(calls[0]["after"])
        self.assertEqual(calls[0]["first"], 50)
        self.assertEqual(calls[1]["after"], 'end"cursor')


class TypstSnippetTests(unittest.TestCase):
    def test_bullets_use_only_json_facts(self):
        rec = _sample_record()
        bullets = cio.build_project_bullets(rec)
        self.assertIn("A widget library", bullets[0])
        self.assertIn("Python", bullets[1])
        self.assertIn("5 commit", bullets[2])

    def test_typst_contains_repo_name_and_no_fabricated_metrics(self):
        rec = _sample_record(commit_count=2, stars=99)
        typst = cio.format_typst_cv_experience(rec)
        self.assertIn("acme/widget", typst)
        self.assertIn("https://github.com/acme/widget", typst)
        self.assertIn("2 commit", typst)
        self.assertNotIn("99", typst)

    def test_repo_name_from_typst_company(self):
        self.assertEqual(
            cio.repo_name_from_typst_company("acme/widget (https://github.com/acme/widget)"),
            "acme/widget",
        )

    def test_typst_keeps_unicode_and_escapes_specials(self):
        rec = _sample_record(
            description='Tiếng "Việt"\nsecond line',
            primary_language=None,
            topics=[],
            commit_count=0,
        )
        typst = cio.format_typst_cv_experience(rec)
        self.assertIn("Tiếng", typst)
        self.assertIn('\\"', typst)
        self.assertIn("\\n", typst)
        self.assertNotIn("\\u", typst)


class WorkspaceRootTests(unittest.TestCase):
    def test_ignores_parent_with_only_empty_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            parent = base / "parent"
            workspace = base / "workspace"
            (parent / "assets").mkdir(parents=True)
            (workspace / "assets").mkdir(parents=True)
            (workspace / "assets" / "cv_base.typ").write_text("cv\n", encoding="utf-8")
            root = cio.find_workspace_root(workspace)
            self.assertEqual(root.resolve(), workspace.resolve())


class BuildPayloadTests(unittest.TestCase):
    def test_payload_shape(self):
        viewer = {"login": "dev", "node_id": "U_kgDO"}
        payload = cio.build_payload(viewer, [_sample_record()])
        self.assertIn("collected_at", payload)
        self.assertEqual(payload["viewer"]["login"], "dev")
        self.assertEqual(len(payload["repos"]), 1)
        json.dumps(payload)


if __name__ == "__main__":
    unittest.main()
