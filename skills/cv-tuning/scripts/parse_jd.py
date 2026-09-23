#!/usr/bin/env python3
"""
parse_jd.py - Extracts plain text from Job Description (JD) files of various formats:
HTML (.html, .htm), PDF (.pdf), Markdown (.md), Plain Text (.txt).
"""

import sys
import os
import json
from pathlib import Path

def parse_jd(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JD file not found: {file_path}")

    ext = path.suffix.lower()
    
    if ext in ['.html', '.htm']:
        try:
            from bs4 import BeautifulSoup
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style", "head", "title", "meta", "[document]"]):
                    script.extract()
                text = soup.get_text(separator='\n')
                # Clean up empty lines
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                return '\n'.join(chunk for chunk in chunks if chunk)
        except Exception as e:
            print(
                f"Warning: HTML parse failed ({e}); reading raw file as text.",
                file=sys.stderr,
            )
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

    elif ext == '.pdf':
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            text_pages = []
            for i, page in enumerate(reader.pages):
                text_pages.append(page.extract_text() or '')
            return '\n\n'.join(text_pages)
        except Exception as e:
            raise RuntimeError(f"Error reading PDF file {file_path}: {e}")

    else: # .md, .txt or any text file
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_jd.py <path_to_jd_file> [--json]")
        sys.exit(1)

    file_path = sys.argv[1]
    as_json = "--json" in sys.argv

    try:
        text = parse_jd(file_path)
        if as_json:
            print(json.dumps({
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "text": text
            }, ensure_ascii=False, indent=2))
        else:
            print(text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
