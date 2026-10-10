"""
Tests for the Anthropic prompting documentation source.

Network access is always monkeypatched: the catalogue and the page
downloads are replaced by in-memory fixtures, so the suite is offline and
deterministic.
"""

# Standard libraries
import json
from pathlib import Path

# 3pps
import pytest

# Own modules
import docsync.net as net_module
from docsync.sources.anthropic import (
    CATALOGUE_URL,
    DOCS_PREFIX,
    TRACKED_PAGES,
    AnthropicSource,
    catalogue_slugs,
    get_doc_pages,
    is_in_scope,
    select_pages,
    slug_for,
)
from docsync.sync import sync
from docsync.types import MirrorPaths

# Slugs the fixture catalogue advertises on top of every tracked page:
# two prompting-subtree pages, and two out-of-scope pages standing for
# the rest of the upstream documentation.
SUBTREE_SLUGS = (
    "build-with-claude/prompt-engineering/overview",
    "build-with-claude/prompt-engineering/prompting-claude-opus-5",
)
FOREIGN_SLUGS = (
    "build-with-claude/embeddings",
    "test-and-evaluate/strengthen-guardrails/reduce-latency",
)


def catalogue_text(slugs: tuple[str, ...]) -> str:
    """
    Render a catalogue advertising the given slugs.

    The shape mirrors the upstream file: a heading, prose, and one
    Markdown link per page, some carrying a trailing description.

    Args:
        slugs: Documentation slugs to advertise.

    Returns:
        Catalogue text as llms.txt publishes it.
    """
    lines = [
        "# Anthropic Developer Documentation",
        "",
        "## English",
        "",
        "### Best practices",
        "",
    ]
    for index, slug in enumerate(slugs):
        suffix = " - A description" if index % 2 else ""
        lines.append(f"- [Title]({DOCS_PREFIX}{slug}.md){suffix}")
    lines.append("- [Not a docs page](https://www.anthropic.com/news/something)")
    return "\n".join(lines) + "\n"


FULL_CATALOGUE = catalogue_text(
    (*SUBTREE_SLUGS, *sorted(TRACKED_PAGES), *FOREIGN_SLUGS)
)
EXPECTED_PATHS = sorted(f"{slug}.md" for slug in (*SUBTREE_SLUGS, *TRACKED_PAGES))


@pytest.fixture()
def source() -> AnthropicSource:
    """
    Build the source under test.

    Returns:
        The Anthropic prompting documentation source.
    """
    return AnthropicSource()


@pytest.fixture()
def paths(source: AnthropicSource, tmp_path: Path) -> MirrorPaths:
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
        if url == CATALOGUE_URL:
            return FULL_CATALOGUE.encode("utf-8")
        if not url.startswith(DOCS_PREFIX):
            message = f"404 for {url}"
            raise OSError(message)
        return f"---\nurl: {url}\n---\n\nBody.\n".encode()

    monkeypatch.setattr(net_module, "fetch", fake_fetch)


def test_mirror_paths_follow_the_convention(
    source: AnthropicSource, tmp_path: Path
) -> None:
    """The mirror lives under the claude-prompting-reference skill."""
    mirror = source.mirror_paths(tmp_path)
    skill_dir = tmp_path / ".kiro" / "skills" / "claude-prompting-reference"
    assert mirror.refs_dir == skill_dir / "references"
    assert mirror.marker_path == skill_dir / ".last-sync.json"


def test_the_marker_sits_outside_the_pruned_directory(
    source: AnthropicSource, tmp_path: Path
) -> None:
    """Pruning walks refs_dir, so companion files stay above it."""
    mirror = source.mirror_paths(tmp_path)
    assert mirror.refs_dir not in mirror.marker_path.parents


def test_a_docs_url_reduces_to_its_slug() -> None:
    """The slug is the URL without the docs prefix and the suffix."""
    assert slug_for(f"{DOCS_PREFIX}build-with-claude/effort.md") == (
        "build-with-claude/effort"
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.anthropic.com/news/claude-opus-5",
        f"{DOCS_PREFIX}build-with-claude/effort",
        f"{DOCS_PREFIX}.md",
        "https://platform.claude.com/docs/es/build-with-claude/effort.md",
    ],
)
def test_a_foreign_or_unsuffixed_url_yields_no_slug(url: str) -> None:
    """Only English documentation pages in .md form are candidates."""
    assert slug_for(url) is None


def test_the_prompting_subtree_is_in_scope_by_prefix() -> None:
    """A new per-model guide needs no catalogue edit."""
    assert is_in_scope("build-with-claude/prompt-engineering/prompting-claude-x-9")


def test_a_tracked_page_is_in_scope_by_slug() -> None:
    """Pages outside the subtree are selected individually."""
    assert is_in_scope("build-with-claude/effort")


def test_a_sibling_of_a_tracked_page_is_out_of_scope() -> None:
    """Selecting a page never drags in its section."""
    assert not is_in_scope("build-with-claude/embeddings")


def test_catalogue_parsing_ignores_non_documentation_links() -> None:
    """Only links to English .md documentation pages are extracted."""
    slugs = catalogue_slugs(FULL_CATALOGUE)
    assert "build-with-claude/embeddings" in slugs
    assert all(not slug.startswith("http") for slug in slugs)


