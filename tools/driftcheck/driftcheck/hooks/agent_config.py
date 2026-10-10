"""
Post-write hook: validate agent JSON configuration files.

Reports missing required fields and unresolvable resources as warnings
on stderr. Never fails the write: the hook exists to inform, and
anything it cannot inspect is skipped with a warning.

Resource resolution is delegated to the drift check, so file:// and
skill:// URIs are treated identically here and there. Validating only
file:// URIs is how a dangling skill:// reference survived a bulk skill
rename unnoticed.
"""

# Standard libraries
import json
import pathlib
import sys
from typing import Final, TextIO

# Own modules
from driftcheck.checks.agents import missing_resources
from driftcheck.hooks import event_parts, event_path, warn
from driftcheck.paths import find_repo_root
from driftcheck.types import AgentConfig

REQUIRED_FIELDS: tuple[str, ...] = ("name", "description", "prompt", "model")

# Repository-relative components of the directory this hook guards.
AGENTS_DIR_PARTS: Final[tuple[str, ...]] = (".kiro", "agents")


def _validate(config_path: pathlib.Path, root: pathlib.Path) -> None:
    """
    Validate one agent config, printing findings.

    Args:
        config_path: Agent config that was just written.
        root: Repository root, for resolving skill:// resources.
    """
    data = json.loads(config_path.read_text(encoding="utf-8"))
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        print(
            f"WARN: {config_path.name} missing fields: {missing}",
            file=sys.stderr,
        )
    config = AgentConfig(path=config_path, data=data, error=None)
    for resource in missing_resources(config, root):
        print(
            f"WARN: {config_path.name} references missing file: {resource}",
            file=sys.stderr,
        )
    if not missing:
        print(f"OK: {config_path.name} is valid")


def _target_path(path: str, root: pathlib.Path) -> pathlib.Path | None:
    """
    Resolve the agent config the event refers to, if any.

    A config is inspected only when it sits directly inside
    ``.kiro/agents/``: a nested subdirectory is not part of the agent
    registry layout and is left alone.

    Args:
        path: Path reported by the event.
        root: Repository root that relative event paths resolve against.

    Returns:
        The written agent config, or None when the event names something
        else or the file no longer exists.
    """
    # Changed: component match instead of `"/.kiro/agents/" in path` -
    # Reason: the substring never matched the relative paths the runtime
    # reports, so the check silently never ran.
    parts = event_parts(path, root)
    if len(parts) != len(AGENTS_DIR_PARTS) + 1:
        return None
    if parts[:-1] != AGENTS_DIR_PARTS or not parts[-1].endswith(".json"):
        return None
    config_path = root.joinpath(*parts)
    return config_path if config_path.is_file() else None


def run(stream: TextIO | None = None, root: pathlib.Path | None = None) -> None:
    """
    Run the check for the file named by the hook event.

    Args:
        stream: Stream holding the event JSON, defaulting to stdin.
        root: Repository root, discovered from markers when omitted.
    """
    path = event_path(stream)
    if not path:
        return
    repo_root = root if root is not None else find_repo_root()
    config_path = _target_path(path, repo_root)
    if config_path is None:
        return
    _validate(config_path, repo_root)


def main() -> int:
    """
    Entry point for the driftcheck-hook-agent-config console script.

    Returns:
        Always 0 — a hook must never break the agent it runs under.
    """
    try:
        run()
    except Exception as error:  # noqa: BLE001 - degrade, never break the agent
        warn(f"agent config validation skipped ({error!r})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
