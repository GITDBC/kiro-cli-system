"""
Startup hook: check the kiro-cli-reference doc mirror for staleness.

Reads (and discards) the agentSpawn event JSON from stdin. Prints a
reminder on stdout when the mirror is older than the threshold, prints
nothing when it is fresh, and always exits 0 — startup is never blocked.

No network I/O, so it stays well inside the 5 s hook timeout.
"""

# Standard libraries
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final

# Own modules
from driftcheck.hooks import warn
from driftcheck.paths import VENDORED_SKILL, find_repo_root

STALENESS_THRESHOLD_DAYS: Final[int] = 7
STALENESS_DELTA: Final[timedelta] = timedelta(days=STALENESS_THRESHOLD_DAYS)

SECONDS_PER_DAY: Final[int] = 86400
MARKER_NAME: Final[str] = ".last-sync.json"


def _skill_dir(root: Path) -> Path:
    """
    Return the vendored mirror's skill directory.

    Args:
        root: Repository root.

    Returns:
        Path to .kiro/skills/kiro-cli-reference.
    """
    return root / ".kiro" / "skills" / VENDORED_SKILL


def _read_stdin_event() -> None:
    """Consume and discard the hook event JSON from stdin."""
    try:
        sys.stdin.read()
    except Exception as error:  # noqa: BLE001 - stdin is optional context
        warn(f"could not read the hook event ({error!r})")


def _age_from_marker(skill_dir: Path) -> timedelta | None:
    """
    Parse the sync marker and return the age of the last sync.

    Args:
        skill_dir: Vendored mirror's skill directory.

    Returns:
        Age as timedelta, or None when the marker is unusable.
    """
    marker = skill_dir / MARKER_NAME
    if not marker.is_file():
        return None
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        sync_time = datetime.fromisoformat(str(data["timestamp"]))
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if sync_time.tzinfo is None:
        sync_time = sync_time.replace(tzinfo=UTC)
    return datetime.now(tz=UTC) - sync_time


def _age_from_mtime(skill_dir: Path) -> timedelta | None:
    """
    Fall back to the newest mtime of *.md files under references/.

    Args:
        skill_dir: Vendored mirror's skill directory.

    Returns:
        Age as timedelta, or None when no reference files exist.
    """
    refs_dir = skill_dir / "references"
    if not refs_dir.is_dir():
        return None
    md_files = [path for path in refs_dir.rglob("*.md") if path.is_file()]
    if not md_files:
        return None
    newest = max(path.stat().st_mtime for path in md_files)
    return datetime.now(tz=UTC) - datetime.fromtimestamp(newest, tz=UTC)


def compute_doc_age(skill_dir: Path) -> timedelta | None:
    """
    Compute the age of the kiro-cli-reference docs.

    Tries the sync marker first, then the newest *.md mtime.

    Args:
        skill_dir: Vendored mirror's skill directory.

    Returns:
        Age as timedelta, or None when it cannot be determined.
    """
    age = _age_from_marker(skill_dir)
    if age is not None:
        return age
    return _age_from_mtime(skill_dir)


def run() -> None:
    """Emit a reminder when the vendored docs look stale."""
    age = compute_doc_age(_skill_dir(find_repo_root()))
    if age is None:
        print(
            "[kiro-cli-reference] Doc freshness unknown "
            "(no sync marker or reference files found). "
            "Run `make sync-docs` to update the Kiro CLI reference docs."
        )
        return
    if age > STALENESS_DELTA:
        age_days = int(age.total_seconds() // SECONDS_PER_DAY)
        print(
            f"[kiro-cli-reference] Docs may be outdated "
            f"(last synced {age_days} day(s) ago, "
            f"threshold: {STALENESS_THRESHOLD_DAYS} days). "
            "Run `make sync-docs` to refresh the Kiro CLI reference docs."
        )


def main() -> int:
    """
    Entry point for the driftcheck-hook-refs-freshness console script.

    Returns:
        Always 0 — startup is never blocked.
    """
    _read_stdin_event()
    try:
        run()
    except Exception as error:  # noqa: BLE001 - degrade, never break the agent
        warn(f"doc freshness check skipped ({error!r})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
