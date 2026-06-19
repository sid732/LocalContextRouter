"""Estimate the token cost of a page as extracted text versus as an image.

The numbers are estimates that follow each provider's documented tokenization so
the router can report the savings of routing a page to text instead of vision.

- Claude tokenizes images in 28x28 pixel patches, downscaling so the long edge
  fits a cap (1568 px / 1568 tokens for most models; 2576 px / 4784 tokens for
  the high-resolution models).
- OpenAI's tile models bill a flat 85 tokens at ``detail="low"``; at ``"high"``
  they fit the image to 2048x2048, scale the short side to 768, and bill
  85 + 170 per 512x512 tile.
- Text is approximated at ~4 characters per token.
"""

from __future__ import annotations

import math

_PATCH = 28
_CLAUDE_MAX_TOKENS = 1568
_CLAUDE_MAX_EDGE = 1568
_CLAUDE_HIRES_MAX_TOKENS = 4784
_CLAUDE_HIRES_MAX_EDGE = 2576

_CHARS_PER_TOKEN = 4


def estimate_text_tokens(text: str) -> int:
    """Estimate tokens for a block of text (~4 characters per token)."""
    return math.ceil(len(text) / _CHARS_PER_TOKEN)


def _fit_long_edge(width: float, height: float, max_edge: int) -> tuple[float, float]:
    long_edge = max(width, height)
    if long_edge <= max_edge:
        return width, height
    scale = max_edge / long_edge
    return width * scale, height * scale


def claude_image_tokens(width: float, height: float, *, high_res: bool = False) -> int:
    """Estimate Claude image tokens for an image of the given pixel size."""
    if width <= 0 or height <= 0:
        return 0
    max_edge = _CLAUDE_HIRES_MAX_EDGE if high_res else _CLAUDE_MAX_EDGE
    cap = _CLAUDE_HIRES_MAX_TOKENS if high_res else _CLAUDE_MAX_TOKENS
    fitted_w, fitted_h = _fit_long_edge(width, height, max_edge)
    patches = math.ceil(fitted_w / _PATCH) * math.ceil(fitted_h / _PATCH)
    return min(patches, cap)


def openai_image_tokens(width: float, height: float, *, detail: str = "high") -> int:
    """Estimate OpenAI tile-model image tokens (GPT-4o / GPT-4.1 family)."""
    if detail == "low":
        return 85
    if width <= 0 or height <= 0:
        return 0
    # Fit within 2048x2048, then scale the shortest side to 768.
    fitted_w, fitted_h = _fit_long_edge(width, height, 2048)
    short_edge = min(fitted_w, fitted_h)
    if short_edge > 768:
        scale = 768 / short_edge
        fitted_w, fitted_h = fitted_w * scale, fitted_h * scale
    tiles = math.ceil(fitted_w / 512) * math.ceil(fitted_h / 512)
    return 85 + 170 * tiles
