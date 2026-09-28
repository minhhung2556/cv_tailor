import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = REPO_ROOT / "skills" / "cv-tuning"
AGENT_SKILLS = REPO_ROOT / ".agent" / "skills" / "cv-tuning"
SCRIPTS = SKILLS / "scripts"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


parse_jd = _load_module("parse_jd", SCRIPTS / "parse_jd.py")
extract_cv = _load_module("extract_cv", SCRIPTS / "extract_cv.py")
compile_cv = _load_module("compile_cv", SCRIPTS / "compile_cv.py")
link_agent_skill = _load_module("link_agent_skill", SCRIPTS / "link_agent_skill.py")


class ParseJdTests(unittest.TestCase):
    def test_html_strips_chrome_and_normalizes_whitespace(self):
        html = """<!DOCTYPE html>
<html><head><title>JD</title><style>.x{}</style></head>
<body>
<nav>Skip to content</nav>
<header>Senior Staff Engineer</header>
<main><p>Senior  Engineer</p><script>alert(1)</script></main>
<footer>Copyright</footer>
</body></html>"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jd.html"
            path.write_text(html, encoding="utf-8")
            text = parse_jd.parse_jd(str(path))

        self.assertIn("Senior Engineer", text)
        self.assertIn("Senior Staff Engineer", text)
        self.assertNotIn("Skip to content", text)
        self.assertNotIn("Copyright", text)
        self.assertNotIn("alert", text)

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            parse_jd.parse_jd("nonexistent_jd.html")

    def test_unsupported_extension_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jd.docx"
            path.write_bytes(b"fake")
            with self.assertRaises(ValueError):
                parse_jd.parse_jd(str(path))

    def test_markdown_collapses_whitespace(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jd.md"
            path.write_text("Role   title\n\nSecond  line\n", encoding="utf-8")
            text = parse_jd.parse_jd(str(path))
        self.assertEqual(text, "Role title\nSecond line")


class ExtractCvTests(unittest.TestCase):
    def test_typ_returns_source_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cv.typ"
            path.write_text("#let x = 1\n", encoding="utf-8")
            text = extract_cv.extract_cv(str(path))
            self.assertEqual(text, "#let x = 1\n")

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            extract_cv.extract_cv("nonexistent_cv.typ")


class CompileCvTests(unittest.TestCase):
    def test_find_repo_root_from_script_path(self):
        root = compile_cv.find_repo_root(SCRIPTS)
        self.assertEqual(root, REPO_ROOT)

    def test_resolve_relative_paths_from_repo_root(self):
        repo_root = compile_cv.find_repo_root(SCRIPTS)
        typ = compile_cv.resolve_repo_path(repo_root, "assets/cv_base.typ")
        pdf = compile_cv.resolve_repo_path(repo_root, "output/smoke.pdf")
        self.assertEqual(typ, (repo_root / "assets/cv_base.typ").resolve())
        self.assertEqual(pdf, (repo_root / "output/smoke.pdf").resolve())


class AgentSkillLinkTests(unittest.TestCase):
    def test_agent_skill_junction_points_at_skills_tree(self):
        link_agent_skill.ensure_agent_skill_junction(REPO_ROOT)
        self.assertTrue(AGENT_SKILLS.exists())
        self.assertEqual(AGENT_SKILLS.resolve(), SKILLS.resolve())


if __name__ == "__main__":
    unittest.main()
