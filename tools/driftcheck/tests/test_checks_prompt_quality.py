"""Tests for the prompt-quality checks."""

# Standard libraries
from pathlib import Path

# Own modules
from driftcheck.checks.prompt_quality import check_prompt_boundaries
from driftcheck.types import Severity, build_context
from tests.helpers import problems, severities, write


def test_prompt_boundaries_flag_missing_section(valid_root: Path) -> None:
    """A routable agent's prompt without boundaries is a warning."""
    write(
        valid_root / ".kiro" / "prompts" / "senior-developer.md",
        "# Senior developer\n\n## Workflow\n\nImplement the change.\n",
    )
    warnings = problems(check_prompt_boundaries(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "prompts/senior-developer.md has no boundary section" in warnings[0].message
    assert "senior-developer" in warnings[0].message


def test_prompt_boundaries_accept_alternative_heading(valid_root: Path) -> None:
    """A renamed boundary heading still counts as a scope statement."""
    write(
        valid_root / ".kiro" / "prompts" / "senior-developer.md",
        "# Senior developer\n\n## When not to use this agent\n\nArchitecture.\n",
    )
    assert problems(check_prompt_boundaries(build_context(valid_root))) == []


def test_prompt_boundaries_skip_non_routable_agents(valid_root: Path) -> None:
    """The orchestrator has no never_when entry, so it is not required."""
    write(valid_root / ".kiro" / "prompts" / "orchestrator.md", "# Orchestrator\n")
    assert problems(check_prompt_boundaries(build_context(valid_root))) == []


def test_prompt_boundaries_skip_unresolvable_prompt(valid_root: Path) -> None:
    """A missing prompt belongs to check_prompt_references, not here."""
    (valid_root / ".kiro" / "prompts" / "senior-developer.md").unlink()
    assert problems(check_prompt_boundaries(build_context(valid_root))) == []


def test_prompt_boundaries_fall_back_to_the_conventional_path(
    valid_root: Path,
) -> None:
    """A routable agent with no config is resolved by convention."""
    write(
        valid_root / ".kiro" / "orchestration" / "routing.md",
        "# Routing\n\n      - id: technical-writer\n",
    )
    write(valid_root / ".kiro" / "prompts" / "technical-writer.md", "# Writer\n")
    warnings = problems(check_prompt_boundaries(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "prompts/technical-writer.md" in warnings[0].message
