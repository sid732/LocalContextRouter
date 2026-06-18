"""Route each PDF page to the cheapest faithful text source.

Digital pages keep their extracted text; scanned or garbled pages are rendered
and sent to OCR. Vision routing and token accounting are added in a later phase.
"""

from __future__ import annotations

from pathlib import Path

from .classify import classify_text
from .models import PageClass, PageRoute, RouteResult, Source
from .ocr import ocr_png_text
from .pdf import Pdf


def route_pdf(path: str | Path, *, render_scale: float = 2.0) -> RouteResult:
    """Route every page of a PDF and return per-page text with its source."""
    pages: list[PageRoute] = []
    with Pdf(path) as pdf:
        for index in range(len(pdf)):
            text = pdf.page_text(index)
            classification = classify_text(text)
            if classification.page_class is PageClass.DIGITAL:
                pages.append(PageRoute(index, classification, Source.TEXT, text))
            else:
                png = pdf.render_page_png(index, scale=render_scale)
                pages.append(PageRoute(index, classification, Source.OCR, ocr_png_text(png)))
    return RouteResult(pages)
