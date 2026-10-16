"""Tests for the fetch and transition subcommands and main."""

# Standard libraries
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

# 3pps
import pytest
import requests

# Own modules
from jirafetcher.cli import (
    _build_parser,
    _cmd_fetch,
    _cmd_transition,
    _connect,
    _fetch_issues,
    _find_transition,
    _transition_one,
    main,
)
from jirafetcher.config import Config

URL: str = "https://jira.test/browse/PROJ-1"


def _issue(
    key: str, status: str = "In Review", summary: str = "s"
) -> dict[str, object]:
    """Build a minimal Jira issue payload."""
    return {"key": key, "fields": {"status": {"name": status}, "summary": summary}}


def _config(statuses: list[str] | None = None, title: str | None = None) -> Config:
    """Build a config without touching the filesystem."""
    return Config(token="t", statuses=statuses or ["In Review"], title_filter=title)


def _client() -> MagicMock:
    """Build a mock Jira client."""
    client = MagicMock()
    client.base_url = "https://jira.test"
    return client


def _parse(*argv: str) -> Namespace:
    """Parse argv with the real parser."""
    return _build_parser().parse_args(list(argv))


# ------------------------------------------------------------------
# _connect
# ------------------------------------------------------------------


def test_connect_missing_config_exits(tmp_path: Path) -> None:
    """Verify _connect exits 1 when no config source exists."""
    args = _parse("fetch", URL, "-c", str(tmp_path / "absent.json"))
    with (
        patch.dict("os.environ", {}, clear=True),
        pytest.raises(SystemExit, match="1"),
    ):
        _connect(args)


def test_connect_invalid_global_toml_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify a malformed global TOML config is reported, not raised."""
    cfg = tmp_path / "config.toml"
    cfg.write_text("[jirafetcher\n", encoding="utf-8")
    monkeypatch.setenv("WORK_AGENTS_CONFIG", str(cfg))
    args = _parse("fetch", URL, "-c", str(tmp_path / "absent.json"))
    with pytest.raises(SystemExit, match="1"):
        _connect(args)


def test_connect_invalid_url_exits(tmp_path: Path) -> None:
    """Verify _connect exits 1 on a URL without an issue key."""
    cfg = tmp_path / "config.json"
    cfg.write_text('{"token": "t"}', encoding="utf-8")
    args = _parse("fetch", "https://jira.test/nope", "-c", str(cfg))
    with pytest.raises(SystemExit, match="1"):
        _connect(args)


def test_connect_returns_client(tmp_path: Path) -> None:
    """Verify _connect builds a client for the URL's server."""
    cfg = tmp_path / "config.json"
    cfg.write_text('{"token": "t"}', encoding="utf-8")
    client, key, config = _connect(_parse("fetch", URL, "-c", str(cfg)))
    assert client.base_url == "https://jira.test"
    assert key == "PROJ-1"
    assert config.token == "t"


# ------------------------------------------------------------------
# _fetch_issues
# ------------------------------------------------------------------


def test_fetch_issues_applies_title_filter() -> None:
    """Verify the title filter narrows the fetched subtasks."""
    args = _parse("fetch", URL, "-t", "keep")
    subtasks = [_issue("P-2", summary="keep me"), _issue("P-3", summary="drop")]
    with patch("jirafetcher.cli.fetch_subtasks", return_value=subtasks):
        issues = _fetch_issues(args, _client(), "P-1", _config())
    assert [issue["key"] for issue in issues] == ["P-2"]


def test_fetch_issues_subtask_error_exits() -> None:
    """Verify a Jira API error while fetching subtasks exits 1."""
    args = _parse("fetch", URL)
    with (
        patch(
            "jirafetcher.cli.fetch_subtasks",
            side_effect=requests.ConnectionError("down"),
        ),
        pytest.raises(SystemExit, match="1"),
    ):
        _fetch_issues(args, _client(), "P-1", _config())


def test_fetch_issues_parent_error_exits() -> None:
    """Verify a Jira API error while fetching the parent exits 1."""
    client = _client()
    client.get_issue.side_effect = requests.HTTPError("404")
    with pytest.raises(SystemExit, match="1"):
        _fetch_issues(_parse("fetch", URL, "--self"), client, "P-1", _config())


# ------------------------------------------------------------------
# fetch
# ------------------------------------------------------------------


def _run_fetch(args: Namespace, issues: list[dict[str, object]]) -> MagicMock:
    """Run _cmd_fetch with mocked connection and subtasks."""
    with (
        patch(
            "jirafetcher.cli._connect",
            return_value=(_client(), "P-1", _config()),
        ),
        patch("jirafetcher.cli.fetch_subtasks", return_value=issues),
        patch("jirafetcher.cli.write_markdown_files") as write,
    ):
        _cmd_fetch(args)
    return write


def test_cmd_fetch_nothing_to_export() -> None:
    """Verify fetch writes nothing when no subtasks match."""
    write = _run_fetch(_parse("fetch", URL), [])
    write.assert_not_called()


