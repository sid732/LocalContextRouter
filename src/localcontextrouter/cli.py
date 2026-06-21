"""``localctx`` — route a document and report the cheapest faithful source per page."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .models import Source
from .ocr import run_ocr
from .pdf import Pdf
from .router import route_pdf
from .tokens import estimate_text_tokens

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif", ".heic"}


def build_report(path: str | Path, vision_dir: str | Path | None = None) -> dict[str, object]:
    """Route a PDF (or OCR a bare image) and return a serializable report.

    For PDFs whose visual pages should go to a vision model, the page images are
    rendered into ``vision_dir`` (when given) and referenced in the report.

    Raises ``ValueError`` for unsupported file types.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _report_pdf(path, Path(vision_dir) if vision_dir is not None else None)
    if suffix in IMAGE_SUFFIXES:
        return _report_image(path)
    raise ValueError(f"unsupported file type: {path.suffix or '(none)'}")


def _report_pdf(path: Path, vision_dir: Path | None) -> dict[str, object]:
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


def _report_image(path: Path) -> dict[str, object]:
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


def render_report(report: dict[str, object], *, as_json: bool) -> str:
    """Render a report from :func:`build_report` as JSON or a human summary."""
    if as_json:
        return json.dumps(report, indent=2)

    pages = report["pages"]
    assert isinstance(pages, list)
    lines = [
        f"Document: {report['path']} ({report['page_count']} pages)",
        f"Tokens saved vs sending every page as an image: {report['tokens_saved']}",
        "",
    ]
    for page in pages:
        header = f"Page {page['index'] + 1} [{page['source']}]"
        if page["image"]:
            header += f" -> attach image: {page['image']}"
        lines.append(header)
        text = str(page["text"]).strip()
        if text:
            lines.append(text if len(text) <= 500 else text[:500] + "...")
        lines.append("")
    return "\n".join(lines).rstrip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="localctx",
        description="Route a PDF or image to the cheapest faithful source for an LLM.",
    )
    parser.add_argument("path", help="PDF or image to analyze")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a summary")
    parser.add_argument("--vision-dir", help="directory for rendered images of visual pages")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.exists():
        parser.error(f"no such file: {path}")

    try:
        report = build_report(path, args.vision_dir)
    except ValueError as error:
        parser.error(str(error))

    print(render_report(report, as_json=args.json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
