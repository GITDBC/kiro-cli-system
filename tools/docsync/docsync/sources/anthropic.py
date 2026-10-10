"""
Mirror Anthropic's prompting documentation from platform.claude.com.

Discovery reads the published ``llms.txt`` catalogue, which lists every
documentation page as a Markdown link to its ``.md`` form. That makes it
the same kind of source of truth the sitemap is for kiro.dev: a page
enters the mirror by appearing there and leaves it by disappearing from
it, so pruning is meaningful and is offered.

Two selection rules decide what the mirror holds, because the upstream
set is far larger than the part this repository needs:

The prompt-engineering subtree is taken by prefix. Anthropic adds a
per-model prompting guide with every release, and a prefix rule picks up
a new one without an edit here — which is the whole point of mirroring
the subtree rather than a fixed list.

Everything else is taken by exact slug. Those pages sit in unrelated
sections (evaluation, guardrails, effort and thinking controls) whose
siblings are irrelevant to writing prompts, so a prefix would drag in
the entire section. An exact slug that disappears from the catalogue
raises instead of being silently dropped: the page was chosen
deliberately, so its removal is a decision to re-take, not a diff to
mirror.

Upstream serves these pages as Markdown with a YAML frontmatter block
naming the canonical URL, so the inherited identity transform applies
and each mirrored file carries its own attribution.
"""

# Standard libraries
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

# Own modules
from docsync import net
from docsync.orphans import prune_orphans
from docsync.sources.base import DocSource
from docsync.types import MirrorPaths, Page

CATALOGUE_URL: Final[str] = "https://platform.claude.com/llms.txt"
DOCS_PREFIX: Final[str] = "https://platform.claude.com/docs/en/"

# Subtree taken wholesale: every prompting guide, including the
# per-model ones added with each release.
SUBTREE: Final[str] = "build-with-claude/prompt-engineering/"

# Pages taken individually, by slug relative to DOCS_PREFIX. Each one is
# prompting guidance whose section siblings are not, so the subtree rule
# cannot reach it. A slug listed here and absent from the catalogue is an
# error rather than a silent removal.
TRACKED_PAGES: Final[frozenset[str]] = frozenset(
    {
        "build-with-claude/context-windows",
        "build-with-claude/effort",
        "build-with-claude/thinking",
        "test-and-evaluate/develop-tests",
        "test-and-evaluate/strengthen-guardrails/increase-consistency",
        "test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks",
        "test-and-evaluate/strengthen-guardrails/reduce-hallucinations",
        "test-and-evaluate/strengthen-guardrails/reduce-prompt-leak",
    }
)

# A Markdown link target in the catalogue: "[Title](<url>)". Only the
# URL is needed, since the local path is derived from it.
LINK_TARGET: Final[re.Pattern[str]] = re.compile(r"\]\((https://[^)\s]+)\)")

# Suffix every catalogue entry carries, and the one the mirror writes.
MARKDOWN_SUFFIX: Final[str] = ".md"


def slug_for(url: str) -> str | None:
    """
    Reduce a catalogue URL to its documentation slug.

    Args:
        url: Absolute URL as advertised in the catalogue.

    Returns:
        Slug relative to the documentation root without its suffix, or
        None when the URL is not an English documentation page.
    """
    if not url.startswith(DOCS_PREFIX) or not url.endswith(MARKDOWN_SUFFIX):
        return None
    slug = url[len(DOCS_PREFIX) : -len(MARKDOWN_SUFFIX)]
    return slug or None


def is_in_scope(slug: str) -> bool:
    """
    Report whether a slug belongs in the mirror.

    Args:
        slug: Documentation slug without its suffix.

    Returns:
        True when the slug is inside the prompting subtree or is tracked
        individually.
    """
    return slug.startswith(SUBTREE) or slug in TRACKED_PAGES


