"""
The mirroring engine shared by every documentation source.

Page content is handled as bytes from the fetch to the write: the hash
that decides whether a page is new, updated or unchanged is taken over
the same bytes that land on disk, so no encoding or newline convention
can sneak in between the comparison and the write. A source that needs
text decodes inside its own transform.
"""

# Standard libraries
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

# Own modules
from docsync import net
from docsync.sources.base import DocSource
from docsync.types import MirrorPaths, Page, SyncCounts


def content_hash(content: bytes) -> str:
    """
    Compute a whitespace-normalized hash of content.

    Leading and trailing whitespace is stripped before hashing so that
    cosmetic churn (such as trailing newlines introduced by formatters)
    does not register as a change.

    Args:
        content: Raw content bytes.

    Returns:
        Hexadecimal SHA-256 digest of the stripped content.
    """
    return hashlib.sha256(content.strip()).hexdigest()


def download_page(source: DocSource, page: Page) -> bytes | None:
    """
    Fetch one page and apply the transform of its source.

    Args:
        source: Source the page belongs to.
        page: Page to mirror.

    Returns:
        Bytes to mirror, or None when the page could not be retrieved or
        converted.
    """
    try:
        raw = net.fetch(page.url)
    except OSError as error:
        print(f"  ! FAILED: {page.relative_path} ({error})")
        return None
    try:
        return source.transform(raw)
    except (UnicodeDecodeError, ValueError) as error:
        print(f"  ! FAILED: {page.relative_path} (cannot convert: {error})")
        return None


def write_marker(source: DocSource, paths: MirrorPaths, counts: SyncCounts) -> None:
    """
    Write the sync success marker file.

    Args:
        source: Source whose provenance the marker records.
        paths: Mirror locations.
        counts: Outcome tallies of the run.
    """
    marker: dict[str, object] = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        **source.provenance(),
        "pages_total": counts.pages,
        "new": counts.new,
        "updated": counts.updated,
    }
    paths.marker_path.parent.mkdir(parents=True, exist_ok=True)
    paths.marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")


def sync(
    source: DocSource,
    paths: MirrorPaths,
    dry_run: bool = False,
    prune: bool = False,
) -> SyncCounts:
    """
    Mirror every page the source publishes.

    Args:
        source: Source to mirror.
        paths: Mirror locations.
        dry_run: If True, only report changes without writing.
        prune: If True, remove local files the source no longer
            publishes.

    Returns:
        Outcome tallies of the run.
    """
    pages = source.discover()
    counts = SyncCounts(pages=len(pages))
    for page in pages:
        _sync_page(source, paths, page, counts, dry_run=dry_run)
    if prune or dry_run:
        counts.orphans = source.prune(paths, pages, dry_run=dry_run or not prune)
    if not dry_run and not (source.strict_failures and counts.failed):
        write_marker(source, paths, counts)
        print(f"Wrote sync marker: {paths.marker_path}")
    return counts


def _sync_page(
    source: DocSource,
    paths: MirrorPaths,
    page: Page,
    counts: SyncCounts,
    dry_run: bool,
) -> None:
    """
    Mirror one page and update the tallies.

    Args:
        source: Source the page belongs to.
        paths: Mirror locations.
        page: Page to mirror.
        counts: Tallies updated in place.
        dry_run: If True, report the change without writing.
    """
    local_path = paths.refs_dir / page.relative_path
    content = download_page(source, page)
    if content is None:
        counts.failed += 1
        return
    if not local_path.exists():
        counts.new += 1
        print(f"  + NEW: {page.relative_path}")
        if not dry_run:
            _write_page(local_path, content)
        return
    if content_hash(local_path.read_bytes()) != content_hash(content):
        counts.updated += 1
        print(f"  ~ UPDATED: {page.relative_path}")
        if not dry_run:
            _write_page(local_path, content)
        return
    counts.unchanged += 1


def _write_page(local_path: Path, content: bytes) -> None:
    """
    Write one mirrored page, creating its directory if needed.

    Args:
        local_path: Destination file.
        content: Bytes to write.
    """
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(content)
