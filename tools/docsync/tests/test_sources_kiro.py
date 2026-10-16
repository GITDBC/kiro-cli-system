"""
Tests for the Kiro CLI documentation source.

Network access is always monkeypatched: the sitemap and page downloads
are replaced by in-memory fixtures, so the suite is offline and
deterministic.
"""

# Standard libraries
import json
from pathlib import Path

# 3pps
import pytest

# Own modules
import docsync.net as net_module
from docsync.sources.kiro import (
    BASE_URL,
    CLI_SECTIONS,
    EXCLUDED_PATHS,
    KiroSource,
    get_doc_pages,
    is_excluded,
    page_for,
    select_pages,
)
from docsync.sync import sync
from docsync.types import MirrorPaths

# The fixture mirrors every shape the real sitemap contains: the two
# documentation indexes, a page still below /docs/cli/, a page relocated
# to a top-level section, a section index, an entry without the usual
# trailing slash, one page advertised under both its legacy and its
# canonical URL, the sections of the other Kiro products, and pages the
# mirror excludes on purpose in both URL forms.
SITEMAP = """<?xml version="1.0"?>
<urlset>
  <url><loc>https://kiro.dev/docs/</loc></url>
  <url><loc>https://kiro.dev/docs/cli/</loc></url>
  <url><loc>https://kiro.dev/docs/cli/chat/context/</loc></url>
  <url><loc>https://kiro.dev/docs/cli/setup</loc></url>
  <url><loc>https://kiro.dev/docs/mcp/usage/</loc></url>
  <url><loc>https://kiro.dev/docs/billing/managing-taxes/</loc></url>
  <url><loc>https://kiro.dev/docs/cli/billing/managing/</loc></url>
  <url><loc>https://kiro.dev/docs/cli/acp/</loc></url>
  <url><loc>https://kiro.dev/docs/cli/terminal-ui/comparison/</loc></url>
  <url><loc>https://kiro.dev/docs/getting-started/installation/</loc></url>
  <url><loc>https://kiro.dev/docs/hooks/</loc></url>
  <url><loc>https://kiro.dev/docs/cli/hooks/</loc></url>
  <url><loc>https://kiro.dev/docs/crew/agents/</loc></url>
  <url><loc>https://kiro.dev/docs/ide/mcp/</loc></url>
  <url><loc>https://kiro.dev/docs/web/automations/</loc></url>
  <url><loc>https://kiro.dev/docs/mobile/</loc></url>
  <url><loc>https://kiro.dev/docs/guides/learn-by-playing/</loc></url>
  <url><loc>https://kiro.dev/blog/kiro-cli/</loc></url>
</urlset>
"""

# What upstream answers at the legacy URL of a relocated page: HTTP 200
# with a stub instead of the documentation.
MOVED_STUB = b"# Moved\n\nThis page is now at: /docs/hooks.md\n"

PAGES = {
    "https://kiro.dev/docs/cli/chat/context.md": b"# Context\n",
    "https://kiro.dev/docs/cli/hooks.md": MOVED_STUB,
    "https://kiro.dev/docs/cli/setup.md": b"# Setup\n",
    "https://kiro.dev/docs/hooks.md": b"# Hooks\n",
    "https://kiro.dev/docs/mcp/usage.md": b"# MCP usage\n",
}

EXPECTED_PATHS = [
    "chat/context.md",
    "hooks.md",
    "mcp/usage.md",
    "setup.md",
]


@pytest.fixture()
def source() -> KiroSource:
    """
    Build the source under test.

    Returns:
        The kiro.dev documentation source.
    """
    return KiroSource()


@pytest.fixture()
def paths(source: KiroSource, tmp_path: Path) -> MirrorPaths:
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

    def fake_fetch(url: str, retries: int = 3) -> bytes:
        if url.endswith("sitemap.xml"):
            return SITEMAP.encode("utf-8")
        if url not in PAGES:
            message = f"404 for {url}"
            raise OSError(message)
        return PAGES[url]

    monkeypatch.setattr(net_module, "fetch", fake_fetch)


def test_mirror_paths_follow_the_convention(source: KiroSource, tmp_path: Path) -> None:
    """The mirror lives under the kiro-cli-reference skill."""
    paths = source.mirror_paths(tmp_path)
    assert paths.refs_dir == (
        tmp_path / ".kiro" / "skills" / "kiro-cli-reference" / "references"
    )
    assert paths.marker_path.name == ".last-sync.json"


