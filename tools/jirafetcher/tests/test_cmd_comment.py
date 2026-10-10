# Standard libraries
import io
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

# 3pps
import pytest

# Own modules
from jirafetcher.cli import _cmd_comment, _resolve_comment_body, build_parser


def _parse_comment(argv: list[str]) -> Namespace:
    """Parse argv for the comment subcommand."""
    return build_parser().parse_args(["comment", *argv])


def test_resolve_body_from_positional() -> None:
    """Verify positional body is returned verbatim."""
    args = _parse_comment(["https://jira.test/browse/P-1", "hello"])
    assert _resolve_comment_body(args) == "hello"


def test_resolve_body_from_file(tmp_path: Path) -> None:
    """Verify --file is read and returned as text."""
    path = tmp_path / "note.txt"
    path.write_text("from file", encoding="utf-8")
    args = _parse_comment(["https://jira.test/browse/P-1", "-f", str(path)])
    assert _resolve_comment_body(args) == "from file"


def test_resolve_body_from_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify stdin is read when no body/file and stdin is not a TTY."""
    stream = io.StringIO("piped body")
    stream.isatty = lambda: False  # type: ignore[method-assign]
    monkeypatch.setattr("jirafetcher.cli.sys.stdin", stream)
    args = _parse_comment(["https://jira.test/browse/P-1"])
    assert _resolve_comment_body(args) == "piped body"


def test_resolve_body_errors_on_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify TTY stdin without body/file exits with an error."""
    stream = io.StringIO("")
    stream.isatty = lambda: True  # type: ignore[method-assign]
    monkeypatch.setattr("jirafetcher.cli.sys.stdin", stream)
    args = _parse_comment(["https://jira.test/browse/P-1"])
    with pytest.raises(SystemExit):
        _resolve_comment_body(args)


def test_resolve_body_errors_on_both_sources() -> None:
    """Verify providing both body and --file exits with an error."""
    args = _parse_comment(
        ["https://jira.test/browse/P-1", "hello", "-f", "note.txt"],
    )
    with pytest.raises(SystemExit):
        _resolve_comment_body(args)


def test_cmd_comment_self_dry_run(tmp_path: Path) -> None:
    """Verify --self uses get_issue and skips fetch_subtasks in dry-run."""
    config = tmp_path / "config.json"
    config.write_text('{"token": "t"}', encoding="utf-8")
    argv = [
        "comment",
        "https://jira.test/browse/P-1",
        "body",
        "-c",
        str(config),
        "--self",
        "--dry-run",
    ]
    args = build_parser().parse_args(argv)
    client = MagicMock()
    client.base_url = "https://jira.test"
    client.get_issue.return_value = {"key": "P-1", "fields": {}}
    with patch(
        "jirafetcher.cli._connect",
        return_value=(client, "P-1", MagicMock(statuses=[], title_filter=None)),
    ):
        _cmd_comment(args)
    client.get_issue.assert_called_once_with("P-1")
    client.search.assert_not_called()
    client.add_comment.assert_not_called()


def test_cmd_comment_include_parent_dry_run(tmp_path: Path) -> None:
    """Verify --include-parent appends the parent to subtasks."""
    config = tmp_path / "config.json"
    config.write_text('{"token": "t"}', encoding="utf-8")
    argv = [
        "comment",
        "https://jira.test/browse/P-1",
        "body",
        "-c",
        str(config),
        "--include-parent",
        "--dry-run",
    ]
    args = build_parser().parse_args(argv)
    client = MagicMock()
    client.base_url = "https://jira.test"
    subtasks = [{"key": "P-2", "fields": {"summary": "a"}}]
    client.get_issue.return_value = {"key": "P-1", "fields": {"summary": "p"}}
    with (
        patch(
            "jirafetcher.cli._connect",
            return_value=(client, "P-1", MagicMock(statuses=[], title_filter=None)),
        ),
        patch("jirafetcher.cli.fetch_subtasks", return_value=subtasks),
    ):
        _cmd_comment(args)
    client.get_issue.assert_called_once_with("P-1")
    client.add_comment.assert_not_called()


