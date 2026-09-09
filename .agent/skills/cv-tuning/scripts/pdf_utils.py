#!/usr/bin/env python3
"""pdf_utils.py - Shared PDF text extraction used by parse_jd.py and extract_cv.py.

Kept in one place so the pypdf read logic is not duplicated across scripts.
"""

from pathlib import Path


def extract_pdf_pages(file_path) -> list:
    """Return the extracted text of each PDF page as a list of strings.

    One entry per page; an empty string is returned for pages with no
    extractable text. Raises whatever pypdf raises on unreadable files.
    """
    import pypdf

    reader = pypdf.PdfReader(str(Path(file_path)))
    return [page.extract_text() or "" for page in reader.pages]
