"""Route each PDF page to the cheapest faithful source: text, OCR, or vision.

- Digital pages keep their extracted text, unless their meaning lives in visuals
  (tables, charts, diagrams) — those go to a vision model.
- Scanned or garbled pages are rendered and sent to OCR.

Every page carries a token estimate so the savings of avoiding the image path
are visible.
"""

from __future__ import annotations

from pathlib import Path

from .classify import classify_text
from .detect import is_vision_worthy
from .models import PageClass, PageRoute, RouteResult, Source, TokenEstimate
from .ocr import ocr_png_text
from .pdf import Pdf
from .tokens import claude_image_tokens, estimate_text_tokens


def route_pdf(path: str | Path, *, render_scale: float = 2.0) -> RouteResult:
    """Route every page of a PDF and return per-page content, source, and tokens."""
    pages: list[PageRoute] = []
    with Pdf(path) as pdf:
        for index in range(len(pdf)):
            text = pdf.page_text(index)
            classification = classify_text(text)
            features = pdf.page_features(index)

            if classification.page_class is PageClass.DIGITAL:
                source = Source.VISION if is_vision_worthy(features)[0] else Source.TEXT
                page_text = text
            else:
                source = Source.OCR
                page_text = ocr_png_text(pdf.render_page_png(index, scale=render_scale))

            # text_tokens reflects the text we would actually send (OCR output for
            # scanned pages), so the reported savings are honest.
            estimate = TokenEstimate(
                text_tokens=estimate_text_tokens(page_text),
                image_tokens=claude_image_tokens(
                    features.width * render_scale, features.height * render_scale
                ),
            )
            pages.append(PageRoute(index, classification, source, page_text, estimate))
    return RouteResult(pages)
