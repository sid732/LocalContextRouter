"""LocalContextRouter — cheapest faithful path for documents bound for a multimodal LLM."""

from .classify import classify_text, compute_signals
from .detect import is_vision_worthy
from .models import (
    BoundingBox,
    Classification,
    OcrLine,
    PageClass,
    PageFeatures,
    PageRoute,
    PageSignals,
    RouteResult,
    Source,
    TokenEstimate,
)
from .ocr import ocr_png_text, run_ocr
from .pdf import Pdf, classify_pdf
from .router import route_pdf
from .tokens import (
    claude_image_tokens,
    estimate_text_tokens,
    openai_image_tokens,
)

__version__ = "0.0.0"

__all__ = [
    "BoundingBox",
    "Classification",
    "OcrLine",
    "PageClass",
    "PageFeatures",
    "PageRoute",
    "PageSignals",
    "Pdf",
    "RouteResult",
    "Source",
    "TokenEstimate",
    "claude_image_tokens",
    "classify_pdf",
    "classify_text",
    "compute_signals",
    "estimate_text_tokens",
    "is_vision_worthy",
    "ocr_png_text",
    "openai_image_tokens",
    "route_pdf",
    "run_ocr",
    "__version__",
]
