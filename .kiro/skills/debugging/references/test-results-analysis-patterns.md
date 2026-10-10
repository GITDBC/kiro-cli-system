# Test Results Analysis — Code Patterns

Reference code for analysing test execution results. Load when parsing test reports,
classifying failures, or computing coverage and flakiness metrics.

## Analysis Framework

```python
import logging
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class CoverageGap:
    """
    A file with coverage below the quality gate.

    Attributes:
        file_path: Path to the source file.
        coverage_pct: Current coverage percentage.
        risk_level: Assessed risk level.
        uncovered_lines: Number of uncovered lines.
    """

    file_path: Path
    coverage_pct: float
    risk_level: str
    uncovered_lines: int


@dataclass(slots=True, kw_only=True)
class TestAnalysisReport:
    """
    Comprehensive test analysis report.

    Attributes:
        total_tests: Total number of tests executed.
        passed: Number of passed tests.
        failed: Number of failed tests.
        skipped: Number of skipped tests.
        coverage_pct: Overall code coverage percentage.
        coverage_gaps: Files below coverage threshold.
        quality_gate_passed: Whether SonarQube gate passed.
        analyzed_at: Timestamp of the analysis.
    """

    total_tests: int
    passed: int
    failed: int
    skipped: int
    coverage_pct: float
    coverage_gaps: list[CoverageGap] = field(default_factory=list)
    quality_gate_passed: bool = False
    analyzed_at: datetime = field(
        default_factory=lambda: datetime.now(tz=UTC)
    )

    @property
    def pass_rate(self) -> float:
        """
        Calculate test pass rate.

        Returns:
            Pass rate as a percentage.
        """

        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100

    @property
    def is_release_ready(self) -> bool:
        """
        Assess release readiness.

        Returns:
            True if pass rate is 100% and quality gate passed.
        """

        return (
            self.pass_rate == 100.0
            and self.quality_gate_passed
        )


def analyze_coverage_gaps(
    coverage_data: dict[str, dict[str, float]],
    threshold: float = 80.0,
) -> list[CoverageGap]:
    """
    Identify files with coverage below threshold.

    Args:
        coverage_data: Per-file coverage data with line
            percentages.
        threshold: Minimum coverage percentage.

    Returns:
        List of coverage gaps sorted by risk level.
    """

    gaps: list[CoverageGap] = []

    for file_path, stats in coverage_data.items():
        pct = stats.get("line_pct", 0.0)
        if pct < threshold:
            risk = _assess_risk(pct, threshold)
            gaps.append(
                CoverageGap(
                    file_path=Path(file_path),
                    coverage_pct=pct,
                    risk_level=risk,
                    uncovered_lines=int(
                        stats.get("uncovered_lines", 0)
                    ),
                )
            )

    gaps.sort(key=lambda g: g.coverage_pct)
    logger.info(
        "[INFO] Found %d files below %.0f%% coverage.",
        len(gaps),
        threshold,
    )
    return gaps


def _assess_risk(coverage_pct: float, threshold: float) -> str:
    """
    Assess risk level based on coverage gap.

    Args:
        coverage_pct: Current coverage percentage.
        threshold: Target coverage threshold.

    Returns:
        Risk level string: critical, high, or medium.
    """

    gap = threshold - coverage_pct
    if gap > 50:
        return "critical"
    if gap > 25:
        return "high"
    return "medium"
```
