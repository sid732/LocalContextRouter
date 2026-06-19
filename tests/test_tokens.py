"""Tests for token estimation, checked against documented provider examples."""

from localcontextrouter.tokens import (
    claude_image_tokens,
    estimate_text_tokens,
    openai_image_tokens,
)


def test_estimate_text_tokens() -> None:
    assert estimate_text_tokens("") == 0
    assert estimate_text_tokens("abcd") == 1
    assert estimate_text_tokens("abcde") == 2


def test_claude_tokens_match_documented_patch_counts() -> None:
    # 28x28 patches: ceil(w/28) * ceil(h/28).
    assert claude_image_tokens(1000, 1000) == 1296
    assert claude_image_tokens(1092, 1092) == 1521


def test_claude_tokens_capped_for_large_images() -> None:
    assert claude_image_tokens(4000, 4000) == 1568
    assert claude_image_tokens(8000, 8000, high_res=True) == 4784


def test_claude_high_res_three_megapixel_page() -> None:
    # 2000x1500 fits under the 2576 px high-res edge, so no downscale.
    assert claude_image_tokens(2000, 1500, high_res=True) == 3888


def test_claude_tokens_zero_for_empty() -> None:
    assert claude_image_tokens(0, 100) == 0


def test_openai_low_detail_is_flat() -> None:
    assert openai_image_tokens(4000, 4000, detail="low") == 85


def test_openai_high_detail_match_documented_examples() -> None:
    assert openai_image_tokens(1024, 1024) == 765
    assert openai_image_tokens(2048, 4096) == 1105
