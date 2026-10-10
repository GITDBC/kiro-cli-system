# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from jirafetcher.cli import build_parser


def test_no_command_returns_none() -> None:
    """
    Verify the parser returns command=None when no
    subcommand is given.
    """

    ns = build_parser().parse_args([])
    assert ns.command is None


def test_fetch_default_output_dir() -> None:
    """
    Verify the default output directory is 'output'.
    """

    ns = build_parser().parse_args(["fetch", "https://jira.test/browse/P-1"])
    assert ns.output_dir == Path("output")


def test_fetch_default_config() -> None:
    """
    Verify the default config path is 'config.json'.
    """

    ns = build_parser().parse_args(["fetch", "https://jira.test/browse/P-1"])
    assert ns.config == Path("config.json")


def test_fetch_dry_run() -> None:
    """
    Verify --dry-run flag is parsed.
    """

    ns = build_parser().parse_args(
        ["fetch", "https://jira.test/browse/P-1", "--dry-run"],
    )
    assert ns.dry_run is True


def test_transition_parses_target() -> None:
    """
    Verify transition subcommand parses target_status.
    """

    ns = build_parser().parse_args(
        ["transition", "https://jira.test/browse/P-1", "Done"],
    )
    assert ns.command == "transition"
    assert ns.target_status == "Done"


def test_transition_with_comment() -> None:
    """
    Verify transition accepts --comment flag.
    """

    ns = build_parser().parse_args(
        ["transition", "https://jira.test/browse/P-1", "Done", "-m", "Fixed"],
    )
    assert ns.comment == "Fixed"


def test_comment_parses_body() -> None:
    """
    Verify comment subcommand parses body.
    """

    ns = build_parser().parse_args(
        ["comment", "https://jira.test/browse/P-1", "Changes applied"],
    )
    assert ns.command == "comment"
    assert ns.body == "Changes applied"


def test_comment_body_optional() -> None:
    """
    Verify comment subcommand accepts a missing body.
    """

    ns = build_parser().parse_args(["comment", "https://jira.test/browse/P-1"])
    assert ns.body is None
    assert ns.file is None


def test_comment_file_flag() -> None:
    """
    Verify comment subcommand parses --file.
    """

    ns = build_parser().parse_args(
        ["comment", "https://jira.test/browse/P-1", "-f", "note.txt"],
    )
    assert ns.file == Path("note.txt")


def test_self_flag_parsed() -> None:
    """
    Verify --self is parsed across subcommands.
    """

    for cmd, extra in (
        ("fetch", []),
        ("transition", ["Done"]),
        ("comment", ["body"]),
    ):
        ns = build_parser().parse_args(
            [cmd, "https://jira.test/browse/P-1", *extra, "--self"],
        )
        assert ns.self_only is True
        assert ns.include_parent is False


def test_include_parent_flag_parsed() -> None:
    """
    Verify --include-parent is parsed across subcommands.
    """

    ns = build_parser().parse_args(
        ["fetch", "https://jira.test/browse/P-1", "--include-parent"],
    )
    assert ns.include_parent is True
    assert ns.self_only is False


def test_self_and_include_parent_mutually_exclusive() -> None:
    """
    Verify --self and --include-parent cannot be combined.
    """

    with pytest.raises(SystemExit):
        build_parser().parse_args(
            [
                "fetch",
                "https://jira.test/browse/P-1",
                "--self",
                "--include-parent",
            ],
        )
