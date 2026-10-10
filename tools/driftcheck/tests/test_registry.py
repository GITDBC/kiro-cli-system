"""Tests for the check registry and its crash isolation."""

# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck import registry
from driftcheck.registry import CHECKS, run_check, run_checks
from driftcheck.report import count_by_severity
from driftcheck.types import DriftContext, Finding, Severity, build_context
from tests.helpers import severities, write

EXPECTED_CHECKS = 27


def test_valid_tree_is_completely_clean(ctx: DriftContext) -> None:
    """A well-formed tree produces no errors and no warnings."""
    results = run_checks(ctx)
    assert count_by_severity(results, Severity.ERROR) == 0
    assert count_by_severity(results, Severity.WARNING) == 0


def test_every_check_is_registered() -> None:
    """The registry exposes every check exactly once."""
    assert len(CHECKS) == EXPECTED_CHECKS
    assert len({section for section, _ in CHECKS}) == EXPECTED_CHECKS


def test_crashing_check_becomes_an_error_finding(ctx: DriftContext) -> None:
    """A check that raises is reported as an error naming it."""

    def exploding(_: DriftContext) -> list[Finding]:
        raise RuntimeError("boom")

    findings = run_check("Made-up section", exploding, ctx)
    assert severities(findings) == [Severity.ERROR]
    assert "Made-up section check failed to run" in findings[0].message
    assert "boom" in findings[0].message


def test_crashing_check_does_not_stop_later_checks(
    ctx: DriftContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every section still runs when an early check explodes."""

    def exploding(_: DriftContext) -> list[Finding]:
        raise RuntimeError("boom")

    patched = ((CHECKS[0][0], exploding),) + CHECKS[1:]
    monkeypatch.setattr(registry, "CHECKS", patched)
    results = run_checks(ctx)
    assert len(results) == EXPECTED_CHECKS
    assert count_by_severity(results, Severity.ERROR) == 1
    assert count_by_severity(results, Severity.WARNING) == 0


def test_malformed_agent_config_keeps_every_check_running(
    valid_root: Path,
) -> None:
    """One bad config yields errors but never aborts the run."""
    write(valid_root / ".kiro" / "agents" / "broken.json", "{not json")
    results = run_checks(build_context(valid_root))
    assert len(results) == EXPECTED_CHECKS
    assert count_by_severity(results, Severity.ERROR) > 0
    sections_with_errors = {
        section
        for section, findings in results
        for finding in findings
        if finding.severity is Severity.ERROR
    }
    assert "Resource references" in sections_with_errors
    assert "Stale agent-named reference files" in sections_with_errors
