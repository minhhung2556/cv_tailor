#!/usr/bin/env python3
"""
parse_jd.py - Extracts plain text from Job Description (JD) files of various formats:
HTML (.html, .htm), PDF (.pdf), Word (.docx), Markdown (.md), Plain Text (.txt).

Legacy Word binary (.doc) is not supported; convert to .docx or export as PDF/text first.
"""

import os
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cv_io

JD_EXTENSIONS = {".html", ".htm", ".pdf", ".md", ".txt", ".docx"}
STRIP_TAGS = ("script", "style", "noscript", "nav", "footer")
HEAD_STRIP_TAGS = ("script", "style", "noscript")


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
        title_text = ""
        if soup.title and soup.title.string:
            title_text = re.sub(r"\s+", " ", soup.title.string).strip()
        head = soup.find("head")
        if head:
            for tag in head.find_all(HEAD_STRIP_TAGS):
                tag.decompose()
            head.decompose()
        for tag in soup.find_all(STRIP_TAGS):
            tag.decompose()
        body_text = soup.get_text(separator="\n")
        if title_text and title_text not in body_text:
            body_text = f"{title_text}\n{body_text}"
        return _normalize_text(body_text)
    except OSError as e:
        raise RuntimeError(f"Error reading HTML file {path}: {e}") from e


def _parse_docx(path: Path) -> str:
    try:
        from docx import Document
        from docx.oxml.ns import qn
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError as e:
        raise RuntimeError(
            "Word parsing requires python-docx. Install with: pip install python-docx"
        ) from e

    def _row_cell_texts(row) -> list[str]:
        texts = [cell.text for cell in row.cells]
        deduped: list[str] = []
        for text in texts:
            if deduped and text == deduped[-1]:
                continue
            deduped.append(text)
        return deduped

    doc = Document(str(path))
    lines = []
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            lines.append(Paragraph(child, doc).text)
        elif child.tag == qn("w:tbl"):
            for row in Table(child, doc).rows:
                lines.append("\t".join(_row_cell_texts(row)))
    return "\n".join(line for line in lines if line.strip())


def parse_jd(file_path: str) -> str:
    path = cv_io.resolve_user_path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JD file not found: {file_path}")

    ext = path.suffix.lower()
    if ext == ".doc":
        raise RuntimeError(
            f"Legacy .doc is not supported: {file_path}. "
            "Convert it to .docx (or export as PDF/text) and retry."
        )
    if ext not in JD_EXTENSIONS:
        raise ValueError(
            f"Unsupported JD format '{ext}'. "
            "Use .html, .htm, .pdf, .md, .txt, or .docx."
        )

    if ext in (".html", ".htm"):
        return _parse_html(path)

    if ext == ".pdf":
        return _normalize_text(cv_io.extract_pdf_text(path))

    if ext == ".docx":
        try:
            return _normalize_text(_parse_docx(path))
        except OSError as e:
            raise RuntimeError(f"Error reading Word file {file_path}: {e}") from e

    return _normalize_text(cv_io.read_text_file(path))


def main():
    cv_io.run_text_cli(
        sys.argv,
        usage="Usage: python parse_jd.py <path_to_jd_file> [--json]",
        read_text=parse_jd,
        extra_fields=lambda path: {"file_name": os.path.basename(path)},
    )


if __name__ == "__main__":
    main()
