"""
Post-write hook: validate memory/state.yaml structure.

Exits 1 only when the check ran and the file is genuinely invalid.
Anything that prevents the check from running — PyYAML missing from the
environment, an undiscoverable repository root, an unreadable event —
warns on stderr and exits 0.
"""

# Standard libraries
import pathlib
import sys
from typing import Any, Final, TextIO

# Own modules
from driftcheck.hooks import event_parts, event_path, warn
from driftcheck.paths import find_repo_root

MAX_ENTRIES: int = 20

# Sections holding a list of entries, each subject to the cap and to the
# unique-id rule. `project_state` is a single mapping and is excluded.
ENTRY_SECTIONS: Final[tuple[str, ...]] = ("decisions", "agent_feedback")

# Repository-relative components of the file this hook guards.
STATE_PARTS: Final[tuple[str, ...]] = ("memory", "state.yaml")


def _first_problem(data: Any) -> str | None:
    """
    Return the first structural problem found in state.yaml.

    Args:
        data: Parsed YAML document.

    Returns:
        An error message, or None when the document is valid.
    """
    if not isinstance(data, dict):
        return "state.yaml root must be a mapping"
    for section in ENTRY_SECTIONS:
        problem = _section_problem(section, data.get(section) or [])
        if problem is not None:
            return problem
    return None


def _section_problem(section: str, entries: Any) -> str | None:
    """
    Validate one entry-list section against the structural rules.

    Args:
        section: Name of the section being validated.
        entries: Value found under that section.

    Returns:
        An error message, or None when the section is valid.
    """
    if not isinstance(entries, list):
        return f"{section} must be a list"
    if len(entries) > MAX_ENTRIES:
        return f"{section} has {len(entries)} entries (max {MAX_ENTRIES})"
    ids = [entry.get("id") for entry in entries if isinstance(entry, dict)]
    if len(ids) != len(set(ids)):
        return f"{section} has duplicate IDs"
    return None


def _target_path(stream: TextIO | None, root: pathlib.Path) -> pathlib.Path | None:
    """
    Resolve the state.yaml file the event refers to, if any.

    Args:
        stream: Stream holding the event JSON, defaulting to stdin.
        root: Repository root that relative event paths resolve against.

    Returns:
        The written state.yaml, or None when the event names something
        else or the file no longer exists.
    """
    path = event_path(stream)
    if not path:
        return None
    # Changed: component match instead of `"/memory/" in path` - Reason:
    # the substring never matched the relative paths the runtime reports,
    # so the check silently never ran.
    if event_parts(path, root) != STATE_PARTS:
        return None
    state_path = root.joinpath(*STATE_PARTS)
    return state_path if state_path.is_file() else None


def run(stream: TextIO | None = None, root: pathlib.Path | None = None) -> int:
    """
    Run the check for the file named by the hook event.

    Args:
        stream: Stream holding the event JSON, defaulting to stdin.
        root: Repository root, discovered from markers when omitted.

    Returns:
        1 when state.yaml is invalid, 0 otherwise.
    """
    state_path = _target_path(stream, root if root is not None else find_repo_root())
    if state_path is None:
        return 0
    try:
        # 3pps
        import yaml
    except ImportError:
        warn("PyYAML not installed, skipping state.yaml validation")
        return 0
    try:
        data = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        print(f"ERROR: state.yaml is malformed: {error}", file=sys.stderr)
        return 1
    problem = _first_problem(data)
    if problem is not None:
        print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    print("OK: state.yaml is valid")
    return 0


def main() -> int:
    """
    Entry point for the driftcheck-hook-state-yaml console script.

    Returns:
        1 when the check ran and found a violation, 0 otherwise —
        including every case where the check could not run at all.
    """
    try:
        return run()
    except Exception as error:  # noqa: BLE001 - degrade, never break the agent
        warn(f"state.yaml validation skipped ({error!r})")
        return 0


if __name__ == "__main__":
    sys.exit(main())
