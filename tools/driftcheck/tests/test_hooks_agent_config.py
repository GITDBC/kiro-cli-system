"""Tests for the agent-config validation hook."""

# Standard libraries
import io
import json
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck.hooks import agent_config
from tests.helpers import write, write_agent

THIN_CONFIG = json.dumps({"name": "thin"})


def event(path: Path | str) -> io.StringIO:
    """
    Build a postToolUse payload naming a written path.

    Args:
        path: Path the hook should inspect, absolute or relative.

    Returns:
        Stream holding the event JSON.
    """
    return io.StringIO(json.dumps({"tool_input": {"path": str(path)}}))


def operations_event(path: Path | str) -> io.StringIO:
    """
    Build a payload using the operations-array shape.

    Args:
        path: Path the hook should inspect, absolute or relative.

    Returns:
        Stream holding the event JSON.
    """
    return io.StringIO(
        json.dumps({"tool_input": {"operations": [{"path": str(path)}]}})
    )


def test_hook_accepts_a_valid_config(
    valid_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A complete config reports OK on stdout."""
    path = write_agent(valid_root, "senior-developer", description="Implements things.")
    agent_config.run(event(path), root=valid_root)
    assert "OK: senior-developer.json is valid" in capsys.readouterr().out


def test_hook_warns_on_missing_fields(
    valid_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A config without required fields warns on stderr."""
    path = write(valid_root / ".kiro" / "agents" / "thin.json", THIN_CONFIG)
    agent_config.run(event(path), root=valid_root)
    captured = capsys.readouterr()
    assert "missing fields" in captured.err
    assert captured.out == ""


def test_hook_warns_on_missing_resource(
    valid_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An unresolvable file:// resource warns on stderr."""
    path = write_agent(
        valid_root,
        "senior-developer",
        description="Implements things.",
        resources=["file://.kiro/steering/absent.md"],
    )
    agent_config.run(operations_event(path), root=valid_root)
    assert "references missing file" in capsys.readouterr().err


def test_hook_warns_on_missing_skill_resource(
    valid_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A dangling skill:// resource warns like a file:// one."""
    path = write_agent(
        valid_root,
        "senior-developer",
        description="Implements things.",
        resources=["skill://.kiro/skills/jira-safety/SKILL.md"],
    )
    agent_config.run(event(path), root=valid_root)
    assert "skill://.kiro/skills/jira-safety/SKILL.md" in capsys.readouterr().err


def test_hook_ignores_unrelated_paths(
    valid_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A write outside .kiro/agents is not inspected."""
    path = write(valid_root / "notes" / "scratch.json", "{}")
    agent_config.run(event(path), root=valid_root)
    assert capsys.readouterr().out == ""


def test_hook_ignores_an_empty_payload() -> None:
    """A payload with no path is a no-op."""
    agent_config.run(io.StringIO(json.dumps({"tool_input": {}})))


@pytest.mark.parametrize(
    "reported",
    [
        ".kiro/agents/senior-developer.json",
        "./.kiro/agents/senior-developer.json",
        ".kiro//agents/senior-developer.json",
    ],
)
def test_hook_validates_a_root_relative_path(
    valid_root: Path, capsys: pytest.CaptureFixture[str], reported: str
) -> None:
    """A relative event path is resolved against the repository root."""
    write_agent(valid_root, "senior-developer", description="Implements things.")
    agent_config.run(event(reported), root=valid_root)
    assert "OK: senior-developer.json is valid" in capsys.readouterr().out


@pytest.mark.parametrize(
    "reported",
    [".kiro/agents/thin.json", "./.kiro/agents/thin.json"],
)
def test_hook_reports_a_violation_from_a_relative_path(
    valid_root: Path, capsys: pytest.CaptureFixture[str], reported: str
) -> None:
    """A relative path must be checked, not silently skipped."""
    write(valid_root / ".kiro" / "agents" / "thin.json", THIN_CONFIG)
    agent_config.run(event(reported), root=valid_root)
    captured = capsys.readouterr()
    assert "thin.json missing fields" in captured.err
    assert captured.out == ""


@pytest.mark.parametrize(
    ("reported", "decoy"),
    [
        (".kiro/prompts/foo.json", ".kiro/prompts/foo.json"),
        (".kiro/agents/sub/foo.json", ".kiro/agents/sub/foo.json"),
        ("agents/foo.json", "agents/foo.json"),
        (".kiro/agents/notes.md", ".kiro/agents/notes.md"),
        ("../.kiro/agents/foo.json", ".kiro/agents/foo.json"),
    ],
)
def test_hook_ignores_paths_at_the_wrong_layout(
    valid_root: Path, capsys: pytest.CaptureFixture[str], reported: str, decoy: str
) -> None:
    """Component matching stays strict about directory, depth and suffix."""
    write(valid_root / decoy, THIN_CONFIG)
    agent_config.run(event(reported), root=valid_root)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_hook_ignores_an_absolute_path_outside_the_repository(
    valid_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An agent config in another tree is not this hook's business."""
    outside = write(
        valid_root.parent / "other" / ".kiro" / "agents" / "thin.json", THIN_CONFIG
    )
    agent_config.run(event(outside), root=valid_root)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_main_degrades_on_an_unreadable_event(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A non-JSON event warns and exits 0 rather than raising."""
    monkeypatch.setattr("sys.stdin", io.StringIO("not json"))
    assert agent_config.main() == 0
    assert "agent config validation skipped" in capsys.readouterr().err


def test_main_degrades_on_a_malformed_config(
    valid_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An unparseable config warns and exits 0."""
    path = write(valid_root / ".kiro" / "agents" / "broken.json", "{not json")
    monkeypatch.setattr("sys.stdin", event(path))
    monkeypatch.setattr(agent_config, "find_repo_root", lambda: valid_root)
    assert agent_config.main() == 0
    assert "agent config validation skipped" in capsys.readouterr().err


def test_main_inspects_a_relative_path(
    valid_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The console script inspects a relative path, as the runtime sends."""
    write(valid_root / ".kiro" / "agents" / "thin.json", THIN_CONFIG)
    monkeypatch.setattr("sys.stdin", event(".kiro/agents/thin.json"))
    monkeypatch.setattr(agent_config, "find_repo_root", lambda: valid_root)
    assert agent_config.main() == 0
    assert "thin.json missing fields" in capsys.readouterr().err
