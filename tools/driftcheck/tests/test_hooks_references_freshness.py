"""Tests for the documentation freshness hook."""

# Standard libraries
import io
import json
import os
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck.hooks import references_freshness
from tests.helpers import write

MIRROR = Path(".kiro") / "skills" / "kiro-cli-reference"


def marker(root: Path, age_days: int) -> Path:
    """
    Write a sync marker with a chosen age.

    Args:
        root: Repository root.
        age_days: How long ago the sync happened.

    Returns:
        Path to the written marker.
    """
    timestamp = (datetime.now(tz=UTC) - timedelta(days=age_days)).isoformat()
    return write(
        root / MIRROR / ".last-sync.json",
        json.dumps({"timestamp": timestamp}) + "\n",
    )


def test_fresh_docs_print_nothing(
    valid_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A recent sync produces no output at all."""
    marker(valid_root, age_days=1)
    monkeypatch.setattr(references_freshness, "find_repo_root", lambda: valid_root)
    references_freshness.run()
    assert capsys.readouterr().out == ""


def test_stale_docs_print_a_reminder(
    valid_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A sync older than the threshold prints a reminder."""
    marker(valid_root, age_days=30)
    monkeypatch.setattr(references_freshness, "find_repo_root", lambda: valid_root)
    references_freshness.run()
    output = capsys.readouterr().out
    assert "Docs may be outdated" in output
    assert "30 day(s) ago" in output


def test_unknown_age_prints_the_unknown_notice(
    valid_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No marker and no reference files means unknown freshness."""
    monkeypatch.setattr(references_freshness, "find_repo_root", lambda: valid_root)
    references_freshness.run()
    assert "Doc freshness unknown" in capsys.readouterr().out


def test_mtime_fallback_when_the_marker_is_unusable(
    valid_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A corrupt marker falls back to the newest reference mtime."""
    write(valid_root / MIRROR / ".last-sync.json", "{not json")
    reference = write(valid_root / MIRROR / "references" / "chat.md", "# Chat\n")
    stale = time.time() - timedelta(days=30).total_seconds()
    os.utime(reference, (stale, stale))
    monkeypatch.setattr(references_freshness, "find_repo_root", lambda: valid_root)
    references_freshness.run()
    assert "Docs may be outdated" in capsys.readouterr().out


def test_compute_doc_age_prefers_the_marker(valid_root: Path) -> None:
    """The marker wins over file mtimes when both exist."""
    marker(valid_root, age_days=3)
    write(valid_root / MIRROR / "references" / "chat.md", "# Chat\n")
    age = references_freshness.compute_doc_age(valid_root / MIRROR)
    assert age is not None
    assert timedelta(days=2) < age < timedelta(days=4)


def test_main_degrades_without_a_repository_root(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """An undiscoverable root warns and exits 0."""

    def explode() -> Path:
        message = "cannot locate the repository root"
        raise ValueError(message)

    monkeypatch.setattr("sys.stdin", io.StringIO("{}"))
    monkeypatch.setattr(references_freshness, "find_repo_root", explode)
    assert references_freshness.main() == 0
    assert "doc freshness check skipped" in capsys.readouterr().err


def test_main_exits_zero_when_stdin_is_closed(
    valid_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unreadable stdin never breaks agent spawn."""

    class Closed(io.StringIO):
        """A stream that refuses to be read."""

        def read(self, size: int | None = -1) -> str:
            message = "stdin is closed"
            raise OSError(message)

    marker(valid_root, age_days=1)
    monkeypatch.setattr("sys.stdin", Closed())
    monkeypatch.setattr(references_freshness, "find_repo_root", lambda: valid_root)
    assert references_freshness.main() == 0
