#!/usr/bin/env python3
"""
compile_cv.py - Compiles a Typst CV file (.typ) into a PDF inside the output/ directory.
"""

import sys
import subprocess
from pathlib import Path

HARVARD_TEMPLATE = Path("skills/cv-tuning/resources/harvard_cv.typ")


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / HARVARD_TEMPLATE).is_file():
            return candidate
    raise RuntimeError(
        f"Could not locate repo root (missing {HARVARD_TEMPLATE}) "
        f"starting from {start}"
    )


def compile_cv(typ_path: str, output_path: str = None) -> str:
    repo_root = find_repo_root(Path(__file__).resolve().parent)
    typ_file = Path(typ_path)
    if not typ_file.is_absolute():
        typ_file = (Path.cwd() / typ_file).resolve()
    if not typ_file.exists():
        raise FileNotFoundError(f"Typst source file not found: {typ_path}")

    if not output_path:
        output_dir = repo_root / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_name = typ_file.stem + ".pdf"
        output_path = str(output_dir / pdf_name)
    else:
        out_p = Path(output_path)
        if not out_p.is_absolute():
            out_p = (Path.cwd() / out_p).resolve()
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
    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode != 0:
        raise RuntimeError(f"Typst compilation failed:\n{res.stderr}")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compile_cv.py <file.typ> [output_pdf_path]")
        sys.exit(1)

    typ_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        pdf = compile_cv(typ_path, output_path)
        print(f"Successfully generated PDF: {pdf}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
