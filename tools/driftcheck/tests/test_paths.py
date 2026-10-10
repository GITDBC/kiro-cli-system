"""
Tests for repository-root discovery and the shared file helpers.

Discovery is marker-based precisely so that no test needs to know how
deep inside the package a module lives, so these tests assert the marker
contract rather than a parent depth.
"""

# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck.paths import contains_word, find_repo_root, is_repo_root, read_text


def test_is_repo_root_requires_every_marker(tmp_path: Path) -> None:
    """A directory with only one marker is not the root."""
    (tmp_path / ".kiro").mkdir()
    assert not is_repo_root(tmp_path)
    (tmp_path / "tools").mkdir()
    assert is_repo_root(tmp_path)


def test_find_repo_root_walks_up_from_a_nested_file(valid_root: Path) -> None:
    """Discovery works from any depth inside the tree."""
    nested = valid_root / "tools" / "driftcheck" / "driftcheck" / "checks"
    nested.mkdir(parents=True, exist_ok=True)
    deep_file = nested / "agents.py"
    deep_file.write_text("# deep\n", encoding="utf-8")
    assert find_repo_root(deep_file) == valid_root.resolve()


def test_find_repo_root_accepts_the_root_itself(valid_root: Path) -> None:
    """The starting directory itself may be the root."""
    assert find_repo_root(valid_root) == valid_root.resolve()


def test_find_repo_root_raises_outside_a_repository(tmp_path: Path) -> None:
    """No ancestor with both markers is a clear failure."""
    orphan = tmp_path / "elsewhere" / "deep"
    orphan.mkdir(parents=True)
    with pytest.raises(ValueError, match="cannot locate the repository root"):
        find_repo_root(orphan)


def test_find_repo_root_falls_back_to_the_working_directory(
    valid_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A non-editable install is rescued by the cwd search."""
    monkeypatch.setattr("driftcheck.paths.__file__", "/nonexistent/pkg/paths.py")
    monkeypatch.chdir(valid_root)
    assert find_repo_root() == valid_root.resolve()


def test_read_text_returns_empty_for_a_missing_file(tmp_path: Path) -> None:
    """A missing file reads as the empty string."""
    assert read_text(tmp_path / "absent.md") == ""


def test_read_text_tolerates_undecodable_bytes(tmp_path: Path) -> None:
    """Undecodable bytes are replaced rather than raising."""
    path = tmp_path / "binary.md"
    path.write_bytes(b"caf\xff\n")
    assert "caf" in read_text(path)


def test_contains_word_matches_hyphenated_neighbours() -> None:
    """Word matching mirrors grep -w, where hyphens are separators."""
    assert contains_word("senior-developer-patterns.md", "senior-developer")
    assert contains_word("use senior-developer here", "senior-developer")
    assert not contains_word("seniordeveloper", "senior-developer")
