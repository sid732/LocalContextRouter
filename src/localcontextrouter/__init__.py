"""LocalContextRouter — cheapest faithful path for documents bound for a multimodal LLM."""

from .classify import classify_text, compute_signals
from .models import Classification, PageClass, PageSignals

__version__ = "0.0.0"

__all__ = [
    "Classification",
    "PageClass",
    "PageSignals",
    "classify_text",
    "compute_signals",
    "__version__",
]
