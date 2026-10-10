"""Tests for console rendering and exit-code logic."""

# 3pps
import pytest

# Own modules
from driftcheck.report import report
from driftcheck.types import Finding, Severity


def test_report_returns_one_when_errors_exist(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Errors fail the run and print the failure line."""
    results = [("Section", [Finding(Severity.ERROR, "Section", "bad")])]
    assert report(results) == 1
    output = capsys.readouterr().out
    assert "Errors: 1 | Warnings: 0" in output
    assert "FAIL: Fix errors before proceeding." in output


def test_report_returns_zero_with_warnings_only(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Warnings alone pass the run."""
    results = [("Section", [Finding(Severity.WARNING, "Section", "meh")])]
    assert report(results) == 0
    assert "PASS with warnings." in capsys.readouterr().out


def test_report_returns_zero_when_clean(capsys: pytest.CaptureFixture[str]) -> None:
    """A clean run prints the all-green line."""
    results = [("Section", [Finding(Severity.OK, "Section", "fine")])]
    assert report(results) == 0
    output = capsys.readouterr().out
    assert "Errors: 0 | Warnings: 0" in output
    assert "PASS: All checks green." in output


def test_report_prints_section_headers_and_finding_lines(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Output keeps the historical console shape."""
    results = [("Resource references", [Finding(Severity.OK, "x", "a.json valid")])]
    report(results)
    output = capsys.readouterr().out
    assert "=== Agent System Drift Detection ===" in output
    assert "--- Resource references ---" in output
    assert "OK: a.json valid" in output
