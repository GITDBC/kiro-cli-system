"""
Console rendering and exit-code logic for a drift run.

The output shape (section banners, "SEVERITY: message" lines, the
summary block and the three possible final lines) is contractual: CI
greps it and humans diff it between runs.
"""

# Standard libraries
from typing import Final

# Own modules
from driftcheck.types import Finding, Severity

TITLE: Final[str] = "=== Agent System Drift Detection ==="


def count_by_severity(
    results: list[tuple[str, list[Finding]]], severity: Severity
) -> int:
    """
    Count findings of a given severity across all sections.

    Args:
        results: Output of run_checks.
        severity: Severity to count.

    Returns:
        Number of matching findings.
    """
    return sum(
        1
        for _, findings in results
        for finding in findings
        if finding.severity is severity
    )


def report(results: list[tuple[str, list[Finding]]]) -> int:
    """
    Print the report and return the process exit code.

    Args:
        results: Output of run_checks.

    Returns:
        1 when any error was found, 0 otherwise.
    """
    print(TITLE)
    print()
    for section, findings in results:
        print(f"--- {section} ---")
        for finding in findings:
            print(finding.render())
        print()
    errors = count_by_severity(results, Severity.ERROR)
    warnings = count_by_severity(results, Severity.WARNING)
    print("=== Summary ===")
    print(f"Errors: {errors} | Warnings: {warnings}")
    if errors > 0:
        print("FAIL: Fix errors before proceeding.")
        return 1
    if warnings > 0:
        print("PASS with warnings.")
        return 0
    print("PASS: All checks green.")
    return 0
