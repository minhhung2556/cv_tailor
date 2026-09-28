"""Shared text and PDF reading for CV tooling scripts."""

from __future__ import annotations

import sys
from pathlib import Path

PYPDF_INSTALL_MSG = "PDF extraction requires pypdf. Install with: pip install pypdf"


def configure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


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
    return "\n\n".join(pages_text)
