"""Read PDFs and pull each page's embedded text layer using pypdfium2.

pypdfium2 is a permissively licensed binding to PDFium that ships its own native
library, so there is no system dependency (no poppler) to install alongside the
package.
"""

from __future__ import annotations

import io
from collections.abc import Iterator
from pathlib import Path

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c

from .classify import classify_text
from .models import Classification, PageFeatures


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

    def page_features(self, index: int) -> PageFeatures:
        """Summarize the page's image and vector-path content for routing.

        Counts raster image and vector path objects and the fraction of the page
        each covers. Charts and diagrams emit many vector paths rather than raster
        images, so the path signals catch content that an image count misses.
        """
        page = self._doc[index]
        try:
            width, height = page.get_size()
            page_area = width * height
            image_count = path_count = 0
            image_area = path_area = 0.0
            for obj in page.get_objects():
                left, bottom, right, top = obj.get_bounds()
                area = abs((right - left) * (top - bottom))
                if obj.type == pdfium_c.FPDF_PAGEOBJ_IMAGE:
                    image_count += 1
                    image_area += area
                elif obj.type == pdfium_c.FPDF_PAGEOBJ_PATH:
                    path_count += 1
                    path_area += area
            return PageFeatures(
                width=width,
                height=height,
                image_count=image_count,
                image_coverage=image_area / page_area if page_area else 0.0,
                path_count=path_count,
                path_coverage=path_area / page_area if page_area else 0.0,
            )
        finally:
            page.close()

    def render_page_png(self, index: int, scale: float = 2.0) -> bytes:
        """Render the page at ``index`` to PNG bytes.

        ``scale`` multiplies the native size (2.0 ~= 144 DPI), trading speed for
        OCR accuracy on small text. Used to feed image-only pages to OCR.
        """
        page = self._doc[index]
        bitmap = page.render(scale=scale)
        try:
            buffer = io.BytesIO()
            bitmap.to_pil().save(buffer, format="PNG")
            return buffer.getvalue()
        finally:
            bitmap.close()
            page.close()

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