def catalogue_slugs(catalogue: str) -> list[str]:
    """
    Extract the documentation slugs the catalogue advertises.

    Args:
        catalogue: Full text of the upstream llms.txt file.

    Returns:
        Every advertised slug, deduplicated and sorted.
    """
    slugs = {
        slug
        for url in LINK_TARGET.findall(catalogue)
        if (slug := slug_for(url)) is not None
    }
    return sorted(slugs)


def select_pages(catalogue: str) -> list[Page]:
    """
    Resolve the catalogue into the pages the mirror should hold.

    Args:
        catalogue: Full text of the upstream llms.txt file.

    Returns:
        Pages to mirror, ordered by their path in the mirror.

    Raises:
        ValueError: If a slug listed in TRACKED_PAGES is absent from the
            catalogue, since the mirror would otherwise lose a page that
            was chosen deliberately without anyone noticing.
    """
    advertised = catalogue_slugs(catalogue)
    missing = TRACKED_PAGES - set(advertised)
    if missing:
        listed = ", ".join(sorted(missing))
        message = (
            f"tracked page(s) no longer advertised in {CATALOGUE_URL}: "
            f"{listed}. Update TRACKED_PAGES in docsync/sources/anthropic.py "
            "to record the decision."
        )
        raise ValueError(message)
    return [
        Page(
            url=f"{DOCS_PREFIX}{slug}{MARKDOWN_SUFFIX}",
            relative_path=f"{slug}{MARKDOWN_SUFFIX}",
        )
        for slug in advertised
        if is_in_scope(slug)
    ]


def get_doc_pages() -> list[Page]:
    """
    Fetch the catalogue and resolve the pages in scope.

    Returns:
        Pages to mirror, ordered by their path in the mirror.

    Raises:
        ValueError: If a tracked page left the catalogue.
    """
    return select_pages(net.fetch(CATALOGUE_URL).decode("utf-8"))


@dataclass(frozen=True)
class AnthropicSource(DocSource):
    """
    The Anthropic prompting documentation mirror.

    The catalogue enumerates the upstream, so a local file absent from
    it is a genuine orphan and pruning is offered. A page that fails to
    download invalidates the run: the mirror is read as current guidance,
    and a silently partial one is worse than a stale one, so the marker
    is withheld and the CLI exits non-zero.
    """

    name: str = "anthropic"
    supports_prune: bool = True
    strict_failures: bool = True

    def mirror_paths(self, root: Path) -> MirrorPaths:
        """
        Build the conventional locations inside a repository.

        The marker sits at the skill root rather than inside the mirror
        directory, because pruning walks that directory for every .md
        file and would report any hand-maintained companion file there
        as an orphan.

        Args:
            root: Repository root.

        Returns:
            Paths for the vendored claude-prompting-reference mirror.
        """
        skill_dir = root / ".kiro" / "skills" / "claude-prompting-reference"
        return MirrorPaths(
            refs_dir=skill_dir / "references",
            marker_path=skill_dir / ".last-sync.json",
        )

    def discover(self) -> list[Page]:
        """
        List the prompting pages the catalogue currently advertises.

        Returns:
            One page per in-scope catalogue entry.

        Raises:
            ValueError: If a tracked page left the catalogue.
        """
        return get_doc_pages()

    def provenance(self) -> dict[str, str]:
        """
        Describe the upstream the marker file records.

        Returns:
            Discovery mechanism, catalogue URL and documentation root.
        """
        return {
            "source": "llms.txt",
            "catalogue_url": CATALOGUE_URL,
            "docs_base_url": DOCS_PREFIX,
        }

    def prune(self, paths: MirrorPaths, pages: list[Page], dry_run: bool) -> int:
        """
        Report or remove local pages absent from the catalogue.

        Args:
            paths: Mirror locations.
            pages: Pages discovered in this run.
            dry_run: If True, only report orphans without deleting.

        Returns:
            Number of orphan files detected.
        """
        known = {Path(page.relative_path).with_suffix("").as_posix() for page in pages}
        return prune_orphans(paths, known, dry_run=dry_run)
