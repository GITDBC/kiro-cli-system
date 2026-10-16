"""
Agent lifecycle hooks, exposed as console scripts.

Every hook degrades instead of failing: when it cannot run its check —
no repository root, an unreadable event, a missing dependency — it warns
on stderr and exits 0.
"""

# Standard libraries
import sys


def warn(message: str) -> None:
    """
    Print a degradation warning on stderr.

    Args:
        message: Reason the check could not run.
    """
    print(f"WARN: {message}", file=sys.stderr)
