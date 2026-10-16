"""Input file collection with exclusion and size limits."""

# Standard libraries
import logging
from pathlib import Path

# Own modules
from doc2md.types import MAX_FILE_SIZE

logger: logging.Logger = logging.getLogger(__name__)


def _walk_dir(path: Path) -> list[Path]:
    """
    Recursively collect files from *path*,
    skipping symlink escapes.

    Args:
        path: Root directory to walk.

    Returns:
        List of files found under *path*.
    """

    root = path.resolve()
    files: list[Path] = []
    try:
        entries = path.rglob("*")
    except PermissionError:
        logger.warning("Permission denied: '%s', skipping.", path)
        return files
    for f in entries:
        if not f.is_file():
            continue
        try:
            f.resolve().relative_to(root)
        except ValueError:
            logger.warning(
                "Symlink escape: '%s' resolves outside '%s', skipping.",
                f,
                path,
            )
            continue
        files.append(f)
    return files


def _deduplicate(files: list[Path]) -> list[Path]:
    """
    Remove duplicates from *files* by resolved
    path, preserving order.

    Args:
        files: List of file paths to deduplicate.

    Returns:
        Deduplicated list of paths.
    """

    seen: set[Path] = set()
    deduped: list[Path] = []
    for f in files:
        r = f.resolve()
        if r not in seen:
            seen.add(r)
            deduped.append(f)
    return deduped


def _check_size(f: Path) -> bool:
    """
    Check that *f* is stattable and within the
    size limit.

    Args:
        f: File path to check.

    Returns:
        True if the file is within limits, False
            otherwise.
    """

    try:
        size = f.stat().st_size
    except OSError:
        logger.warning("Cannot stat '%s', skipping.", f)
        return False
    if size > MAX_FILE_SIZE:
        logger.warning("File '%s' exceeds %d bytes, skipping.", f, MAX_FILE_SIZE)
        return False
    return True


def collect_files(
    paths: list[str],
    exclude: list[str] | None = None,
) -> list[Path]:
    """
    Resolve input paths into a flat list of files,
    recursing into directories.

    Non-existent paths are logged as warnings and skipped.
    Files matching any of the exclude glob patterns are
    filtered out.

    Args:
        paths: File or directory paths to process.
        exclude: Glob patterns to filter out
            (e.g. ``*.log``, ``*.tmp``).

    Returns:
        Flat, deduplicated list of file paths.
    """

    files: list[Path] = []

    for p in paths:
        path: Path = Path(p)
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(_walk_dir(path))
        else:
            logger.warning("'%s' does not exist, skipping.", p)

    if exclude:
        files = [f for f in files if not any(f.match(pat) for pat in exclude)]

    files = _deduplicate(files)
    files = [f for f in files if _check_size(f)]

    return files
