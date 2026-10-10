"""
Mirror the Kiro CLI documentation from https://kiro.dev/docs/.

Pages are discovered from the site sitemap, which is the canonical
source of truth: a page enters the mirror by appearing there and leaves
it by disappearing from it. Local files are never deleted unless pruning
is requested explicitly.

Upstream reorganised the documentation: sections that used to sit below
/docs/cli/ are now top-level /docs/<section>/, shared by every Kiro
product. Two consequences shape this module.

First, a relocated page keeps answering HTTP 200 at its old /docs/cli/
URL, but the body is a "# Moved" stub naming the new location. A status
code therefore cannot distinguish a live page from a relocated one, and
only the sitemap listing can. That is why discovery stays sitemap-driven
and why, when a page is advertised under both forms, the canonical
top-level URL is the one fetched.

Second, the mirror is a CLI reference, so it tracks /docs/cli/ plus the
top-level sections a CLI user needs, and ignores the sections belonging
to the other Kiro products.
"""

# Standard libraries
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Final

# Own modules
from docsync import net
from docsync.orphans import prune_orphans
from docsync.sources.base import DocSource
from docsync.types import MirrorPaths, Page

BASE_URL: Final[str] = "https://kiro.dev/docs"
SITEMAP_URL: Final[str] = "https://kiro.dev/sitemap.xml"
DOCS_PREFIX: Final[str] = f"{BASE_URL}/"

# The subtree the CLI documentation still occupies. Pages below it keep
# their position in the mirror with the section itself stripped, which is
# what the mirror layout has always encoded: /docs/cli/chat/context/ is
# mirrored as chat/context.md.
LEGACY_SECTION: Final[str] = "cli"

# Top-level sections a CLI reference needs. Each entry is either a
# section the mirror already covered before the restructure, or one whose
# own capability table marks the feature as available in the CLI. The
# sections of the other Kiro products (crew, ide, web, mobile) and the
# cross-product tutorial series (guides) are deliberately absent: a page
# outside this set is not mirrored, so extending the mirror is an edit
# here rather than a change to the shared engine.
CLI_SECTIONS: Final[frozenset[str]] = frozenset(
    {
        "billing",
        "checkpoints",
        "cloud-sessions",
        "compaction",
        "configuration",
        "custom-agents",
        "enterprise",
        "getting-started",
        "hooks",
        "how-kiro-works",
        "kiroignore",
        "mcp",
        "models",
        "permissions",
        "powers",
        "privacy-and-security",
        "reference",
        "skills",
        "specs",
        "steering",
        "tools",
        "upgrade-guides",
    }
)

LOCATION_TAG: Final[re.Pattern[str]] = re.compile(r"<loc>([^<]+)</loc>")


def page_for(url: str) -> Page | None:
    """
    Map one sitemap URL to the page the mirror should hold.

    Sitemap entries carry a trailing slash, so the slug is taken with
    the surrounding slashes stripped. The mirror path drops the legacy
    /docs/cli/ section and keeps every other section, which is what
    makes a relocated page such as /docs/billing/managing-taxes/ land
    on the billing/managing-taxes.md it already occupies.

    Args:
        url: Absolute URL as advertised in the sitemap.

    Returns:
        Page to mirror, or None when the URL is a documentation index or
        belongs to a section outside the CLI reference.
    """
    if not url.startswith(DOCS_PREFIX):
        return None
    slug = url[len(DOCS_PREFIX) :].strip("/")
    if not slug:
        return None
    section, _, rest = slug.partition("/")
    if section == LEGACY_SECTION:
        if not rest:
            return None
        local = rest
    elif section in CLI_SECTIONS:
        local = slug
    else:
        return None
    return Page(url=f"{DOCS_PREFIX}{slug}.md", relative_path=f"{local}.md")


def _is_legacy(page: Page) -> bool:
    """
    Report whether a page was found under the legacy CLI subtree.

    Args:
        page: Page resolved from a sitemap entry.

    Returns:
        True when the page is fetched from below /docs/cli/.
    """
    return page.url.startswith(f"{DOCS_PREFIX}{LEGACY_SECTION}/")


def select_pages(urls: Iterable[str]) -> list[Page]:
    """
    Resolve sitemap URLs into exactly one page per mirror path.

    A relocated page can be advertised under both its legacy and its
    canonical URL, and both map to the same mirror path. Keeping both
    would write one local file twice, so the canonical form wins: the
    legacy URL of a relocated page serves a "Moved" stub instead of the
    documentation.

    Args:
        urls: Location values extracted from the sitemap.

    Returns:
        Pages to mirror, ordered by their path in the mirror.
    """
    chosen: dict[str, Page] = {}
    for url in sorted(set(urls)):
        page = page_for(url)
        if page is None:
            continue
        held = chosen.get(page.relative_path)
        if held is None or _is_legacy(held):
            chosen[page.relative_path] = page
    return [chosen[path] for path in sorted(chosen)]


def get_doc_pages() -> list[Page]:
    """
    Fetch the sitemap and resolve the pages in scope.

    Returns:
        Pages to mirror, ordered by their path in the mirror.
    """
    xml = net.fetch(SITEMAP_URL).decode("utf-8")
    return select_pages(LOCATION_TAG.findall(xml))


@dataclass(frozen=True)
class KiroSource(DocSource):
    """
    The kiro.dev CLI documentation mirror.

    Upstream serves Markdown directly, so no transform is needed and the
    inherited identity transform applies. The sitemap enumerates the
    pages, which is what makes pruning meaningful here.
    """

    name: str = "kiro"
    supports_prune: bool = True

    def mirror_paths(self, root: Path) -> MirrorPaths:
        """
        Build the conventional locations inside a repository.

        Args:
            root: Repository root.

        Returns:
            Paths for the vendored kiro-cli-reference mirror.
        """
        skill_dir = root / ".kiro" / "skills" / "kiro-cli-reference"
        return MirrorPaths(
            refs_dir=skill_dir / "references",
            marker_path=skill_dir / ".last-sync.json",
        )

    def discover(self) -> list[Page]:
        """
        List the CLI pages the sitemap currently advertises.

        Returns:
            One page per in-scope sitemap entry.
        """
        return get_doc_pages()

    def provenance(self) -> dict[str, str]:
        """
        Describe the upstream the marker file records.

        Returns:
            Discovery mechanism and documentation base URL.
        """
        return {"source": "sitemap", "base_url": BASE_URL}

    def prune(self, paths: MirrorPaths, pages: list[Page], dry_run: bool) -> int:
        """
        Report or remove local pages absent from the sitemap.

        Args:
            paths: Mirror locations.
            pages: Pages discovered in this run.
            dry_run: If True, only report orphans without deleting.

        Returns:
            Number of orphan files detected.
        """
        known = {Path(page.relative_path).with_suffix("").as_posix() for page in pages}
        return prune_orphans(paths, known, dry_run=dry_run)
