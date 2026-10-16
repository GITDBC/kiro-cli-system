"""
Checks over the vendored documentation mirrors.

docsync records ``pages_total`` in each mirror's sync marker: the number
of pages discovery returned on the last successful run. The mirror
directory should hold exactly that many ``.md`` files. A surplus means
an upstream removal that a sync without ``--prune`` left behind, or a
hand-added file; a shortfall means a page was deleted locally.

Only the mirrors whose marker sits at the skill root, beside a
``references/`` directory holding nothing but mirrored pages, are
checked. The agentskills mirror is left out: its marker and its
hand-maintained PROVENANCE.md live inside the mirror directory, so a
plain ``.md`` count does not measure the same set.
"""

# Standard libraries
import json
from pathlib import Path
from typing import Final

# Own modules
from driftcheck.hooks.references_freshness import MARKER_NAME
from driftcheck.paths import VENDORED_SKILL
from driftcheck.types import DriftContext, Finding, Severity

# Skills whose root holds a docsync marker and whose references/ holds
# only mirrored pages.
MIRRORED_SKILLS: Final[tuple[str, ...]] = (
    VENDORED_SKILL,
    "claude-prompting-reference",
)

SECTION_MIRROR_PAGE_COUNT: Final[str] = "Mirror page count"


def check_mirror_page_count(ctx: DriftContext) -> list[Finding]:
    """
    Verify each mirror holds as many pages as its marker records.

    A skill without a marker is skipped: it has never been synced, and
    the freshness hook already reports that case.

    Args:
        ctx: Shared check context.

    Returns:
        A warning per mismatched or unreadable marker, plus a trailing
        OK finding.
    """
    findings: list[Finding] = []
    for skill in MIRRORED_SKILLS:
        finding = _mirror_finding(ctx.skills_dir / skill)
        if finding is not None:
            findings.append(finding)
    findings.append(
        Finding(Severity.OK, SECTION_MIRROR_PAGE_COUNT, "Mirror page counts checked")
    )
    return findings


def _mirror_finding(skill_dir: Path) -> Finding | None:
    """
    Compare one mirror's recorded page count with its files.

    Args:
        skill_dir: Skill directory holding the marker.

    Returns:
        A warning describing the problem, or None when the counts agree
        or the skill has no marker.
    """
    marker = skill_dir / MARKER_NAME
    if not marker.is_file():
        return None
    label = f"skills/{skill_dir.name}"
    recorded = _recorded_pages(marker)
    if recorded is None:
        return Finding(
            Severity.WARNING,
            SECTION_MIRROR_PAGE_COUNT,
            f"{label}/{MARKER_NAME} has no integer 'pages_total' — "
            "the page count cannot be validated",
        )
    refs_dir = skill_dir / "references"
    actual = sum(1 for path in refs_dir.rglob("*.md") if path.is_file())
    if actual == recorded:
        return None
    return Finding(
        Severity.WARNING,
        SECTION_MIRROR_PAGE_COUNT,
        f"{label}/references holds {actual} .md file(s) but {MARKER_NAME} "
        f"records pages_total={recorded} — prune orphans or re-sync",
    )


def _recorded_pages(marker: Path) -> int | None:
    """
    Read ``pages_total`` from a sync marker.

    Args:
        marker: Path to the marker file.

    Returns:
        The recorded count, or None when the marker is unusable.
    """
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    pages = data.get("pages_total")
    if isinstance(pages, bool) or not isinstance(pages, int):
        return None
    return pages
