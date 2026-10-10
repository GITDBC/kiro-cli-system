"""
The contract a documentation source implements.

A source answers four questions for the shared engine: where the mirror
lives, which pages exist upstream, how raw bytes become the mirrored
document, and what provenance the sync marker should record. Two
policies that genuinely differ between sources — whether local files can
go stale enough to prune, and whether a failed page invalidates the
whole run — are class attributes rather than engine conditionals, so the
engine never asks which source it is driving.
"""

# Standard libraries
from abc import ABC, abstractmethod
from pathlib import Path

# Own modules
from docsync.types import MirrorPaths, Page


class DocSource(ABC):
    """
    One upstream documentation set the repository mirrors.

    Attributes:
        name: Identifier selected on the command line.
        supports_prune: Whether the source can tell that a local file is
            no longer published upstream. A fixed catalogue cannot, so
            for those sources --prune is refused and the orphan tally is
            left out of the summary.
        strict_failures: Whether a page that could not be mirrored
            invalidates the run. When True the sync marker is withheld
            and the CLI exits non-zero, so a partial mirror is never
            recorded as a success.
    """

    name: str
    supports_prune: bool = False
    strict_failures: bool = False

    @abstractmethod
    def mirror_paths(self, root: Path) -> MirrorPaths:
        """
        Build the on-disk locations of the mirror.

        Args:
            root: Repository root.

        Returns:
            Locations this source writes to.
        """

    @abstractmethod
    def discover(self) -> list[Page]:
        """
        List the pages currently published upstream.

        Returns:
            Pages to mirror, in the order they should be processed.
        """

    @abstractmethod
    def provenance(self) -> dict[str, str]:
        """
        Describe the upstream the marker file should record.

        Returns:
            Marker entries inserted between the timestamp and the
            tallies.
        """

    def transform(self, raw: bytes) -> bytes:
        """
        Turn a fetched payload into the bytes to mirror.

        The default is the identity: a source whose upstream already
        serves Markdown mirrors it verbatim. A source that rewrites its
        payload decodes here, at the single boundary where text exists,
        and hands bytes back so that hashing and writing stay byte-based
        throughout the engine.

        Args:
            raw: Response body as fetched.

        Returns:
            Bytes to compare against the mirror and write.

        Raises:
            ValueError: If the payload cannot be converted.
            UnicodeDecodeError: If the payload is not valid text.
        """
        return raw

    def prune(self, paths: MirrorPaths, pages: list[Page], dry_run: bool) -> int:
        """
        Remove local files the source no longer publishes.

        The default reports no orphans, which is the honest answer for a
        source whose catalogue is fixed: a page leaves the mirror by
        leaving the catalogue, never by disappearing upstream.

        Args:
            paths: Mirror locations.
            pages: Pages discovered in this run.
            dry_run: If True, only report orphans without deleting.

        Returns:
            Number of orphan files detected.
        """
        return 0