def test_selection_keeps_the_subtree_and_the_tracked_pages() -> None:
    """Scope is the prompting subtree plus the tracked slugs, sorted."""
    pages = select_pages(FULL_CATALOGUE)
    assert [page.relative_path for page in pages] == EXPECTED_PATHS


def test_the_mirror_path_mirrors_the_upstream_layout() -> None:
    """A page keeps its section, so no two slugs can collide."""
    pages = {page.relative_path: page.url for page in select_pages(FULL_CATALOGUE)}
    path = "build-with-claude/prompt-engineering/overview.md"
    assert pages[path] == f"{DOCS_PREFIX}{path}"


def test_a_tracked_page_leaving_the_catalogue_is_an_error() -> None:
    """A deliberate choice is never dropped silently."""
    reduced = catalogue_text((*SUBTREE_SLUGS, *sorted(TRACKED_PAGES)[1:]))
    with pytest.raises(ValueError, match="no longer advertised"):
        select_pages(reduced)


def test_get_doc_pages_reads_the_catalogue(offline: None) -> None:
    """The catalogue is the discovery mechanism."""
    assert [page.relative_path for page in get_doc_pages()] == EXPECTED_PATHS


def test_sync_writes_every_page_and_the_marker(
    source: AnthropicSource, paths: MirrorPaths, offline: None
) -> None:
    """A first run mirrors the whole selection."""
    counts = sync(source, paths)
    assert (counts.new, counts.updated, counts.unchanged, counts.failed) == (
        len(EXPECTED_PATHS),
        0,
        0,
        0,
    )
    mirrored = paths.refs_dir / "build-with-claude" / "effort.md"
    assert mirrored.read_text(encoding="utf-8").startswith("---\nurl: ")
    marker = json.loads(paths.marker_path.read_text(encoding="utf-8"))
    assert marker["pages_total"] == len(EXPECTED_PATHS)
    assert marker["source"] == "llms.txt"
    assert marker["catalogue_url"] == CATALOGUE_URL


def test_upstream_markdown_is_mirrored_verbatim(
    source: AnthropicSource, offline: None
) -> None:
    """Upstream already serves Markdown, so no transform applies."""
    raw = b"---\ntitle: Effort\n---\n\nBody.\n"
    assert source.transform(raw) == raw


def test_a_second_run_reports_everything_unchanged(
    source: AnthropicSource, paths: MirrorPaths, offline: None
) -> None:
    """Mirroring is idempotent, which is what the -check target relies on."""
    sync(source, paths)
    counts = sync(source, paths)
    assert (counts.new, counts.updated, counts.unchanged) == (
        0,
        0,
        len(EXPECTED_PATHS),
    )


def test_sync_rewrites_only_pages_that_changed(
    source: AnthropicSource, paths: MirrorPaths, offline: None
) -> None:
    """A stale page is refreshed and the rest are left alone."""
    sync(source, paths)
    stale = paths.refs_dir / "build-with-claude" / "effort.md"
    stale.write_text("# Stale\n", encoding="utf-8")
    counts = sync(source, paths, dry_run=False)
    assert (counts.new, counts.updated, counts.unchanged) == (
        0,
        1,
        len(EXPECTED_PATHS) - 1,
    )
    assert stale.read_text(encoding="utf-8").startswith("---\nurl: ")


def test_dry_run_writes_nothing(
    source: AnthropicSource, paths: MirrorPaths, offline: None
) -> None:
    """A dry run reports changes without touching the disk."""
    counts = sync(source, paths, dry_run=True)
    assert counts.new == len(EXPECTED_PATHS)
    assert counts.has_pending_changes
    assert not paths.refs_dir.exists()
    assert not paths.marker_path.exists()


def test_a_failed_download_blocks_the_marker(
    source: AnthropicSource, paths: MirrorPaths, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A partial mirror is never recorded as a successful sync."""

    def catalogue_only(url: str, retries: int = 3) -> bytes:
        if url == CATALOGUE_URL:
            return FULL_CATALOGUE.encode("utf-8")
        message = "network down"
        raise OSError(message)

    monkeypatch.setattr(net_module, "fetch", catalogue_only)
    counts = sync(source, paths)
    assert counts.failed == len(EXPECTED_PATHS)
    assert not paths.marker_path.exists()


def test_a_page_absent_from_the_catalogue_is_pruned(
    source: AnthropicSource, paths: MirrorPaths, offline: None
) -> None:
    """The catalogue enumerates the upstream, so orphans are real."""
    sync(source, paths)
    stale = paths.refs_dir / "build-with-claude" / "retired-guide.md"
    stale.write_text("# Retired\n", encoding="utf-8")
    counts = sync(source, paths, prune=True)
    assert counts.orphans == 1
    assert not stale.exists()
    assert (paths.refs_dir / "build-with-claude" / "effort.md").is_file()


def test_a_dry_run_reports_orphans_without_deleting(
    source: AnthropicSource, paths: MirrorPaths, offline: None
) -> None:
    """Pruning is never implicit, even when orphans are reported."""
    sync(source, paths)
    stale = paths.refs_dir / "build-with-claude" / "retired-guide.md"
    stale.write_text("# Retired\n", encoding="utf-8")
    counts = sync(source, paths, dry_run=True)
    assert counts.orphans == 1
    assert stale.is_file()
