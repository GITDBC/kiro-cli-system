"""
Tests for the hook-command and hook-coverage checks.

Both resolution branches are covered: a command naming a script file on
disk, and a command running a console script that must be declared in a
tool's ``[project.scripts]`` table. The second branch is the one that
silently passed before hooks became console scripts. The git-safety
coverage check is exercised from both directions: a shell-capable agent
with no PreToolUse hook wiring the script at all, and a matcher too
narrow to cover one of the two shell tool ids.
"""

# Standard libraries
from pathlib import Path

# Own modules
from driftcheck.checks.hooks import (
    _console_script_target,
    check_git_safety_hook,
    check_hook_scripts,
)
from driftcheck.types import Severity, build_context
from tests.helpers import (
    problems,
    severities,
    write,
    write_agent,
    write_git_safety_hook,
    write_hooks_file,
)

CONSOLE_COMMAND = "uv run --project tools/driftcheck driftcheck-hook-state-yaml"


def _hooks_document(command: str, trigger: str = "PostToolUse") -> dict[str, object]:
    """Build a minimal single-hook document for the given command."""
    return {
        "version": "v1",
        "hooks": [
            {
                "name": "test-hook",
                "trigger": trigger,
                "matcher": "",
                "action": {"type": "command", "command": command},
                "timeout": 5,
                "enabled": True,
            }
        ],
    }


