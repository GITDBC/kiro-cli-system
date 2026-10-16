"""Tests for the steering-layer checks."""

# Standard libraries
from pathlib import Path

# Own modules
from driftcheck.checks.steering import (
    check_numbered_headers,
    check_orchestration_placement,
    check_orchestration_reachability,
    check_steering_duplication,
)
from driftcheck.types import Severity, build_context
from tests.helpers import (
    COMMON_MD,
    DELEGATION_LIFECYCLE_MD,
    problems,
    severities,
    write,
    write_agent,
)


def test_steering_duplication_detects_copied_body(valid_root: Path) -> None:
    """A steering file reproducing a skill body is a warning."""
    body = "\n".join(
        f"This is a sufficiently long duplicated sentence number {index}."
        for index in range(10)
    )
    write(valid_root / ".kiro" / "steering" / "twin.md", body)
    write(valid_root / ".kiro" / "skills" / "twin" / "SKILL.md", body)
    findings = check_steering_duplication(build_context(valid_root))
    warnings = problems(findings)
    assert severities(warnings) == [Severity.WARNING]
    assert "twin.md overlaps 100%" in warnings[0].message


def test_steering_duplication_ignores_short_and_heading_lines(
    valid_root: Path,
) -> None:
    """Short lines and short headings do not count as duplication."""
    shared_noise = "## Rules\n- ok\n- fine\n"
    write(
        valid_root / ".kiro" / "steering" / "twin.md",
        shared_noise + "A unique steering sentence that is long enough to count.\n",
    )
    write(
        valid_root / ".kiro" / "skills" / "twin" / "SKILL.md",
        shared_noise + "A different skill sentence that is also long enough.\n",
    )
    assert problems(check_steering_duplication(build_context(valid_root))) == []


def test_steering_duplication_pairs_summary_file_with_its_skill(
    valid_root: Path,
) -> None:
    """A "-summary" steering file is compared to its base skill."""
    body = "\n".join(
        f"This is a sufficiently long duplicated sentence number {index}."
        for index in range(10)
    )
    write(valid_root / ".kiro" / "steering" / "twin-summary.md", body)
    write(valid_root / ".kiro" / "skills" / "twin" / "SKILL.md", body)
    findings = check_steering_duplication(build_context(valid_root))
    warnings = problems(findings)
    assert severities(warnings) == [Severity.WARNING]
    assert "twin-summary.md overlaps 100%" in warnings[0].message
    assert "skills/twin/SKILL.md" in warnings[0].message


def test_numbered_headers_detect_enumerated_heading(valid_root: Path) -> None:
    """An enumerated heading is a warning."""
    write(valid_root / ".kiro" / "steering" / "numbered.md", "## 1. Bogus\n")
    findings = check_numbered_headers(build_context(valid_root))
    warnings = problems(findings)
    assert severities(warnings) == [Severity.WARNING]
    assert "numbered.md:1: ## 1. Bogus" in warnings[0].message


def test_numbered_headers_detect_parenthesised_enumeration(
    valid_root: Path,
) -> None:
    """The "1)" enumeration form is also flagged."""
    write(valid_root / ".kiro" / "steering" / "numbered.md", "### 2) Second\n")
    assert len(problems(check_numbered_headers(build_context(valid_root)))) == 1


def test_numbered_headers_allow_proper_noun_heading(valid_root: Path) -> None:
    """ "## 3GPP Interfaces" is a proper noun, not an enumeration."""
    write(
        valid_root / ".kiro" / "steering" / "domain.md",
        "## 3GPP Interfaces\n\n## 5G Core\n",
    )
    assert problems(check_numbered_headers(build_context(valid_root))) == []


def test_numbered_headers_skip_import_section_comment_in_fence(
    valid_root: Path,
) -> None:
    """ "# 3pps" inside a fenced block is an import section header."""
    write(
        valid_root / ".kiro" / "steering" / "fenced.md",
        "# Conventions\n\n```python\n# Standard libraries\n# 3pps\nimport yaml\n```\n",
    )
    assert problems(check_numbered_headers(build_context(valid_root))) == []


