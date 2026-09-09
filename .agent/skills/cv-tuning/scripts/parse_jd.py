#!/usr/bin/env python3
"""
parse_jd.py - Extracts plain text from Job Description (JD) files of various formats:
HTML (.html, .htm), PDF (.pdf), Word (.docx), Markdown (.md), Plain Text (.txt).

Note: legacy Word binary format (.doc) is NOT supported by python-docx; convert it
to .docx (or export the JD as PDF/text) before parsing.
"""

import sys
import os
import json
from pathlib import Path

from pdf_utils import extract_pdf_pages

def _parse_docx(path: Path) -> str:
    """Extract text from a .docx, walking body elements in document order so that
    paragraphs and tables stay interleaved the way they appear to a reader."""
    from docx import Document
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(str(path))
    lines = []
    for child in doc.element.body.iterchildren():
        if child.tag == qn('w:p'):
            lines.append(Paragraph(child, doc).text)
        elif child.tag == qn('w:tbl'):
            for row in Table(child, doc).rows:
                lines.append('\t'.join(cell.text for cell in row.cells))
    return '\n'.join(line for line in lines if line.strip())


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
            # Fallback to plain text read if BeautifulSoup fails
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

    elif ext == '.pdf':
        try:
            return '\n\n'.join(extract_pdf_pages(path))
        except Exception as e:
            raise RuntimeError(f"Error reading PDF file {file_path}: {e}")

    elif ext == '.docx':
        try:
            return _parse_docx(path)
        except Exception as e:
            raise RuntimeError(f"Error reading Word file {file_path}: {e}")

    elif ext == '.doc':
        raise RuntimeError(
            f"Legacy .doc is not supported: {file_path}. "
            "Convert it to .docx (or export as PDF/text) and retry."
        )

    else: # .md, .txt or any text file
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

def main():
    # JD content is often non-ASCII (e.g. Vietnamese); avoid a Windows console
    # crash when printing it by forcing UTF-8 on stdout.
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass

    if len(sys.argv) < 2:
        print("Usage: python parse_jd.py <path_to_jd_file> [--json]")
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
