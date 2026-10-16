"""Tests for the skill-tree checks."""

# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck.checks import skills
from driftcheck.checks.skills import (
    SECTION_STALE_REFS,
    SECTION_STALE_SKILL_MENTIONS,
    check_orphaned_skill_references,
    check_pattern_resource_wiring,
    check_skill_routing,
    check_stale_agent_references,
    check_stale_skill_mentions,
)
from driftcheck.registry import run_check
from driftcheck.types import Severity, build_context
from tests.helpers import SKILL_MD, problems, severities, write, write_agent


def test_skill_routing_detects_uncovered_skill(valid_root: Path) -> None:
    """A skill absent from routing.md is a warning."""
    write(valid_root / ".kiro" / "skills" / "lonely-skill" / "SKILL.md", "# Lonely\n")
    findings = check_skill_routing(build_context(valid_root))
    warnings = problems(findings)
    assert severities(warnings) == [Severity.WARNING]
    assert "lonely-skill" in warnings[0].message


def test_skill_routing_exempts_direct_invoke_skills(valid_root: Path) -> None:
    """Direct-invoke skills need no collaboration pattern."""
    write(valid_root / ".kiro" / "skills" / "commit-message" / "SKILL.md", "# C\n")
    assert problems(check_skill_routing(build_context(valid_root))) == []


def test_skill_routing_exempts_the_vendored_prompting_mirror(
    valid_root: Path,
) -> None:
    """A vendored documentation mirror is a reference, not a workflow."""
    assert "claude-prompting-reference" in skills.DIRECT_INVOKE_SKILLS
    write(
        valid_root / ".kiro" / "skills" / "claude-prompting-reference" / "SKILL.md",
        "# Claude prompting reference\n",
    )
    assert problems(check_skill_routing(build_context(valid_root))) == []


