"""Shared text and PDF reading for CV tooling scripts."""

from __future__ import annotations

import sys
from pathlib import Path

PYPDF_INSTALL_MSG = "PDF extraction requires pypdf. Install with: pip install pypdf"
HARVARD_TEMPLATE = Path("skills/cv-tuning/resources/harvard_cv.typ")
DEFAULT_BASE_CV = Path("assets/cv_base.typ")


def configure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / HARVARD_TEMPLATE).is_file():
            return candidate
    raise RuntimeError(
        f"Could not locate repo root (missing {HARVARD_TEMPLATE}) starting from {start}"
    )


def resolve_repo_path(repo_root: Path, path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path.resolve()
    return (repo_root / path).resolve()


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


def read_text_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def extract_pdf_text(path: Path, *, page_markers: bool = False) -> str:
    try:
        import pypdf
    except ImportError as e:
        raise RuntimeError(PYPDF_INSTALL_MSG) from e

    reader = pypdf.PdfReader(str(path))
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
