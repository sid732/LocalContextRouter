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


def test_text_page_reports_token_savings(make_text_pdf: Callable[..., Path]) -> None:
    result = route_pdf(make_text_pdf(PROSE))
    page = result.pages[0]
    # A short prose page is far cheaper as text than as a full-page image.
    assert page.tokens.image_tokens > page.tokens.text_tokens
    assert result.tokens_saved == page.tokens.saved > 0


def test_routes_table_page_to_vision(make_table_pdf: Callable[..., Path]) -> None:
    result = route_pdf(make_table_pdf())
    page = result.pages[0]
    assert page.source is Source.VISION
    # Vision pages are sent as images, so they contribute no savings.
    assert result.tokens_saved == 0


@pytest.mark.integration
def test_routes_scanned_page_to_ocr(lcr_binary: Path, make_image_pdf: Callable[..., Path]) -> None:
    result = route_pdf(make_image_pdf("SCANNED INVOICE 2026"))
    assert len(result.pages) == 1
    page = result.pages[0]
    assert page.source is Source.OCR
    assert "INVOICE" in page.text.upper()
