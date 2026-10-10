"""
Tests for the orphan pruning shared by the enumerating sources.

The helper touches only the filesystem, so these tests need no network
seam at all: they build a mirror directory and assert on what survives.
"""

# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from docsync.orphans import prune_orphans
from docsync.types import MirrorPaths


@pytest.fixture()
def paths(tmp_path: Path) -> MirrorPaths:
    """
    Build mirror locations inside a temporary tree.

    Args:
        tmp_path: Pytest-provided temporary directory.

    Returns:
        Mirror locations under the temporary tree.
    """
    return MirrorPaths(
        refs_dir=tmp_path / "references",
        marker_path=tmp_path / ".last-sync.json",
    )


def test_prune_orphans_reports_without_deleting(
    paths: MirrorPaths, capsys: pytest.CaptureFixture[str]
) -> None:
    """A dry prune leaves the orphan on disk and names it."""
    orphan = paths.refs_dir / "removed.md"
    orphan.parent.mkdir(parents=True)
    orphan.write_text("# Removed\n", encoding="utf-8")
    assert prune_orphans(paths, {"hooks"}, dry_run=True) == 1
    assert orphan.is_file()
    expected = "  - ORPHAN: removed.md (would remove with --prune)"
    assert expected in capsys.readouterr().out


def test_prune_orphans_deletes_when_asked(
    paths: MirrorPaths, capsys: pytest.CaptureFixture[str]
) -> None:
    """A real prune removes files the source no longer publishes."""
    orphan = paths.refs_dir / "nested" / "removed.md"
    orphan.parent.mkdir(parents=True)
    orphan.write_text("# Removed\n", encoding="utf-8")
    assert prune_orphans(paths, {"hooks"}, dry_run=False) == 1
    assert not orphan.exists()
    assert "  - PRUNED: nested/removed.md" in capsys.readouterr().out


def test_prune_orphans_keeps_a_known_slug(paths: MirrorPaths) -> None:
    """A page the run discovered is never mistaken for an orphan."""
    kept = paths.refs_dir / "nested" / "kept.md"
    kept.parent.mkdir(parents=True)
    kept.write_text("# Kept\n", encoding="utf-8")
    assert prune_orphans(paths, {"nested/kept"}, dry_run=False) == 0
    assert kept.is_file()


def test_prune_orphans_tolerates_a_missing_mirror(paths: MirrorPaths) -> None:
    """No mirror directory means no orphans."""
    assert prune_orphans(paths, set(), dry_run=True) == 0
