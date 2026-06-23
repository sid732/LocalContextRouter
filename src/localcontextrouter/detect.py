"""Decide whether a page should go to a vision model rather than as text.

Some pages carry a perfectly good text layer yet still lose their meaning when
flattened to text: tables, charts, diagrams, and figure-heavy layouts. Those are
worth the vision-token cost. This module decides that from cheap layout features
(:class:`~.models.PageFeatures`), no rendering and no ML.
"""

from __future__ import annotations

from .models import PageFeatures

#: A page with at least this many vector paths is treated as a table or diagram.
#: Charts and ruled tables emit many line/curve objects.
MIN_VISION_PATHS = 25

#: A page with at least this fraction covered by raster images is figure-heavy.
MIN_VISION_IMAGE_COVERAGE = 0.40

#: A page with at least this fraction covered by vector paths holds a large
#: filled chart or diagram.
MIN_VISION_PATH_COVERAGE = 0.30


def is_vision_worthy(features: PageFeatures) -> tuple[bool, str]:
    """Return whether a page should go to a vision model, with the reason."""
    if features.image_coverage >= MIN_VISION_IMAGE_COVERAGE:
        return True, (
            f"{features.image_coverage:.0%} image coverage "
            f"(>= {MIN_VISION_IMAGE_COVERAGE:.0%}); figure-heavy"
        )
    if features.path_coverage >= MIN_VISION_PATH_COVERAGE:
        return True, (
            f"{features.path_coverage:.0%} vector coverage "
            f"(>= {MIN_VISION_PATH_COVERAGE:.0%}); large chart or diagram"
        )
    if features.path_count >= MIN_VISION_PATHS:
        return True, f"{features.path_count} vector paths (>= {MIN_VISION_PATHS}); table or diagram"
    return False, "no dominant visual structure; text is faithful"
