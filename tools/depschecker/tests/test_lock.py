# Standard libraries
import tomllib
from pathlib import Path

# 3pps
import pytest

# Own modules
from depschecker.lock import parse_lock

LOCK: str = """
version = 1
requires-python = ">=3.11"

[[package]]
name = "requests"
version = "2.33.1"
source = { registry = "https://pypi.org/simple" }

[[package]]
name = "urllib3"
version = "2.6.3"
source = { registry = "https://pypi.org/simple" }

[[package]]
name = "types_Requests"
version = "2.33.0.20260408"
source = { registry = "https://pypi.org/simple" }

[[package]]
name = "work-depschecker"
version = "0.3.1"
source = { editable = "." }

[[package]]
name = "some-virtual"
version = "1.0.0"
source = { virtual = "." }

[[package]]
name = "no-version"
source = { registry = "https://pypi.org/simple" }
"""


def _write(tmp_path: Path, text: str) -> Path:
    """
    Write a lockfile into the temporary directory.

    Args:
        tmp_path: Pytest temporary directory.
        text: Lockfile contents.

    Returns:
        Path to the written lockfile.
    """

    path: Path = tmp_path / "uv.lock"
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_lock_returns_resolved_versions(tmp_path: Path) -> None:
    """
    Verify parse_lock reads exact resolved versions,
    including transitive packages.
    """

    result = parse_lock(_write(tmp_path, LOCK))
    assert result["requests"] == "2.33.1"
    assert result["urllib3"] == "2.6.3"


def test_parse_lock_normalises_names(tmp_path: Path) -> None:
    """
    Verify parse_lock normalises names so lock entries
    match parsed pyproject names.
    """

    result = parse_lock(_write(tmp_path, LOCK))
    assert "types-requests" in result
    assert "types_Requests" not in result


def test_parse_lock_skips_non_registry_sources(tmp_path: Path) -> None:
    """
    Verify editable and virtual entries are skipped,
    since they are not on PyPI.
    """

    result = parse_lock(_write(tmp_path, LOCK))
    assert "work-depschecker" not in result
    assert "some-virtual" not in result


def test_parse_lock_skips_entries_without_version(tmp_path: Path) -> None:
    """
    Verify entries missing a version are skipped rather
    than audited as an empty version.
    """

    assert "no-version" not in parse_lock(_write(tmp_path, LOCK))


def test_parse_lock_empty_lock(tmp_path: Path) -> None:
    """
    Verify parse_lock returns an empty mapping for a
    lockfile with no packages.
    """

    assert parse_lock(_write(tmp_path, "version = 1\n")) == {}


def test_parse_lock_missing_file(tmp_path: Path) -> None:
    """
    Verify parse_lock raises FileNotFoundError for a
    missing lockfile.
    """

    with pytest.raises(FileNotFoundError):
        parse_lock(tmp_path / "absent.lock")


def test_parse_lock_invalid_toml(tmp_path: Path) -> None:
    """
    Verify parse_lock propagates TOML decode errors.
    """

    with pytest.raises(tomllib.TOMLDecodeError):
        parse_lock(_write(tmp_path, "not = = toml"))
