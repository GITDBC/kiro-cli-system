"""Read declared dependency constraints from pyproject.toml."""

# Standard libraries
import logging
import re
import tomllib
from pathlib import Path
from typing import Any

logger: logging.Logger = logging.getLogger(__name__)

_DEP_RE: re.Pattern[str] = re.compile(r"^([A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?)")
_VER_RE: re.Pattern[str] = re.compile(r"[=~!<>]=?\s*([\d][^\s,;\"']*)")


def parse_pyproject(path: Path) -> dict[str, str]:
    """
    Extract dependency names and pinned versions from a
    ``pyproject.toml`` file.

    Reads the ``[project] dependencies`` array and all
    ``[dependency-groups]`` sections. For each entry,
    extracts the first version specifier found.

    Args:
        path: Path to the ``pyproject.toml`` file.

    Returns:
        Mapping of normalised package name to version
        string. Version is empty if unpinned.

    Raises:
        FileNotFoundError: If the file does not exist.
    """

    text: str = path.read_text(encoding="utf-8")
    data: dict[str, Any] = tomllib.loads(text)

    deps: dict[str, str] = {}

    project_deps: list[str] = data.get("project", {}).get("dependencies", [])
    for raw in project_deps:
        _parse_dep_string(raw, deps)

    groups: dict[str, list[str]] = data.get("dependency-groups", {})
    for group_deps in groups.values():
        for raw in group_deps:
            if isinstance(raw, str):
                _parse_dep_string(raw, deps)

    logger.info("Parsed %d dependencies from %s.", len(deps), path)
    return deps


def _parse_dep_string(raw: str, out: dict[str, str]) -> None:
    """
    Parse a single PEP 508 dependency string into name
    and version.

    Args:
        raw: Raw dependency string (e.g. ``requests>=2.32,<3``).
        out: Dictionary to update with the parsed result.

    Returns:
        None.
    """

    name_match: re.Match[str] | None = _DEP_RE.match(raw)
    if not name_match:
        return

    name: str = normalise(name_match.group(1))
    ver_match: re.Match[str] | None = _VER_RE.search(raw)
    version: str = ver_match.group(1) if ver_match else ""
    out[name] = version


def normalise(name: str) -> str:
    """
    Normalise a package name to lowercase with hyphens.

    Args:
        name: Raw package name.

    Returns:
        Normalised package name.
    """

    return re.sub(r"[-_.]+", "-", name).lower()