def test_skill_routing_flags_stale_direct_invoke_entry(
    valid_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An exemption for a deleted skill is a stale allowlist entry."""
    monkeypatch.setattr(
        skills,
        "DIRECT_INVOKE_SKILLS",
        skills.DIRECT_INVOKE_SKILLS | {"lint-validate"},
    )
    warnings = problems(check_skill_routing(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "DIRECT_INVOKE_SKILLS exempts 'lint-validate'" in warnings[0].message
    assert "stale allowlist entry" in warnings[0].message


def test_pattern_wiring_accepts_declared_skill(valid_root: Path) -> None:
    """A pattern row whose agent declares the skill is clean."""
    assert problems(check_pattern_resource_wiring(build_context(valid_root))) == []


def test_pattern_wiring_detects_skill_missing_from_resources(
    valid_root: Path,
) -> None:
    """A pattern row naming an agent that omits the skill is an error."""
    write_agent(
        valid_root,
        "senior-developer",
        resources=["file://.kiro/steering/COMMON.md"],
    )
    errors = problems(check_pattern_resource_wiring(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "skill 'reviewing-code'" in errors[0].message
    assert "senior-developer.json" in errors[0].message


def test_pattern_wiring_accepts_wildcard_resource(valid_root: Path) -> None:
    """A skill:// glob counts as declaring every skill it matches."""
    write_agent(
        valid_root,
        "senior-developer",
        resources=["skill://.kiro/skills/*/SKILL.md"],
    )
    assert problems(check_pattern_resource_wiring(build_context(valid_root))) == []


def test_pattern_wiring_exempts_orchestrator_only_skills(
    valid_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An allowlisted skill needs no specialist wiring."""
    monkeypatch.setattr(
        skills,
        "ORCHESTRATOR_ONLY_SKILLS",
        skills.ORCHESTRATOR_ONLY_SKILLS | {"reviewing-code"},
    )
    write_agent(
        valid_root,
        "senior-developer",
        resources=["file://.kiro/steering/COMMON.md"],
    )
    assert problems(check_pattern_resource_wiring(build_context(valid_root))) == []


def test_pattern_wiring_ignores_rows_without_an_exact_skill_cell(
    valid_root: Path,
) -> None:
    """A prose skill cell claims nothing, keeping the parse conservative."""
    write(
        valid_root / ".kiro" / "orchestration" / "routing.md",
        "## Collaboration Patterns\n\n"
        "| Task | Skill | Agents |\n"
        "| ---- | ----- | ------ |\n"
        "| Design | — (pattern only, no skill) | senior-developer |\n",
    )
    write_agent(
        valid_root,
        "senior-developer",
        resources=["file://.kiro/steering/COMMON.md"],
    )
    assert problems(check_pattern_resource_wiring(build_context(valid_root))) == []


def test_pattern_wiring_ignores_tables_outside_the_section(
    valid_root: Path,
) -> None:
    """Only the Collaboration Patterns section contributes rows."""
    write(
        valid_root / ".kiro" / "orchestration" / "routing.md",
        "## Quick Lookup\n\n"
        "| Agent | Skill |\n"
        "| ----- | ----- |\n"
        "| senior-developer | reviewing-code |\n\n"
        "## Routing Rules\n\nNothing here.\n",
    )
    write_agent(
        valid_root,
        "senior-developer",
        resources=["file://.kiro/steering/COMMON.md"],
    )
    assert problems(check_pattern_resource_wiring(build_context(valid_root))) == []


def test_orphaned_skill_references_detects_unmentioned_file(
    valid_root: Path,
) -> None:
    """A reference file absent from SKILL.md is unreachable."""
    write(
        valid_root / ".kiro" / "skills" / "reviewing-code" / "references" / "deep.md",
        "# Deep\n",
    )
    findings = check_orphaned_skill_references(build_context(valid_root))
    warnings = problems(findings)
    assert severities(warnings) == [Severity.WARNING]
    assert "deep.md" in warnings[0].message


def test_orphaned_skill_references_accept_mentioned_file(valid_root: Path) -> None:
    """A reference cited by its SKILL.md is reachable."""
    skill_dir = valid_root / ".kiro" / "skills" / "reviewing-code"
    write(skill_dir / "SKILL.md", SKILL_MD + "\nSee references/cited.md for detail.\n")
    write(skill_dir / "references" / "cited.md", "# Cited\n")
    assert problems(check_orphaned_skill_references(build_context(valid_root))) == []


def test_orphaned_skill_references_exclude_vendored_mirror(
    valid_root: Path,
) -> None:
    """The kiro-cli-reference mirror is exempt from the orphan check."""
    mirror = valid_root / ".kiro" / "skills" / "kiro-cli-reference"
    write(mirror / "SKILL.md", "# Kiro CLI reference mirror kept verbatim here.\n")
    write(mirror / "references" / "chat" / "subagents.md", "# Subagents\n")
    assert problems(check_orphaned_skill_references(build_context(valid_root))) == []


def test_stale_references_detect_retired_agent_name(valid_root: Path) -> None:
    """A patterns file naming no current agent is a warning."""
    write(
        valid_root
        / ".kiro"
        / "skills"
        / "reviewing-code"
        / "references"
        / "ghost-automator-patterns.md",
        "# Ghost\n",
    )
    findings = check_stale_agent_references(build_context(valid_root))
    warnings = problems(findings)
    assert severities(warnings) == [Severity.WARNING]
    assert "no agent named 'ghost-automator'" in warnings[0].message


def test_stale_references_allow_current_agent_name(valid_root: Path) -> None:
    """A patterns file naming a current agent is not stale."""
    write_agent(valid_root, "security-engineer")
    write(
        valid_root
        / ".kiro"
        / "skills"
        / "reviewing-code"
        / "references"
        / "security-engineer-patterns.md",
        "# Security engineer patterns\n",
    )
    assert problems(check_stale_agent_references(build_context(valid_root))) == []


def test_stale_references_allow_content_named_file(valid_root: Path) -> None:
    """A content-named patterns file has no role suffix to rot."""
    write(
        valid_root
        / ".kiro"
        / "skills"
        / "reviewing-code"
        / "references"
        / "finding-calibration-patterns.md",
        "# Calibration\n",
    )
    assert problems(check_stale_agent_references(build_context(valid_root))) == []


def test_stale_references_report_broken_roster_as_error(valid_root: Path) -> None:
    """An unreadable roster is an error, not a false accusation."""
    write(valid_root / ".kiro" / "agents" / "broken.json", "{not json")
    findings = run_check(
        SECTION_STALE_REFS,
        check_stale_agent_references,
        build_context(valid_root),
    )
    assert severities(findings) == [Severity.ERROR]
    assert "check failed to run" in findings[0].message


def test_stale_skill_mentions_detects_deleted_skill_in_frontmatter(
    valid_root: Path,
) -> None:
    """A description routing to a deleted skill is an error."""
    write(
        valid_root / ".kiro" / "skills" / "reviewing-code" / "SKILL.md",
        "---\nname: reviewing-code\ndescription: >\n"
        "  Not for code style/linting (use lint-validate).\n---\n\n# Reviewing\n",
    )
    findings = check_stale_skill_mentions(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "reviewing-code/SKILL.md" in errors[0].message
    assert "skill 'lint-validate'" in errors[0].message


def test_stale_skill_mentions_accepts_current_skill_reference(
    valid_root: Path,
) -> None:
    """A mention naming an existing skill resolves cleanly."""
    write(
        valid_root / ".kiro" / "skills" / "reviewing-code" / "SKILL.md",
        "---\nname: reviewing-code\ndescription: >\n"
        "  Not for proactive refactoring (use other-skill skill).\n"
        "---\n\n# Reviewing\n",
    )
    write(valid_root / ".kiro" / "skills" / "other-skill" / "SKILL.md", "# Other\n")
    assert problems(check_stale_skill_mentions(build_context(valid_root))) == []


def test_stale_skill_mentions_accepts_current_agent_cross_reference(
    valid_root: Path,
) -> None:
    """A parenthetical '(use <agent>)' cross-reference is not a skill claim."""
    write(
        valid_root / ".kiro" / "orchestration" / "routing.md",
        "## Collaboration Patterns\n\n"
        "- high-level architecture decisions (use senior-developer)\n",
    )
    assert problems(check_stale_skill_mentions(build_context(valid_root))) == []


def test_stale_skill_mentions_ignores_non_reference_hyphenated_slug(
    valid_root: Path,
) -> None:
    """A hyphenated slug outside the three mention shapes is not flagged."""
    write(
        valid_root / ".kiro" / "skills" / "reviewing-code" / "SKILL.md",
        "---\nname: reviewing-code\ndescription: >\n"
        "  Detects made-up-slug patterns without claiming they are skills.\n"
        "---\n\n# Reviewing\n",
    )
    assert problems(check_stale_skill_mentions(build_context(valid_root))) == []


def test_stale_skill_mentions_report_broken_roster_as_error(valid_root: Path) -> None:
    """An unreadable roster is an error, not a false accusation."""
    write(valid_root / ".kiro" / "agents" / "broken.json", "{not json")
    findings = run_check(
        SECTION_STALE_SKILL_MENTIONS,
        check_stale_skill_mentions,
        build_context(valid_root),
    )
    assert severities(findings) == [Severity.ERROR]
    assert "check failed to run" in findings[0].message
