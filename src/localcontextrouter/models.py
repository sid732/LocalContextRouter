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
    """Where a page's final content should come from."""

    TEXT = "text"
    """Extracted directly from the embedded text layer."""

    OCR = "ocr"
    """Produced by on-device OCR after rendering the page."""

    VISION = "vision"
    """Send the page to a vision model — its meaning lives in the visuals."""


@dataclass(frozen=True)
class PageFeatures:
    """Layout signals for a page, derived from its content objects."""

    width: float
    """Page width in PDF points."""

    height: float
    """Page height in PDF points."""

    image_count: int
    """Number of raster image objects on the page."""

    image_coverage: float
    """Fraction of the page area covered by raster images, in 0...1."""

    path_count: int
    """Number of vector path objects (lines, curves, fills)."""

    path_coverage: float
    """Fraction of the page area covered by vector paths, in 0...1."""


@dataclass(frozen=True)
class TokenEstimate:
    """Estimated token cost of a page as extracted text versus as an image."""

    text_tokens: int
    image_tokens: int

    @property
    def saved(self) -> int:
        """Tokens avoided by sending text instead of the page image (never negative)."""
        return max(0, self.image_tokens - self.text_tokens)


@dataclass(frozen=True)
class PageRoute:
    """The routing outcome for one page."""

    index: int
    classification: Classification
    source: Source
    text: str
    tokens: TokenEstimate


@dataclass(frozen=True)
class RouteResult:
    """The routing outcome for a whole document."""

    pages: list[PageRoute]

    @property
    def text(self) -> str:
        """All page text joined in reading order."""
        return "\n\n".join(page.text for page in self.pages)

    @property
    def tokens_saved(self) -> int:
        """Total tokens avoided versus sending every page as an image.

        Counts only pages routed to text or OCR; vision pages are sent as
        images, so they save nothing.
        """
        return sum(page.tokens.saved for page in self.pages if page.source is not Source.VISION)
