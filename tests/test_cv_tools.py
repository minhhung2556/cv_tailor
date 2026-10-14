import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = REPO_ROOT / "skills" / "cv-tuning"
AGENT_SKILLS = REPO_ROOT / ".agent" / "skills" / "cv-tuning"
SCRIPTS = SKILLS / "scripts"
HARVARD = SKILLS / "resources" / "harvard_cv.typ"


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
cv_io = _load_module("cv_io", SCRIPTS / "cv_io.py")


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

    def test_html_keeps_title_when_not_in_body(self):
        html = """<!DOCTYPE html>
<html><head><title>Senior Backend Engineer - Acme</title></head>
<body><main><p>About the role</p></main></body></html>"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jd.html"
            path.write_text(html, encoding="utf-8")
            text = parse_jd.parse_jd(str(path))
        self.assertIn("Senior Backend Engineer - Acme", text)
        self.assertIn("About the role", text)

    def test_cli_json_flag_before_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jd.txt"
            path.write_text("hello", encoding="utf-8")
            buf = io.StringIO()
            with mock.patch.object(sys, "argv", ["parse_jd.py", "--json", str(path)]):
                with mock.patch.object(sys, "stdout", buf):
                    parse_jd.main()
        self.assertIn('"text": "hello"', buf.getvalue())

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

    def test_prefers_sibling_typ_over_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "cv_base"
            base.with_suffix(".pdf").write_bytes(b"%PDF-1.4\n")
            base.with_suffix(".typ").write_text("from typ\n", encoding="utf-8")
            text = extract_cv.extract_cv(str(base.with_suffix(".pdf")))
            self.assertEqual(text, "from typ\n")

    def test_cli_json_flag_before_default_path(self):
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["extract_cv.py", "--json"]):
            with mock.patch.object(sys, "stdout", buf):
                extract_cv.main()
        out = buf.getvalue()
        self.assertIn('"text":', out)
        self.assertIn("cv_base", out.lower())

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            extract_cv.extract_cv("nonexistent_cv.typ")


class CvIoPdfTests(unittest.TestCase):
    def test_empty_pdf_raises(self):
        try:
            import pypdf
        except ImportError:
            self.skipTest("pypdf not installed")

        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "blank.pdf"
            with open(path, "wb") as f:
                writer.write(f)
            with self.assertRaises(RuntimeError):
                cv_io.extract_pdf_text(path)


class CompileCvTests(unittest.TestCase):
    def test_find_repo_root_from_script_path(self):
        root = cv_io.find_repo_root(SCRIPTS)
        self.assertEqual(root, REPO_ROOT)

    def test_resolve_relative_paths_from_repo_root(self):
        repo_root = cv_io.find_repo_root(SCRIPTS)
        typ = cv_io.resolve_repo_path(repo_root, "assets/cv_base.typ")
        pdf = cv_io.resolve_repo_path(repo_root, "output/smoke.pdf")
        self.assertEqual(typ, (repo_root / "assets/cv_base.typ").resolve())
        self.assertEqual(pdf, (repo_root / "output/smoke.pdf").resolve())


class AgentSkillLinkTests(unittest.TestCase):
    def _minimal_repo(self, tmp: Path) -> Path:
        root = tmp / "repo"
        (root / "skills" / "cv-tuning" / "resources").mkdir(parents=True)
        (root / "skills" / "cv-tuning" / "resources" / "harvard_cv.typ").write_text(
            HARVARD.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (root / "skills" / "cv-tuning" / "scripts").mkdir(parents=True, exist_ok=True)
        return root

    def test_real_directory_without_force_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._minimal_repo(Path(tmp))
            agent = root / ".agent" / "skills" / "cv-tuning"
            agent.mkdir(parents=True)
            (agent / "keep.txt").write_text("data", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                link_agent_skill.ensure_agent_skill_junction(root, force=False)

    def test_junction_points_at_skills_tree_in_temp_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._minimal_repo(Path(tmp))
            link_agent_skill.ensure_agent_skill_junction(root)
            agent = root / ".agent" / "skills" / "cv-tuning"
            self.assertTrue(agent.exists())
            self.assertEqual(
                agent.resolve(),
                (root / "skills" / "cv-tuning").resolve(),
            )

    def test_reparse_point_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._minimal_repo(Path(tmp))
            agent = root / ".agent" / "skills" / "cv-tuning"
            agent.parent.mkdir(parents=True, exist_ok=True)
            skills = (root / "skills" / "cv-tuning").resolve()
            if sys.platform == "win32":
                import subprocess

                subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(agent), str(skills)],
                    check=True,
                    capture_output=True,
                )
            else:
                agent.symlink_to(skills, target_is_directory=True)
            marker = root / "skills" / "cv-tuning" / "resources" / "marker.txt"
            marker.write_text("ok", encoding="utf-8")
            link_agent_skill.ensure_agent_skill_junction(root)
            self.assertTrue((agent / "resources" / "marker.txt").is_file())


if __name__ == "__main__":
    unittest.main()
