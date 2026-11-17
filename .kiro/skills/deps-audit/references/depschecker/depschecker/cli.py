"""Command-line interface for the dependency report."""

# Standard libraries
import argparse
import logging
import os
import sys
import tomllib
from pathlib import Path
from typing import Any

# Own modules
from depschecker.lock import parse_lock
from depschecker.parser import parse_pyproject
from depschecker.pypi import DEFAULT_TIMEOUT, check_freshness, scan_vulnerabilities
from depschecker.report import render_freshness, render_full, render_vulnerabilities
from depschecker.types import DepStatus, VulnStatus

logger: logging.Logger = logging.getLogger(__name__)

_TOOL_SECTION: str = "depschecker"
_LOCK_NAME: str = "uv.lock"


def _load_global_defaults() -> dict[str, Any]:
    """
    Read defaults from the global TOML config.

    Returns:
        Dictionary with tool settings, or empty dict.

    Raises:
        ValueError: If the config file is not valid TOML.
    """

    path_str: str | None = os.environ.get("WORK_AGENTS_CONFIG")
    if not path_str:
        return {}
    path: Path = Path(path_str)
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as fh:
            result: dict[str, Any] = tomllib.load(fh).get(_TOOL_SECTION, {})
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid TOML in config file {path}: {exc}") from exc
    return result


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser.

    Returns:
        Configured argument parser.
    """

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Check Python dependency freshness and vulnerabilities via PyPI.",
    )

    parser.add_argument(
        "pyproject",
        nargs="?",
        type=Path,
        default=Path("pyproject.toml"),
        help="Path to pyproject.toml (default: pyproject.toml).",
    )

    parser.add_argument(
        "--lock",
        type=Path,
        default=None,
        help=(
            "Path to uv.lock (default: uv.lock beside the given pyproject.toml). "
            "Resolved versions come from the lock; vulnerability scanning "
            "requires it."
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write report to file instead of stdout.",
    )

    group: argparse._MutuallyExclusiveGroup = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--freshness-only",
        action="store_true",
        help="Only check version freshness, skip vulnerability scan.",
    )

    group.add_argument(
        "--vulns-only",
        action="store_true",
        help="Only check vulnerabilities, skip freshness report.",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=(
            "HTTP timeout per PyPI request in seconds "
            f"(default: {DEFAULT_TIMEOUT}, or `timeout` in the global config)."
        ),
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )

    return parser


def _resolve_lock_path(pyproject: Path, explicit: Path | None) -> Path:
    """
    Determine which lockfile to read.

    Args:
        pyproject: Path to the ``pyproject.toml`` file.
        explicit: Path given via ``--lock``, if any.

    Returns:
        Path to the lockfile, existing or not.
    """

    if explicit is not None:
        return explicit
    return pyproject.parent / _LOCK_NAME


def _load_resolved(lock: Path, required: bool) -> dict[str, str] | None:
    """
    Read resolved versions from the lockfile.

    Args:
        lock: Path to the ``uv.lock`` file.
        required: Whether a missing lockfile is fatal.

    Returns:
        Mapping of package name to resolved version, empty
        if absent and not required, or None when the lockfile
        is required but missing, or cannot be parsed.
    """

    if not lock.is_file():
        if required:
            logger.error(
                "Lockfile not found: %s. Vulnerability scanning needs resolved "
                "versions; pass --lock or use --freshness-only.",
                lock,
            )
            return None
        logger.warning(
            "Lockfile not found: %s. Freshness will compare against the "
            "declared constraint instead of the resolved version.",
            lock,
        )
        return {}

    try:
        return parse_lock(lock)
    except tomllib.TOMLDecodeError as exc:
        logger.error("Failed to parse lockfile %s: %s.", lock, exc)
        return None


def _collect_freshness(
    declared: dict[str, str],
    resolved: dict[str, str],
    timeout: int,
) -> list[DepStatus]:
    """
    Check freshness for every declared direct dependency.

    Args:
        declared: Declared name to constraint floor.
        resolved: Resolved name to locked version.
        timeout: HTTP timeout per request in seconds.

    Returns:
        Freshness statuses sorted by package name.
    """

    statuses: list[DepStatus] = []
    for name, version in sorted(declared.items()):
        logger.info("Checking freshness of %s.", name)
        statuses.append(
            check_freshness(
                name,
                version,
                resolved=resolved.get(name, ""),
                timeout=timeout,
            )
        )
    return statuses


def _collect_vulnerabilities(
    declared: dict[str, str],
    resolved: dict[str, str],
    timeout: int,
) -> list[VulnStatus]:
    """
    Audit every resolved package against PyPI advisories.

    The whole lock resolution is audited, not just the
    declared dependencies: transitive packages are
    installed too and carry advisories of their own.

    Args:
        declared: Declared name to constraint floor.
        resolved: Resolved name to locked version.
        timeout: HTTP timeout per request in seconds.

    Returns:
        Vulnerability statuses sorted by package name.
    """

    packages: list[tuple[str, str, bool]] = [
        (name, version, name in declared) for name, version in sorted(resolved.items())
    ]
    logger.info("Auditing %d resolved packages for advisories.", len(packages))
    return scan_vulnerabilities(packages, timeout=timeout)


def main(argv: list[str] | None = None) -> int:
    """
    Entry point for the depschecker CLI.

    Reads declared constraints from ``pyproject.toml`` and
    resolved versions from ``uv.lock``, queries PyPI, and
    outputs a Markdown report.

    Args:
        argv: Command-line arguments, defaulting to sys.argv[1:].

    Returns:
        Process exit code: 1 when the global config, the
        pyproject or a required lockfile is missing or invalid;
        0 otherwise.
    """

    parser: argparse.ArgumentParser = _build_parser()
    try:
        defaults: dict[str, Any] = _load_global_defaults()
    except ValueError as exc:
        logger.error("%s.", exc)
        return 1
    parser.set_defaults(timeout=defaults.get("timeout", DEFAULT_TIMEOUT))
    args: argparse.Namespace = parser.parse_args(argv)
    timeout: int = args.timeout

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    pyproject: Path = args.pyproject
    if not pyproject.exists():
        logger.error("File not found: %s.", pyproject)
        return 1

    try:
        declared: dict[str, str] = parse_pyproject(pyproject)
    except tomllib.TOMLDecodeError as exc:
        logger.error("Failed to parse TOML: %s.", exc)
        return 1

    lock: Path = _resolve_lock_path(pyproject, args.lock)
    resolved: dict[str, str] | None = _load_resolved(
        lock, required=not args.freshness_only
    )
    if resolved is None:
        return 1

    if not declared and not resolved:
        logger.warning("No dependencies found in %s.", pyproject)
        return 0

    if args.freshness_only:
        report: str = render_freshness(
            _collect_freshness(declared, resolved, timeout),
        )
    elif args.vulns_only:
        report = render_vulnerabilities(
            _collect_vulnerabilities(declared, resolved, timeout),
        )
    else:
        report = render_full(
            _collect_freshness(declared, resolved, timeout),
            _collect_vulnerabilities(declared, resolved, timeout),
        )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        logger.info("Report written to %s.", args.output)
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
