# SRE — Reliability Patterns

Reference patterns for the sre agent. Load when defining SLOs, configuring burn-rate
alerts, or building SLO monitoring automation.

## SLO Definition Framework

```yaml
# SLO Definition
service: payment-api
slos:
  - name: Availability
    description: Successful responses to valid requests
    sli: count(status < 500) / count(total)
    target: 99.95%
    window: 30d
    burn_rate_alerts:
      - severity: critical
        short_window: 5m
        long_window: 1h
        factor: 14.4
      - severity: warning
        short_window: 30m
        long_window: 6h
        factor: 6

  - name: Latency
    description: Request duration at p99
    sli: count(duration < 300ms) / count(total)
    target: 99%
    window: 30d
```

## SLO Status Automation

```python
import logging
from dataclasses import dataclass
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class SLOStatus:
    """
    Current SLO status for a service.

    Attributes:
        service: Service name.
        slo_name: SLO identifier.
        target: SLO target percentage.
        current: Current SLI value.
        budget_remaining: Remaining error budget percentage.
        window_elapsed: Percentage of SLO window elapsed.
        checked_at: Timestamp of the check.
    """

    service: str
    slo_name: str
    target: float
    current: float
    budget_remaining: float
    window_elapsed: float
    checked_at: datetime

    @property
    def is_burning_fast(self) -> bool:
        """
        Check if error budget is burning faster than expected.

        Returns:
            True if budget consumption exceeds window elapsed.
        """

        budget_consumed = 100.0 - self.budget_remaining
        expected_consumed = self.window_elapsed
        return budget_consumed > expected_consumed * 1.5


def check_slo_status(
    service: str,
    slo_name: str,
    target: float,
    current: float,
    window_elapsed: float,
) -> SLOStatus:
    """
    Check SLO status and calculate error budget.

    Args:
        service: Service name.
        slo_name: SLO identifier.
        target: SLO target as percentage (e.g. 99.95).
        current: Current SLI value as percentage.
        window_elapsed: Percentage of SLO window elapsed.

    Returns:
        SLO status with budget calculations.
    """

    error_budget_total = 100.0 - target
    error_budget_used = max(0.0, 100.0 - current)
    budget_remaining = max(
        0.0,
        ((error_budget_total - error_budget_used) / error_budget_total)
        * 100,
    )

    status = SLOStatus(
        service=service,
        slo_name=slo_name,
        target=target,
        current=current,
        budget_remaining=budget_remaining,
        window_elapsed=window_elapsed,
        checked_at=datetime.now(tz=UTC),
    )

    if status.is_burning_fast:
        logger.warning(
            "[WARNING] %s/%s: error budget burning fast "
            "(%.1f%% remaining, %.1f%% window elapsed).",
            service,
            slo_name,
            budget_remaining,
            window_elapsed,
        )
    else:
        logger.info(
            "[INFO] %s/%s: SLO healthy (%.2f%%, budget %.1f%%).",
            service,
            slo_name,
            current,
            budget_remaining,
        )

    return status
```
