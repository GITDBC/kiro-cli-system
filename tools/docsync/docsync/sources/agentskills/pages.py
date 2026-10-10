"""
Catalogue of the upstream pages the mirror tracks.

The set is fixed and small by design: the mirror covers the format
specification plus the skill-creation guides, and nothing else from the
upstream documentation site. Listing the pages explicitly keeps the
source free of discovery machinery such as a sitemap crawl or a tree
listing.
"""

# Standard libraries
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Final

UPSTREAM_REPOSITORY: Final[str] = "agentskills/agentskills"
UPSTREAM_BRANCH: Final[str] = "main"
UPSTREAM_LICENSE: Final[str] = "CC-BY-4.0"
RAW_BASE_URL: Final[str] = (
    f"https://raw.githubusercontent.com/{UPSTREAM_REPOSITORY}/{UPSTREAM_BRANCH}"
)
DOCS_ROOT: Final[str] = "docs"


@dataclass(frozen=True)
class VendoredPage:
    """
    One upstream documentation page tracked by the mirror.

    Attributes:
        source_path: Path of the .mdx file in the upstream repository.
    """

    source_path: str

    @property
    def filename(self) -> str:
        """
        Return the local Markdown filename of the page.

        Returns:
            Slug of the upstream page with a .md suffix.
        """
        return f"{PurePosixPath(self.source_path).stem}.md"

    @property
    def route(self) -> str:
        """
        Return the site route the upstream page is published at.

        Returns:
            Absolute route such as "/skill-creation/quickstart".
        """
        relative = PurePosixPath(self.source_path).with_suffix("")
        return f"/{relative.relative_to(DOCS_ROOT).as_posix()}"

    @property
    def url(self) -> str:
        """
        Return the raw URL the page is fetched from.

        Returns:
            Absolute raw.githubusercontent.com URL.
        """
        return f"{RAW_BASE_URL}/{self.source_path}"


PAGES: Final[tuple[VendoredPage, ...]] = (
    VendoredPage("docs/specification.mdx"),
    VendoredPage("docs/skill-creation/quickstart.mdx"),
    VendoredPage("docs/skill-creation/best-practices.mdx"),
    VendoredPage("docs/skill-creation/optimizing-descriptions.mdx"),
    VendoredPage("docs/skill-creation/evaluating-skills.mdx"),
    VendoredPage("docs/skill-creation/using-scripts.mdx"),
)

# Site route to local filename, used to keep cross-references between
# vendored pages navigable once the pages sit in one flat directory.
ROUTE_TO_FILENAME: Final[dict[str, str]] = {page.route: page.filename for page in PAGES}
