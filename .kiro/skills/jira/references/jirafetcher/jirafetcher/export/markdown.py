"""Render Jira issues as Markdown files grouped by status."""

# Standard libraries
import logging
import re
from pathlib import Path
from typing import Any

# Own modules
from jirafetcher.types import JiraIssue

logger: logging.Logger = logging.getLogger(__name__)


def _render_issue(issue: JiraIssue) -> str:
    """
    Render a single Jira issue as a Markdown section.

    Includes metadata (status, assignee, priority, dates),
    the full description, and any comments.

    Args:
        issue: Raw issue dict from the Jira API.

    Returns:
        Markdown-formatted string for the issue.
    """

    f: dict[str, Any] = issue["fields"]

    assignee: str = (f.get("assignee") or {}).get("displayName", "Unassigned")
    priority: str = (f.get("priority") or {}).get("name", "N/A")
    desc: str = f.get("description") or "_No description_"

    lines: list[str] = [
        f"## {issue['key']}: {f.get('summary', '')}\n",
        f"- **Status:** {f['status']['name']}",
        f"- **Assignee:** {assignee}",
        f"- **Priority:** {priority}",
        f"- **Created:** {f.get('created', 'N/A')}",
        f"- **Updated:** {f.get('updated', 'N/A')}",
        f"\n### Description\n\n{desc}\n",
    ]

    comments: list[dict[str, Any]] = (f.get("comment") or {}).get("comments", [])

    if comments:
        lines.append("### Comments\n")

        for c in comments:
            author: str = (c.get("author") or {}).get("displayName", "Unknown")
            lines.append(f"**{author}** ({c.get('created', '')}):\n")
            lines.append(f"{c.get('body', '')}\n")

    lines.append("---\n")

    return "\n".join(lines)


def issues_to_markdown(issues: list[JiraIssue], parent_key: str, status: str) -> str:
    """
    Convert a list of issues into a full Markdown document.

    Produces a document with a heading that identifies the
    parent story and status, followed by one rendered
    section per issue.

    Args:
        issues: List of raw issue dicts from the Jira API.
        parent_key: Jira issue key of the parent story.
        status: Status name shared by all issues in the
            list.

    Returns:
        Complete Markdown document as a string.
    """

    header: str = f"# Subtasks of {parent_key} — {status}\n\n"

    return header + "\n".join(_render_issue(i) for i in issues)


def _sanitize_filename(name: str) -> str:
    """
    Turn a status name into a safe, lowercase filename
    stem.

    Replaces any character that is not alphanumeric,
    underscore, or hyphen with an underscore.

    Args:
        name: Raw status name.

    Returns:
        Sanitised string suitable for use as a filename.
    """

    return re.sub(r"[^\w\-]", "_", name.strip().lower())


def write_markdown_files(
    grouped: dict[str, list[JiraIssue]],
    parent_key: str,
    output_dir: Path,
) -> None:
    """
    Write one Markdown file per status group into the
    output directory.

    Creates the directory if it does not exist. Each file
    is named after the sanitised status name.

    Args:
        grouped: Dictionary mapping each status name to
            its list of issues.
        parent_key: Jira issue key of the parent story.
        output_dir: Directory where Markdown files will
            be written.

    Returns:
        None.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    for status, group in grouped.items():
        path: Path = output_dir / f"{_sanitize_filename(status)}.md"

        path.write_text(issues_to_markdown(group, parent_key, status), encoding="utf-8")

        logger.info("%s: %d ticket(s) -> %s.", status, len(group), path)
