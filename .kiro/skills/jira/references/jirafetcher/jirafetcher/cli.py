"""Command-line interface: fetch, transition and comment subcommands."""

# Standard libraries
import argparse
import logging
import sys
from pathlib import Path

# 3pps
import requests

# Own modules
from jirafetcher.config import DEFAULT_CONFIG_PATH, Config
from jirafetcher.export.markdown import write_markdown_files
from jirafetcher.jira.client import JiraClient, parse_jira_url
from jirafetcher.jira.filters import fetch_subtasks, filter_by_title, group_by_status
from jirafetcher.types import JiraIssue

DEFAULT_OUTPUT_DIR: Path = Path("output")

logger: logging.Logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Shared CLI helpers
# ------------------------------------------------------------------


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments shared by all subcommands."""
    parser.add_argument(
        "url",
        help="Jira story URL (e.g. https://jira.example.com/browse/PROJ-123)",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Config file path (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument(
        "--self",
        dest="self_only",
        action="store_true",
        help="Operate on the ticket itself, not its subtasks.",
    )
    scope.add_argument(
        "--include-parent",
        action="store_true",
        help="Include the parent ticket alongside its subtasks.",
    )


def _connect(args: argparse.Namespace) -> tuple[JiraClient, str, Config]:
    """
    Load config, parse URL, and return a connected
    client, the parent issue key, and the loaded config.
    """

    try:
        config: Config = Config.from_file(args.config)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("%s.", exc)
        sys.exit(1)

    try:
        base_url, parent_key = parse_jira_url(args.url)
    except ValueError as exc:
        logger.error("%s.", exc)
        sys.exit(1)

    client = JiraClient(base_url=base_url, token=config.token)
    return client, parent_key, config


def _fetch_parent(client: JiraClient, parent_key: str) -> JiraIssue:
    """Fetch the parent issue itself, exiting on HTTP errors."""
    try:
        return client.get_issue(parent_key)
    except requests.RequestException as exc:
        logger.error("Jira API request failed: %s.", exc)
        sys.exit(1)


def _fetch_subtasks_filtered(
    args: argparse.Namespace,
    client: JiraClient,
    parent_key: str,
    config: Config,
) -> list[JiraIssue]:
    """Fetch subtasks and apply status/title filters."""
    statuses: list[str] = getattr(args, "statuses", None) or config.statuses
    title_filter: str | None = (
        getattr(args, "title_filter", None) or config.title_filter
    )

    try:
        issues = fetch_subtasks(client, parent_key, statuses)
    except requests.RequestException as exc:
        logger.error("Jira API request failed: %s.", exc)
        sys.exit(1)

    if title_filter:
        issues = filter_by_title(issues, title_filter)

    return issues


def _fetch_issues(
    args: argparse.Namespace,
    client: JiraClient,
    parent_key: str,
    config: Config,
) -> list[JiraIssue]:
    """
    Fetch issues based on CLI scope flags.

    Returns only the parent when ``--self`` is set,
    filtered subtasks by default, or filtered subtasks
    plus the parent when ``--include-parent`` is set.
    """
    if getattr(args, "self_only", False):
        return [_fetch_parent(client, parent_key)]

    issues = _fetch_subtasks_filtered(args, client, parent_key, config)

    if getattr(args, "include_parent", False):
        issues.append(_fetch_parent(client, parent_key))

    return issues


# ------------------------------------------------------------------
# Subcommand: fetch
# ------------------------------------------------------------------


def _cmd_fetch(args: argparse.Namespace) -> None:
    """Execute the fetch subcommand."""
    client, parent_key, config = _connect(args)

    logger.info("Server: %s.", client.base_url)
    logger.info("Parent story: %s.", parent_key)

    issues = _fetch_issues(args, client, parent_key, config)

    logger.info("Found %d subtask(s).", len(issues))

    if not issues:
        logger.warning("Nothing to export.")
        return

    if args.dry_run:
        for issue in issues:
            f = issue["fields"]
            status = f["status"]["name"]
            summary = f.get("summary", "")
            logger.info("  %s [%s] %s", issue["key"], status, summary)
        logger.info("Dry-run: %d issue(s) would be exported.", len(issues))
        return

    grouped = group_by_status(issues)
    write_markdown_files(grouped, parent_key, args.output_dir)

    for status, group in grouped.items():
        logger.info("%s: %d ticket(s).", status, len(group))


# ------------------------------------------------------------------
# Subcommand: transition
# ------------------------------------------------------------------


def _find_transition(
    client: JiraClient,
    issue_key: str,
    target: str,
) -> dict[str, str] | None:
    """
    Find a transition matching the target name
    (case-insensitive).
    """

    target_lower = target.lower()
    for t in client.get_transitions(issue_key):
        if t["name"].lower() == target_lower:
            return {"id": t["id"], "name": t["name"]}
    return None


def _add_transition_comment(client: JiraClient, key: str, comment: str) -> None:
    """Attach a comment after a transition, logging failures without raising."""
    try:
        client.add_comment(key, comment)
        logger.info("%s: comment added.", key)
    except requests.RequestException as exc:
        logger.error("%s: comment failed: %s.", key, exc)


def _transition_one(
    client: JiraClient,
    issue: JiraIssue,
    args: argparse.Namespace,
) -> str:
    """
    Transition a single issue and return its outcome.

    Returns:
        One of "success", "skipped", "failed".
    """
    key: str = issue["key"]
    current: str = issue["fields"]["status"]["name"]

    if current.lower() == args.target_status.lower():
        logger.info("%s already in '%s', skipping.", key, current)
        return "skipped"

    transition = _find_transition(client, key, args.target_status)
    if not transition:
        logger.warning(
            "%s: no transition to '%s' from '%s'.",
            key,
            args.target_status,
            current,
        )
        return "failed"

    if args.dry_run:
        logger.info(
            "%s: would transition '%s' -> '%s'.",
            key,
            current,
            transition["name"],
        )
        return "success"

    try:
        client.transition_issue(key, transition["id"])
        logger.info("%s: '%s' -> '%s'.", key, current, transition["name"])
    except requests.RequestException as exc:
        logger.error("%s: transition failed: %s.", key, exc)
        return "failed"

    if args.comment:
        _add_transition_comment(client, key, args.comment)
    return "success"


def _cmd_transition(args: argparse.Namespace) -> None:
    """Execute the transition subcommand."""
    client, parent_key, config = _connect(args)
    issues = _fetch_issues(args, client, parent_key, config)

    if not issues:
        logger.warning("No matching subtasks found.")
        return

    outcomes = [_transition_one(client, issue, args) for issue in issues]

    prefix = "Would transition" if args.dry_run else "Transitioned"
    logger.info(
        "Summary: %s %d, skipped %d, failed %d.",
        prefix,
        outcomes.count("success"),
        outcomes.count("skipped"),
        outcomes.count("failed"),
    )


# ------------------------------------------------------------------
# Subcommand: comment
# ------------------------------------------------------------------


def _resolve_comment_body(args: argparse.Namespace) -> str:
    """
    Resolve the comment body from CLI args.

    Exactly one source must be provided: positional
    ``body``, ``--file``, or piped stdin. Reading from
    stdin requires a non-TTY stream. The resolved body
    must not be empty or whitespace-only.

    Returns:
        The resolved comment body.

    Raises:
        SystemExit: If zero or multiple sources are
            provided, stdin is a TTY, ``--file`` cannot
            be read, or the resolved body is empty.
    """
    body: str | None = args.body
    file_path: Path | None = args.file

    if body is not None and file_path is not None:
        logger.error("provide either body argument or --file, not both.")
        sys.exit(2)

    if body is not None:
        resolved: str = body
    elif file_path is not None:
        try:
            resolved = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            logger.error("cannot read --file %s: %s.", file_path, exc)
            sys.exit(2)
    elif sys.stdin.isatty():
        logger.error("provide body argument, --file, or pipe content via stdin.")
        sys.exit(2)
    else:
        resolved = sys.stdin.read()

    if not resolved.strip():
        logger.error("comment body is empty.")
        sys.exit(2)

    return resolved


def _cmd_comment(args: argparse.Namespace) -> None:
    """Execute the comment subcommand."""
    body: str = _resolve_comment_body(args)
    client, parent_key, config = _connect(args)
    issues = _fetch_issues(args, client, parent_key, config)

    if not issues:
        logger.warning("No matching subtasks found.")
        return

    success: int = 0
    failed: int = 0

    for issue in issues:
        key: str = issue["key"]

        if args.dry_run:
            logger.info("%s: would add comment.", key)
            success += 1
            continue

        try:
            client.add_comment(key, body)
            logger.info("%s: comment added.", key)
            success += 1
        except requests.RequestException as exc:
            logger.error("%s: comment failed: %s.", key, exc)
            failed += 1

    prefix = "Would comment on" if args.dry_run else "Commented on"
    logger.info("Summary: %s %d, failed %d.", prefix, success, failed)


# ------------------------------------------------------------------
# Parser
# ------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser with subcommands.

    Returns:
        Configured argument parser.
    """

    parser = argparse.ArgumentParser(
        description="Fetch, transition, and comment on Jira subtasks.",
    )
    subs = parser.add_subparsers(dest="command")

    # -- fetch --
    fetch_p = subs.add_parser("fetch", help="Fetch subtasks and export to Markdown.")
    _add_common_args(fetch_p)
    fetch_p.add_argument(
        "-s",
        "--statuses",
        nargs="+",
        help="Override statuses from config.",
    )
    fetch_p.add_argument(
        "-t",
        "--title-filter",
        help="Filter issues by title substring.",
    )
    fetch_p.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR}).",
    )
    fetch_p.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="List issues without writing files.",
    )

    # -- transition --
    trans_p = subs.add_parser(
        "transition",
        help="Transition subtasks to a new status.",
    )
    _add_common_args(trans_p)
    trans_p.add_argument(
        "target_status",
        help="Target status name (e.g. 'Done', 'In Progress').",
    )
    trans_p.add_argument(
        "-s",
        "--statuses",
        nargs="+",
        help="Source statuses to filter by.",
    )
    trans_p.add_argument(
        "-t",
        "--title-filter",
        help="Filter issues by title substring.",
    )
    trans_p.add_argument(
        "-m",
        "--comment",
        help="Add a comment when transitioning.",
    )
    trans_p.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would change without applying.",
    )

    # -- comment --
    comment_p = subs.add_parser("comment", help="Add a comment to subtasks.")
    _add_common_args(comment_p)
    comment_p.add_argument(
        "body",
        nargs="?",
        default=None,
        help="Comment text (optional; reads --file or stdin if omitted).",
    )
    comment_p.add_argument(
        "-f",
        "--file",
        type=Path,
        default=None,
        help="Read comment body from a UTF-8 text file.",
    )
    comment_p.add_argument(
        "-s",
        "--statuses",
        nargs="+",
        help="Filter by statuses.",
    )
    comment_p.add_argument(
        "-t",
        "--title-filter",
        help="Filter issues by title substring.",
    )
    comment_p.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would change without applying.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """
    Entry point for the jirafetcher CLI.

    Args:
        argv: Command-line arguments, defaulting to sys.argv[1:].

    Returns:
        Process exit code: 1 when no subcommand is given, 0 once
        the subcommand completes. Fatal errors inside a subcommand
        (config, URL, Jira API, comment body) still exit through
        ``SystemExit`` with their own code.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    handlers = {
        "fetch": _cmd_fetch,
        "transition": _cmd_transition,
        "comment": _cmd_comment,
    }
    handlers[args.command](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
