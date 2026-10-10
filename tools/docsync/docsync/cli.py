"""
Command-line entry point for the documentation mirrors.

Usage:
    docsync kiro --dry-run          # Check for updates
    docsync kiro                    # Download updates
    docsync kiro --prune            # Also remove orphans
    docsync agentskills --dry-run   # Check for updates
    docsync agentskills             # Vendor updates
    docsync anthropic --dry-run     # Check for updates
    docsync anthropic               # Vendor updates
"""

# Standard libraries
import argparse
import sys
from pathlib import Path

# Own modules
from docsync.paths import find_repo_root
from docsync.sources import SOURCES
from docsync.sources.base import DocSource
from docsync.sync import sync


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Sync a vendored docs mirror")
    parser.add_argument(
        "source",
        choices=sorted(SOURCES),
        help="Documentation source to mirror.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check for updates without writing.",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Remove local pages the source no longer publishes.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help=(
            "Repository root holding the mirror (default: the nearest "
            "ancestor containing .kiro/ and tools/)."
        ),
    )
    return parser


def _resolve_root(explicit: Path | None) -> Path | None:
    """
    Determine the repository root to mirror into.

    Args:
        explicit: Root passed on the command line, if any.

    Returns:
        Repository root, or None when discovery failed and the reason
        has been reported.
    """
    if explicit is not None:
        return explicit
    try:
        return find_repo_root()
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return None


def _rejects_prune(source: DocSource, prune: bool) -> bool:
    """
    Report whether --prune was asked of a source that cannot prune.

    Args:
        source: Selected source.
        prune: Whether --prune was passed.

    Returns:
        True when the request is invalid and has been reported.
    """
    if not prune or source.supports_prune:
        return False
    print(
        f"ERROR: the {source.name} source has a fixed page catalogue, "
        "so --prune does not apply.",
        file=sys.stderr,
    )
    return True


def main(argv: list[str] | None = None) -> int:
    """
    Parse arguments and run the sync.

    Args:
        argv: Command-line arguments, defaulting to sys.argv[1:].

    Returns:
        Process exit code: 1 when the request is invalid, when the
        repository root could not be resolved, when the source rejected
        the upstream catalogue, when a page failed on a source that
        treats failures as fatal, or when a dry run found pending
        updates; 0 otherwise.
    """
    args = _build_parser().parse_args(argv)
    source = SOURCES[args.source]
    if _rejects_prune(source, args.prune):
        return 1
    root = _resolve_root(args.root)
    if root is None:
        return 1
    try:
        counts = sync(
            source, source.mirror_paths(root), dry_run=args.dry_run, prune=args.prune
        )
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print()
    print(
        counts.render(
            "DRY RUN" if args.dry_run else "SYNC", show_orphans=source.supports_prune
        )
    )
    if source.strict_failures and counts.failed:
        print(
            f"\n{counts.failed} page(s) could not be vendored.",
            file=sys.stderr,
        )
        return 1
    if args.dry_run and counts.has_pending_changes:
        print("\nRun without --dry-run to apply updates.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
