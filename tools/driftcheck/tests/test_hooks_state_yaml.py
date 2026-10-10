"""Tests for the state.yaml validation hook."""

# Standard libraries
import io
import json
import sys
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck.hooks import state_yaml
from tests.helpers import STATE_YAML, write

DUPLICATE_IDS = "decisions:\n  - id: D1\n  - id: D1\n"


def event(path: Path | str) -> io.StringIO:
    """
    Build a postToolUse payload naming a written path.

    Args:
        path: Path the hook should inspect, absolute or relative.

    Returns:
        Stream holding the event JSON.
    """
    return io.StringIO(json.dumps({"tool_input": {"path": str(path)}}))


def test_hook_accepts_a_valid_registry(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A well-formed state.yaml exits 0 and reports OK."""
    path = write(tmp_path / "memory" / "state.yaml", STATE_YAML)
    assert state_yaml.run(event(path), root=tmp_path) == 0
    assert "OK: state.yaml is valid" in capsys.readouterr().out


def test_hook_rejects_a_non_mapping_root(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A sequence at the root exits 1."""
    path = write(tmp_path / "memory" / "state.yaml", "- one\n- two\n")
    assert state_yaml.run(event(path), root=tmp_path) == 1
    assert "must be a mapping" in capsys.readouterr().err


def test_hook_rejects_an_oversized_section(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """More than twenty decisions exits 1."""
    entries = "".join(f"  - id: D{index}\n" for index in range(21))
    path = write(tmp_path / "memory" / "state.yaml", f"decisions:\n{entries}")
    assert state_yaml.run(event(path), root=tmp_path) == 1
    assert "21 entries" in capsys.readouterr().err


def test_hook_rejects_an_oversized_agent_feedback_section(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The entry cap applies to agent_feedback as well."""
    entries = "".join(f"  - id: F{index}\n" for index in range(21))
    path = write(tmp_path / "memory" / "state.yaml", f"agent_feedback:\n{entries}")
    assert state_yaml.run(event(path), root=tmp_path) == 1
    assert "agent_feedback has 21 entries" in capsys.readouterr().err


def test_hook_rejects_duplicate_ids(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Duplicate ids exit 1."""
    path = write(tmp_path / "memory" / "state.yaml", DUPLICATE_IDS)
    assert state_yaml.run(event(path), root=tmp_path) == 1
    assert "duplicate IDs" in capsys.readouterr().err


def test_hook_rejects_malformed_yaml(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Unparseable YAML exits 1."""
    path = write(tmp_path / "memory" / "state.yaml", "decisions: [unclosed\n")
    assert state_yaml.run(event(path), root=tmp_path) == 1
    assert "malformed" in capsys.readouterr().err


def test_hook_ignores_unrelated_paths(tmp_path: Path) -> None:
    """A write that is not state.yaml is a no-op."""
    path = write(tmp_path / "memory" / "notes.md", "# Notes\n")
    assert state_yaml.run(event(path), root=tmp_path) == 0


def test_hook_ignores_an_empty_payload(tmp_path: Path) -> None:
    """A payload with no path is a no-op."""
    payload = io.StringIO(json.dumps({"tool_input": {}}))
    assert state_yaml.run(payload, root=tmp_path) == 0


@pytest.mark.parametrize(
    "reported",
    ["memory/state.yaml", "./memory/state.yaml", "memory//state.yaml"],
)
def test_hook_validates_a_root_relative_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], reported: str
) -> None:
    """A relative event path is resolved against the repository root."""
    write(tmp_path / "memory" / "state.yaml", STATE_YAML)
    assert state_yaml.run(event(reported), root=tmp_path) == 0
    assert "OK: state.yaml is valid" in capsys.readouterr().out


@pytest.mark.parametrize(
    "reported",
    ["memory/state.yaml", "./memory/state.yaml", "memory//state.yaml"],
)
def test_hook_rejects_a_violation_from_a_relative_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], reported: str
) -> None:
    """A relative path must be checked, not silently skipped."""
    write(tmp_path / "memory" / "state.yaml", DUPLICATE_IDS)
    assert state_yaml.run(event(reported), root=tmp_path) == 1
    assert "duplicate IDs" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("reported", "decoy"),
    [
        ("memory/state.yaml.bak", "memory/state.yaml.bak"),
        ("notes/memory/state.yaml", "notes/memory/state.yaml"),
        ("state.yaml", "state.yaml"),
        ("../memory/state.yaml", "memory/state.yaml"),
    ],
)
def test_hook_ignores_paths_at_the_wrong_layout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], reported: str, decoy: str
) -> None:
    """Component matching stays strict about name and depth."""
    write(tmp_path / decoy, DUPLICATE_IDS)
    assert state_yaml.run(event(reported), root=tmp_path) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_hook_ignores_an_absolute_path_outside_the_repository(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A state.yaml belonging to another tree is not this hook's business."""
    outside = write(tmp_path / "elsewhere" / "memory" / "state.yaml", DUPLICATE_IDS)
    assert state_yaml.run(event(outside), root=tmp_path / "repo") == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_hook_degrades_without_pyyaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A venv without PyYAML warns and exits 0, never non-zero."""
    path = write(tmp_path / "memory" / "state.yaml", STATE_YAML)
    monkeypatch.setitem(sys.modules, "yaml", None)
    assert state_yaml.run(event(path), root=tmp_path) == 0
    assert "PyYAML not installed" in capsys.readouterr().err


def test_main_degrades_on_an_unreadable_event(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A non-JSON event warns and exits 0 rather than raising."""
    monkeypatch.setattr("sys.stdin", io.StringIO("not json"))
    assert state_yaml.main() == 0
    assert "state.yaml validation skipped" in capsys.readouterr().err


def test_main_degrades_without_a_repository_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Undiscoverable root warns and exits 0, never non-zero."""
    write(tmp_path / "memory" / "state.yaml", DUPLICATE_IDS)
    monkeypatch.setattr("sys.stdin", event("memory/state.yaml"))
    monkeypatch.setattr(state_yaml, "find_repo_root", _unlocatable_root)
    assert state_yaml.main() == 0
    assert "state.yaml validation skipped" in capsys.readouterr().err


def test_main_propagates_a_real_violation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A check that ran and failed still exits 1."""
    path = write(tmp_path / "memory" / "state.yaml", "- one\n")
    monkeypatch.setattr("sys.stdin", event(path))
    monkeypatch.setattr(state_yaml, "find_repo_root", lambda: tmp_path)
    assert state_yaml.main() == 1


def test_main_propagates_a_violation_from_a_relative_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The console script exits 1 for a relative path, as the runtime sends."""
    write(tmp_path / "memory" / "state.yaml", DUPLICATE_IDS)
    monkeypatch.setattr("sys.stdin", event("memory/state.yaml"))
    monkeypatch.setattr(state_yaml, "find_repo_root", lambda: tmp_path)
    assert state_yaml.main() == 1
    assert "duplicate IDs" in capsys.readouterr().err


def _unlocatable_root() -> Path:
    """
    Stand in for root discovery failing.

    Returns:
        Never returns.

    Raises:
        ValueError: Always, mirroring find_repo_root on an alien tree.
    """
    message = "cannot locate the repository root"
    raise ValueError(message)
