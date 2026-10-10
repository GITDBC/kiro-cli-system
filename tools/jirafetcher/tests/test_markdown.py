# Standard libraries
from pathlib import Path
from typing import Any

# Own modules
from jirafetcher.export.markdown import (
    _render_issue,
    _sanitize_filename,
    issues_to_markdown,
    write_markdown_files,
)


def _issue(
    key: str = "PROJ-1",
    summary: str = "Fix bug",
    status: str = "In Review",
    description: str | None = "Details here.",
) -> dict[str, Any]:
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
            "assignee": {"displayName": "Alice"},
            "priority": {"name": "High"},
            "created": "2026-01-01",
            "updated": "2026-01-02",
            "description": description,
            "comment": {"comments": []},
        },
    }


def test_render_issue() -> None:
    """
    Verify _render_issue renders all fields.
    """

    md = _render_issue(_issue())
    assert "PROJ-1" in md
    assert "Fix bug" in md
    assert "Alice" in md
    assert "High" in md
    assert "Details here." in md


def test_render_issue_no_description() -> None:
    """
    Verify _render_issue uses placeholder when
    description is None.
    """

    issue = _issue(description=None)
    issue["fields"]["description"] = None
    md = _render_issue(issue)
    assert "_No description_" in md


def test_issues_to_markdown() -> None:
    """
    Verify issues_to_markdown generates a complete
    document.
    """

    issues = [_issue()]
    md = issues_to_markdown(issues, "PROJ-100", "In Review")
    assert "PROJ-100" in md
    assert "In Review" in md
    assert "PROJ-1" in md


def test_sanitize_filename() -> None:
    """
    Verify _sanitize_filename converts status names
    to safe filenames.
    """

    assert _sanitize_filename("In Review") == "in_review"
    assert _sanitize_filename("On Hold!") == "on_hold_"


def test_write_markdown_files(tmp_path: Path) -> None:
    """
    Verify write_markdown_files creates files in the
    output directory.
    """

    grouped = {"In Review": [_issue()]}
    write_markdown_files(grouped, "PROJ-100", tmp_path)
    files = list(tmp_path.glob("*.md"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert "PROJ-1" in content
