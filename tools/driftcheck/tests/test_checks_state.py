"""
Tests for the memory store and state.yaml registry checks.

The memory-store check is framework-scoped, so its tests come in two
shapes: a framework tree, which the valid_root fixture provides by
carrying the .gitignore rule that ignores memory/ contents, and a
consuming-project tree, which drops that rule and must therefore produce
no findings at all.
"""

# Standard libraries
import sys
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck.checks.state import check_memory_store, check_state_registry
from driftcheck.types import DriftContext, Severity, build_context
from tests.helpers import (
    GITIGNORE_WITHOUT_MEMORY_RULE,
    STATE_YAML,
    severities,
    write,
)


def test_state_registry_accepts_valid_file(ctx: DriftContext) -> None:
    """A well-formed state.yaml yields an informational finding."""
    findings = check_state_registry(ctx)
    assert severities(findings) == [Severity.OK]
    assert findings[0].message == "state.yaml is valid"


def test_state_registry_tolerates_absent_file(valid_root: Path) -> None:
    """A missing state.yaml is acceptable."""
    (valid_root / "memory" / "state.yaml").unlink()
    findings = check_state_registry(build_context(valid_root))
    assert severities(findings) == [Severity.OK]
    assert "No state.yaml" in findings[0].message


def test_state_registry_rejects_oversized_section(valid_root: Path) -> None:
    """More than twenty decisions is an error."""
    entries = "".join(f"  - id: D{index}\n" for index in range(21))
    write(valid_root / "memory" / "state.yaml", f"decisions:\n{entries}")
    findings = check_state_registry(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "21 entries" in findings[0].message


def test_state_registry_rejects_duplicate_ids(valid_root: Path) -> None:
    """Duplicate decision ids are an error."""
    write(
        valid_root / "memory" / "state.yaml",
        "decisions:\n  - id: D1\n  - id: D1\n",
    )
    findings = check_state_registry(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "duplicate IDs" in findings[0].message


def test_state_registry_rejects_oversized_agent_feedback(valid_root: Path) -> None:
    """The entry cap applies to agent_feedback as well."""
    entries = "".join(f"  - id: F{index}\n" for index in range(21))
    write(valid_root / "memory" / "state.yaml", f"agent_feedback:\n{entries}")
    findings = check_state_registry(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "agent_feedback has 21 entries" in findings[0].message


def test_state_registry_rejects_duplicate_agent_feedback_ids(
    valid_root: Path,
) -> None:
    """Duplicate agent_feedback ids are an error."""
    write(
        valid_root / "memory" / "state.yaml",
        "agent_feedback:\n  - id: F1\n  - id: F1\n",
    )
    findings = check_state_registry(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "agent_feedback has duplicate IDs" in findings[0].message


def test_state_registry_rejects_non_list_section(valid_root: Path) -> None:
    """A section that is a mapping instead of a list is an error."""
    write(valid_root / "memory" / "state.yaml", "agent_feedback:\n  id: F1\n")
    findings = check_state_registry(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "agent_feedback is not a list" in findings[0].message


def test_state_registry_rejects_malformed_yaml(valid_root: Path) -> None:
    """Unparseable YAML is an error."""
    write(valid_root / "memory" / "state.yaml", "decisions: [unclosed\n")
    findings = check_state_registry(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "malformed" in findings[0].message


def test_state_registry_rejects_non_mapping(valid_root: Path) -> None:
    """A top-level sequence is an error."""
    write(valid_root / "memory" / "state.yaml", "- one\n- two\n")
    findings = check_state_registry(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "not a mapping" in findings[0].message


def test_state_registry_reports_missing_pyyaml(
    ctx: DriftContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An environment without PyYAML is an error, not an import crash."""
    monkeypatch.setitem(sys.modules, "yaml", None)
    findings = check_state_registry(ctx)
    assert severities(findings) == [Severity.ERROR]
    assert "PyYAML is not installed" in findings[0].message


def test_memory_store_accepts_the_empty_template(ctx: DriftContext) -> None:
    """A memory/ holding only an empty state.yaml is clean."""
    findings = check_memory_store(ctx)
    assert severities(findings) == [Severity.OK]
    assert "only an empty state.yaml template" in findings[0].message


def test_memory_store_tolerates_absent_directory(valid_root: Path) -> None:
    """A repository without memory/ is acceptable."""
    (valid_root / "memory" / "state.yaml").unlink()
    (valid_root / "memory").rmdir()
    findings = check_memory_store(build_context(valid_root))
    assert severities(findings) == [Severity.OK]
    assert "No memory/ directory" in findings[0].message


def test_memory_store_rejects_a_stray_directory(valid_root: Path) -> None:
    """Documentation filed under memory/ is an error."""
    write(valid_root / "memory" / "out-of-scope" / "idea.md", "# Rejected\n")
    findings = check_memory_store(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "memory/out-of-scope/ must not exist here" in findings[0].message
    assert "per-consuming-project runtime state" in findings[0].message
    assert "docs/" in findings[0].message


def test_memory_store_rejects_a_stray_file(valid_root: Path) -> None:
    """A leftover backup file under memory/ is an error."""
    write(valid_root / "memory" / "state.yaml.bak", "decisions: []\n")
    findings = check_memory_store(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "memory/state.yaml.bak must not exist here" in findings[0].message


def test_memory_store_rejects_a_populated_registry(valid_root: Path) -> None:
    """A shipped decision entry is an error naming its section."""
    write(valid_root / "memory" / "state.yaml", STATE_YAML)
    findings = check_memory_store(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "carries 1 decisions entries" in findings[0].message
    assert "records the state of a consuming project" in findings[0].message


def test_memory_store_rejects_populated_agent_feedback(valid_root: Path) -> None:
    """The emptiness rule covers agent_feedback as well."""
    write(
        valid_root / "memory" / "state.yaml",
        "agent_feedback:\n  - id: F1\n",
    )
    findings = check_memory_store(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "carries 1 agent_feedback entries" in findings[0].message


def test_memory_store_reports_every_violation(valid_root: Path) -> None:
    """Strays and populated sections are reported together."""
    write(valid_root / "memory" / "notes.md", "# Notes\n")
    write(valid_root / "memory" / "state.yaml", STATE_YAML)
    findings = check_memory_store(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR, Severity.ERROR]


def test_memory_store_stays_silent_on_malformed_yaml(valid_root: Path) -> None:
    """Parse failures belong to the registry check, not this one."""
    write(valid_root / "memory" / "state.yaml", "decisions: [unclosed\n")
    findings = check_memory_store(build_context(valid_root))
    assert severities(findings) == [Severity.OK]


def test_memory_store_stays_silent_without_pyyaml(
    ctx: DriftContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing dependency is reported by the registry check only."""
    monkeypatch.setitem(sys.modules, "yaml", None)
    findings = check_memory_store(ctx)
    assert severities(findings) == [Severity.OK]


def test_memory_store_is_inapplicable_in_a_consuming_project(
    valid_root: Path,
) -> None:
    """Without the ignore rule the check reports nothing whatsoever."""
    write(valid_root / ".gitignore", GITIGNORE_WITHOUT_MEMORY_RULE)
    write(valid_root / "memory" / "state.yaml", STATE_YAML)
    write(valid_root / "memory" / "notes.md", "# Project notes\n")
    assert check_memory_store(build_context(valid_root)) == []


def test_memory_store_is_inapplicable_without_a_gitignore(valid_root: Path) -> None:
    """A tree carrying no .gitignore at all declares no boundary."""
    (valid_root / ".gitignore").unlink()
    write(valid_root / "memory" / "notes.md", "# Project notes\n")
    assert check_memory_store(build_context(valid_root)) == []


def test_memory_store_ignores_a_commented_out_ignore_rule(valid_root: Path) -> None:
    """A commented "memory/*" line ignores nothing, so declares nothing."""
    write(valid_root / ".gitignore", "tmp/\n# memory/*\n!memory/state.yaml\n")
    write(valid_root / "memory" / "notes.md", "# Project notes\n")
    assert check_memory_store(build_context(valid_root)) == []


def test_memory_store_ignores_a_negated_rule_alone(valid_root: Path) -> None:
    """An un-ignore line is not a declaration that memory/ is empty."""
    write(valid_root / ".gitignore", "tmp/\n!memory/state.yaml\n")
    write(valid_root / "memory" / "notes.md", "# Project notes\n")
    assert check_memory_store(build_context(valid_root)) == []


@pytest.mark.parametrize(
    "rule", ["memory/", "memory/*", "memory/**", "/memory/*", "  memory/*  "]
)
def test_memory_store_recognises_every_accepted_rule_spelling(
    valid_root: Path, rule: str
) -> None:
    """Each recognised spelling of the marker makes the check apply."""
    write(valid_root / ".gitignore", f"tmp/\n{rule}\n!memory/state.yaml\n")
    write(valid_root / "memory" / "notes.md", "# Notes\n")
    findings = check_memory_store(build_context(valid_root))
    assert severities(findings) == [Severity.ERROR]
    assert "memory/notes.md must not exist here" in findings[0].message


def test_memory_store_ignores_a_narrower_glob(valid_root: Path) -> None:
    """A partial rule lies outside the documented match."""
    write(valid_root / ".gitignore", "tmp/\nmemory/*.md\n")
    write(valid_root / "memory" / "notes.md", "# Project notes\n")
    assert check_memory_store(build_context(valid_root)) == []
