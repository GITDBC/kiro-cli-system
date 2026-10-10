"""
Types describing a documentation mirroring run.

Kept deliberately small: a page record, a location record and a counter
record carry everything the CLI, the shared engine and the source
adapters need to exchange.
"""

# Standard libraries
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

# Page slug relative to a mirror directory, without the .md suffix.
Slug: TypeAlias = str


@dataclass(frozen=True)
class Page:
    """
    One upstream page a source asks the engine to mirror.

    The relative path is what the engine reports, writes and compares,
    so a source that publishes a flat catalogue and one that crawls a
    nested site describe their pages the same way.

    Attributes:
        url: Absolute URL the page is fetched from.
        relative_path: Destination below the mirror directory, as a
            POSIX-relative path such as "chat/subagents.md".
    """

    url: str
    relative_path: str


@dataclass(frozen=True)
class MirrorPaths:
    """
    On-disk locations a sync writes to.

    Attributes:
        refs_dir: Directory holding the mirrored Markdown pages.
        marker_path: Sync marker recording the last successful run.
    """

    refs_dir: Path
    marker_path: Path


@dataclass
class SyncCounts:
    """
    Outcome tallies of a sync run.

    Attributes:
        pages: Pages the source offered for mirroring.
        new: Pages written for the first time.
        updated: Pages whose content changed.
        unchanged: Pages already up to date.
        failed: Pages that could not be downloaded or converted.
        orphans: Local files the source no longer publishes.
    """

    pages: int = 0
    new: int = 0
    updated: int = 0
    unchanged: int = 0
    failed: int = 0
    orphans: int = 0

    @property
    def has_pending_changes(self) -> bool:
        """
        Report whether a dry run found work to apply.

        Returns:
            True when a page is new or updated.
        """
        return self.new > 0 or self.updated > 0

    def render(self, mode: str, show_orphans: bool = False) -> str:
        """
        Render the one-line summary.

        Args:
            mode: Run mode shown in the prefix ("SYNC" or "DRY RUN").
            show_orphans: Whether to append the orphan tally, which
                only carries meaning for a source that tracks
                deletions.

        Returns:
            Summary line of the run.
        """
        line = (
            f"[{mode}] New: {self.new}, Updated: {self.updated}, "
            f"Unchanged: {self.unchanged}, Failed: {self.failed}"
        )
        if show_orphans:
            line = f"{line}, Orphans: {self.orphans}"
        return line
