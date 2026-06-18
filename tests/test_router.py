"""Tests for the per-page router."""

from collections.abc import Callable
from pathlib import Path

import pytest

from localcontextrouter.models import Source
from localcontextrouter.router import route_pdf

PROSE = (
    "The quarterly report summarizes revenue, expenses, and net income for the "
    "period ending in March. All figures are stated in thousands of US dollars."
)


def test_routes_digital_page_to_text(make_text_pdf: Callable[..., Path]) -> None:
    result = route_pdf(make_text_pdf(PROSE))
    assert len(result.pages) == 1
    page = result.pages[0]
    assert page.source is Source.TEXT
    assert "revenue" in page.text
    assert "revenue" in result.text


@pytest.mark.integration
def test_routes_scanned_page_to_ocr(lcr_binary: Path, make_image_pdf: Callable[..., Path]) -> None:
    result = route_pdf(make_image_pdf("SCANNED INVOICE 2026"))
    assert len(result.pages) == 1
    page = result.pages[0]
    assert page.source is Source.OCR
    assert "INVOICE" in page.text.upper()
