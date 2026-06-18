"""Bridge to the on-device ``lcr-ocr`` binary.

The Swift binary does the actual recognition (Apple Vision); this module finds
it, invokes it, and parses its JSON output into :class:`~.models.OcrLine`.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .models import BoundingBox, OcrLine

#: Environment variable that, if set, overrides where the binary is found.
BINARY_ENV_VAR = "LCR_OCR_BIN"

_BINARY_NAME = "lcr-ocr"
# Dev fallback: the binary built from the bundled Swift package in this repo.
_DEV_BINARY = Path(__file__).resolve().parents[2] / "ocr" / ".build" / "release" / _BINARY_NAME


class OcrBinaryNotFound(RuntimeError):
    """Raised when the ``lcr-ocr`` binary cannot be located."""


class OcrError(RuntimeError):
    """Raised when the ``lcr-ocr`` binary exits with an error."""


def locate_binary() -> Path:
    """Locate the ``lcr-ocr`` binary.

    Resolution order: the ``LCR_OCR_BIN`` environment variable, then ``PATH``,
    then the binary built from the bundled Swift package.
    """
    override = os.environ.get(BINARY_ENV_VAR)
    if override:
        path = Path(override)
        if not path.exists():
            raise OcrBinaryNotFound(f"{BINARY_ENV_VAR} points to a missing file: {path}")
        return path

    on_path = shutil.which(_BINARY_NAME)
    if on_path:
        return Path(on_path)

    if _DEV_BINARY.exists():
        return _DEV_BINARY

    raise OcrBinaryNotFound(
        f"could not find '{_BINARY_NAME}'. Build it with 'swift build -c release' in "
        f"the ocr/ directory, or set {BINARY_ENV_VAR} to its path."
    )


def parse_ocr_lines(payload: str) -> list[OcrLine]:
    """Parse the binary's ``--json`` output into :class:`OcrLine` objects."""
    return [
        OcrLine(
            text=item["text"],
            confidence=float(item["confidence"]),
            bounding_box=BoundingBox(
                x=float(item["boundingBox"]["x"]),
                y=float(item["boundingBox"]["y"]),
                width=float(item["boundingBox"]["width"]),
                height=float(item["boundingBox"]["height"]),
            ),
        )
        for item in json.loads(payload)
    ]


def run_ocr(
    image_path: str | Path,
    *,
    fast: bool = False,
    languages: list[str] | None = None,
    correction: bool = True,
) -> list[OcrLine]:
    """Run the binary on an image file and return the recognized lines."""
    args = [str(locate_binary()), str(image_path), "--json"]
    if fast:
        args.append("--fast")
    if not correction:
        args.append("--no-correction")
    if languages:
        args += ["--lang", ",".join(languages)]

    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise OcrError(f"lcr-ocr exited with {result.returncode}: {result.stderr.strip()}")
    return parse_ocr_lines(result.stdout)


def ocr_png_text(
    png: bytes,
    *,
    fast: bool = False,
    languages: list[str] | None = None,
    correction: bool = True,
    min_confidence: float = 0.0,
) -> str:
    """OCR a PNG given as bytes; return the recognized lines joined by newlines.

    Lines below ``min_confidence`` are dropped — useful for filtering the
    low-confidence glyphs that icons and logos tend to produce.
    """
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        tmp.write(png)
        tmp.flush()
        lines = run_ocr(tmp.name, fast=fast, languages=languages, correction=correction)
    return "\n".join(line.text for line in lines if line.confidence >= min_confidence)
