"""Tests for the shared types and context assembly."""

# Standard libraries
import json
from pathlib import Path

# Own modules
from driftcheck.types import Finding, Severity, build_context, load_agent_configs
from tests.helpers import write


def test_finding_renders_severity_prefix() -> None:
    """A finding renders as "SEVERITY: message"."""
    assert Finding(Severity.WARNING, "s", "text").render() == "WARNING: text"


def test_load_agent_configs_records_decode_failures(valid_root: Path) -> None:
    """A malformed config is kept with data None and an error."""
    write(valid_root / ".kiro" / "agents" / "broken.json", "{not json")
    configs = load_agent_configs(valid_root / ".kiro" / "agents")
    broken = next(config for config in configs if config.stem == "broken")
    assert broken.data is None
    assert broken.error is not None
    assert broken.name is None
    assert broken.model == ""


def test_load_agent_configs_rejects_non_object_top_level(valid_root: Path) -> None:
    """A JSON array is preserved as an unparseable config."""
    write(valid_root / ".kiro" / "agents" / "listy.json", json.dumps([1, 2]))
    configs = load_agent_configs(valid_root / ".kiro" / "agents")
    listy = next(config for config in configs if config.stem == "listy")
    assert listy.data is None
    assert listy.error == "top level is not an object"


def test_load_agent_configs_tolerates_absent_directory(tmp_path: Path) -> None:
    """A missing agents directory yields no configs."""
    assert load_agent_configs(tmp_path / "nope") == ()


def test_context_exposes_the_expected_layout(valid_root: Path) -> None:
    """Context paths point at the conventional locations."""
    ctx = build_context(valid_root)
    assert ctx.agents_dir == valid_root.resolve() / ".kiro" / "agents"
    assert ctx.skills_dir == valid_root.resolve() / ".kiro" / "skills"
    assert ctx.state_yaml == valid_root.resolve() / "memory" / "state.yaml"
    assert ctx.orchestrator is not None
    assert ctx.orchestrator.name == "orchestrator"
    names = [path.name for path in ctx.skill_dirs()]
    assert names == sorted(names)
    assert "reviewing-code" in names
