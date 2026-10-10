# Standard libraries
from pathlib import Path

# Own modules
from depschecker.parser import _parse_dep_string, normalise, parse_pyproject


def test_parse_pyproject_project_deps(tmp_path: Path) -> None:
    """
    Verify parse_pyproject extracts project
    dependencies with versions.
    """

    toml = tmp_path / "pyproject.toml"
    toml.write_text(
        '[project]\ndependencies = ["requests>=2.32,<3"]\n',
        encoding="utf-8",
    )
    result = parse_pyproject(toml)
    assert "requests" in result
    assert result["requests"] == "2.32"


def test_parse_pyproject_dependency_groups(tmp_path: Path) -> None:
    """
    Verify parse_pyproject extracts dependency-groups
    entries.
    """

    toml = tmp_path / "pyproject.toml"
    toml.write_text(
        '[dependency-groups]\ndev = ["pytest==9.0.2"]\n',
        encoding="utf-8",
    )
    result = parse_pyproject(toml)
    assert "pytest" in result
    assert result["pytest"] == "9.0.2"


def test_parse_pyproject_unpinned(tmp_path: Path) -> None:
    """
    Verify parse_pyproject handles unpinned
    dependencies with empty version.
    """

    toml = tmp_path / "pyproject.toml"
    toml.write_text(
        '[project]\ndependencies = ["requests"]\n',
        encoding="utf-8",
    )
    result = parse_pyproject(toml)
    assert result["requests"] == ""


def test_parse_pyproject_empty(tmp_path: Path) -> None:
    """
    Verify parse_pyproject returns empty dict when
    no dependencies exist.
    """

    toml = tmp_path / "pyproject.toml"
    toml.write_text("[project]\nname = 'x'\n", encoding="utf-8")
    result = parse_pyproject(toml)
    assert result == {}


def test_parse_dep_string_extras() -> None:
    """
    Verify _parse_dep_string handles extras in
    brackets.
    """

    out: dict[str, str] = {}
    _parse_dep_string("markitdown[all]==0.1.5", out)
    assert "markitdown" in out
    assert out["markitdown"] == "0.1.5"


def test_parse_dep_string_invalid() -> None:
    """
    Verify _parse_dep_string skips invalid strings.
    """

    out: dict[str, str] = {}
    _parse_dep_string("---invalid", out)
    assert out == {}


def test_normalise_underscores() -> None:
    """
    Verify normalise converts underscores and dots
    to hyphens.
    """

    assert normalise("My_Package.Name") == "my-package-name"


def test_normalise_case() -> None:
    """
    Verify normalise lowercases the name.
    """

    assert normalise("Requests") == "requests"
