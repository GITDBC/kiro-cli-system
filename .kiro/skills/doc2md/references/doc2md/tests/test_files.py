"""Tests for input file collection."""

# Standard libraries
from pathlib import Path
from unittest.mock import patch

# 3pps
import pytest

# Own modules
from doc2md.files import _check_size, _deduplicate, collect_files


def test_collect_files_single_file(tmp_path: Path) -> None:
    """
    Verify collect_files returns a single file when
    given a direct file path.
    """

    f = tmp_path / "a.txt"
    f.write_text("x")
    result = collect_files([str(f)])
    assert result == [f]


def test_collect_files_directory(tmp_path: Path) -> None:
    """
    Verify collect_files discovers all files inside
    a directory.
    """

    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "b.txt").write_text("y")
    result = collect_files([str(tmp_path)])
    assert len(result) == 2


def test_collect_files_nonexistent(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Verify collect_files logs a warning for
    nonexistent paths.
    """

    result = collect_files([str(tmp_path / "nope")])
    assert result == []
    assert "does not exist" in caplog.text


def test_collect_files_exclude(tmp_path: Path) -> None:
    """
    Verify collect_files respects glob-based exclude
    patterns.
    """

    (tmp_path / "keep.txt").write_text("x")
    (tmp_path / "drop.log").write_text("y")
    result = collect_files([str(tmp_path)], exclude=["*.log"])
    assert len(result) == 1
    assert result[0].name == "keep.txt"


def test_deduplicate_preserves_order() -> None:
    """
    Verify _deduplicate removes duplicates while
    preserving insertion order.
    """

    a, b, c = Path("/a"), Path("/b"), Path("/c")
    assert _deduplicate([a, b, a, c, b]) == [a, b, c]


def test_check_size_oversized(tmp_path: Path) -> None:
    """
    Verify _check_size rejects files exceeding
    MAX_FILE_SIZE.
    """

    f = tmp_path / "big.bin"
    f.write_bytes(b"x" * 20)
    with patch("doc2md.files.MAX_FILE_SIZE", 10):
        assert _check_size(f) is False


def test_check_size_oserror(tmp_path: Path) -> None:
    """
    Verify _check_size returns False when stat raises
    OSError.
    """

    f = tmp_path / "gone.txt"
    f.write_text("x")
    with patch.object(Path, "stat", side_effect=OSError("boom")):
        assert _check_size(f) is False
