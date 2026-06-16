"""Smoke tests for the package surface."""

import re

import localcontextrouter


def test_version_is_pep440_string() -> None:
    assert isinstance(localcontextrouter.__version__, str)
    assert re.fullmatch(r"\d+\.\d+\.\d+", localcontextrouter.__version__)
