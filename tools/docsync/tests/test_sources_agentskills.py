"""
Tests for the Agent Skills documentation source.

Network access is always monkeypatched: page downloads are replaced by
in-memory fixtures, so the suite is offline and deterministic.
"""

# Standard libraries
import json
from pathlib import Path

# 3pps
import pytest

# Own modules
import docsync.net as net_module
from docsync.sources.agentskills import AgentSkillsSource
from docsync.sources.agentskills.pages import PAGES, VendoredPage
from docsync.sync import download_page, sync
from docsync.types import MirrorPaths

UPSTREAM = '---\ntitle: "Page {index}"\n---\n\nBody {index}.\n'


@pytest.fixture()
def source() -> AgentSkillsSource:
    """
    Build the source under test.

    Returns:
        The Agent Skills documentation source.
    """
    return AgentSkillsSource()


@pytest.fixture()
def paths(source: AgentSkillsSource, tmp_path: Path) -> MirrorPaths:
    """
    Build mirror locations inside a temporary repository.

    Args:
        source: Source under test.
        tmp_path: Pytest-provided temporary directory.

    Returns:
        Mirror locations under the temporary tree.
    """
    return source.mirror_paths(tmp_path)


@pytest.fixture()
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Replace every network call with in-memory fixtures.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    bodies = {
        page.url: UPSTREAM.format(index=index) for index, page in enumerate(PAGES)
    }

    def fake_fetch(url: str, retries: int = 3) -> bytes:
        if url not in bodies:
            message = f"404 for {url}"
            raise OSError(message)
        return bodies[url].encode("utf-8")

    monkeypatch.setattr(net_module, "fetch", fake_fetch)


def test_mirror_paths_follow_the_convention(
    source: AgentSkillsSource, tmp_path: Path
) -> None:
    """The mirror lives under the agent-creation skill references."""
    mirror = source.mirror_paths(tmp_path)
    assert mirror.refs_dir == (
        tmp_path / ".kiro" / "skills" / "agent-creation" / "references" / "agentskills"
    )
    assert mirror.marker_path == mirror.refs_dir / ".last-sync.json"


def test_the_catalogue_covers_the_six_vendored_pages() -> None:
    """The mirror tracks the specification plus the creation guides."""
    assert [page.filename for page in PAGES] == [
        "specification.md",
        "quickstart.md",
        "best-practices.md",
        "optimizing-descriptions.md",
        "evaluating-skills.md",
        "using-scripts.md",
    ]


def test_page_metadata_is_derived_from_the_source_path() -> None:
    """A catalogue entry knows its route and its raw URL."""
    page = VendoredPage("docs/skill-creation/quickstart.mdx")
    assert page.route == "/skill-creation/quickstart"
    assert page.url.endswith("/main/docs/skill-creation/quickstart.mdx")


def test_discovery_flattens_the_catalogue_into_mirror_pages(
    source: AgentSkillsSource,
) -> None:
    """Each catalogue entry becomes a flat page in the mirror."""
    pages = source.discover()
    assert [page.relative_path for page in pages] == [page.filename for page in PAGES]
    assert pages[0].url == PAGES[0].url


def test_the_transform_converts_mdx_to_markdown_bytes(
    source: AgentSkillsSource,
) -> None:
    """Decoding happens inside the transform, which returns bytes."""
    converted = source.transform(UPSTREAM.format(index=0).encode("utf-8"))
    assert converted == b"# Page 0\n\nBody 0.\n"


def test_sync_writes_every_page_and_the_marker(
    source: AgentSkillsSource, paths: MirrorPaths, offline: None
) -> None:
    """A first run vendors the whole catalogue."""
    counts = sync(source, paths)
    assert (counts.new, counts.updated, counts.unchanged, counts.failed) == (6, 0, 0, 0)
    assert (paths.refs_dir / "specification.md").read_text(
        encoding="utf-8"
    ) == "# Page 0\n\nBody 0.\n"
    marker = json.loads(paths.marker_path.read_text(encoding="utf-8"))
    assert marker["pages_total"] == 6
    assert marker["upstream_branch"] == "main"


def test_a_second_run_reports_everything_unchanged(
    source: AgentSkillsSource, paths: MirrorPaths, offline: None
) -> None:
    """Vendoring is idempotent, which is what CI relies on."""
    sync(source, paths)
    counts = sync(source, paths)
    assert (counts.new, counts.updated, counts.unchanged) == (0, 0, 6)


def test_sync_rewrites_only_pages_that_changed(
    source: AgentSkillsSource, paths: MirrorPaths, offline: None
) -> None:
    """A stale page is refreshed and the rest are left alone."""
    sync(source, paths)
    (paths.refs_dir / "specification.md").write_text("# Stale\n", encoding="utf-8")
    counts = sync(source, paths)
    assert (counts.new, counts.updated, counts.unchanged) == (0, 1, 5)
    assert (paths.refs_dir / "specification.md").read_text(
        encoding="utf-8"
    ) == "# Page 0\n\nBody 0.\n"


def test_dry_run_writes_nothing(
    source: AgentSkillsSource, paths: MirrorPaths, offline: None
) -> None:
    """A dry run reports changes without touching the disk."""
    counts = sync(source, paths, dry_run=True)
    assert counts.new == 6
    assert counts.has_pending_changes
    assert not paths.refs_dir.exists()


def test_a_failed_download_is_counted_and_blocks_the_marker(
    source: AgentSkillsSource, paths: MirrorPaths, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing page leaves the marker untouched, so CI notices."""

    def always_fail(url: str, retries: int = 3) -> bytes:
        message = "network down"
        raise OSError(message)

    monkeypatch.setattr(net_module, "fetch", always_fail)
    counts = sync(source, paths)
    assert counts.failed == len(PAGES)
    assert not paths.marker_path.exists()


def test_an_unconvertible_page_is_reported_as_failed(
    source: AgentSkillsSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Malformed upstream content fails the page, not the process."""
    monkeypatch.setattr(
        net_module, "fetch", lambda url, retries=3: b'---\ntitle: "Broken"\n'
    )
    assert download_page(source, source.discover()[0]) is None


def test_write_marker_records_the_provenance(
    source: AgentSkillsSource, paths: MirrorPaths, offline: None
) -> None:
    """The marker carries the upstream identity and the tallies."""
    sync(source, paths)
    marker = json.loads(paths.marker_path.read_text(encoding="utf-8"))
    assert marker["upstream_repository"] == "agentskills/agentskills"
    assert marker["upstream_license"] == "CC-BY-4.0"
    assert marker["new"] == 6
    assert marker["timestamp"].endswith("+00:00")


def test_the_source_refuses_to_prune(
    source: AgentSkillsSource, paths: MirrorPaths, offline: None
) -> None:
    """A fixed catalogue never reports a local file as orphaned."""
    assert source.supports_prune is False
    paths.refs_dir.mkdir(parents=True)
    (paths.refs_dir / "unrelated.md").write_text("# Kept\n", encoding="utf-8")
    counts = sync(source, paths, dry_run=True)
    assert counts.orphans == 0
    assert (paths.refs_dir / "unrelated.md").is_file()
