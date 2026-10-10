"""Read resolved package versions from a ``uv.lock`` file.

Declared constraints in ``pyproject.toml`` are ranges, and a range floor is not
what gets installed: ``requests>=2.32,<3`` resolves to whatever version uv
pinned. Vulnerability scanning therefore reads the lock, which is also the only
place transitive dependencies appear at all.
"""

# Standard libraries
import logging
import tomllib
from pathlib import Path
from typing import Any

# Own modules
from depschecker.parser import normalise

logger: logging.Logger = logging.getLogger(__name__)


def parse_lock(path: Path) -> dict[str, str]:
    """
    Extract resolved package versions from a ``uv.lock``
    file.

    Only registry-sourced packages are returned. The
    project's own package and any path or editable entry
    is skipped, since those are not on PyPI and cannot
    carry an advisory.

    Args:
        path: Path to the ``uv.lock`` file.

    Returns:
        Mapping of normalised package name to the exact
        resolved version.

    Raises:
        FileNotFoundError: If the file does not exist.
        tomllib.TOMLDecodeError: If the file is not valid
            TOML.
    """

    data: dict[str, Any] = tomllib.loads(path.read_text(encoding="utf-8"))

    resolved: dict[str, str] = {}
    for package in data.get("package", []):
        name: str = package.get("name", "")
        version: str = package.get("version", "")
        source: dict[str, Any] = package.get("source", {})
        if not name or not version or "registry" not in source:
            continue
        resolved[normalise(name)] = version

    logger.info("Parsed %d resolved packages from %s.", len(resolved), path)
    return resolved
