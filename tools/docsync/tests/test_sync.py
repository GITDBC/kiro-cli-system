"""
Tests for the shared mirroring engine and the source adapter seam.

The engine is exercised through fake sources rather than the real ones,
so the contract in sources/base.py is tested on its own terms: what the
engine does with a transform, a provenance mapping, a prune capability
and a failure policy. Network access is always monkeypatched, so the
suite is offline and deterministic.
"""

# Standard libraries
import json
from dataclasses import dataclass, field
from pathlib import Path

# 3pps
import pytest

# Own modules
import docsync.net as net_module
from docsync.sources.base import DocSource
from docsync.sync import content_hash, download_page, sync, write_marker
from docsync.types import MirrorPaths, Page, SyncCounts

BODIES: dict[str, bytes] = {
    "https://example.test/one.md": b"# One\n",
    "https://example.test/deep/two.md": b"# Two\n",
}


@dataclass(frozen=True)
class FakeSource(DocSource):
    """
    Minimal source used to exercise the engine.

    Attributes:
        name: Identifier of the source.
        pages: Pages the source publishes.
    """

    name: str = "fake"
    pages: tuple[Page, ...] = field(
        default_factory=lambda: (
            Page(url="https://example.test/one.md", relative_path="one.md"),
            Page(url="https://example.test/deep/two.md", relative_path="deep/two.md"),
        )
    )

    def mirror_paths(self, root: Path) -> MirrorPaths:
        """
        Build locations below a temporary root.

        Args:
            root: Repository root.

        Returns:
            Mirror locations for the fake source.
        """
        return MirrorPaths(refs_dir=root / "mirror", marker_path=root / "marker.json")

    def discover(self) -> list[Page]:
        """
        List the pages the fake source publishes.

        Returns:
            The configured pages.
        """
        return list(self.pages)

    def provenance(self) -> dict[str, str]:
        """
        Describe the fake upstream.

        Returns:
            A single provenance entry.
        """
        return {"upstream": "example.test"}


@dataclass(frozen=True)
class ShoutingSource(FakeSource):
    """A source whose transform rewrites the payload."""

    name: str = "shouting"

    def transform(self, raw: bytes) -> bytes:
        """
        Upper-case the decoded payload.

        Args:
            raw: Response body as fetched.

        Returns:
            Upper-cased payload re-encoded as UTF-8.
        """
        return raw.decode("utf-8").upper().encode("utf-8")


@dataclass(frozen=True)
class BrokenSource(FakeSource):
    """A source whose transform always rejects the payload."""

    name: str = "broken"
    strict_failures: bool = True

    def transform(self, raw: bytes) -> bytes:
        """
        Reject every payload.

        Args:
            raw: Response body as fetched.

        Returns:
            Never returns.

        Raises:
            ValueError: Always.
        """
        message = "malformed page"
        raise ValueError(message)


@dataclass(frozen=True)
class PruningSource(FakeSource):
    """A source that reports one orphan whenever it is asked."""

    name: str = "pruning"
    supports_prune: bool = True

    def prune(self, paths: MirrorPaths, pages: list[Page], dry_run: bool) -> int:
        """
        Report a single orphan.

        Args:
            paths: Mirror locations.
            pages: Pages discovered in this run.
            dry_run: If True, only report orphans without deleting.

        Returns:
            Always one orphan.
        """
        return 1


