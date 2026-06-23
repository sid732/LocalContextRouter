"""Tests for output text normalization."""

from localcontextrouter.text import clean_text


def test_strips_control_characters() -> None:
    # U+0002 is how some PDFs encode a discretionary hyphen.
    assert clean_text("observ\x02ability") == "observability"
    assert clean_text("a\x00b\x07c") == "abc"


def test_keeps_newlines_and_tabs() -> None:
    assert clean_text("a\tb\nc") == "a\tb\nc"


def test_normalizes_line_endings() -> None:
    assert clean_text("a\r\nb\rc") == "a\nb\nc"


def test_leaves_clean_text_untouched() -> None:
    text = "Revenue rose. Net income up.\nAll figures in USD."
    assert clean_text(text) == text


def test_preserves_unicode_punctuation() -> None:
    # Bullets and accents are not control characters and must survive.
    assert clean_text("• café") == "• café"
