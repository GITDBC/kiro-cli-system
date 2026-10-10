"""
Tests for the permissions.rules and tools-tag checks.

Each documented vocabulary rule gets a passing case (the value accepted)
and a failing case (a violation caught), since a check that cannot fail
is not a check. The regex-smell cases also cover the valid glob
constructs it must not flag: '*', '**', and the concurrently-introduced
patterns this task's coordination note calls out by name.
"""

# Standard libraries
from pathlib import Path

# Own modules
from driftcheck.checks.permissions import check_permission_rules, check_tool_tags
from driftcheck.types import Severity, build_context
from tests.helpers import problems, severities, write, write_agent


def _agent_with_rule(root: Path, **rule: object) -> None:
    """Write senior-developer with a single permissions.rules entry."""
    write_agent(
        root,
        "senior-developer",
        permissions={"rules": [rule]},
    )


def test_permission_rules_accept_documented_capability(valid_root: Path) -> None:
    """A documented capability with a clean pattern is clean."""
    _agent_with_rule(
        valid_root, capability="shell", match=["git *", "uv *"], effect="allow"
    )
    assert problems(check_permission_rules(build_context(valid_root))) == []


def test_permission_rules_reject_undocumented_capability(valid_root: Path) -> None:
    """A capability outside the documented set is an error."""
    _agent_with_rule(valid_root, capability="banana", match=["*"], effect="allow")
    errors = problems(check_permission_rules(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "banana" in errors[0].message
    assert "not a documented capability" in errors[0].message


def test_permission_rules_accept_every_documented_effect(valid_root: Path) -> None:
    """allow, deny and ask are all accepted, including the new 'ask'."""
    write_agent(
        valid_root,
        "senior-developer",
        permissions={
            "rules": [
                {"capability": "shell", "match": ["git *"], "effect": "allow"},
                {"capability": "fs_write", "match": ["*.env"], "effect": "deny"},
                {
                    "capability": "shell",
                    "match": ["terraform apply*"],
                    "effect": "ask",
                },
            ]
        },
    )
    assert problems(check_permission_rules(build_context(valid_root))) == []


def test_permission_rules_reject_bad_effect(valid_root: Path) -> None:
    """An effect outside allow/deny/ask is an error."""
    _agent_with_rule(valid_root, capability="shell", match=["*"], effect="banana")
    errors = problems(check_permission_rules(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "effect 'banana'" in errors[0].message


def test_permission_rules_accept_valid_globs_from_concurrent_agent(
    valid_root: Path,
) -> None:
    """Real-world glob patterns introduced alongside this check are clean."""
    write_agent(
        valid_root,
        "senior-developer",
        permissions={
            "rules": [
                {
                    "capability": "fs_read",
                    "match": ["~/.ssh/**"],
                    "effect": "deny",
                },
                {
                    "capability": "shell",
                    "match": ["terraform apply*", "rm -rf *"],
                    "effect": "ask",
                },
                {
                    "capability": "fs_write",
                    "match": ["**/.env.*"],
                    "effect": "deny",
                },
                {
                    "capability": "shell",
                    "match": ["cp memory/state.yaml*"],
                    "effect": "allow",
                },
            ]
        },
    )
    assert problems(check_permission_rules(build_context(valid_root))) == []


def test_permission_rules_reject_regex_anchor(valid_root: Path) -> None:
    """A leftover v2 '^...$' anchor pair is an error."""
    _agent_with_rule(
        valid_root, capability="shell", match=["^git status$"], effect="allow"
    )
    errors = problems(check_permission_rules(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR, Severity.ERROR]
    messages = " ".join(error.message for error in errors)
    assert "^git status$" in messages
    assert "regex" in messages.lower()


def test_permission_rules_reject_anchored_dotstar(valid_root: Path) -> None:
    """A leftover regex '^.*$' is caught by the anchor checks."""
    _agent_with_rule(valid_root, capability="shell", match=["^.*$"], effect="allow")
    errors = problems(check_permission_rules(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR, Severity.ERROR]
    messages = " ".join(error.message for error in errors)
    assert "^.*$" in messages


def test_permission_rules_accept_dot_star_as_valid_glob(valid_root: Path) -> None:
    """Bare '.*' is valid glob (literal dot + wildcard), not a smell."""
    _agent_with_rule(
        valid_root, capability="fs_write", match=["**/.env.*"], effect="deny"
    )
    assert problems(check_permission_rules(build_context(valid_root))) == []


def test_permission_rules_accept_star_and_double_star(valid_root: Path) -> None:
    """The valid glob wildcards '*' and '**' never trigger a smell."""
    _agent_with_rule(
        valid_root, capability="fs_write", match=["*", "**", "src/**"], effect="allow"
    )
    assert problems(check_permission_rules(build_context(valid_root))) == []


def test_permission_rules_reject_backslash_escape(valid_root: Path) -> None:
    """A leftover regex escape such as '\\.ts$' is an error."""
    _agent_with_rule(
        valid_root, capability="fs_write", match=["\\.ts$"], effect="allow"
    )
    errors = problems(check_permission_rules(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR, Severity.ERROR]


def test_permission_rules_accept_question_mark_for_filesystem(
    valid_root: Path,
) -> None:
    """'?' is valid in fs_read/fs_write patterns per the spec."""
    _agent_with_rule(
        valid_root, capability="fs_read", match=["file?.txt"], effect="allow"
    )
    assert problems(check_permission_rules(build_context(valid_root))) == []


def test_permission_rules_reject_question_mark_for_shell(valid_root: Path) -> None:
    """'?' is unsupported outside fs_read/fs_write patterns."""
    _agent_with_rule(
        valid_root, capability="shell", match=["gi? status"], effect="allow"
    )
    errors = problems(check_permission_rules(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "'?'" in errors[0].message


def test_permission_rules_check_exclude_patterns_too(valid_root: Path) -> None:
    """The exclude field is validated the same way as match."""
    _agent_with_rule(
        valid_root,
        capability="mcp",
        match=["my-server/*"],
        exclude=["^dangerous$"],
        effect="allow",
    )
    errors = problems(check_permission_rules(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR, Severity.ERROR]
    assert any("exclude" in error.message for error in errors)


def test_permission_rules_ignore_malformed_config(valid_root: Path) -> None:
    """An unparseable config belongs to the resource check, not this one."""
    write(valid_root / ".kiro" / "agents" / "broken.json", "{not json")
    assert problems(check_permission_rules(build_context(valid_root))) == []


def test_permission_rules_tolerate_absent_permissions(valid_root: Path) -> None:
    """An agent with no permissions field at all is clean."""
    assert problems(check_permission_rules(build_context(valid_root))) == []


def test_tool_tags_accept_documented_tags(valid_root: Path) -> None:
    """Every documented tag, including the meta-tags, is accepted."""
    write_agent(
        valid_root,
        "senior-developer",
        tools=["read", "write", "shell", "web", "subagent", "@mcp", "@builtin", "*"],
    )
    assert problems(check_tool_tags(build_context(valid_root))) == []


def test_tool_tags_reject_typo(valid_root: Path) -> None:
    """A typo such as 'shel' is an error, not a silent no-op grant."""
    write_agent(valid_root, "senior-developer", tools=["read", "shel"])
    errors = problems(check_tool_tags(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "'shel'" in errors[0].message
    assert "not a documented tag" in errors[0].message


def test_tool_tags_tolerate_absent_tools_field(valid_root: Path) -> None:
    """An agent config with no tools array has nothing to validate."""
    assert problems(check_tool_tags(build_context(valid_root))) == []
