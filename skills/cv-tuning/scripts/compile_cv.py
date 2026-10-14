#!/usr/bin/env python3
"""
compile_cv.py - Compiles a Typst CV file (.typ) into a PDF inside the output/ directory.
"""

import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cv_io

TYPST_TIMEOUT_SECONDS = 120


def pdf_page_count(pdf_path: str) -> int:
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    try:
        import pypdf
    except ImportError as e:
        raise RuntimeError(cv_io.PYPDF_INSTALL_MSG) from e
    try:
        return len(pypdf.PdfReader(str(path)).pages)
    except Exception as e:
        raise RuntimeError(f"Could not read PDF page count for {pdf_path}: {e}") from e


def compile_cv(typ_path: str, output_path: str | None = None) -> str:
    repo_root = cv_io.find_repo_root(Path(__file__).resolve().parent)
    typ_file = cv_io.resolve_repo_path(repo_root, typ_path)
    if not typ_file.exists():
        raise FileNotFoundError(f"Typst source file not found: {typ_path}")

    if not output_path:
        output_dir = repo_root / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_name = typ_file.stem + ".pdf"
        output_path = str(output_dir / pdf_name)
    else:
        out_p = cv_io.resolve_repo_path(repo_root, output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        output_path = str(out_p)

    cmd = [
        "typst",
        "compile",
        "--root",
        str(repo_root),
        str(typ_file),
        output_path,
    ]
    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TYPST_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Typst compiler not found on PATH. Install Typst and ensure the `typst` command is available."
        ) from None
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"Typst compilation timed out after {TYPST_TIMEOUT_SECONDS} seconds"
        ) from e

    if res.returncode != 0:
        detail = (res.stderr or res.stdout or "").strip()
        raise RuntimeError(f"Typst compilation failed:\n{detail}")

    typst_output = "\n".join(
        part.strip()
        for part in (res.stdout, res.stderr)
        if part and part.strip()
    )
    if typst_output:
        print(typst_output, file=sys.stderr)

    return output_path


def main():
    cv_io.configure_utf8_stdout()
    if len(sys.argv) < 2:
        print("Usage: python compile_cv.py <file.typ> [output_pdf_path]")
        sys.exit(1)

    typ_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        pdf = compile_cv(typ_path, output_path)
        pages = pdf_page_count(pdf)
        print(f"Successfully generated PDF: {pdf}")
        print(f"Page count: {pages}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
