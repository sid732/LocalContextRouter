"""Tests for the lcr-ocr bridge."""

from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from localcontextrouter.ocr import (
    BINARY_ENV_VAR,
    OcrBinaryNotFound,
    locate_binary,
    parse_ocr_lines,
    run_ocr,
)

SAMPLE_JSON = (
    '[{"text":"Hello","confidence":0.9,"boundingBox":{"x":0.1,"y":0.2,"width":0.3,"height":0.4}}]'
)


def test_parse_ocr_lines() -> None:
    [line] = parse_ocr_lines(SAMPLE_JSON)
    assert line.text == "Hello"
    assert line.confidence == pytest.approx(0.9)
    assert line.bounding_box.x == pytest.approx(0.1)
    assert line.bounding_box.height == pytest.approx(0.4)


def test_parse_empty_payload() -> None:
    assert parse_ocr_lines("[]") == []


def test_locate_binary_env_pointing_at_missing_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv(BINARY_ENV_VAR, str(tmp_path / "nope"))
    with pytest.raises(OcrBinaryNotFound):
        locate_binary()


def test_locate_binary_prefers_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake = tmp_path / "lcr-ocr"
    fake.write_text("#!/bin/sh\n")
    monkeypatch.setenv(BINARY_ENV_VAR, str(fake))
    assert locate_binary() == fake


@pytest.mark.integration
def test_run_ocr_reads_text(lcr_binary: Path, tmp_path: Path) -> None:
    image = Image.new("RGB", (700, 180), "white")
    draw = ImageDraw.Draw(image)
    draw.text((20, 70), "HELLO OCR", fill="black", font=ImageFont.load_default(size=52))
    path = tmp_path / "image.png"
    image.save(path)

    lines = run_ocr(path)
    transcript = " ".join(line.text for line in lines).upper()
    assert "HELLO OCR" in transcript
