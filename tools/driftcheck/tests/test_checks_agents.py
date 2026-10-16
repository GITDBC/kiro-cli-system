"""Tests for the agent-configuration checks."""

# Standard libraries
import json
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck.checks.agents import (
    check_agent_registry,
    check_cost_labels,
    check_model_defaults,
    check_model_governance,
    check_resource_path_form,
    check_resource_references,
    check_v2_config_fields,
)
from driftcheck.types import Severity, build_context
from tests.helpers import ROUTING_MD, problems, severities, write, write_agent


def test_resource_references_detect_missing_file(valid_root: Path) -> None:
    """A resource pointing at a missing file is an error."""
    write_agent(valid_root, "senior-developer", resources=["file://nope.md"])
    findings = check_resource_references(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "missing resource: nope.md" in errors[0].message


def test_resource_references_report_every_missing_entry(valid_root: Path) -> None:
    """All unresolvable resources of a config are reported, not one."""
    write_agent(
        valid_root,
        "senior-developer",
        resources=[
            "file://.kiro/steering/gone-one.md",
            "file://.kiro/steering/gone-two.md",
            "skill://.kiro/skills/gone-three/SKILL.md",
        ],
    )
    errors = problems(check_resource_references(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR] * 3
    messages = " ".join(error.message for error in errors)
    assert "gone-one.md" in messages
    assert "gone-two.md" in messages
    assert "skill://.kiro/skills/gone-three/SKILL.md" in messages


def test_resource_references_detect_missing_skill_uri(valid_root: Path) -> None:
    """A skill:// URI naming no skill directory is an error."""
    write_agent(
        valid_root,
        "senior-developer",
        resources=["skill://.kiro/skills/jira-safety/SKILL.md"],
    )
    errors = problems(check_resource_references(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "skill://.kiro/skills/jira-safety/SKILL.md" in errors[0].message


def test_resource_references_accept_matching_skill_glob(valid_root: Path) -> None:
    """A wildcard matching at least one skill resolves."""
    write_agent(
        valid_root,
        "senior-developer",
        resources=["skill://.kiro/skills/*/SKILL.md"],
    )
    assert problems(check_resource_references(build_context(valid_root))) == []


def test_resource_references_reject_skill_glob_matching_nothing(
    valid_root: Path,
) -> None:
    """A wildcard that matches no skill is an error."""
    write_agent(
        valid_root,
        "senior-developer",
        resources=["skill://.kiro/skills/*/MISSING.md"],
    )
    errors = problems(check_resource_references(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "MISSING.md" in errors[0].message


def test_resource_references_skip_unresolvable_skill_forms(valid_root: Path) -> None:
    """Home-directory and bare-name skill URIs are not path checks."""
    write_agent(
        valid_root,
        "senior-developer",
        resources=["skill://~/.kiro/skills/personal/SKILL.md", "skill://backend"],
    )
    assert problems(check_resource_references(build_context(valid_root))) == []


def test_resource_references_ignore_non_string_resources(valid_root: Path) -> None:
    """A knowledgeBase object carries no path to resolve."""
    write_agent(
        valid_root,
        "senior-developer",
        resources=[{"type": "knowledgeBase", "source": "file://nowhere"}],
    )
    assert problems(check_resource_references(build_context(valid_root))) == []


def test_resource_references_resolve_against_the_workspace_root(
    valid_root: Path,
) -> None:
    """
    Reject the config-relative form even when the file exists on disk.

    ``file://../steering/COMMON.md`` names a real file when joined to
    ``.kiro/agents/``, which is exactly why a config-relative resolution
    base passed thirteen broken configs: Kiro joins it to the workspace
    root instead, lands outside the repository and loads nothing.
    """
    write_agent(
        valid_root,
        "senior-developer",
        resources=["file://../steering/COMMON.md"],
    )
    errors = problems(check_resource_references(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "../steering/COMMON.md" in errors[0].message


def test_resource_references_accept_a_root_relative_file_glob(
    valid_root: Path,
) -> None:
    """A file:// glob matching at least one file resolves."""
    write_agent(
        valid_root,
        "senior-developer",
        resources=["file://.kiro/steering/*.md"],
    )
    assert problems(check_resource_references(build_context(valid_root))) == []


def test_resource_references_reject_a_file_glob_matching_nothing(
    valid_root: Path,
) -> None:
    """A file:// glob that matches nothing is an error."""
    write_agent(
        valid_root,
        "senior-developer",
        resources=["file://.kiro/steering/*.txt"],
    )
    errors = problems(check_resource_references(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "*.txt" in errors[0].message


def test_resource_path_form_accepts_the_valid_tree(valid_root: Path) -> None:
    """Root-relative declarations are the form Kiro resolves."""
    assert problems(check_resource_path_form(build_context(valid_root))) == []


def test_resource_path_form_rejects_a_config_relative_entry(
    valid_root: Path,
) -> None:
    """Name the offending entry and the rule it breaks."""
    write_agent(
        valid_root,
        "senior-developer",
        resources=["file://../steering/COMMON.md", "file://./local.md"],
    )
    errors = problems(check_resource_path_form(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR] * 2
    assert "resolves against the workspace root" in errors[0].message


def test_resource_path_form_leaves_the_prompt_field_alone(valid_root: Path) -> None:
    """The prompt field is documented as config-relative, so it passes."""
    write_agent(
        valid_root,
        "senior-developer",
        prompt="file://../prompts/senior-developer.md",
        resources=["file://.kiro/steering/COMMON.md"],
    )
    assert problems(check_resource_path_form(build_context(valid_root))) == []


def test_resource_references_report_malformed_json(valid_root: Path) -> None:
    """An unparseable config is an error, not a crash."""
    write(valid_root / ".kiro" / "agents" / "broken.json", "{not json")
    findings = check_resource_references(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "broken.json is not valid JSON" in errors[0].message


def test_agent_registry_detects_unregistered_agent(valid_root: Path) -> None:
    """An agent missing from availableAgents is a warning."""
    write_agent(valid_root, "ghost-writer")
    findings = check_agent_registry(build_context(valid_root))
    warnings = problems(findings)
    assert severities(warnings) == [Severity.WARNING]
    assert "ghost-writer" in warnings[0].message


def test_agent_registry_reports_config_without_name(valid_root: Path) -> None:
    """A config with no name field is an error."""
    write(valid_root / ".kiro" / "agents" / "nameless.json", json.dumps({"a": 1}))
    findings = check_agent_registry(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "has no 'name' field" in errors[0].message


def test_v2_fields_clean_tree_reports_no_problem(valid_root: Path) -> None:
    """A v3-shaped tree, orchestrator included, is clean."""
    assert problems(check_v2_config_fields(build_context(valid_root))) == []


def test_v2_fields_reject_allowed_tools(valid_root: Path) -> None:
    """A reappearing allowedTools field is an error."""
    write_agent(
        valid_root,
        "senior-developer",
        allowedTools=["fs_read", "fs_write", "execute_bash"],
    )
    errors = problems(check_v2_config_fields(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "removed v2 field 'allowedTools'" in errors[0].message
    assert "permissions.rules" in errors[0].message


def test_v2_fields_reject_embedded_hooks(valid_root: Path) -> None:
    """An embedded hooks key is an error naming the standalone file."""
    write_agent(
        valid_root,
        "senior-developer",
        hooks={"agentSpawn": [{"command": "git status"}]},
    )
    errors = problems(check_v2_config_fields(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "removed v2 field 'hooks'" in errors[0].message
    assert ".kiro/hooks/*.json" in errors[0].message


def test_v2_fields_reject_per_tool_blocks(valid_root: Path) -> None:
    """A full v2-shaped config is reported key by key."""
    write_agent(
        valid_root,
        "senior-developer",
        allowedTools=["execute_bash"],
        toolsSettings={
            "execute_bash": {
                "allowedCommands": ["^git status$"],
                "denyByDefault": False,
            },
            "fs_write": {"deniedPaths": ["*.lock"]},
        },
    )
    errors = problems(check_v2_config_fields(build_context(valid_root)))
    messages = " ".join(error.message for error in errors)
    assert severities(errors) == [Severity.ERROR] * 6
    assert "toolsSettings.execute_bash" in messages
    assert "toolsSettings.execute_bash.allowedCommands" in messages
    assert "toolsSettings.execute_bash.denyByDefault" in messages
    assert "toolsSettings.fs_write.deniedPaths" in messages


def test_v2_fields_reject_bare_setting_key(valid_root: Path) -> None:
    """A setting key hoisted to the toolsSettings root is an error."""
    write_agent(
        valid_root,
        "senior-developer",
        toolsSettings={"autoAllowReadonly": True},
    )
    errors = problems(check_v2_config_fields(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "toolsSettings.autoAllowReadonly" in errors[0].message


def test_v2_fields_permit_the_subagent_block(valid_root: Path) -> None:
    """toolsSettings.subagent survives in v3 and must not be flagged."""
    write_agent(
        valid_root,
        "orchestrator",
        model="claude-sonnet-5.5",
        toolsSettings={
            "subagent": {
                "availableAgents": ["senior-developer"],
                "trustedAgents": ["*"],
            }
        },
    )
    assert problems(check_v2_config_fields(build_context(valid_root))) == []


def test_v2_fields_ignore_malformed_config(valid_root: Path) -> None:
    """An unparseable config belongs to the resource check, not this one."""
    write(valid_root / ".kiro" / "agents" / "broken.json", "{not json")
    assert problems(check_v2_config_fields(build_context(valid_root))) == []


def test_v2_fields_tolerate_non_object_tools_settings(valid_root: Path) -> None:
    """A toolsSettings value of the wrong type never crashes the check."""
    write_agent(valid_root, "senior-developer", toolsSettings=["shell"])
    assert problems(check_v2_config_fields(build_context(valid_root))) == []


def test_model_governance_rejects_auto(valid_root: Path) -> None:
    """The auto model is an error, not a warning."""
    write_agent(valid_root, "senior-developer", model="auto")
    findings = check_model_governance(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "Auto routing" in errors[0].message


def test_model_governance_rejects_unapproved_model(valid_root: Path) -> None:
    """A non-Anthropic model is an error."""
    write_agent(valid_root, "senior-developer", model="gpt-4o")
    findings = check_model_governance(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "unapproved model 'gpt-4o'" in errors[0].message


@pytest.mark.parametrize(
    "model",
    ["claude-opus-5.5", "claude-sonnet-5.5", "claude-opus-5", "claude-sonnet-5"],
)
def test_model_governance_accepts_both_five_generations(
    valid_root: Path, model: str
) -> None:
    """Adopting 5.5 keeps the previously approved 5.0 ids approved."""
    write_agent(valid_root, "senior-developer", model=model)
    assert problems(check_model_governance(build_context(valid_root))) == []


def test_model_governance_warns_on_missing_model(valid_root: Path) -> None:
    """An agent without a model field is a warning."""
    write_agent(valid_root, "senior-developer", model="")
    findings = check_model_governance(build_context(valid_root))
    warnings = problems(findings)
    assert severities(warnings) == [Severity.WARNING]
    assert "no 'model' field set" in warnings[0].message


def test_cost_labels_detect_wrong_label(valid_root: Path) -> None:
    """An opus agent documented as low cost is a warning."""
    write(
        valid_root / ".kiro" / "orchestration" / "routing.md",
        ROUTING_MD.replace("high (2.0x)", "low (0.4x)"),
    )
    findings = check_cost_labels(build_context(valid_root))
    warnings = problems(findings)
    assert severities(warnings) == [Severity.WARNING]
    assert "cost label" in warnings[0].message


def test_cost_labels_detect_wrong_multiplier(valid_root: Path) -> None:
    """A right label with a wrong multiplier is a warning."""
    write(
        valid_root / ".kiro" / "orchestration" / "routing.md",
        ROUTING_MD.replace("high (2.0x)", "high (1.3x)"),
    )
    findings = check_cost_labels(build_context(valid_root))
    warnings = problems(findings)
    assert severities(warnings) == [Severity.WARNING]
    assert "cost multiplier" in warnings[0].message


def test_cost_labels_hold_opus_five_point_five_at_two_point_zero(
    valid_root: Path,
) -> None:
    """Opus 5.5 is 2.0x, so the 2.2x of the rest of its family is wrong."""
    write(
        valid_root / ".kiro" / "orchestration" / "routing.md",
        ROUTING_MD.replace("high (2.0x)", "high (2.2x)"),
    )
    warnings = problems(check_cost_labels(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "expected '2.0x'" in warnings[0].message


def test_cost_labels_keep_other_opus_models_at_two_point_two(
    valid_root: Path,
) -> None:
    """The 5.5 exception does not leak to the rest of the Opus family."""
    write_agent(valid_root, "senior-developer", model="claude-opus-5")
    write(
        valid_root / ".kiro" / "orchestration" / "routing.md",
        ROUTING_MD.replace("high (2.0x)", "high (2.2x)"),
    )
    assert problems(check_cost_labels(build_context(valid_root))) == []


def test_cost_labels_accept_legacy_label_without_multiplier(
    valid_root: Path,
) -> None:
    """A bare label is tolerated when no multiplier is published."""
    write(
        valid_root / ".kiro" / "orchestration" / "routing.md",
        ROUTING_MD.replace("high (2.0x)", "high"),
    )
    assert problems(check_cost_labels(build_context(valid_root))) == []


def test_cost_labels_skip_agents_without_a_row(valid_root: Path) -> None:
    """An agent with no routing.md row is not flagged."""
    write_agent(valid_root, "undocumented-analyst")
    findings = check_cost_labels(build_context(valid_root))
    assert problems(findings) == []


def test_cost_labels_tolerate_absent_routing_md(valid_root: Path) -> None:
    """A missing routing.md skips the check."""
    (valid_root / ".kiro" / "orchestration" / "routing.md").unlink()
    findings = check_cost_labels(build_context(valid_root))
    assert problems(findings) == []
    assert "skipping" in findings[0].message


def write_cli_settings(root: Path, models: list[str]) -> Path:
    """
    Write a .kiro/settings/cli.json configuring model defaults.

    Args:
        root: Repository root.
        models: Model ids to place under chat.modelDefaults.

    Returns:
        Path to the written settings file.
    """
    payload = {"chat.modelDefaults": {model: {} for model in models}}
    path = root / ".kiro" / "settings" / "cli.json"
    return write(path, json.dumps(payload, indent=2))


def test_model_defaults_accept_models_every_agent_uses(valid_root: Path) -> None:
    """Defaults matching the agents' own models are clean."""
    write_cli_settings(valid_root, ["claude-opus-5.5", "claude-sonnet-5.5"])
    findings = check_model_defaults(build_context(valid_root))
    assert problems(findings) == []


def test_model_defaults_reject_unapproved_model(valid_root: Path) -> None:
    """A non-Anthropic default model is an error."""
    write_cli_settings(valid_root, ["gpt-4o"])
    errors = problems(check_model_defaults(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "unapproved model 'gpt-4o'" in errors[0].message


def test_model_defaults_reject_auto(valid_root: Path) -> None:
    """The auto default is an error, like it is on an agent."""
    write_cli_settings(valid_root, ["auto"])
    errors = problems(check_model_defaults(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "Auto routing" in errors[0].message


def test_model_defaults_warn_on_approved_but_unused_model(
    valid_root: Path,
) -> None:
    """An approved model no agent uses is dead configuration."""
    write_cli_settings(valid_root, ["claude-haiku-4.5"])
    warnings = problems(check_model_defaults(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "no agent uses it" in warnings[0].message


def test_model_defaults_tolerate_missing_file(valid_root: Path) -> None:
    """The settings file is optional, so its absence is OK."""
    findings = check_model_defaults(build_context(valid_root))
    assert problems(findings) == []
    assert "skipping" in findings[0].message


def test_model_defaults_report_malformed_json(valid_root: Path) -> None:
    """Unparseable settings are an error naming the file."""
    write(valid_root / ".kiro" / "settings" / "cli.json", "{not json")
    errors = problems(check_model_defaults(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert ".kiro/settings/cli.json is not valid JSON" in errors[0].message


def test_model_defaults_tolerate_file_without_model_defaults(
    valid_root: Path,
) -> None:
    """Settings with no modelDefaults key have nothing to validate."""
    write(
        valid_root / ".kiro" / "settings" / "cli.json",
        json.dumps({"chat.editMode": "vi"}),
    )
    assert problems(check_model_defaults(build_context(valid_root))) == []


def test_model_defaults_reject_non_object_model_defaults(
    valid_root: Path,
) -> None:
    """A modelDefaults entry of the wrong shape is an error."""
    write(
        valid_root / ".kiro" / "settings" / "cli.json",
        json.dumps({"chat.modelDefaults": ["claude-opus-5.5"]}),
    )
    errors = problems(check_model_defaults(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "'chat.modelDefaults' is not an object" in errors[0].message
