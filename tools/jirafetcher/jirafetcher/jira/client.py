"""Minimal Jira REST client and Jira URL parsing."""

# Standard libraries
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import ParseResult, urlparse

# 3pps
import requests

# Own modules
from jirafetcher.types import JiraIssue

logger: logging.Logger = logging.getLogger(__name__)

ISSUE_FIELDS: str = (
    "summary,status,description,assignee,priority,created,updated,comment"
)

_MAX_RETRIES: int = 3
_RETRYABLE_STATUS: set[int] = {429, 502, 503, 504}


@dataclass
class JiraClient:
    """
    Jira REST API client using Bearer token authentication.

    Provides paginated search, issue transitions, and
    comment creation over the Jira REST API v2.
    """

    base_url: str
    token: str = field(repr=False)
    timeout: int = 30

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # ------------------------------------------------------------------
    # Low-level request with retry
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> requests.Response:
        """
        Execute an HTTP request with retry on transient
        errors and rate-limiting.

        Args:
            method: HTTP method (GET, POST, PUT).
            path: API path appended to base_url.
            params: Query parameters.
            json_body: JSON body for POST/PUT.

        Returns:
            The successful response.

        Raises:
            requests.HTTPError: After exhausting retries.
        """

        url: str = f"{self.base_url}{path}"

        for attempt in range(_MAX_RETRIES):
            resp: requests.Response = requests.request(
                method,
                url,
                headers=self._headers,
                params=params,
                json=json_body,
                timeout=self.timeout,
            )

            if resp.status_code not in _RETRYABLE_STATUS:
                resp.raise_for_status()
                return resp

            wait: int = int(resp.headers.get("Retry-After", 2**attempt))
            logger.warning(
                "Retryable %d from %s, waiting %ds (attempt %d/%d).",
                resp.status_code,
                path,
                wait,
                attempt + 1,
                _MAX_RETRIES,
            )
            time.sleep(wait)

        resp.raise_for_status()
        return resp

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def search(self, jql: str, fields: str = ISSUE_FIELDS) -> list[JiraIssue]:
        """
        Execute a JQL query and return all matching issues.

        Automatically paginates through the full result set
        in batches of 100.

        Args:
            jql: JQL query string.
            fields: Comma-separated list of Jira fields to
                retrieve for each issue.

        Returns:
            List of raw issue dicts as returned by the
                Jira API.

        Raises:
            requests.HTTPError: On any non-2xx response.
        """

        issues: list[JiraIssue] = []
        start: int = 0
        max_results: int = 100

        while True:
            params: dict[str, str | int] = {
                "jql": jql,
                "startAt": start,
                "maxResults": max_results,
                "fields": fields,
            }

            resp = self._request("GET", "/rest/api/2/search", params=params)
            data: dict[str, Any] = resp.json()
            batch: list[JiraIssue] = data["issues"]
            issues.extend(batch)

            if len(batch) < max_results:
                break

            start += len(batch)

        return issues

    def get_issue(self, issue_key: str, fields: str = ISSUE_FIELDS) -> JiraIssue:
        """
        Fetch a single issue by key.

        Args:
            issue_key: Jira issue key (e.g. PROJ-123).
            fields: Comma-separated list of Jira fields to
                retrieve.

        Returns:
            Raw issue dict as returned by the Jira API.

        Raises:
            requests.HTTPError: On any non-2xx response.
        """

        resp = self._request(
            "GET",
            f"/rest/api/2/issue/{issue_key}",
            params={"fields": fields},
        )
        result: JiraIssue = resp.json()
        return result

    def get_transitions(self, issue_key: str) -> list[dict[str, Any]]:
        """
        Get available transitions for an issue.

        Args:
            issue_key: Jira issue key (e.g. PROJ-123).

        Returns:
            List of transition dicts with ``id`` and
            ``name`` keys.
        """

        resp = self._request(
            "GET",
            f"/rest/api/2/issue/{issue_key}/transitions",
        )
        result: list[dict[str, Any]] = resp.json().get("transitions", [])
        return result

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def transition_issue(self, issue_key: str, transition_id: str) -> None:
        """
        Transition an issue to a new status.

        Args:
            issue_key: Jira issue key.
            transition_id: ID of the target transition.

        Raises:
            requests.HTTPError: On failure.
        """

        self._request(
            "POST",
            f"/rest/api/2/issue/{issue_key}/transitions",
            json_body={"transition": {"id": transition_id}},
        )

    def add_comment(self, issue_key: str, body: str) -> dict[str, Any]:
        """
        Add a comment to an issue.

        Args:
            issue_key: Jira issue key.
            body: Plain-text comment body.

        Returns:
            Created comment dict from the API.

        Raises:
            requests.HTTPError: On failure.
        """

        resp = self._request(
            "POST",
            f"/rest/api/2/issue/{issue_key}/comment",
            json_body={"body": body},
        )
        result: dict[str, Any] = resp.json()
        return result


def parse_jira_url(url: str) -> tuple[str, str]:
    """
    Extract the base URL and issue key from a Jira
    browse URL.

    Args:
        url: Full Jira browse URL.

    Returns:
        Tuple of ``(base_url, issue_key)``.

    Raises:
        ValueError: If the URL is not HTTPS or the issue
            key cannot be extracted.
    """

    parsed: ParseResult = urlparse(url)
    base_url: str = f"{parsed.scheme}://{parsed.netloc}"

    if parsed.scheme != "https":
        raise ValueError(f"HTTPS required, got {parsed.scheme}:// in {url}")

    match: re.Match[str] | None = re.search(
        r"/browse/([A-Z][A-Z0-9_]+-\d+)", parsed.path
    )

    if not match:
        raise ValueError(f"Cannot extract issue key from URL: {url}")

    return base_url, match.group(1)