def test_a_cli_page_drops_the_section_from_its_mirror_path() -> None:
    """A /docs/cli/<rest> URL is mirrored as <rest>.md."""
    page = page_for("https://kiro.dev/docs/cli/chat/context/")
    assert page is not None
    assert page.relative_path == "chat/context.md"
    assert page.url == "https://kiro.dev/docs/cli/chat/context.md"


def test_a_relocated_page_keeps_the_section_in_its_mirror_path() -> None:
    """A /docs/<section>/<rest> URL is mirrored as <section>/<rest>.md."""
    page = page_for("https://kiro.dev/docs/mcp/usage/")
    assert page is not None
    assert page.relative_path == "mcp/usage.md"
    assert page.url == "https://kiro.dev/docs/mcp/usage.md"


def test_a_section_index_maps_to_a_top_level_file() -> None:
    """A bare /docs/<section>/ URL is mirrored as <section>.md."""
    page = page_for("https://kiro.dev/docs/hooks/")
    assert page is not None
    assert page.relative_path == "hooks.md"


def test_the_trailing_slash_does_not_change_the_mapping() -> None:
    """Both spellings of one URL resolve identically."""
    assert page_for("https://kiro.dev/docs/cli/setup/") == page_for(
        "https://kiro.dev/docs/cli/setup"
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://kiro.dev/docs/crew/agents/",
        "https://kiro.dev/docs/ide/mcp/",
        "https://kiro.dev/docs/web/automations/",
        "https://kiro.dev/docs/mobile/",
        "https://kiro.dev/docs/guides/learn-by-playing/",
    ],
)
def test_another_kiro_product_is_out_of_scope(url: str) -> None:
    """Sections belonging to other products are never mirrored."""
    assert page_for(url) is None


@pytest.mark.parametrize(
    "url",
    [
        "https://kiro.dev/docs/",
        "https://kiro.dev/docs/cli/",
        "https://kiro.dev/blog/kiro-cli/",
        "https://kiro.dev/",
    ],
)
def test_an_index_or_foreign_url_is_out_of_scope(url: str) -> None:
    """Documentation indexes and non-docs URLs yield no page."""
    assert page_for(url) is None


@pytest.mark.parametrize(
    "url",
    [
        "https://kiro.dev/docs/billing/managing-taxes/",
        "https://kiro.dev/docs/cli/billing/managing/",
        "https://kiro.dev/docs/enterprise/",
        "https://kiro.dev/docs/cli/acp/",
        "https://kiro.dev/docs/cli/terminal-ui/",
        "https://kiro.dev/docs/cli/terminal-ui/comparison/",
        "https://kiro.dev/docs/cli/v3/migration-guide/",
        "https://kiro.dev/docs/getting-started/installation/",
        "https://kiro.dev/docs/models/govcloud/",
        "https://kiro.dev/docs/mcp/registry/",
    ],
)
def test_an_excluded_page_is_out_of_scope_in_either_url_form(url: str) -> None:
    """Exclusions match the mirror path, legacy or canonical URL alike."""
    assert page_for(url) is None


@pytest.mark.parametrize(
    "url",
    [
        "https://kiro.dev/docs/cli/v3/agent-config/",
        "https://kiro.dev/docs/cli/v3/permissions/",
        "https://kiro.dev/docs/cli/v3/new-features/",
        "https://kiro.dev/docs/cli/v3/tangent/",
        "https://kiro.dev/docs/getting-started/first-project/",
        "https://kiro.dev/docs/models/available-models/",
    ],
)
def test_a_sibling_of_an_excluded_page_stays_in_scope(url: str) -> None:
    """A page-level exclusion never drops its whole section."""
    assert page_for(url) is not None


def test_an_exclusion_matches_whole_path_segments_only() -> None:
    """An entry excludes its subtree, never a path that merely extends it."""
    assert is_excluded("voice")
    assert is_excluded("terminal-ui/comparison")
    assert not is_excluded("voice-notes")
    assert not is_excluded("terminal-uix")


def test_no_dropped_section_is_still_tracked() -> None:
    """A section excluded wholesale is absent from CLI_SECTIONS too."""
    assert not EXCLUDED_PATHS & CLI_SECTIONS