def test_numbered_headers_skip_enumeration_inside_fence(valid_root: Path) -> None:
    """A numbered heading inside a fence is sample content."""
    write(
        valid_root / ".kiro" / "steering" / "fenced.md",
        "# Example\n\n```markdown\n## 1. Sample heading\n```\n",
    )
    assert problems(check_numbered_headers(build_context(valid_root))) == []


def test_numbered_headers_exclude_vendored_mirror(valid_root: Path) -> None:
    """The kiro-cli-reference mirror is exempt from the heading rule."""
    mirror = valid_root / ".kiro" / "skills" / "kiro-cli-reference" / "references"
    write(mirror / "chat" / "mcp.md", "## 1. Install the server\n")
    assert problems(check_numbered_headers(build_context(valid_root))) == []


def test_orchestration_placement_accepts_the_valid_tree(valid_root: Path) -> None:
    """Both files under .kiro/orchestration/ and referenced is clean."""
    assert problems(check_orchestration_placement(build_context(valid_root))) == []


def test_orchestration_placement_detects_file_back_in_steering(
    valid_root: Path,
) -> None:
    """A copy under .kiro/steering/ re-imposes the always-on cost."""
    write(valid_root / ".kiro" / "steering" / "routing.md", "# Routing\n")
    findings = check_orchestration_placement(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert ".kiro/steering/routing.md re-imposes" in errors[0].message


def test_orchestration_placement_detects_dropped_resource(
    valid_root: Path,
) -> None:
    """Dropping the resources entry strips the orchestrator's routing."""
    write_agent(
        valid_root,
        "orchestrator",
        model="claude-sonnet-5.5",
        resources=["file://.kiro/steering/COMMON.md"],
        toolsSettings={"subagent": {"availableAgents": ["senior-developer"]}},
    )
    findings = check_orchestration_placement(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR, Severity.ERROR]
    assert "no longer references .kiro/orchestration/routing.md" in errors[0].message


def test_orchestration_reachability_accepts_the_valid_tree(valid_root: Path) -> None:
    """Both files are declared resources, so both are reachable."""
    assert problems(check_orchestration_reachability(build_context(valid_root))) == []


def test_orchestration_reachability_detects_unreferenced_file(
    valid_root: Path,
) -> None:
    """An on-demand file no always-on text names is unreachable."""
    write(valid_root / ".kiro" / "orchestration" / "rationale.md", "# Rationale\n")
    findings = check_orchestration_reachability(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert ".kiro/orchestration/rationale.md is in no agent's resources" in (
        errors[0].message
    )


def test_orchestration_reachability_accepts_pointer_from_steering(
    valid_root: Path,
) -> None:
    """A steering pointer is enough, since steering is always loaded."""
    write(valid_root / ".kiro" / "orchestration" / "rationale.md", "# Rationale\n")
    write(
        valid_root / ".kiro" / "steering" / "COMMON.md",
        f"{COMMON_MD}\nSee `.kiro/orchestration/rationale.md` when challenged.\n",
    )
    assert problems(check_orchestration_reachability(build_context(valid_root))) == []


def test_orchestration_reachability_accepts_pointer_from_declared_resource(
    valid_root: Path,
) -> None:
    """A pointer inside a declared resource is equally always-on."""
    write(valid_root / ".kiro" / "orchestration" / "rationale.md", "# Rationale\n")
    write(
        valid_root / ".kiro" / "orchestration" / "delegation-lifecycle.md",
        f"{DELEGATION_LIFECYCLE_MD}\nArgument: `rationale.md`.\n",
    )
    assert problems(check_orchestration_reachability(build_context(valid_root))) == []


def test_orchestration_reachability_rejects_self_reference(valid_root: Path) -> None:
    """A file naming its own path does not vouch for itself."""
    write(
        valid_root / ".kiro" / "orchestration" / "rationale.md",
        "# Rationale\n\nThis is `.kiro/orchestration/rationale.md`.\n",
    )
    findings = check_orchestration_reachability(build_context(valid_root))
    assert len(problems(findings)) == 1
