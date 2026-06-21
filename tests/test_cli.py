"""Tests for the localctx command-line interface."""

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from localcontextrouter import __version__
from localcontextrouter.cli import build_report, main, render_report

PROSE = "Annual report. Revenue rose across every region this year. " * 3


def test_build_report_for_text_pdf(make_text_pdf: Callable[..., Path]) -> None:
    report = build_report(make_text_pdf(PROSE))
    assert report["page_count"] == 1
    pages = report["pages"]
    assert isinstance(pages, list)
    assert pages[0]["source"] == "text"
    assert isinstance(report["tokens_saved"], int)


def test_build_report_rejects_unsupported_type(tmp_path: Path) -> None:
    bad = tmp_path / "notes.txt"
    bad.write_text("hello")
    with pytest.raises(ValueError, match="unsupported file type"):
        build_report(bad)


def test_render_report_json_roundtrips(make_text_pdf: Callable[..., Path]) -> None:
    report = build_report(make_text_pdf(PROSE))
    assert json.loads(render_report(report, as_json=True)) == report


def test_render_report_human_mentions_savings(make_text_pdf: Callable[..., Path]) -> None:
    text = render_report(build_report(make_text_pdf(PROSE)), as_json=False)
    assert "Tokens saved" in text
    assert "Page 1 [text]" in text


def test_main_routes_and_prints(
    make_text_pdf: Callable[..., Path], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([str(make_text_pdf(PROSE)), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["pages"][0]["source"] == "text"


def test_main_missing_file_errors(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["/no/such/file.pdf"])
    assert exc.value.code != 0
    assert "no such file" in capsys.readouterr().err


def test_main_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out