def test_discovery_resolves_every_shape_in_the_sitemap(
    source: KiroSource, offline: None
) -> None:
    """Only in-scope pages are discovered, ordered by mirror path."""
    assert [page.relative_path for page in source.discover()] == EXPECTED_PATHS


def test_a_page_advertised_under_both_forms_is_mirrored_once() -> None:
    """The canonical URL wins, so no path is written twice."""
    pages = select_pages(
        [
            "https://kiro.dev/docs/cli/hooks/",
            "https://kiro.dev/docs/hooks/",
        ]
    )
    assert [page.url for page in pages] == ["https://kiro.dev/docs/hooks.md"]


def test_the_canonical_page_wins_over_the_legacy_stub(
    source: KiroSource, paths: MirrorPaths, offline: None
) -> None:
    """A relocated page is mirrored from its new URL, not its stub."""
    sync(source, paths)
    assert (paths.refs_dir / "hooks.md").read_bytes() == PAGES[
        "https://kiro.dev/docs/hooks.md"
    ]


def test_get_doc_pages_reads_the_sitemap(offline: None) -> None:
    """The sitemap is the discovery mechanism."""
    assert [page.relative_path for page in get_doc_pages()] == EXPECTED_PATHS


def test_sync_downloads_new_pages(
    source: KiroSource, paths: MirrorPaths, offline: None
) -> None:
    """A first run writes every page and the marker."""
    counts = sync(source, paths)
    assert (counts.new, counts.updated, counts.unchanged, counts.failed) == (4, 0, 0, 0)
    assert (paths.refs_dir / "setup.md").read_bytes() == b"# Setup\n"
    assert (paths.refs_dir / "mcp" / "usage.md").is_file()
    assert (paths.refs_dir / "chat" / "context.md").is_file()
    marker = json.loads(paths.marker_path.read_text(encoding="utf-8"))
    assert marker["pages_total"] == 4
    assert marker["source"] == "sitemap"
    assert marker["base_url"] == BASE_URL


def test_sync_detects_updated_and_unchanged_pages(
    source: KiroSource, paths: MirrorPaths, offline: None
) -> None:
    """Only changed content counts as an update."""
    sync(source, paths)
    (paths.refs_dir / "setup.md").write_bytes(b"# Stale\n")
    counts = sync(source, paths)
    assert (counts.new, counts.updated, counts.unchanged) == (0, 1, 3)
    assert (paths.refs_dir / "setup.md").read_bytes() == b"# Setup\n"


def test_dry_run_writes_nothing(
    source: KiroSource, paths: MirrorPaths, offline: None
) -> None:
    """A dry run reports changes without touching the disk."""
    counts = sync(source, paths, dry_run=True)
    assert counts.new == 4
    assert counts.has_pending_changes
    assert not paths.refs_dir.exists()
    assert not paths.marker_path.exists()


def test_sync_counts_failed_downloads(
    source: KiroSource,
    paths: MirrorPaths,
    monkeypatch: pytest.MonkeyPatch,
    offline: None,
) -> None:
    """A page missing upstream is counted, not fatal."""
    monkeypatch.setattr(
        "docsync.sources.kiro.get_doc_pages",
        lambda: [*select_pages(["https://kiro.dev/docs/cli/gone/"]), *get_doc_pages()],
    )
    counts = sync(source, paths)
    assert counts.failed == 1
    assert counts.new == 4
    assert paths.marker_path.is_file()


def test_the_adapter_derives_known_slugs_from_the_discovered_pages(
    source: KiroSource, paths: MirrorPaths, offline: None
) -> None:
    """A mirrored page is never mistaken for an orphan."""
    sync(source, paths)
    stale = paths.refs_dir / "gone.md"
    stale.write_text("# Gone\n", encoding="utf-8")
    counts = sync(source, paths, prune=True)
    assert counts.orphans == 1
    assert not stale.exists()
    assert (paths.refs_dir / "mcp" / "usage.md").is_file()


def test_prune_removes_a_local_copy_of_an_excluded_page(
    source: KiroSource, paths: MirrorPaths, offline: None
) -> None:
    """An excluded page is never discovered, so pruning treats it as an orphan."""
    sync(source, paths)
    excluded = paths.refs_dir / "billing" / "managing-taxes.md"
    excluded.parent.mkdir(parents=True)
    excluded.write_text("# Taxes\n", encoding="utf-8")
    counts = sync(source, paths, prune=True)
    assert counts.orphans == 1
    assert not excluded.exists()
