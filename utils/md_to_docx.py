"""
Convert Markdown to Word (.docx) using the Pandoc CLI.

Requires Pandoc on PATH (https://pandoc.org/).

**CLI (recommended):** from the repository root, run the module file so
``utils/__init__.py`` is not loaded::

    python utils/md_to_docx.py report_outputs/0511_process_update.md
    python utils/md_to_docx.py report_outputs/0511_process_update.md report_outputs/custom.docx

**``python -m utils.md_to_docx``** only works if ``import utils`` succeeds
(full ``requirements.txt`` env, e.g. PyMuPDF for other helpers).

**Library:** ``from utils.md_to_docx import markdown_to_docx`` (same env as above).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def markdown_to_docx(
    src: Path,
    dest: Path,
    *,
    pandoc_exe: str = "pandoc",
    extra_args: list[str] | None = None,
) -> None:
    """
    Run Pandoc: ``pandoc src -o dest`` (plus any ``extra_args``).

    Raises:
        FileNotFoundError: if ``src`` is missing.
        RuntimeError: if ``pandoc_exe`` is not on PATH.
        subprocess.CalledProcessError: if Pandoc exits non-zero.
    """
    src = Path(src).resolve()
    dest = Path(dest).resolve()
    if not src.is_file():
        raise FileNotFoundError(src)
    if shutil.which(pandoc_exe) is None:
        raise RuntimeError(
            f"Pandoc executable {pandoc_exe!r} not found on PATH. Install pandoc (e.g. brew install pandoc)."
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [pandoc_exe, str(src), "-o", str(dest)]
    if extra_args:
        cmd.extend(extra_args)
    subprocess.run(cmd, check=True)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Markdown → Word via Pandoc.")
    p.add_argument("input", type=Path, help="Source .md path")
    p.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=None,
        help="Output .docx path (default: same directory and stem as input)",
    )
    p.add_argument(
        "--pandoc",
        default="pandoc",
        help="Pandoc executable name or path (default: pandoc)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    src = args.input
    dest = args.output if args.output is not None else src.with_suffix(".docx")
    markdown_to_docx(src, dest, pandoc_exe=args.pandoc)
    print(dest)


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
