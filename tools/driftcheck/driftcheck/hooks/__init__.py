"""
Agent lifecycle hooks, exposed as console scripts.

Every hook degrades instead of failing: when it cannot run its check —
no repository root, an unreadable event, a missing dependency — it warns
on stderr and exits 0. Only a check that actually ran and found a real
violation is allowed to exit non-zero.

The event-payload plumbing lives here because two of the three hooks
consume the same postToolUse payload shape and must decide, from the
same rules, whether a written path concerns them.
"""

# Standard libraries
import json
import sys
from pathlib import Path, PurePath
from typing import Any, TextIO


def event_parts(path: str, root: Path) -> tuple[str, ...]:
    """
    Split a reported event path into repository-relative components.

    Hooks MUST decide whether an event concerns them by comparing path
    components, never by substring tests such as ``"/memory/" in path``.
    A substring carrying separators cannot match the relative paths the
    runtime also reports, so such a test skips those events silently and
    the check never runs — a latent bug this helper exists to prevent
    from returning. Comparing ``PurePath.parts`` makes
    ``memory/state.yaml``, ``./memory/state.yaml``,
    ``memory//state.yaml`` and the absolute form behave identically.

    Relative paths are anchored at the repository root rather than at
    the current working directory, which a hook process cannot rely on.
    Anchoring also fixes the depth of a match: a path is only considered
    when it sits exactly where the repository layout puts it.

    Args:
        path: Path reported by the postToolUse event.
        root: Repository root that relative paths resolve against.

    Returns:
        Components of the path relative to root, or an empty tuple when
        the path falls outside the repository.
    """
    candidate = PurePath(path)
    anchored = candidate if candidate.is_absolute() else PurePath(root) / candidate
    try:
        return anchored.relative_to(root).parts
    except ValueError:
        return ()


def event_path(stream: TextIO | None = None) -> str:
    """
    Extract the written file path from a postToolUse event payload.

    Both payload shapes are accepted: a direct ``path`` field and an
    ``operations`` array whose first entry carries the path.

    Args:
        stream: Stream holding the event JSON, defaulting to stdin.

    Returns:
        The reported path, or an empty string when absent.

    Raises:
        ValueError: If the payload is not a JSON object.
    """
    event = json.load(stream if stream is not None else sys.stdin)
    if not isinstance(event, dict):
        message = "hook event payload is not a JSON object"
        raise ValueError(message)
    tool_input = event.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return ""
    path = tool_input.get("path", "")
    if isinstance(path, str) and path:
        return path
    operations: Any = tool_input.get("operations", [])
    if isinstance(operations, list) and operations:
        first = operations[0]
        if isinstance(first, dict):
            candidate = first.get("path", "")
            if isinstance(candidate, str):
                return candidate
    return ""


def warn(message: str) -> None:
    """
    Print a degradation warning on stderr.

    Args:
        message: Reason the check could not run.
    """
    print(f"WARN: {message}", file=sys.stderr)