def test_hook_scripts_detect_missing_script(valid_root: Path) -> None:
    """A hook command naming a missing script is an error."""
    write_hooks_file(
        valid_root,
        document=_hooks_document("python3 scripts/hooks/absent.py"),
    )
    findings = check_hook_scripts(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "scripts/hooks/absent.py" in errors[0].message


def test_hook_scripts_accept_existing_script(valid_root: Path) -> None:
    """A hook command naming an existing script is clean."""
    write(valid_root / "scripts" / "hooks" / "present.py", "print('hi')\n")
    write_hooks_file(
        valid_root,
        document=_hooks_document(
            "python3 scripts/hooks/present.py", trigger="SessionStart"
        ),
    )
    assert problems(check_hook_scripts(build_context(valid_root))) == []


def test_hook_scripts_accept_declared_console_script(valid_root: Path) -> None:
    """A console script declared in [project.scripts] is clean."""
    write_hooks_file(valid_root, document=_hooks_document(CONSOLE_COMMAND))
    assert problems(check_hook_scripts(build_context(valid_root))) == []


def test_hook_scripts_detect_undeclared_console_script(valid_root: Path) -> None:
    """A console script absent from [project.scripts] is an error."""
    write_hooks_file(
        valid_root,
        document=_hooks_document(
            "uv run --project tools/driftcheck driftcheck-hook-ghost"
        ),
    )
    findings = check_hook_scripts(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "driftcheck-hook-ghost" in errors[0].message
    assert "[project.scripts]" in errors[0].message


def test_hook_scripts_detect_missing_project_manifest(valid_root: Path) -> None:
    """A console script from a non-existent tool is an error."""
    write_hooks_file(
        valid_root,
        document=_hooks_document("uv run --project tools/absent absent-hook"),
    )
    findings = check_hook_scripts(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "does not exist" in errors[0].message


def test_hook_scripts_detect_uv_run_without_a_command(valid_root: Path) -> None:
    """A uv run invocation naming nothing runnable is an error."""
    write_hooks_file(
        valid_root,
        document=_hooks_document("uv run --project tools/driftcheck"),
    )
    findings = check_hook_scripts(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "neither a script file nor a console script" in errors[0].message


def test_hook_scripts_report_malformed_json(valid_root: Path) -> None:
    """An unparseable hooks file is an error, not a crash."""
    write(valid_root / ".kiro" / "hooks" / "broken.json", "{not json")
    findings = check_hook_scripts(build_context(valid_root))
    errors = problems(findings)
    assert severities(errors) == [Severity.ERROR]
    assert "broken.json is not valid JSON" in errors[0].message


def test_hook_scripts_ignore_unrelated_commands(valid_root: Path) -> None:
    """A command that is neither uv run nor a script is left alone."""
    write_hooks_file(
        valid_root,
        document=_hooks_document("echo hello", trigger="SessionStart"),
    )
    assert problems(check_hook_scripts(build_context(valid_root))) == []


def test_hook_scripts_validate_pre_tool_use_trigger(valid_root: Path) -> None:
    """A PreToolUse script path is validated like the other triggers."""
    write_hooks_file(
        valid_root,
        document=_hooks_document(".kiro/hooks/absent.sh", trigger="PreToolUse"),
    )
    errors = problems(check_hook_scripts(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert ".kiro/hooks/absent.sh" in errors[0].message


def test_hook_scripts_accept_every_documented_trigger(valid_root: Path) -> None:
    """Each of the eleven documented PascalCase triggers is accepted."""
    triggers = [
        "SessionStart",
        "Stop",
        "PreToolUse",
        "PostToolUse",
        "PreTaskExec",
        "PostTaskExec",
        "UserPromptSubmit",
        "PostFileCreate",
        "PostFileSave",
        "PostFileDelete",
        "Manual",
    ]
    document = {
        "version": "v1",
        "hooks": [
            {
                "name": f"hook-{trigger}",
                "trigger": trigger,
                "action": {"type": "command", "command": "echo hello"},
                "timeout": 5,
                "enabled": True,
            }
            for trigger in triggers
        ],
    }
    write_hooks_file(valid_root, document=document)
    assert problems(check_hook_scripts(build_context(valid_root))) == []


def test_hook_scripts_reject_lowercase_trigger(valid_root: Path) -> None:
    """A leftover v2 casing such as 'preToolUse' is an error."""
    write_hooks_file(
        valid_root,
        document=_hooks_document("echo hello", trigger="preToolUse"),
    )
    errors = problems(check_hook_scripts(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "preToolUse" in errors[0].message
    assert "not one of the documented triggers" in errors[0].message


def test_hook_scripts_reject_unknown_trigger(valid_root: Path) -> None:
    """A trigger name that is not on the documented list is an error."""
    write_hooks_file(
        valid_root,
        document=_hooks_document("echo hello", trigger="OnFileOpen"),
    )
    errors = problems(check_hook_scripts(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "OnFileOpen" in errors[0].message


def test_hook_scripts_accept_current_schema_version(valid_root: Path) -> None:
    """A document declaring version 'v1' is clean."""
    write_hooks_file(valid_root, document=_hooks_document("echo hello"))
    assert problems(check_hook_scripts(build_context(valid_root))) == []


def test_hook_scripts_reject_wrong_schema_version(valid_root: Path) -> None:
    """A document declaring any version other than 'v1' is an error."""
    document = _hooks_document("echo hello")
    document["version"] = "v0"
    write_hooks_file(valid_root, document=document)
    errors = problems(check_hook_scripts(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "v0" in errors[0].message
    assert "expected 'v1'" in errors[0].message


def test_hook_scripts_accept_compiling_matcher(valid_root: Path) -> None:
    """A matcher that is valid regex syntax is clean."""
    write_hooks_file(
        valid_root,
        document=_hooks_document("echo hello", trigger="PostFileSave"),
    )
    document = _hooks_document("echo hello", trigger="PostFileSave")
    document["hooks"][0]["matcher"] = r"\.(ts|tsx)$"
    write_hooks_file(valid_root, name="matcher-ok", document=document)
    assert problems(check_hook_scripts(build_context(valid_root))) == []


def test_hook_scripts_reject_non_compiling_matcher(valid_root: Path) -> None:
    """A matcher that is not valid regex is an error, not silently ignored."""
    document = _hooks_document("echo hello", trigger="PostFileSave")
    document["hooks"][0]["matcher"] = "(unclosed"
    write_hooks_file(valid_root, document=document)
    errors = problems(check_hook_scripts(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "does not compile as a regex" in errors[0].message
    assert "(unclosed" in errors[0].message


def test_hook_scripts_accept_empty_matcher(valid_root: Path) -> None:
    """An explicit empty-string matcher is tolerated (always-match)."""
    document = _hooks_document("echo hello", trigger="SessionStart")
    document["hooks"][0]["matcher"] = ""
    write_hooks_file(valid_root, document=document)
    assert problems(check_hook_scripts(build_context(valid_root))) == []


def test_git_safety_accepts_shell_agent_with_full_matcher(valid_root: Path) -> None:
    """A shell-capable agent is clean when the matcher covers both tool ids."""
    write_git_safety_hook(valid_root)
    write_hooks_file(valid_root)
    write_agent(valid_root, "senior-developer", tools=["read", "shell"])
    assert problems(check_git_safety_hook(build_context(valid_root))) == []


def test_git_safety_detects_shell_agent_without_any_hook(valid_root: Path) -> None:
    """A shell-capable agent with no git-safety hook at all is an error."""
    write_git_safety_hook(valid_root)
    write_agent(valid_root, "senior-developer", tools=["read", "shell"])
    errors = problems(check_git_safety_hook(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "destructive git commands run unguarded" in errors[0].message
    assert "senior-developer" in errors[0].message


def test_git_safety_warns_on_matcher_missing_control_bash_process(
    valid_root: Path,
) -> None:
    """A matcher covering only execute_bash warns about the gap."""
    write_git_safety_hook(valid_root)
    write_hooks_file(
        valid_root,
        document={
            "version": "v1",
            "hooks": [
                {
                    "name": "git-safety",
                    "trigger": "PreToolUse",
                    "matcher": "execute_bash",
                    "action": {
                        "type": "command",
                        "command": ".kiro/hooks/git-safety.sh",
                    },
                    "timeout": 5,
                    "enabled": True,
                }
            ],
        },
    )
    write_agent(valid_root, "senior-developer", tools=["read", "shell"])
    warnings = problems(check_git_safety_hook(build_context(valid_root)))
    assert severities(warnings) == [Severity.WARNING]
    assert "control_bash_process" in warnings[0].message


def test_git_safety_detects_missing_script(valid_root: Path) -> None:
    """A referenced but absent hook script is an error."""
    write_hooks_file(valid_root)
    write_agent(valid_root, "senior-developer", tools=["read", "shell"])
    errors = problems(check_git_safety_hook(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "does not exist" in errors[0].message


def test_git_safety_ignores_absent_script_when_no_shell_agent(
    valid_root: Path,
) -> None:
    """A tree with no shell-capable agent needs no guardrail."""
    assert problems(check_git_safety_hook(build_context(valid_root))) == []


def test_git_safety_detects_non_executable_script(valid_root: Path) -> None:
    """A hook script without the execute bit is an error."""
    script = write_git_safety_hook(valid_root)
    script.chmod(0o644)
    write_hooks_file(valid_root)
    write_agent(valid_root, "senior-developer", tools=["read", "shell"])
    errors = problems(check_git_safety_hook(build_context(valid_root)))
    assert severities(errors) == [Severity.ERROR]
    assert "not executable" in errors[0].message


def test_console_script_target_parses_flag_forms() -> None:
    """Both --project forms resolve to the same target."""
    assert _console_script_target(CONSOLE_COMMAND) == (
        "tools/driftcheck",
        "driftcheck-hook-state-yaml",
    )
    assert _console_script_target(
        "uv run --project=tools/driftcheck --no-sync driftcheck"
    ) == ("tools/driftcheck", "driftcheck")
    assert _console_script_target("uv run driftcheck") == ("", "driftcheck")
