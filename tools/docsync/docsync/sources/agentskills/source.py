"""
Vendor the Agent Skills documentation from the upstream repository.

The page catalogue is fixed, so a run downloads each known .mdx file,
converts it to plain Markdown and writes it only when the content
changed. Local files are never deleted: the catalogue in pages.py is the
only place a page enters or leaves the mirror.
"""

# Standard libraries
from dataclasses import dataclass
from pathlib import Path

# Own modules
from docsync.sources.agentskills.convert import convert_mdx
from docsync.sources.agentskills.pages import (
    PAGES,
    RAW_BASE_URL,
    UPSTREAM_BRANCH,
    UPSTREAM_LICENSE,
    UPSTREAM_REPOSITORY,
)
from docsync.sources.base import DocSource
from docsync.types import MirrorPaths, Page


@dataclass(frozen=True)
class AgentSkillsSource(DocSource):
    """
    The Agent Skills standard documentation mirror.

    Upstream serves Mintlify-flavoured MDX, so the transform decodes the
    payload, converts it and re-encodes. A fixed catalogue cannot orphan
    a local file, so pruning is not offered. A page that fails to
    download or convert invalidates the run, so that a partial mirror is
    never recorded as a successful sync.
    """

    name: str = "agentskills"
    strict_failures: bool = True

    def mirror_paths(self, root: Path) -> MirrorPaths:
        """
        Build the conventional locations inside a repository.

        The marker sits beside the pages it describes, inside the
        vendored subdirectory, so that the mirror is self-contained.

        Args:
            root: Repository root.

        Returns:
            Paths for the vendored Agent Skills mirror.
        """
        mirror_dir = (
            root / ".kiro" / "skills" / "agent-creation" / "references" / "agentskills"
        )
        return MirrorPaths(
            refs_dir=mirror_dir,
            marker_path=mirror_dir / ".last-sync.json",
        )

    def discover(self) -> list[Page]:
        """
        List the catalogued pages.

        Returns:
            One page per catalogue entry, in catalogue order.
        """
        return [Page(url=page.url, relative_path=page.filename) for page in PAGES]

    def provenance(self) -> dict[str, str]:
        """
        Describe the upstream the marker file records.

        Returns:
            Upstream repository, branch, licence and raw URL prefix.
        """
        return {
            "upstream_repository": UPSTREAM_REPOSITORY,
            "upstream_branch": UPSTREAM_BRANCH,
            "upstream_license": UPSTREAM_LICENSE,
            "raw_base_url": RAW_BASE_URL,
        }

    def transform(self, raw: bytes) -> bytes:
        """
        Convert an upstream MDX payload into Markdown bytes.

        Args:
            raw: Response body as fetched.

        Returns:
            Converted Markdown encoded as UTF-8.

        Raises:
            ValueError: If the page frontmatter is malformed.
            UnicodeDecodeError: If the payload is not valid UTF-8.
        """
        return convert_mdx(raw.decode("utf-8")).encode("utf-8")
