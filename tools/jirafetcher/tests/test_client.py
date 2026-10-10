# Standard libraries
from unittest.mock import MagicMock, patch

# 3pps
import pytest

# Own modules
from jirafetcher.jira.client import JiraClient, parse_jira_url


def _mock_response(json_data: dict[str, object], status_code: int = 200) -> MagicMock:
    """Build a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.headers = {}
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = Exception(f"{status_code}")
    return resp


def test_parse_jira_url_valid() -> None:
    """
    Verify parse_jira_url extracts base URL and issue
    key from a valid Jira URL.
    """

    base, key = parse_jira_url("https://jira.example.com/browse/PROJ-123")
    assert base == "https://jira.example.com"
    assert key == "PROJ-123"


def test_parse_jira_url_invalid() -> None:
    """
    Verify parse_jira_url raises ValueError for URLs
    without a valid issue key.
    """

    with pytest.raises(ValueError, match="Cannot extract"):
        parse_jira_url("https://jira.example.com/not-valid")


def test_parse_jira_url_http_rejected() -> None:
    """
    Verify parse_jira_url rejects non-HTTPS URLs.
    """

    with pytest.raises(ValueError, match="HTTPS required"):
        parse_jira_url("http://jira.example.com/browse/PROJ-1")


def test_search_single_page() -> None:
    """
    Verify search returns all issues from a single
    page response.
    """

    resp = _mock_response({"issues": [{"key": "PROJ-1"}], "total": 1})
    client = JiraClient(base_url="https://jira.test", token="tok")
    with patch("jirafetcher.jira.client.requests.request", return_value=resp):
        result = client.search("parent = PROJ-1")
    assert len(result) == 1
    assert result[0]["key"] == "PROJ-1"


def test_search_multi_page() -> None:
    """
    Verify search paginates through multiple pages.
    """

    page1 = _mock_response(
        {
            "issues": [{"key": f"PROJ-{i}"} for i in range(100)],
            "total": 150,
        }
    )
    page2 = _mock_response(
        {
            "issues": [{"key": f"PROJ-{i}"} for i in range(100, 150)],
            "total": 150,
        }
    )
    client = JiraClient(base_url="https://jira.test", token="tok")
    with patch(
        "jirafetcher.jira.client.requests.request",
        side_effect=[page1, page2],
    ):
        result = client.search("parent = PROJ-1")
    assert len(result) == 150


def test_headers() -> None:
    """
    Verify _headers includes Bearer token and content
    type.
    """

    client = JiraClient(base_url="https://jira.test", token="my-token")
    h = client._headers
    assert h["Authorization"] == "Bearer my-token"
    assert h["Content-Type"] == "application/json"


def test_get_transitions() -> None:
    """
    Verify get_transitions returns the transitions list.
    """

    resp = _mock_response(
        {
            "transitions": [
                {"id": "31", "name": "Done"},
                {"id": "21", "name": "In Progress"},
            ],
        }
    )
    client = JiraClient(base_url="https://jira.test", token="tok")
    with patch("jirafetcher.jira.client.requests.request", return_value=resp):
        result = client.get_transitions("PROJ-1")
    assert len(result) == 2
    assert result[0]["name"] == "Done"


def test_transition_issue() -> None:
    """
    Verify transition_issue sends the correct payload.
    """

    resp = _mock_response({}, status_code=204)
    resp.raise_for_status = MagicMock()
    client = JiraClient(base_url="https://jira.test", token="tok")
    with patch("jirafetcher.jira.client.requests.request", return_value=resp) as mock:
        client.transition_issue("PROJ-1", "31")
    call_kwargs = mock.call_args
    assert call_kwargs[1]["json"] == {"transition": {"id": "31"}}


def test_add_comment() -> None:
    """
    Verify add_comment sends the correct payload and
    returns the response.
    """

    resp = _mock_response({"id": "10001", "body": "test comment"})
    client = JiraClient(base_url="https://jira.test", token="tok")
    with patch("jirafetcher.jira.client.requests.request", return_value=resp) as mock:
        result = client.add_comment("PROJ-1", "test comment")
    assert result["body"] == "test comment"
    call_kwargs = mock.call_args
    assert call_kwargs[1]["json"] == {"body": "test comment"}


def test_retry_on_429(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify _request retries on HTTP 429.
    """

    rate_limited = MagicMock()
    rate_limited.status_code = 429
    rate_limited.headers = {"Retry-After": "0"}

    success = _mock_response({"ok": True})

    client = JiraClient(base_url="https://jira.test", token="tok")
    with patch(
        "jirafetcher.jira.client.requests.request",
        side_effect=[rate_limited, success],
    ):
        with patch("jirafetcher.jira.client.time.sleep"):
            resp = client._request("GET", "/test")
    assert resp.json() == {"ok": True}


def test_retry_on_503(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify _request retries on HTTP 503.
    """

    error = MagicMock()
    error.status_code = 503
    error.headers = {}

    success = _mock_response({"ok": True})

    client = JiraClient(base_url="https://jira.test", token="tok")
    with patch(
        "jirafetcher.jira.client.requests.request",
        side_effect=[error, success],
    ):
        with patch("jirafetcher.jira.client.time.sleep"):
            resp = client._request("GET", "/test")
    assert resp.json() == {"ok": True}


def test_get_issue() -> None:
    """
    Verify get_issue issues a GET and returns the JSON
    body.
    """

    resp = _mock_response({"key": "PROJ-1", "fields": {"summary": "s"}})
    client = JiraClient(base_url="https://jira.test", token="tok")
    with patch("jirafetcher.jira.client.requests.request", return_value=resp) as mock:
        result = client.get_issue("PROJ-1")
    assert result["key"] == "PROJ-1"
    call_args = mock.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == "https://jira.test/rest/api/2/issue/PROJ-1"
    assert "fields" in call_args[1]["params"]
