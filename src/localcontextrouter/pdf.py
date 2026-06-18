"""Read PDFs and pull each page's embedded text layer using pypdfium2.

pypdfium2 is a permissively licensed binding to PDFium that ships its own native
library, so there is no system dependency (no poppler) to install alongside the
package.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pypdfium2 as pdfium

from .classify import classify_text
from .models import Classification


class Pdf:
    """A read-only handle over a PDF document.

    Use as a context manager so the native document is always released::

        with Pdf(path) as pdf:
            for text in pdf.page_texts():
                ...
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._doc = pdfium.PdfDocument(str(self.path))

    def __len__(self) -> int:
        return len(self._doc)

    def page_text(self, index: int) -> str:
        """Return the embedded text of the page at ``index``."""
        page = self._doc[index]
        textpage = page.get_textpage()
        try:
            return str(textpage.get_text_bounded())
        finally:
            textpage.close()
            page.close()

    def page_texts(self) -> Iterator[str]:
        """Yield the embedded text of every page in order."""
        for index in range(len(self)):
            yield self.page_text(index)

    def close(self) -> None:
        self._doc.close()

    def __enter__(self) -> Pdf:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def classify_pdf(path: str | Path) -> list[Classification]:
    """Classify every page of a PDF from its extracted text layer."""
    with Pdf(path) as pdf:
        return [classify_text(text) for text in pdf.page_texts()]
