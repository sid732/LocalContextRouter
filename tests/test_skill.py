"""Tests for the local-context-router Agent Skill."""

import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "local-context-router"
SKILL_MD = SKILL_DIR / "SKILL.md"
PREFLIGHT = SKILL_DIR / "scripts" / "preflight.py"


def _frontmatter(markdown: str) -> str:
    assert markdown.startswith("---\n"), "SKILL.md must open with YAML frontmatter"
    end = markdown.index("\n---", 4)
    return markdown[4:end]


def test_skill_files_exist() -> None:
    assert SKILL_MD.is_file()
    assert PREFLIGHT.is_file()


def test_frontmatter_name_matches_directory() -> None:
    front = _frontmatter(SKILL_MD.read_text())
    assert "name: local-context-router" in front
    assert SKILL_DIR.name == "local-context-router"


def test_frontmatter_description_is_present_and_bounded() -> None:
    front = _frontmatter(SKILL_MD.read_text())
    description = front.split("description:", 1)[1]
    assert len(description) < 1024
    for keyword in ("PDF", "OCR", "vision"):
        assert keyword in description


def test_preflight_runs_on_text_pdf(make_text_pdf: Callable[..., Path]) -> None:
    pdf = make_text_pdf("Annual report. Revenue rose across every region this year. " * 3)
    completed = subprocess.run(
        [sys.executable, str(PREFLIGHT), str(pdf), "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(completed.stdout)
    assert report["page_count"] == 1
    page = report["pages"][0]
    assert page["source"] == "text"
    assert "revenue" in page["text"].lower()
    assert isinstance(report["tokens_saved"], int)


def test_preflight_rejects_unsupported_type(tmp_path: Path) -> None:
    bad = tmp_path / "notes.txt"
    bad.write_text("hello")
    completed = subprocess.run(
        [sys.executable, str(PREFLIGHT), str(bad)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
    assert "unsupported file type" in completed.stderr
