"""
Repository-root discovery for the documentation mirrors.

Discovery is marker-based rather than a fixed parent count so that
moving a module cannot silently point a sync at the wrong tree.
"""

# Standard libraries
from pathlib import Path
from typing import Final

# Directories that together identify the repository root. The helper
# below is deliberately duplicated from driftcheck, and stays
# duplicated: tools under tools/ share no Python code imported at
# runtime, so each remains independently installable and runnable via
# `uv run --project tools/<tool>`. That convention does not reach
# developer build tooling such as a shared Make include, which affects
# neither installability nor runtime behaviour. Merging two tools into
# one removed a boundary and the duplication that lived inside it; this
# remaining copy sits across a boundary that is meant to be there.
ROOT_MARKERS: Final[tuple[str, ...]] = (".kiro", "tools")


def find_repo_root(start: Path | None = None) -> Path:
    """
    Locate the repository root by walking upward from a starting point.

    Args:
        start: Path to walk up from. Defaults to this module's file, then
            the current working directory.

    Returns:
        Absolute path to the repository root.

    Raises:
        ValueError: If no ancestor holds the marker directories.
    """
    origins: list[Path] = [(start or Path(__file__)).resolve()]
    if start is None:
        origins.append(Path.cwd().resolve())
    for origin in origins:
        for candidate in (origin, *origin.parents):
            if all((candidate / marker).is_dir() for marker in ROOT_MARKERS):
                return candidate
    markers = ", ".join(f"{marker}/" for marker in ROOT_MARKERS)
    searched = ", ".join(str(origin) for origin in origins)
    message = (
        f"cannot locate the repository root: no ancestor of {searched} "
        f"contains all of {markers}. Pass --root explicitly."
    )
    raise ValueError(message)
