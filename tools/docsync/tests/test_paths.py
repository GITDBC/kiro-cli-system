"""Tests for repository-root discovery."""

# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from docsync.paths import find_repo_root


def test_find_repo_root_walks_up_to_the_markers(tmp_path: Path) -> None:
    """Discovery returns the nearest ancestor with .kiro/ and tools/."""
    root = tmp_path / "repo"
    (root / ".kiro").mkdir(parents=True)
    package = root / "tools" / "docsync" / "docsync"
    package.mkdir(parents=True)
    deep = package / "sync.py"
    deep.write_text("# deep\n", encoding="utf-8")
    assert find_repo_root(deep) == root.resolve()


def test_find_repo_root_raises_outside_a_repository(tmp_path: Path) -> None:
    """A tree without the markers is a clear failure."""
    with pytest.raises(ValueError, match="cannot locate the repository root"):
        find_repo_root(tmp_path)
