"""Subtask fetching, title filtering and status grouping."""

# Standard libraries
import re

# Own modules
from jirafetcher.jira.client import JiraClient
from jirafetcher.types import JiraIssue

_SAFE_STATUS_RE: re.Pattern[str] = re.compile(r"^[\w\s\-]+$")


def _validate_status(status: str) -> str:
    """
    Validate that a status name is safe for JQL
    interpolation.

    Args:
        status: Status name to validate.

    Returns:
        The original status string if valid.

    Raises:
        ValueError: If the status contains unsafe
            characters.
    """

    if not _SAFE_STATUS_RE.fullmatch(status):
        raise ValueError(f"Invalid status name: {status!r}")
    return status


def fetch_subtasks(
    client: JiraClient, parent_key: str, statuses: list[str]
) -> list[JiraIssue]:
    """
    Fetch all subtasks of a parent issue whose status
    matches any of the given statuses.

    Builds a JQL query using ``parent = <key>`` combined
    with an OR clause over the requested statuses.

    Args:
        client: Authenticated Jira API client.
        parent_key: Jira issue key of the parent story.
        statuses: Status names to include in the query.

    Returns:
        List of raw issue dicts matching the criteria.

    Raises:
        ValueError: If statuses is empty or contains
            unsafe characters.
    """

    if not statuses:
        raise ValueError("At least one status is required.")

    status_clause: str = " OR ".join(
        f'status = "{_validate_status(s)}"' for s in statuses
    )
    jql: str = f"parent = {parent_key} AND ({status_clause}) ORDER BY key ASC"

    return client.search(jql)


def filter_by_title(issues: list[JiraIssue], title_filter: str) -> list[JiraIssue]:
    """
    Keep only issues whose summary contains the given
    substring.

    The comparison is case-insensitive.

    Args:
        issues: List of raw issue dicts from the Jira API.
        title_filter: Substring to match against each
            issue summary.

    Returns:
        Filtered list of issue dicts.
    """

    needle: str = title_filter.lower()

    return [i for i in issues if needle in (i["fields"].get("summary") or "").lower()]


def group_by_status(issues: list[JiraIssue]) -> dict[str, list[JiraIssue]]:
    """
    Group issues by their status name.

    Args:
        issues: List of raw issue dicts from the Jira API.

    Returns:
        Dictionary mapping each status name to its list
            of issues.
    """

    groups: dict[str, list[JiraIssue]] = {}

    for issue in issues:
        status: str = issue["fields"]["status"]["name"]
        groups.setdefault(status, []).append(issue)

    return groups
