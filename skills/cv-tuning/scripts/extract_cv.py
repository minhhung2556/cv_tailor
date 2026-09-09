#!/usr/bin/env python3
"""
extract_cv.py - Extracts text content from base CV PDF file (e.g. assets/cv_base.pdf).
"""

import sys
import os
import json
from pathlib import Path

from pdf_utils import extract_pdf_pages

def extract_cv(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Base CV PDF not found: {file_path}")

    pages = extract_pdf_pages(path)
    return "\n\n".join(
        f"--- PAGE {i+1} ---\n{text}"
        for i, text in enumerate(pages)
        if text.strip()
    )

def main():
    # CV content may be non-ASCII (e.g. Vietnamese); force UTF-8 on stdout to
    # avoid a Windows console crash when printing it.
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass

    cv_path = sys.argv[1] if len(sys.argv) > 1 else "assets/cv_base.pdf"
    as_json = "--json" in sys.argv

    try:
        text = extract_cv(cv_path)
        if as_json:
            print(json.dumps({
                "file_path": cv_path,
                "text": text
            }, ensure_ascii=False, indent=2))
        else:
            print(text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
