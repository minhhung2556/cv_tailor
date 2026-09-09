#!/usr/bin/env python3
"""docx_to_pdf.py - Convert a .docx to PDF without the Typst CLI.

Tries, in order:
  1. Microsoft Word via COM automation (Windows; needs `pywin32` + Word installed).
  2. LibreOffice headless (`soffice` / `libreoffice` on PATH).

This is the Word-based PDF path used when `typst` is not installed: render the CV
to .docx with build_docx_cv.py, then convert here.

Usage:
    python docx_to_pdf.py <input.docx> <output.pdf>
"""

import sys
import shutil
import subprocess
from pathlib import Path

WD_EXPORT_FORMAT_PDF = 17  # Word's wdExportFormatPDF constant


def _convert_with_word(src: Path, dst: Path) -> bool:
    """Convert via MS Word COM. Returns False if pywin32/Word is unavailable."""
    try:
        import win32com.client
    except ImportError:
        return False

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(str(src), False, True)
        doc.ExportAsFixedFormat(str(dst), WD_EXPORT_FORMAT_PDF)
        doc.Close(False)
    finally:
        word.Quit()
    return dst.exists()


def _convert_with_libreoffice(src: Path, dst: Path) -> bool:
    """Convert via LibreOffice headless. Returns False if soffice is not found."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return False

    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf",
         "--outdir", str(dst.parent), str(src)],
        check=True, capture_output=True, text=True,
    )
    # LibreOffice names the output <stem>.pdf in the outdir; rename if needed.
    produced = dst.parent / (src.stem + ".pdf")
    if produced != dst and produced.exists():
        produced.replace(dst)
    return dst.exists()


def docx_to_pdf(in_path: str, out_path: str) -> str:
    src = Path(in_path)
    if not src.exists():
        raise FileNotFoundError(f"Word file not found: {in_path}")
    dst = Path(out_path)
    dst.parent.mkdir(parents=True, exist_ok=True)

    for convert in (_convert_with_word, _convert_with_libreoffice):
        if convert(src, dst):
            return str(dst)

    raise RuntimeError(
        "No docx->pdf converter available. Install Microsoft Word + pywin32 "
        "(Windows), or LibreOffice (soffice on PATH)."
    )


def main():
    if len(sys.argv) < 3:
        print("Usage: python docx_to_pdf.py <input.docx> <output.pdf>", file=sys.stderr)
        sys.exit(1)
    try:
        print(f"Successfully generated PDF: {docx_to_pdf(sys.argv[1], sys.argv[2])}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
