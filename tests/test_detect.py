"""Tests for the vision-worthy page detector."""

from collections.abc import Callable
from pathlib import Path

from localcontextrouter.detect import is_vision_worthy
from localcontextrouter.models import PageFeatures
from localcontextrouter.pdf import Pdf


def _features(
    *,
    image_count: int = 0,
    image_coverage: float = 0.0,
    path_count: int = 0,
    path_coverage: float = 0.0,
) -> PageFeatures:
    return PageFeatures(
        width=600,
        height=800,
        image_count=image_count,
        image_coverage=image_coverage,
        path_count=path_count,
        path_coverage=path_coverage,
    )


def test_plain_page_is_not_vision_worthy() -> None:
    worthy, _ = is_vision_worthy(_features(path_count=3))
    assert worthy is False


def test_figure_heavy_page_is_vision_worthy() -> None:
    worthy, reason = is_vision_worthy(_features(image_count=1, image_coverage=0.6))
    assert worthy is True
    assert "image" in reason


def test_large_vector_chart_is_vision_worthy() -> None:
    worthy, reason = is_vision_worthy(_features(path_count=5, path_coverage=0.5))
    assert worthy is True
    assert "chart" in reason or "diagram" in reason


def test_many_paths_is_vision_worthy() -> None:
    worthy, reason = is_vision_worthy(_features(path_count=40))
    assert worthy is True
    assert "table" in reason or "diagram" in reason


def test_table_pdf_features_trip_detector(make_table_pdf: Callable[..., Path]) -> None:
    with Pdf(make_table_pdf()) as pdf:
        features = pdf.page_features(0)
    assert features.path_count >= 25
    assert is_vision_worthy(features)[0] is True


def test_prose_pdf_is_not_vision_worthy(make_text_pdf: Callable[..., Path]) -> None:
    with Pdf(make_text_pdf("Plain prose with several sentences of body text. " * 3)) as pdf:
        features = pdf.page_features(0)
    assert is_vision_worthy(features)[0] is False
