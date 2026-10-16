"""Tests for the vendored-mirror page-count check."""

# Standard libraries
import json
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck.checks.mirrors import MIRRORED_SKILLS, check_mirror_page_count
from driftcheck.types import Severity, build_context
from tests.helpers import problems, severities, write

SKILL = "claude-prompting-reference"


def _write_mirror(root: Path, skill: str, marker: object, pages: int) -> Path:
    """
    Write a sync marker and a number of mirrored pages for one skill.

    Args:
        root: Repository root.
        skill: Skill directory name.
        marker: Marker payload, JSON-encoded unless already a string.
        pages: Number of .md files to create, one of them nested.

    Returns:
        The skill directory.
    """
    skill_dir = root / ".kiro" / "skills" / skill
    payload = marker if isinstance(marker, str) else json.dumps(marker)
    write(skill_dir / ".last-sync.json", payload)
    for index in range(pages):
        write(skill_dir / "references" / "nested" / f"page-{index}.md", "# Page\n")
    return skill_dir


def test_mirror_without_marker_is_skipped(valid_root: Path) -> None:
    """A skill that was never synced produces no warning."""
    findings = check_mirror_page_count(build_context(valid_root))
    assert problems(findings) == []
    assert severities(findings) == [Severity.OK]


@pytest.mark.parametrize("skill", MIRRORED_SKILLS)
def test_matching_count_is_clean(valid_root: Path, skill: str) -> None:
    """A mirror holding exactly pages_total pages passes."""
    _write_mirror(valid_root, skill, {"pages_total": 3}, pages=3)
    assert problems(check_mirror_page_count(build_context(valid_root))) == []


def test_surplus_page_is_reported(valid_root: Path) -> None:
    """An unpruned orphan makes the count exceed pages_total."""
    _write_mirror(valid_root, SKILL, {"pages_total": 2}, pages=3)
    found = problems(check_mirror_page_count(build_context(valid_root)))
    assert severities(found) == [Severity.WARNING]
    assert f"skills/{SKILL}/references holds 3 .md file(s)" in found[0].message
    assert "pages_total=2" in found[0].message


def test_missing_references_dir_counts_zero(valid_root: Path) -> None:
    """A marker with no mirrored pages at all is a shortfall."""
    _write_mirror(valid_root, SKILL, {"pages_total": 1}, pages=0)
    found = problems(check_mirror_page_count(build_context(valid_root)))
    assert severities(found) == [Severity.WARNING]
    assert "holds 0 .md file(s)" in found[0].message


def test_companion_files_outside_references_are_ignored(valid_root: Path) -> None:
    """SKILL.md and PROVENANCE.md at the skill root are not pages."""
    skill_dir = _write_mirror(valid_root, SKILL, {"pages_total": 1}, pages=1)
    write(skill_dir / "PROVENANCE.md", "# Provenance\n")
    assert problems(check_mirror_page_count(build_context(valid_root))) == []


@pytest.mark.parametrize(
    "marker",
    [
        "{not json",
        "[1, 2]",
        {"new": 0},
        {"pages_total": "3"},
        {"pages_total": True},
    ],
    ids=["invalid-json", "not-a-mapping", "absent", "string", "boolean"],
)
def test_unusable_pages_total_is_reported(valid_root: Path, marker: object) -> None:
    """A marker without an integer pages_total cannot be validated."""
    _write_mirror(valid_root, SKILL, marker, pages=1)
    found = problems(check_mirror_page_count(build_context(valid_root)))
    assert severities(found) == [Severity.WARNING]
    assert "has no integer 'pages_total'" in found[0].message