@pytest.fixture()
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Replace the single network seam with in-memory fixtures.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """

    def fake_fetch(url: str, retries: int = 3) -> bytes:
        if url not in BODIES:
            message = f"404 for {url}"
            raise OSError(message)
        return BODIES[url]

    monkeypatch.setattr(net_module, "fetch", fake_fetch)


def test_content_hash_ignores_surrounding_whitespace() -> None:
    """Trailing newline churn is not a content change."""
    assert content_hash(b"# Page\n") == content_hash(b"  # Page\n\n\n")
    assert content_hash(b"# Page\n") != content_hash(b"# Other\n")


def test_engine_writes_new_pages_and_nested_directories(
    tmp_path: Path, offline: None
) -> None:
    """A first run creates every page, parent directories included."""
    source = FakeSource()
    paths = source.mirror_paths(tmp_path)
    counts = sync(source, paths)
    assert (counts.new, counts.updated, counts.unchanged, counts.failed) == (2, 0, 0, 0)
    assert (paths.refs_dir / "one.md").read_bytes() == b"# One\n"
    assert (paths.refs_dir / "deep" / "two.md").read_bytes() == b"# Two\n"


def test_the_default_transform_mirrors_bytes_verbatim(
    tmp_path: Path, offline: None
) -> None:
    """A source without a transform writes exactly what it fetched."""
    source = FakeSource()
    paths = source.mirror_paths(tmp_path)
    sync(source, paths)
    assert (paths.refs_dir / "one.md").read_bytes() == BODIES[source.pages[0].url]


def test_a_source_transform_is_applied_before_writing(
    tmp_path: Path, offline: None
) -> None:
    """The engine mirrors the transformed bytes, not the raw payload."""
    source = ShoutingSource()
    paths = source.mirror_paths(tmp_path)
    sync(source, paths)
    assert (paths.refs_dir / "one.md").read_bytes() == b"# ONE\n"


def test_a_transformed_page_is_unchanged_on_a_second_run(
    tmp_path: Path, offline: None
) -> None:
    """Hashing compares transformed bytes on both sides of the write."""
    source = ShoutingSource()
    paths = source.mirror_paths(tmp_path)
    sync(source, paths)
    counts = sync(source, paths)
    assert (counts.new, counts.updated, counts.unchanged) == (0, 0, 2)


def test_a_rejected_transform_counts_the_page_as_failed(
    tmp_path: Path, offline: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """A transform error fails the page, not the process."""
    source = BrokenSource()
    counts = sync(source, source.mirror_paths(tmp_path))
    assert counts.failed == 2
    assert "cannot convert: malformed page" in capsys.readouterr().out


def test_download_page_reports_a_fetch_failure(
    offline: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """A page missing upstream is reported and returns no content."""
    page = Page(url="https://example.test/gone.md", relative_path="gone.md")
    assert download_page(FakeSource(), page) is None
    assert "! FAILED: gone.md" in capsys.readouterr().out


def test_a_stale_page_is_rewritten(tmp_path: Path, offline: None) -> None:
    """Only changed content counts as an update."""
    source = FakeSource()
    paths = source.mirror_paths(tmp_path)
    sync(source, paths)
    (paths.refs_dir / "one.md").write_bytes(b"# Stale\n")
    counts = sync(source, paths)
    assert (counts.new, counts.updated, counts.unchanged) == (0, 1, 1)
    assert (paths.refs_dir / "one.md").read_bytes() == b"# One\n"


def test_dry_run_writes_nothing(tmp_path: Path, offline: None) -> None:
    """A dry run reports changes without touching the disk."""
    source = FakeSource()
    paths = source.mirror_paths(tmp_path)
    counts = sync(source, paths, dry_run=True)
    assert counts.new == 2
    assert counts.has_pending_changes
    assert not paths.refs_dir.exists()
    assert not paths.marker_path.exists()


def test_the_marker_carries_the_source_provenance(
    tmp_path: Path, offline: None
) -> None:
    """Provenance entries sit between the timestamp and the tallies."""
    source = FakeSource()
    paths = source.mirror_paths(tmp_path)
    sync(source, paths)
    marker = json.loads(paths.marker_path.read_text(encoding="utf-8"))
    assert list(marker) == [
        "timestamp",
        "upstream",
        "pages_total",
        "new",
        "updated",
    ]
    assert marker["upstream"] == "example.test"


def test_write_marker_records_the_tallies(tmp_path: Path) -> None:
    """The marker carries the timestamp and the counts."""
    source = FakeSource()
    write_marker(source, source.mirror_paths(tmp_path), SyncCounts(pages=7, new=2))
    marker = json.loads(
        source.mirror_paths(tmp_path).marker_path.read_text(encoding="utf-8")
    )
    assert marker["pages_total"] == 7
    assert marker["new"] == 2
    assert marker["timestamp"].endswith("+00:00")


def test_a_strict_source_withholds_the_marker_after_a_failure(
    tmp_path: Path, offline: None
) -> None:
    """A partial mirror is never recorded as a successful sync."""
    source = BrokenSource()
    paths = source.mirror_paths(tmp_path)
    sync(source, paths)
    assert not paths.marker_path.exists()


def test_a_tolerant_source_still_writes_the_marker_after_a_failure(
    tmp_path: Path, offline: None
) -> None:
    """A source that tolerates gaps records the run it completed."""
    source = FakeSource(
        pages=(Page(url="https://example.test/gone.md", relative_path="gone.md"),)
    )
    paths = source.mirror_paths(tmp_path)
    counts = sync(source, paths)
    assert counts.failed == 1
    assert paths.marker_path.is_file()


def test_the_default_prune_reports_no_orphans(tmp_path: Path, offline: None) -> None:
    """A fixed catalogue cannot orphan a local file."""
    source = FakeSource()
    counts = sync(source, source.mirror_paths(tmp_path), dry_run=True)
    assert counts.orphans == 0


def test_a_pruning_source_contributes_its_orphan_tally(
    tmp_path: Path, offline: None
) -> None:
    """The engine records whatever the source reports as orphaned."""
    source = PruningSource()
    counts = sync(source, source.mirror_paths(tmp_path), prune=True)
    assert counts.orphans == 1


def test_counts_render_the_summary_line() -> None:
    """The summary reports each outcome class once."""
    line = SyncCounts(new=1, updated=2, unchanged=3, failed=4).render("SYNC")
    assert line == "[SYNC] New: 1, Updated: 2, Unchanged: 3, Failed: 4"


def test_counts_render_the_historical_summary_line_with_orphans() -> None:
    """A pruning source keeps the historical shape of the summary."""
    line = SyncCounts(new=1, updated=2, unchanged=3, failed=4, orphans=5).render(
        "SYNC", show_orphans=True
    )
    assert line == "[SYNC] New: 1, Updated: 2, Unchanged: 3, Failed: 4, Orphans: 5"


def test_fetch_retries_then_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exhausted retries surface the underlying OSError."""
    attempts: list[str] = []

    def always_fail(request: object, timeout: int = 0) -> object:
        attempts.append("call")
        message = "network down"
        raise OSError(message)

    monkeypatch.setattr(net_module.urllib.request, "urlopen", always_fail)
    monkeypatch.setattr(net_module.time, "sleep", lambda _seconds: None)
    with pytest.raises(OSError, match="network down"):
        net_module.fetch("https://example.test/one.md")
    assert len(attempts) == net_module.MAX_RETRIES
