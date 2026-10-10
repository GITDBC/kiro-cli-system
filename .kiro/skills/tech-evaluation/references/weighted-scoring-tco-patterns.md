# Weighted Scoring and TCO — Code Patterns

Reference code for weighted evaluation scoring and total-cost-of-ownership calculation.

## Evaluation Framework

```python
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class EvaluationCriteria:
    """
    A weighted evaluation criterion.

    Attributes:
        name: Criterion name.
        weight: Importance weight (0.0 to 1.0).
        description: What this criterion measures.
    """

    name: str
    weight: float
    description: str = ""


@dataclass(slots=True, kw_only=True)
class ToolScore:
    """
    Evaluation score for a single tool.

    Attributes:
        tool_name: Name of the evaluated tool.
        scores: Per-criterion scores (0-10).
        weighted_score: Calculated weighted total.
        notes: Per-criterion evaluation notes.
    """

    tool_name: str
    scores: dict[str, float] = field(default_factory=dict)
    weighted_score: float = 0.0
    notes: dict[str, str] = field(default_factory=dict)


EVALUATION_CRITERIA: list[EvaluationCriteria] = [
    EvaluationCriteria(
        name="functionality", weight=0.25,
        description="Core feature completeness",
    ),
    EvaluationCriteria(
        name="usability", weight=0.20,
        description="User experience and ease of use",
    ),
    EvaluationCriteria(
        name="performance", weight=0.15,
        description="Speed, reliability, scalability",
    ),
    EvaluationCriteria(
        name="security", weight=0.15,
        description="Data protection and compliance",
    ),
    EvaluationCriteria(
        name="integration", weight=0.10,
        description="API quality and ecosystem fit",
    ),
    EvaluationCriteria(
        name="support", weight=0.08,
        description="Vendor support and documentation",
    ),
    EvaluationCriteria(
        name="cost", weight=0.07,
        description="Total cost of ownership and value",
    ),
]


def calculate_weighted_score(
    scores: dict[str, float],
    criteria: list[EvaluationCriteria] | None = None,
) -> float:
    """
    Calculate weighted score from per-criterion scores.

    Args:
        scores: Per-criterion scores (0-10 scale).
        criteria: Evaluation criteria with weights. Uses
            defaults if not provided.

    Returns:
        Weighted total score.
    """

    if criteria is None:
        criteria = EVALUATION_CRITERIA

    total = sum(
        scores.get(c.name, 0.0) * c.weight for c in criteria
    )
    logger.info("[INFO] Weighted score calculated: %.2f.", total)
    return total


def calculate_tco(
    annual_license: float,
    implementation: float,
    training: float,
    annual_maintenance: float,
    users: int,
    years: int = 3,
) -> dict[str, float]:
    """
    Calculate total cost of ownership.

    Args:
        annual_license: Annual license cost.
        implementation: One-time implementation cost.
        training: One-time training cost.
        annual_maintenance: Annual maintenance cost.
        users: Expected number of users.
        years: Analysis period in years.

    Returns:
        Cost breakdown with total and per-user-year.
    """

    total = (
        (annual_license + annual_maintenance) * years
        + implementation
        + training
    )
    per_user_year = total / (users * years) if users > 0 else 0.0

    logger.info(
        "[INFO] TCO for %d years: $%.2f ($%.2f/user/year).",
        years,
        total,
        per_user_year,
    )
    return {
        "total": total,
        "per_user_year": per_user_year,
        "years": float(years),
    }
```
