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

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cv_io

WD_EXPORT_FORMAT_PDF = 17
LIBREOFFICE_TIMEOUT_SECONDS = 120


def _convert_with_word(src: Path, dst: Path) -> bool:
    try:
        import win32com.client
    except ImportError:
        return False

    word = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(str(src.resolve()), False, True)
        doc.ExportAsFixedFormat(str(dst.resolve()), WD_EXPORT_FORMAT_PDF)
        doc.Close(False)
        return dst.is_file()
    except Exception:
        return False
    finally:
        if word is not None:
            try:
                word.Quit()
            except Exception:
                pass


def _convert_with_libreoffice(src: Path, dst: Path) -> bool:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return False

    try:
        proc = subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf",
             "--outdir", str(dst.parent), str(src)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=LIBREOFFICE_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False

    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        if detail:
            print(detail, file=sys.stderr)
        return False

    produced = dst.parent / (src.stem + ".pdf")
    if produced != dst and produced.exists():
        produced.replace(dst)
    return dst.is_file()


def docx_to_pdf(in_path: str, out_path: str) -> str:
    src = cv_io.resolve_user_path(in_path)
    if not src.exists():
        raise FileNotFoundError(f"Word file not found: {in_path}")
    dst = cv_io.resolve_user_path(out_path)
    dst.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        dir=dst.parent,
        delete=False,
    ) as tmp:
        temp_pdf = Path(tmp.name)

    try:
        for convert in (_convert_with_word, _convert_with_libreoffice):
            if temp_pdf.exists():
                temp_pdf.unlink(missing_ok=True)
            try:
                ok = convert(src, temp_pdf)
            except Exception:
                ok = False
            if ok:
                temp_pdf.replace(dst)
                return str(dst)
    finally:
        temp_pdf.unlink(missing_ok=True)

    raise RuntimeError(
        "No docx->pdf converter available. Install Microsoft Word + pywin32 "
        "(Windows), or LibreOffice (soffice on PATH)."
    )


def main():
    cv_io.configure_utf8_stdout()
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
