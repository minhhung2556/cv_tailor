#!/usr/bin/env python3
"""
extract_cv.py - Extracts text content from base CV PDF file (e.g. assets/cv_base.pdf).
"""

import sys
import os
import json
import pypdf
from pathlib import Path

def extract_cv(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Base CV PDF not found: {file_path}")

    reader = pypdf.PdfReader(str(path))
    pages_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages_text.append(f"--- PAGE {i+1} ---\n{text}")
    return "\n\n".join(pages_text)

def main():
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
