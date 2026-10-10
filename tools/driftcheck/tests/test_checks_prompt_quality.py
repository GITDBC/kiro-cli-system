"""Tests for the prompt-quality checks."""

# Standard libraries
import re
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck.checks import prompt_quality
from driftcheck.checks.prompt_quality import (
    KNOWN_CONTRADICTIONS,
    ContradictionPair,
    check_known_contradictions,
    check_prompt_boundaries,
    check_severity_filtering,
)
from driftcheck.types import Severity, build_context
from tests.helpers import problems, severities, write

REVIEW_SKILL = Path(".kiro") / "skills" / "reviewing-code" / "SKILL.md"

# The mitigated form: a severity instruction next to an explicit
# emission bar. This is the shape reviewing-code carries, and it must
# not be flagged.
GOVERNED_REVIEW_BODY = """# Reviewing and Fixing Code

### Concrete finding bar

Emit a finding only when it clears this bar: a named `file:line`, a code
fragment, and a concrete proposed change. Severity and effort anchors are in
`references/finding-calibration.md`.

Only report findings that clear the bar above.
"""


def test_severity_filtering_flags_unmitigated_instruction(valid_root: Path) -> None:
    """A reporting floor with no stated bar lowers recall."""
    write(
        valid_root / REVIEW_SKILL,
        "# Review\n\nOnly report high-severity issues.\n",
    )
    warnings = problems(check_severity_filtering(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "reviewing-code/SKILL.md:3" in warnings[0].message
    assert "only-report" in warnings[0].message


def test_severity_filtering_flags_be_conservative(valid_root: Path) -> None:
    """ "Be conservative" is one of the phrases Anthropic names."""
    write(valid_root / REVIEW_SKILL, "# Review\n\nBe conservative when reporting.\n")
    warnings = problems(check_severity_filtering(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "be-conservative" in warnings[0].message


def test_severity_filtering_flags_no_nitpicking(valid_root: Path) -> None:
    """ "Don't nitpick" suppresses low-severity findings."""
    write(valid_root / REVIEW_SKILL, "# Review\n\nDon't nitpick on style.\n")
    assert len(problems(check_severity_filtering(build_context(valid_root)))) == 1


def test_severity_filtering_accepts_a_concrete_bar(valid_root: Path) -> None:
    """A stated finding bar governs the threshold instead of hiding it."""
    write(valid_root / REVIEW_SKILL, GOVERNED_REVIEW_BODY)
    assert problems(check_severity_filtering(build_context(valid_root))) == []


def test_severity_filtering_evaluates_a_skill_as_one_group(
    valid_root: Path,
) -> None:
    """The bar may sit in the SKILL.md and the instruction in a reference."""
    skill_dir = valid_root / ".kiro" / "skills" / "reviewing-code"
    write(skill_dir / "SKILL.md", GOVERNED_REVIEW_BODY)
    write(
        skill_dir / "references" / "finding-calibration.md",
        "# Calibration\n\nBe conservative: High means data corruption.\n",
    )
    assert problems(check_severity_filtering(build_context(valid_root))) == []


def test_severity_filtering_flags_a_reference_with_no_bar_anywhere(
    valid_root: Path,
) -> None:
    """The same reference is flagged when no file in the group states a bar."""
    skill_dir = valid_root / ".kiro" / "skills" / "reviewing-code"
    write(skill_dir / "SKILL.md", "# Review\n\nReview the diff.\n")
    write(
        skill_dir / "references" / "anchors.md",
        "# Anchors\n\nBe conservative: High means data corruption.\n",
    )
    warnings = problems(check_severity_filtering(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "references/anchors.md:3" in warnings[0].message


def test_severity_filtering_accepts_the_report_everything_remedy(
    valid_root: Path,
) -> None:
    """Anthropic's own remedy is reporting everything and filtering later."""
    write(
        valid_root / REVIEW_SKILL,
        "# Review\n\nOnly report issues you can name, and report everything you\n"
        "find rather than filtering during the pass.\n",
    )
    assert problems(check_severity_filtering(build_context(valid_root))) == []


def test_severity_filtering_allows_a_fixing_budget(valid_root: Path) -> None:
    """Fixing only Critical and High findings is not a reporting floor."""
    write(
        valid_root / REVIEW_SKILL,
        "# Review\n\nFix `Critical` and `High` findings, plus `Medium` at `XS`.\n",
    )
    assert problems(check_severity_filtering(build_context(valid_root))) == []


def test_severity_filtering_ignores_only_surface_prose(valid_root: Path) -> None:
    """ "They only surface if searched for" is prose, not an instruction."""
    write(
        valid_root / REVIEW_SKILL,
        "# Review\n\nLinters miss these, so they only surface if actively sought.\n",
    )
    assert problems(check_severity_filtering(build_context(valid_root))) == []


def test_severity_filtering_ignores_non_review_skills(valid_root: Path) -> None:
    """A statistics reference may legitimately advise being conservative."""
    write(
        valid_root / ".kiro" / "skills" / "statistical-analysis" / "SKILL.md",
        "# Stats\n\n- Be conservative with interpretation.\n",
    )
    assert problems(check_severity_filtering(build_context(valid_root))) == []


def test_severity_filtering_scans_agent_prompts(valid_root: Path) -> None:
    """Every agent prompt is in scope, with no allowlist to keep."""
    write(
        valid_root / ".kiro" / "prompts" / "orchestrator.md",
        "# Orchestrator\n\nOnly report critical problems to the user.\n",
    )
    warnings = problems(check_severity_filtering(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "prompts/orchestrator.md:3" in warnings[0].message


def test_severity_filtering_flags_stale_allowlist_entry(valid_root: Path) -> None:
    """An allowlisted skill that no longer exists is dead configuration."""
    skill_md = valid_root / REVIEW_SKILL
    skill_md.unlink()
    skill_md.parent.rmdir()
    warnings = problems(check_severity_filtering(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "REVIEW_ORIENTED_SKILLS exempts 'reviewing-code'" in warnings[0].message


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


def _make_pair(
    left_phrase: str = "left claim", right_phrase: str = "right claim"
) -> ContradictionPair:
    """Build a synthetic pair pointed at files that always exist."""
    return ContradictionPair(
        label="synthetic",
        left=".kiro/prompts/orchestrator.md",
        left_phrase=re.compile(re.escape(left_phrase), re.IGNORECASE),
        right=".kiro/steering/COMMON.md",
        right_phrase=re.compile(re.escape(right_phrase), re.IGNORECASE),
        explanation="both claims cannot hold at once",
    )


def test_known_contradictions_pass_on_an_empty_seed(valid_root: Path) -> None:
    """KNOWN_CONTRADICTIONS is empty, so the check reports nothing."""
    assert KNOWN_CONTRADICTIONS == ()
    assert problems(check_known_contradictions(build_context(valid_root))) == []


def test_known_contradictions_report_a_live_pair(
    valid_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Both phrases present is the contradiction the pair describes."""
    pair = _make_pair()
    monkeypatch.setattr(prompt_quality, "KNOWN_CONTRADICTIONS", (pair,))
    write(valid_root / pair.left, "# Orchestrator\n\nleft claim stated here.\n")
    write(valid_root / pair.right, "# Common\n\nright claim stated here.\n")
    warnings = problems(check_known_contradictions(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "synthetic" in warnings[0].message
    assert "prompts/orchestrator.md:3" in warnings[0].message
    assert "steering/COMMON.md:3" in warnings[0].message


def test_known_contradictions_flag_a_stale_pair(
    valid_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pair naming a deleted file can never fire again."""
    stale = ContradictionPair(
        label="gone",
        left=".kiro/prompts/removed.md",
        left_phrase=re.compile("never"),
        right=".kiro/steering/COMMON.md",
        right_phrase=re.compile("never"),
        explanation="nothing",
    )
    monkeypatch.setattr(prompt_quality, "KNOWN_CONTRADICTIONS", (stale,))
    warnings = problems(check_known_contradictions(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "stale pair" in warnings[0].message
    assert "does not exist" in warnings[0].message


def test_known_contradictions_flag_a_resolved_pair(
    valid_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One phrase missing, the other present, reads as resolved on purpose."""
    pair = _make_pair()
    monkeypatch.setattr(prompt_quality, "KNOWN_CONTRADICTIONS", (pair,))
    write(valid_root / pair.left, "# Orchestrator\n\nno matching claim here.\n")
    write(valid_root / pair.right, "# Common\n\nright claim stated here.\n")
    warnings = problems(check_known_contradictions(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "stale pair" in warnings[0].message
    assert "resolved on purpose" in warnings[0].message
    assert str(pair.left) in warnings[0].message


def test_known_contradictions_flag_a_pair_invalidated_by_rewrite(
    valid_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Neither phrase present reads as invalidated, not resolved."""
    pair = _make_pair()
    monkeypatch.setattr(prompt_quality, "KNOWN_CONTRADICTIONS", (pair,))
    write(valid_root / pair.left, "# Orchestrator\n\nunrelated content here.\n")
    write(valid_root / pair.right, "# Common\n\nalso unrelated content.\n")
    warnings = problems(check_known_contradictions(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "stale pair" in warnings[0].message
    assert "invalidated by an unrelated rewrite" in warnings[0].message
