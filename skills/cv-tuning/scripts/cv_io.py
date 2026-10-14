"""Shared text and PDF reading for CV tooling scripts."""

from __future__ import annotations

import json
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

PYPDF_INSTALL_MSG = "PDF extraction requires pypdf. Install with: pip install pypdf"
HARVARD_TEMPLATE_REL = Path("resources/harvard_cv.typ")
DEFAULT_BASE_CV = Path("assets/cv_base.typ")


def configure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def find_skill_root(start: Path | None = None) -> Path:
    if start is None:
        start = Path(__file__).resolve().parent
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / HARVARD_TEMPLATE_REL).is_file():
            return candidate
    raise RuntimeError(
        f"Could not locate skill root (missing {HARVARD_TEMPLATE_REL}) starting from {start}"
    )


def _has_workspace_markers(directory: Path) -> bool:
    return (directory / DEFAULT_BASE_CV).is_file() or (directory / "assets" / "jd").is_dir()


def find_workspace_root(start: Path | None = None) -> Path:
    if start is None:
        start = Path.cwd()
    current = start.resolve()
    for candidate in (current, *current.parents):
        if _has_workspace_markers(candidate):
            return candidate

    skill_root = find_skill_root(Path(__file__).resolve().parent)
    if skill_root.name == "cv-tuning" and skill_root.parent.name == "skills":
        return skill_root.parent.parent

    return current


def resolve_workspace_path(workspace_root: Path, path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path.resolve()
    return (workspace_root / path).resolve()


def resolve_user_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path.resolve()
    workspace = find_workspace_root()
    return resolve_workspace_path(workspace, path_str)


def harvard_template_path(skill_root: Path | None = None) -> Path:
    if skill_root is None:
        skill_root = find_skill_root()
    return skill_root / HARVARD_TEMPLATE_REL


def stage_harvard_template_next_to(typ_file: Path, skill_root: Path | None = None) -> Path:
    """Copy harvard_cv.typ beside the Typst source for compilation."""
    dest = typ_file.parent / "harvard_cv.typ"
    src = harvard_template_path(skill_root)
    if not src.is_file():
        raise FileNotFoundError(f"Harvard template not found: {src}")
    shutil.copy2(src, dest)
    return dest


def parse_cli_path_and_json(
    argv: list[str],
    *,
    default_path: str | None = None,
) -> tuple[str | None, bool]:
    """Return (first non-flag path, --json present). Flags may appear in any order."""
    as_json = "--json" in argv
    path_args = [a for a in argv[1:] if a != "--json"]
    if path_args:
        return path_args[0], as_json
    return default_path, as_json


def run_text_cli(
    argv: list[str],
    *,
    usage: str,
    read_text: Callable[[str], str],
    default_path: str | None = None,
    extra_fields: Callable[[str], dict] | None = None,
) -> None:
    configure_utf8_stdout()
    file_path, as_json = parse_cli_path_and_json(argv, default_path=default_path)
    if not file_path:
        print(usage)
        sys.exit(1)

    try:
        text = read_text(file_path)
        if as_json:
            payload: dict = {"file_path": file_path, "text": text}
            if extra_fields:
                payload.update(extra_fields(file_path))
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def read_text_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _pdf_reader(path: Path):
    try:
        import pypdf
    except ImportError as e:
        raise RuntimeError(PYPDF_INSTALL_MSG) from e
    return pypdf.PdfReader(str(path))


def extract_pdf_text(path: Path, *, page_markers: bool = False) -> str:
    reader = _pdf_reader(path)
    pages_text: list[str] = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if not text:
            continue
        if page_markers:
            pages_text.append(f"--- PAGE {i + 1} ---\n{text}")
        else:
            pages_text.append(text)
    if not pages_text:
        raise RuntimeError(
            f"No extractable text in PDF {path} (empty or scanned pages). "
            "Use a .typ or .md base CV instead."
        )
    return "\n\n".join(pages_text)
