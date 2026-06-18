"""Tests for the page text classifier."""

from localcontextrouter import PageClass, classify_text
from localcontextrouter.classify import MIN_TEXT_CHARS

PROSE = (
    "The quarterly report summarizes revenue, expenses, and net income for the "
    "period ending in March. All figures are stated in thousands of US dollars."
)


def test_prose_is_digital() -> None:
    result = classify_text(PROSE)
    assert result.page_class is PageClass.DIGITAL
    assert result.signals.char_count > MIN_TEXT_CHARS


def test_empty_is_scanned() -> None:
    result = classify_text("")
    assert result.page_class is PageClass.SCANNED
    assert result.signals.char_count == 0


def test_whitespace_only_is_scanned() -> None:
    assert classify_text("   \n\t  \n ").page_class is PageClass.SCANNED


def test_short_text_is_scanned() -> None:
    # A few stray characters from a scan are not a real text layer.
    assert classify_text("page 1").page_class is PageClass.SCANNED


def test_cid_artifacts_are_garbled() -> None:
    text = "Heading " + "(cid:12)(cid:7)(cid:99) " * 10 + "more body text here"
    result = classify_text(text)
    assert result.page_class is PageClass.GARBLED
    assert result.signals.cid_token_count >= 3


def test_one_cid_artifact_is_not_garbled() -> None:
    # A lone artifact in otherwise-clean prose should not force OCR.
    result = classify_text(PROSE + " (cid:5)")
    assert result.page_class is PageClass.DIGITAL


def test_replacement_characters_are_garbled() -> None:
    text = "Important text " + "�" * 40
    result = classify_text(text)
    assert result.page_class is PageClass.GARBLED
    assert result.signals.replacement_ratio > 0.10


def test_mostly_nonprintable_is_garbled() -> None:
    text = "ok " + "\x00\x01\x02\x03\x04\x05" * 20
    result = classify_text(text)
    assert result.page_class is PageClass.GARBLED
    assert result.signals.printable_ratio < 0.80


def test_signals_count_non_whitespace_only() -> None:
    signals = classify_text("ab cd\nef").signals
    assert signals.char_count == 6


def test_reason_is_populated() -> None:
    assert classify_text(PROSE).reason
    assert classify_text("").reason
