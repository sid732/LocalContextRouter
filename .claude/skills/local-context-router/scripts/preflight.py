#!/usr/bin/env python3
"""Preflight a document and report the cheapest faithful source for each page.

PDFs run through the full router (text / OCR / vision); a bare image is OCR'd.
Output is human-readable by default, or JSON with ``--json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif", ".heic"}


def _ensure_importable() -> None:
    """Make localcontextrouter importable, falling back to the repo source tree."""
    try:
        import localcontextrouter  # noqa: F401
    except ModuleNotFoundError:
        repo_src = Path(__file__).resolve().parents[4] / "src"
        if repo_src.is_dir():
            sys.path.insert(0, str(repo_src))


def _preflight_pdf(path: Path, vision_dir: Path | None) -> dict[str, object]:
    from localcontextrouter import Pdf, Source, route_pdf

    result = route_pdf(path)
    pages: list[dict[str, object]] = []
    rendered: Pdf | None = None
    try:
        for page in result.pages:
            image_path: str | None = None
            if page.source is Source.VISION and vision_dir is not None:
                vision_dir.mkdir(parents=True, exist_ok=True)
                if rendered is None:
                    rendered = Pdf(path)
                out = vision_dir / f"{path.stem}-page-{page.index + 1}.png"
                out.write_bytes(rendered.render_page_png(page.index))
                image_path = str(out)
            pages.append(
                {
                    "index": page.index,
                    "source": page.source.value,
                    "text": page.text,
                    "text_tokens": page.tokens.text_tokens,
                    "image_tokens": page.tokens.image_tokens,
                    "image": image_path,
                }
            )
    finally:
        if rendered is not None:
            rendered.close()

    return {
        "path": str(path),
        "page_count": len(result.pages),
        "tokens_saved": result.tokens_saved,
        "pages": pages,
    }


def _preflight_image(path: Path) -> dict[str, object]:
    from localcontextrouter import estimate_text_tokens
    from localcontextrouter.ocr import run_ocr

    text = "\n".join(line.text for line in run_ocr(path))
    return {
        "path": str(path),
        "page_count": 1,
        "tokens_saved": 0,
        "pages": [
            {
                "index": 0,
                "source": "ocr",
                "text": text,
                "text_tokens": estimate_text_tokens(text),
                "image_tokens": None,
                "image": None,
            }
        ],
    }


def _print_human(report: dict[str, object]) -> None:
    pages = report["pages"]
    assert isinstance(pages, list)
    print(f"Document: {report['path']} ({report['page_count']} pages)")
    print(f"Tokens saved vs sending every page as an image: {report['tokens_saved']}\n")
    for page in pages:
        header = f"Page {page['index'] + 1} [{page['source']}]"
        if page["image"]:
            print(f"{header} -> attach image: {page['image']}")
        else:
            print(header)
        text = str(page["text"]).strip()
        if text:
            preview = text if len(text) <= 500 else text[:500] + "..."
            print(preview)
        print()


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
    vision_dir = Path(args.vision_dir) if args.vision_dir else None

    if path.suffix.lower() == ".pdf":
        report = _preflight_pdf(path, vision_dir)
    elif path.suffix.lower() in _IMAGE_SUFFIXES:
        report = _preflight_image(path)
    else:
        parser.error(f"unsupported file type: {path.suffix or '(none)'}")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
