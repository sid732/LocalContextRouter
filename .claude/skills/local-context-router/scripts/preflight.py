#!/usr/bin/env python3
"""Preflight a document and report the cheapest faithful source for each page.

Thin wrapper over ``localcontextrouter``'s report logic so the skill and the
installed CLI stay in lockstep. PDFs run through the full router (text / OCR /
vision); a bare image is OCR'd.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _ensure_importable() -> None:
    """Make localcontextrouter importable, falling back to the repo source tree."""
    try:
        import localcontextrouter  # noqa: F401
    except ModuleNotFoundError:
        repo_src = Path(__file__).resolve().parents[4] / "src"
        if repo_src.is_dir():
            sys.path.insert(0, str(repo_src))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight a document for an LLM.")
    parser.add_argument("path", help="PDF or image to analyze")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument("--vision-dir", help="directory for rendered images of visual pages")
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.exists():
        parser.error(f"no such file: {path}")

    _ensure_importable()
    from localcontextrouter.cli import build_report, render_report

    try:
        report = build_report(path, args.vision_dir)
    except ValueError as error:
        parser.error(str(error))

    print(render_report(report, as_json=args.json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
