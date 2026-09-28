#!/usr/bin/env python3
"""
parse_jd.py - Extracts plain text from Job Description (JD) files of various formats:
HTML (.html, .htm), PDF (.pdf), Markdown (.md), Plain Text (.txt).
"""

import json
import os
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cv_io

JD_EXTENSIONS = {".html", ".htm", ".pdf", ".md", ".txt"}
STRIP_TAGS = ("script", "style", "noscript", "head", "nav", "footer")


def _normalize_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        collapsed = re.sub(r"\s+", " ", line).strip()
        if collapsed:
            lines.append(collapsed)
    return "\n".join(lines)


def _parse_html(path: Path) -> str:
    try:
        from bs4 import BeautifulSoup
    except ImportError as e:
        raise RuntimeError(
            "HTML parsing requires beautifulsoup4. Install with: pip install beautifulsoup4"
        ) from e

    try:
        soup = BeautifulSoup(cv_io.read_text_file(path), "html.parser")
        for tag in soup.find_all(STRIP_TAGS):
            tag.decompose()
        text = soup.get_text(separator="\n")
        return _normalize_text(text)
    except Exception as e:
        raise RuntimeError(f"Error parsing HTML file {path}: {e}") from e


def parse_jd(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JD file not found: {file_path}")

    ext = path.suffix.lower()
    if ext not in JD_EXTENSIONS:
        raise ValueError(
            f"Unsupported JD format '{ext}'. Use .html, .htm, .pdf, .md, or .txt."
        )

    if ext in (".html", ".htm"):
        return _parse_html(path)

    if ext == ".pdf":
        return _normalize_text(cv_io.extract_pdf_text(path))

    return _normalize_text(cv_io.read_text_file(path))


def main():
    cv_io.configure_utf8_stdout()
    if len(sys.argv) < 2:
        print("Usage: python parse_jd.py <path_to_jd_file> [--json]")
        sys.exit(1)

    file_path = sys.argv[1]
    as_json = "--json" in sys.argv

    try:
        text = parse_jd(file_path)
        if as_json:
            print(
                json.dumps(
                    {
                        "file_path": file_path,
                        "file_name": os.path.basename(file_path),
                        "text": text,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
