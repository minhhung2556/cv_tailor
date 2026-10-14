#!/usr/bin/env python3
"""
extract_cv.py - Extracts text content from base CV files (PDF, Typst, Markdown, plain text).
"""

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cv_io

TEXT_EXTENSIONS = {".typ", ".md", ".txt"}
CV_EXTENSIONS = TEXT_EXTENSIONS | {".pdf"}


def _prefer_typ_over_pdf(path: Path) -> Path:
    if path.suffix.lower() != ".pdf":
        return path
    sibling_typ = path.with_suffix(".typ")
    if sibling_typ.is_file():
        return sibling_typ
    return path


def extract_cv(file_path: str) -> str:
    path = _prefer_typ_over_pdf(cv_io.resolve_user_path(file_path))

    if not path.exists():
        raise FileNotFoundError(f"Base CV file not found: {file_path}")

    ext = path.suffix.lower()
    if ext not in CV_EXTENSIONS:
        raise ValueError(
            f"Unsupported CV format '{ext}'. Use .typ, .md, .txt, or .pdf."
        )

    if ext in TEXT_EXTENSIONS:
        return cv_io.read_text_file(path)

    return cv_io.extract_pdf_text(path, page_markers=True)


def default_cv_path() -> str:
    return str(cv_io.resolve_user_path(str(cv_io.DEFAULT_BASE_CV)))


def main():
    cv_io.run_text_cli(
        sys.argv,
        usage="Usage: python extract_cv.py [path_to_cv] [--json]",
        read_text=extract_cv,
        default_path=default_cv_path(),
    )


if __name__ == "__main__":
    main()
