"""Classify a PDF page from its extracted text.

The classifier is a pure function over a page's extracted text. It decides
whether the text layer is usable (:class:`PageClass.DIGITAL`), effectively
absent (:class:`PageClass.SCANNED`), or present but broken
(:class:`PageClass.GARBLED`). The two latter cases route to OCR downstream.

Thresholds are deliberately conservative — when in doubt the page is sent to
OCR, since a wrong "digital" verdict silently feeds garbage to the model.
"""

from __future__ import annotations

import re

from .models import Classification, PageClass, PageSignals

#: Minimum non-whitespace characters for a page to count as having a text layer.
MIN_TEXT_CHARS = 50

#: Above this share of U+FFFD replacement characters the text layer is unreliable.
MAX_REPLACEMENT_RATIO = 0.10

#: Below this share of printable characters the extraction is treated as garbage.
MIN_PRINTABLE_RATIO = 0.80

#: At or above this many ``(cid:NNN)`` artifacts the font mapping is considered broken.
MIN_CID_TOKENS = 3

_CID_RE = re.compile(r"\(cid:\d+\)")
_REPLACEMENT_CHAR = "�"
_WHITESPACE = "\t\n\r\f\v "


def _is_printable(char: str) -> bool:
    return char.isprintable() or char in _WHITESPACE


def compute_signals(text: str) -> PageSignals:
    """Compute the cheap text signals used to classify a page."""
    if not text:
        return PageSignals(
            char_count=0,
            printable_ratio=1.0,
            replacement_ratio=0.0,
            cid_token_count=0,
        )

    char_count = sum(1 for char in text if not char.isspace())
    printable = sum(1 for char in text if _is_printable(char))
    return PageSignals(
        char_count=char_count,
        printable_ratio=printable / len(text),
        replacement_ratio=text.count(_REPLACEMENT_CHAR) / len(text),
        cid_token_count=len(_CID_RE.findall(text)),
    )


def classify_text(text: str) -> Classification:
    """Classify a page given its extracted text."""
    signals = compute_signals(text)

    if signals.char_count < MIN_TEXT_CHARS:
        return Classification(
            PageClass.SCANNED,
            signals,
            f"only {signals.char_count} text chars (< {MIN_TEXT_CHARS}); likely image-only",
        )

    if signals.cid_token_count >= MIN_CID_TOKENS:
        return Classification(
            PageClass.GARBLED,
            signals,
            f"{signals.cid_token_count} (cid:) artifacts; font-to-Unicode map broken",
        )

    if signals.replacement_ratio > MAX_REPLACEMENT_RATIO:
        return Classification(
            PageClass.GARBLED,
            signals,
            f"{signals.replacement_ratio:.0%} replacement characters "
            f"(> {MAX_REPLACEMENT_RATIO:.0%})",
        )

    if signals.printable_ratio < MIN_PRINTABLE_RATIO:
        return Classification(
            PageClass.GARBLED,
            signals,
            f"only {signals.printable_ratio:.0%} printable characters "
            f"(< {MIN_PRINTABLE_RATIO:.0%})",
        )

    return Classification(PageClass.DIGITAL, signals, "usable embedded text layer")
