"""Shared test fixtures: a binary guard and PDF builders."""

from collections.abc import Callable
from pathlib import Path

import pytest
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

from localcontextrouter.ocr import OcrBinaryNotFound, locate_binary


@pytest.fixture
def lcr_binary() -> Path:
    """Path to the lcr-ocr binary, or skip the test when it is not built."""
    try:
        return locate_binary()
    except OcrBinaryNotFound:
        pytest.skip("lcr-ocr binary not built")


@pytest.fixture
def make_text_pdf(tmp_path: Path) -> Callable[..., Path]:
    """Return a factory that writes a PDF with a real text layer."""

    def _make(text: str, pages: int = 1, name: str = "text.pdf") -> Path:
        pdf = FPDF()
        pdf.set_font("Helvetica", size=12)
        for _ in range(pages):
            pdf.add_page()
            pdf.multi_cell(0, 8, text)
        path = tmp_path / name
        pdf.output(str(path))
        return path

    return _make


@pytest.fixture
def make_image_pdf(tmp_path: Path) -> Callable[..., Path]:
    """Return a factory that writes an image-only PDF (no text layer)."""

    def _make(text: str, name: str = "scan.pdf") -> Path:
        image = Image.new("RGB", (900, 220), "white")
        draw = ImageDraw.Draw(image)
        draw.text((25, 80), text, fill="black", font=ImageFont.load_default(size=56))
        png = tmp_path / "scan.png"
        image.save(png)
        pdf = FPDF()
        pdf.add_page()
        pdf.image(str(png), x=10, y=10, w=180)
        path = tmp_path / name
        pdf.output(str(path))
        return path

    return _make
