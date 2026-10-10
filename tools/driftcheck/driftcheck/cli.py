"""
Command-line entry point for the drift checks.

Usage:
    driftcheck                # Validate the enclosing repository
    driftcheck --root DIR     # Validate another tree
"""

# Standard libraries
import argparse
import sys
from pathlib import Path

# Own modules
from driftcheck.paths import find_repo_root
from driftcheck.registry import run_checks
from driftcheck.report import report
from driftcheck.types import build_context


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Agent system drift detection")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help=(
            "Repository root to validate (default: the nearest ancestor "
            "containing .kiro/ and tools/)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """
    Parse arguments, run the checks and report.

    Args:
        argv: Command-line arguments, defaulting to sys.argv[1:].

    Returns:
        Process exit code: 1 on errors, 0 otherwise.
    """
    args = _build_parser().parse_args(argv)
    if args.root is not None:
        root: Path = args.root
    else:
        try:
            root = find_repo_root()
        except ValueError as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
    return report(run_checks(build_context(root)))


if __name__ == "__main__":
    sys.exit(main())