def test_cmd_comment_body_from_file(tmp_path: Path) -> None:
    """Verify body read from --file is forwarded to add_comment."""
    config = tmp_path / "config.json"
    config.write_text('{"token": "t"}', encoding="utf-8")
    note = tmp_path / "note.txt"
    note.write_text("filed body", encoding="utf-8")
    argv = [
        "comment",
        "https://jira.test/browse/P-1",
        "-f",
        str(note),
        "-c",
        str(config),
        "--self",
    ]
    args = build_parser().parse_args(argv)
    client = MagicMock()
    client.get_issue.return_value = {"key": "P-1", "fields": {}}
    with patch(
        "jirafetcher.cli._connect",
        return_value=(client, "P-1", MagicMock(statuses=[], title_filter=None)),
    ):
        _cmd_comment(args)
    client.add_comment.assert_called_once_with("P-1", "filed body")


def test_cmd_comment_body_from_stdin(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify body read from stdin is forwarded to add_comment."""
    config = tmp_path / "config.json"
    config.write_text('{"token": "t"}', encoding="utf-8")
    stream = io.StringIO("stdin body")
    stream.isatty = lambda: False  # type: ignore[method-assign]
    monkeypatch.setattr("jirafetcher.cli.sys.stdin", stream)
    argv = [
        "comment",
        "https://jira.test/browse/P-1",
        "-c",
        str(config),
        "--self",
    ]
    args = build_parser().parse_args(argv)
    client = MagicMock()
    client.get_issue.return_value = {"key": "P-1", "fields": {}}
    with patch(
        "jirafetcher.cli._connect",
        return_value=(client, "P-1", MagicMock(statuses=[], title_filter=None)),
    ):
        _cmd_comment(args)
    client.add_comment.assert_called_once_with("P-1", "stdin body")


def test_resolve_body_errors_on_missing_file(tmp_path: Path) -> None:
    """Verify --file pointing to a missing path exits with an error."""
    missing = tmp_path / "nope.txt"
    args = _parse_comment(["https://jira.test/browse/P-1", "-f", str(missing)])
    with pytest.raises(SystemExit):
        _resolve_comment_body(args)


def test_resolve_body_errors_on_empty_body() -> None:
    """Verify an empty positional body exits with an error."""
    args = _parse_comment(["https://jira.test/browse/P-1", ""])
    with pytest.raises(SystemExit):
        _resolve_comment_body(args)


def test_resolve_body_errors_on_empty_file(tmp_path: Path) -> None:
    """Verify an empty --file exits with an error."""
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")
    args = _parse_comment(["https://jira.test/browse/P-1", "-f", str(path)])
    with pytest.raises(SystemExit):
        _resolve_comment_body(args)


def test_cmd_comment_include_parent_posts_to_all(tmp_path: Path) -> None:
    """Verify --include-parent without dry-run comments on subtasks and parent."""
    config = tmp_path / "config.json"
    config.write_text('{"token": "t"}', encoding="utf-8")
    argv = [
        "comment",
        "https://jira.test/browse/P-1",
        "body",
        "-c",
        str(config),
        "--include-parent",
    ]
    args = build_parser().parse_args(argv)
    client = MagicMock()
    client.base_url = "https://jira.test"
    subtasks = [
        {"key": "P-2", "fields": {"summary": "a"}},
        {"key": "P-3", "fields": {"summary": "b"}},
    ]
    client.get_issue.return_value = {"key": "P-1", "fields": {"summary": "p"}}
    with (
        patch(
            "jirafetcher.cli._connect",
            return_value=(client, "P-1", MagicMock(statuses=[], title_filter=None)),
        ),
        patch("jirafetcher.cli.fetch_subtasks", return_value=subtasks),
    ):
        _cmd_comment(args)
    assert client.add_comment.call_count == 3
    keys = [call.args[0] for call in client.add_comment.call_args_list]
    assert keys == ["P-2", "P-3", "P-1"]
