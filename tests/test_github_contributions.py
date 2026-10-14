import importlib.util
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GH_SCRIPTS = REPO_ROOT / "skills" / "github-contributions" / "scripts"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, GH_SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


cio = _load("contributions_io", "contributions_io.py")


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
            cio.should_include_repo(
                _sample_record(description="x", commit_count=0), is_fork=True
            )
        )

    def test_includes_with_commits_only(self):
        self.assertTrue(
            cio.should_include_repo(
                _sample_record(description=None, commit_count=3), is_fork=False
            )
        )

    def test_skips_empty_fork(self):
        self.assertFalse(
            cio.should_include_repo(
                _sample_record(description=None, commit_count=0), is_fork=True
            )
        )

    def test_skips_empty_non_fork(self):
        self.assertFalse(
            cio.should_include_repo(
                _sample_record(description=None, commit_count=0), is_fork=False
            )
        )


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
