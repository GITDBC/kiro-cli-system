"""Tests for the issue filters."""

# Standard libraries
from unittest.mock import MagicMock

# Own modules
from jirafetcher.jira.filters import fetch_subtasks, filter_by_title, group_by_status


def _issue(key: str, summary: str, status: str) -> dict[str, object]:
    """
    Build a minimal Jira issue dict for testing.

    Returns:
        Minimal issue dict.
    """

    return {
        "key": key,
        "fields": {
            "summary": summary,
            "status": {"name": status},
        },
    }


def test_fetch_subtasks_builds_jql() -> None:
    """
    Verify fetch_subtasks builds the correct JQL
    query and calls client.search.
    """

    client = MagicMock()
    client.search.return_value = []
    fetch_subtasks(client, "PROJ-1", ["In Review", "On Hold"])
    jql = client.search.call_args[0][0]
    assert "parent = PROJ-1" in jql
    assert 'status = "In Review"' in jql
    assert 'status = "On Hold"' in jql


def test_filter_by_title_match() -> None:
    """
    Verify filter_by_title keeps matching issues.
    """

    issues = [_issue("P-1", "[API] Fix bug", "Done")]
    result = filter_by_title(issues, "[API]")
    assert len(result) == 1


def test_filter_by_title_case_insensitive() -> None:
    """
    Verify filter_by_title is case-insensitive.
    """

    issues = [_issue("P-1", "API Fix", "Done")]
    result = filter_by_title(issues, "api")
    assert len(result) == 1


def test_filter_by_title_no_match() -> None:
    """
    Verify filter_by_title returns empty list when
    no issues match.
    """

    issues = [_issue("P-1", "Backend task", "Done")]
    result = filter_by_title(issues, "Frontend")
    assert result == []


def test_group_by_status() -> None:
    """
    Verify group_by_status groups issues correctly.
    """

    issues = [
        _issue("P-1", "A", "In Review"),
        _issue("P-2", "B", "On Hold"),
        _issue("P-3", "C", "In Review"),
    ]
    groups = group_by_status(issues)
    assert len(groups["In Review"]) == 2
    assert len(groups["On Hold"]) == 1
