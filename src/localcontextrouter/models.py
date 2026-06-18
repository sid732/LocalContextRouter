"""Core data types for page classification and routing."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PageClass(str, Enum):
    """How a PDF page should be sourced before it reaches an LLM."""

    DIGITAL = "digital"
    """A usable embedded text layer is present — extract the text directly."""

    SCANNED = "scanned"
    """Little or no text layer — the page is image-only and needs OCR."""

    GARBLED = "garbled"
    """A text layer exists but is broken (unmapped glyphs) — OCR is safer."""


@dataclass(frozen=True)
class PageSignals:
    """Cheap signals derived from a page's extracted text."""

    char_count: int
    """Number of non-whitespace characters in the extracted text."""

    printable_ratio: float
    """Share of characters that are printable (or standard whitespace), in 0...1."""

    replacement_ratio: float
    """Share of U+FFFD replacement characters, in 0...1."""

    cid_token_count: int
    """Count of ``(cid:NNN)`` artifacts left by a broken font-to-Unicode map."""


@dataclass(frozen=True)
class Classification:
    """The verdict for a single page together with the signals behind it."""

    page_class: PageClass
    signals: PageSignals
    reason: str


@dataclass(frozen=True)
class BoundingBox:
    """A normalized box with a top-left origin; all values are fractions in 0...1."""

    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class OcrLine:
    """A single line recognized by the OCR binary."""

    text: str
    confidence: float
    bounding_box: BoundingBox


class Source(str, Enum):
    """Where a page's final text came from."""

    TEXT = "text"
    """Extracted directly from the embedded text layer."""

    OCR = "ocr"
    """Produced by on-device OCR after rendering the page."""


@dataclass(frozen=True)
class PageRoute:
    """The routing outcome for one page: its classification, source, and text."""

    index: int
    classification: Classification
    source: Source
    text: str


@dataclass(frozen=True)
class RouteResult:
    """The routing outcome for a whole document."""

    pages: list[PageRoute]

    @property
    def text(self) -> str:
        """All page text joined in reading order."""
        return "\n\n".join(page.text for page in self.pages)
