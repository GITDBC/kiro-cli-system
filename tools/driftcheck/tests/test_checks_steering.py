"""Tests for the steering-layer checks."""

# Standard libraries
from pathlib import Path

# Own modules
from driftcheck.checks.steering import (
    check_docs_reachability,
    check_numbered_headers,
    check_orchestration_placement,
    check_steering_duplication,
)
from driftcheck.types import Severity, build_context
from tests.helpers import (
    COMMON_MD,
    ORCHESTRATOR_PROMPT,
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
    """ "## 2FA Setup" is a proper noun, not an enumeration."""
    write(
        valid_root / ".kiro" / "steering" / "domain.md",
        "## 2FA Setup\n\n## 3D Rendering\n",
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
    """A prompt with every section and nothing in steering is clean."""
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
    assert ".kiro/prompts/orchestrator.md" in errors[0].message


def test_orchestration_placement_detects_missing_prompt_sections(
    valid_root: Path,
) -> None:
    """A prompt that loses a section leaves the orchestrator without its rules."""
    write(valid_root / ".kiro" / "prompts" / "orchestrator.md", "# Orchestrator\n")
    errors = problems(check_orchestration_placement(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR] * 4
    assert "orchestrator prompt has no '## Routing' section" in errors[0].message


def test_orchestration_placement_detects_a_single_dropped_section(
    valid_root: Path,
) -> None:
    """Only the dropped section is reported."""
    prompt = valid_root / ".kiro" / "prompts" / "orchestrator.md"
    write(prompt, ORCHESTRATOR_PROMPT.replace("## Conductor", "## Composition"))
    errors = problems(check_orchestration_placement(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "'## Conductor' section" in errors[0].message


def test_orchestration_placement_rejects_demoted_section_heading(
    valid_root: Path,
) -> None:
    """A level-3 heading does not stand in for a required level-2 section."""
    prompt = valid_root / ".kiro" / "prompts" / "orchestrator.md"
    write(prompt, ORCHESTRATOR_PROMPT.replace("## Conductor", "### Conductor"))
    errors = problems(check_orchestration_placement(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]


def test_orchestration_placement_rejects_dispatcher_file_resources(
    valid_root: Path,
) -> None:
    """Subagents inherit a dispatcher's file:// resources, so it declares none."""
    write_agent(
        valid_root,
        "orchestrator",
        model="claude-sonnet-5.5",
        resources=["file://.kiro/steering/COMMON.md"],
        tools=["subagent/senior-developer"],
    )
    errors = problems(check_orchestration_placement(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "orchestrator.json declares file:// resource" in errors[0].message
    assert "inherit" in errors[0].message


def test_orchestration_placement_allows_skill_resources_on_dispatchers(
    valid_root: Path,
) -> None:
    """Only file:// resources are inherited; skills stay on the dispatcher."""
    write_agent(
        valid_root,
        "orchestrator",
        model="claude-sonnet-5.5",
        resources=["skill://.kiro/skills/reviewing-code/SKILL.md"],
        tools=["subagent/senior-developer"],
    )
    assert problems(check_orchestration_placement(build_context(valid_root))) == []


def test_docs_reachability_accepts_the_valid_tree(valid_root: Path) -> None:
    """With no docs/ directory there is nothing to strand."""
    assert problems(check_docs_reachability(build_context(valid_root))) == []


def test_docs_reachability_accepts_pointer_from_the_orchestrator_prompt(
    valid_root: Path,
) -> None:
    """A document named by an agent prompt is reachable."""
    write(valid_root / "docs" / "rationale.md", "# Rationale\n")
    write(
        valid_root / ".kiro" / "prompts" / "orchestrator.md",
        f"{ORCHESTRATOR_PROMPT}\nSee `docs/rationale.md` when challenged.\n",
    )
    assert problems(check_docs_reachability(build_context(valid_root))) == []


def test_docs_reachability_detects_unreferenced_file(
    valid_root: Path,
) -> None:
    """A document no always-on text names is unreachable."""
    write(valid_root / "docs" / "rationale.md", "# Rationale\n")
    findings = check_docs_reachability(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "docs/rationale.md is in no agent's resources" in errors[0].message


def test_docs_reachability_accepts_pointer_from_steering(
    valid_root: Path,
) -> None:
    """A steering pointer is enough, since steering is always loaded."""
    write(valid_root / "docs" / "rationale.md", "# Rationale\n")
    write(
        valid_root / ".kiro" / "steering" / "COMMON.md",
        f"{COMMON_MD}\nSee `docs/rationale.md` when challenged.\n",
    )
    assert problems(check_docs_reachability(build_context(valid_root))) == []


def test_docs_reachability_follows_pointers_between_files(
    valid_root: Path,
) -> None:
    """A pointer inside a reachable docs file reaches the next one."""
    write(valid_root / "docs" / "overview.md", "Argument: `rationale.md`.\n")
    write(valid_root / "docs" / "rationale.md", "# Rationale\n")
    write(
        valid_root / ".kiro" / "steering" / "COMMON.md",
        f"{COMMON_MD}\nSee `docs/overview.md`.\n",
    )
    assert problems(check_docs_reachability(build_context(valid_root))) == []


def test_docs_reachability_rejects_mutually_pointing_islands(
    valid_root: Path,
) -> None:
    """Two files naming only each other are still unreachable from a session."""
    write(valid_root / "docs" / "island-a.md", "See `island-b.md`.\n")
    write(valid_root / "docs" / "island-b.md", "See `island-a.md`.\n")
    errors = problems(check_docs_reachability(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR, Severity.ERROR]


def test_docs_reachability_rejects_self_reference(valid_root: Path) -> None:
    """A file naming its own path does not vouch for itself."""
    write(
        valid_root / "docs" / "rationale.md",
        "# Rationale\n\nThis is `docs/rationale.md`.\n",
    )
    findings = check_docs_reachability(build_context(valid_root))
    assert len(problems(findings)) == 1
