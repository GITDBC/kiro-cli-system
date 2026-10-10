"""Tests for the driftcheck command-line entry point."""

# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck import cli
from driftcheck.cli import main
from tests.helpers import write_agent


def test_main_validates_an_arbitrary_root(
    valid_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The --root flag validates a tree outside this repository."""
    assert main(["--root", str(valid_root)]) == 0
    assert "PASS: All checks green." in capsys.readouterr().out


def test_main_fails_on_a_broken_root(
    valid_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A tree with a governance violation exits non-zero."""
    write_agent(valid_root, "senior-developer", model="auto")
    assert main(["--root", str(valid_root)]) == 1
    assert "FAIL: Fix errors before proceeding." in capsys.readouterr().out


def test_main_reports_undiscoverable_root(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A failed root discovery exits 1 with an explanation."""

    def explode() -> Path:
        message = "cannot locate the repository root"
        raise ValueError(message)

    monkeypatch.setattr(cli, "find_repo_root", explode)
    assert main([]) == 1
    assert "cannot locate the repository root" in capsys.readouterr().err


def test_main_discovers_the_enclosing_repository(
    monkeypatch: pytest.MonkeyPatch,
    valid_root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Without --root the enclosing repository is validated."""
    monkeypatch.setattr(cli, "find_repo_root", lambda: valid_root)
    assert main([]) == 0
    assert "PASS: All checks green." in capsys.readouterr().out
