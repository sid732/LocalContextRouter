"""Text normalization for routed output.

Applied to the text a page contributes to the model, not before
classification, which relies on seeing control and replacement characters to
spot a broken text layer.
"""

from __future__ import annotations

import unicodedata

_KEEP = {"\n", "\t"}


def clean_text(text: str) -> str:
    """Normalize line endings and drop stray control characters.

    PDFs sometimes encode discretionary hyphens and other artifacts as control
    characters (e.g. U+0002), which would otherwise leak into the model's input.
    Newlines and tabs are preserved; CR and CRLF collapse to ``\\n``.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "".join(char for char in text if char in _KEEP or unicodedata.category(char) != "Cc")
