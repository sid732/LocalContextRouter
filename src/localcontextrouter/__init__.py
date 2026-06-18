"""LocalContextRouter — cheapest faithful path for documents bound for a multimodal LLM."""

from .classify import classify_text, compute_signals
from .models import (
    BoundingBox,
    Classification,
    OcrLine,
    PageClass,
    PageRoute,
    PageSignals,
    RouteResult,
    Source,
)
from .ocr import ocr_png_text, run_ocr
from .pdf import Pdf, classify_pdf
from .router import route_pdf

__version__ = "0.0.0"

__all__ = [
    "BoundingBox",
    "Classification",
    "OcrLine",
    "PageClass",
    "PageRoute",
    "PageSignals",
    "Pdf",
    "RouteResult",
    "Source",
    "classify_pdf",
    "classify_text",
    "compute_signals",
    "ocr_png_text",
    "route_pdf",
    "run_ocr",
    "__version__",
]
