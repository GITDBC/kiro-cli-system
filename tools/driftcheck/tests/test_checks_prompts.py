"""Tests for the prompt-file checks."""

# Standard libraries
from pathlib import Path

# Own modules
from driftcheck.checks.prompts import check_orphan_prompts, check_prompt_references
from driftcheck.types import Severity, build_context
from tests.helpers import problems, severities, write, write_agent


def test_prompt_references_detect_missing_prompt(valid_root: Path) -> None:
    """A prompt pointing at a missing file is an error."""
    write_agent(valid_root, "senior-developer", prompt="file://../prompts/gone.md")
    findings = check_prompt_references(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "missing prompt: ../prompts/gone.md" in errors[0].message


def test_prompt_references_accept_inline_prompt(valid_root: Path) -> None:
    """A non-file prompt is never resolved on disk."""
    write_agent(valid_root, "senior-developer", prompt="You are a developer.")
    assert problems(check_prompt_references(build_context(valid_root))) == []


def test_orphan_prompts_detects_unreferenced_file(valid_root: Path) -> None:
    """A prompt file no agent references is a warning."""
    write(valid_root / ".kiro" / "prompts" / "nobody.md", "# Nobody\n")
    findings = check_orphan_prompts(build_context(valid_root))
    warnings = problems(findings)
    assert severities(warnings) == [Severity.WARNING]
    assert "nobody.md" in warnings[0].message
