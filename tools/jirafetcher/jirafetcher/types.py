"""Shared type aliases for Jira payloads."""

# Standard libraries
from typing import Any

# Changed: TypeAlias annotation -> PEP 695 type statement - Reason: Python 3.13
# baseline (ruff UP040).
type JiraIssue = dict[str, Any]
