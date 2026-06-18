"""Tests for PDF text extraction and per-page classification."""

from pathlib import Path

from fpdf import FPDF

from localcontextrouter import PageClass
from localcontextrouter.pdf import Pdf, classify_pdf

PROSE = (
    "The quarterly report summarizes revenue, expenses, and net income for the "
    "period ending in March. All figures are stated in thousands of US dollars."
)


def _text_pdf(path: Path, text: str, pages: int = 1) -> Path:
    pdf = FPDF()
    pdf.set_font("Helvetica", size=12)
    for _ in range(pages):
        pdf.add_page()
        pdf.multi_cell(0, 8, text)
    pdf.output(str(path))
    return path


def _blank_pdf(path: Path, pages: int = 1) -> Path:
    pdf = FPDF()
    for _ in range(pages):
        pdf.add_page()
    pdf.output(str(path))
    return path


def test_extracts_text(tmp_path: Path) -> None:
    pdf_path = _text_pdf(tmp_path / "report.pdf", PROSE)
    with Pdf(pdf_path) as pdf:
        assert len(pdf) == 1
        assert "revenue" in pdf.page_text(0)


def test_page_texts_iterates_every_page(tmp_path: Path) -> None:
    pdf_path = _text_pdf(tmp_path / "multi.pdf", PROSE, pages=3)
    with Pdf(pdf_path) as pdf:
        assert len(list(pdf.page_texts())) == 3


def test_classify_pdf_marks_text_pages_digital(tmp_path: Path) -> None:
    pdf_path = _text_pdf(tmp_path / "report.pdf", PROSE, pages=2)
    results = classify_pdf(pdf_path)
    assert len(results) == 2
    assert all(result.page_class is PageClass.DIGITAL for result in results)


def test_classify_pdf_marks_blank_page_scanned(tmp_path: Path) -> None:
    pdf_path = _blank_pdf(tmp_path / "blank.pdf")
    [result] = classify_pdf(pdf_path)
    assert result.page_class is PageClass.SCANNED