def test_cmd_fetch_dry_run_writes_nothing() -> None:
    """Verify --dry-run lists issues without exporting."""
    write = _run_fetch(_parse("fetch", URL, "--dry-run"), [_issue("P-2")])
    write.assert_not_called()


def test_cmd_fetch_exports_grouped_issues(tmp_path: Path) -> None:
    """Verify fetch groups issues by status and writes them."""
    args = _parse("fetch", URL, "-o", str(tmp_path))
    write = _run_fetch(args, [_issue("P-2"), _issue("P-3", status="On Hold")])
    grouped, parent, out = write.call_args.args
    assert set(grouped) == {"In Review", "On Hold"}
    assert parent == "P-1"
    assert out == tmp_path


# ------------------------------------------------------------------
# transition
# ------------------------------------------------------------------


def test_find_transition_is_case_insensitive() -> None:
    """Verify the target status matches regardless of case."""
    client = _client()
    client.get_transitions.return_value = [{"id": "31", "name": "Done"}]
    assert _find_transition(client, "P-2", "done") == {"id": "31", "name": "Done"}
    assert _find_transition(client, "P-2", "Closed") is None


def test_transition_one_skips_issue_already_in_target() -> None:
    """Verify an issue already in the target status is skipped."""
    client = _client()
    args = _parse("transition", URL, "Done")
    assert _transition_one(client, _issue("P-2", status="done"), args) == "skipped"
    client.get_transitions.assert_not_called()


def test_transition_one_fails_without_transition() -> None:
    """Verify a missing workflow transition is a failure."""
    client = _client()
    client.get_transitions.return_value = []
    args = _parse("transition", URL, "Done")
    assert _transition_one(client, _issue("P-2"), args) == "failed"


def test_transition_one_dry_run_does_not_write() -> None:
    """Verify --dry-run reports success without transitioning."""
    client = _client()
    client.get_transitions.return_value = [{"id": "31", "name": "Done"}]
    args = _parse("transition", URL, "Done", "--dry-run")
    assert _transition_one(client, _issue("P-2"), args) == "success"
    client.transition_issue.assert_not_called()


def test_transition_one_applies_and_comments() -> None:
    """Verify a real transition writes the transition and the comment."""
    client = _client()
    client.get_transitions.return_value = [{"id": "31", "name": "Done"}]
    args = _parse("transition", URL, "Done", "-m", "closing")
    assert _transition_one(client, _issue("P-2"), args) == "success"
    client.transition_issue.assert_called_once_with("P-2", "31")
    client.add_comment.assert_called_once_with("P-2", "closing")


def test_transition_one_comment_failure_still_succeeds() -> None:
    """Verify a failed follow-up comment does not undo the transition."""
    client = _client()
    client.get_transitions.return_value = [{"id": "31", "name": "Done"}]
    client.add_comment.side_effect = requests.HTTPError("403")
    args = _parse("transition", URL, "Done", "-m", "closing")
    assert _transition_one(client, _issue("P-2"), args) == "success"


def test_transition_one_reports_api_failure() -> None:
    """Verify a Jira error during the transition is a failure."""
    client = _client()
    client.get_transitions.return_value = [{"id": "31", "name": "Done"}]
    client.transition_issue.side_effect = requests.HTTPError("409")
    args = _parse("transition", URL, "Done", "-m", "closing")
    assert _transition_one(client, _issue("P-2"), args) == "failed"
    client.add_comment.assert_not_called()


@pytest.mark.parametrize("dry_run", [False, True])
def test_cmd_transition_processes_every_issue(dry_run: bool) -> None:
    """Verify transition runs once per fetched issue."""
    argv = ["transition", URL, "Done", *(["--dry-run"] if dry_run else [])]
    client = _client()
    client.get_transitions.return_value = [{"id": "31", "name": "Done"}]
    with (
        patch(
            "jirafetcher.cli._connect",
            return_value=(client, "P-1", _config()),
        ),
        patch(
            "jirafetcher.cli.fetch_subtasks",
            return_value=[_issue("P-2"), _issue("P-3", status="Done")],
        ),
    ):
        _cmd_transition(_parse(*argv))
    assert client.transition_issue.call_count == (0 if dry_run else 1)


def test_cmd_transition_without_issues() -> None:
    """Verify transition stops early when nothing matches."""
    client = _client()
    with (
        patch(
            "jirafetcher.cli._connect",
            return_value=(client, "P-1", _config()),
        ),
        patch("jirafetcher.cli.fetch_subtasks", return_value=[]),
    ):
        _cmd_transition(_parse("transition", URL, "Done"))
    client.get_transitions.assert_not_called()


# ------------------------------------------------------------------
# main
# ------------------------------------------------------------------


def test_main_without_command_returns_1() -> None:
    """Verify main prints help and returns 1 with no subcommand."""
    assert main([]) == 1


def test_main_dispatches_subcommand() -> None:
    """Verify main runs the chosen subcommand and returns 0."""
    with patch("jirafetcher.cli._cmd_fetch") as fetch:
        assert main(["fetch", URL, "-v"]) == 0
    fetch.assert_called_once()
