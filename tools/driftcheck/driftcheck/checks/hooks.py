"""
Checks over the hook commands declared by standalone hook files.

CLI 3.0 moved hook definitions out of each agent config's embedded
``hooks`` object into standalone ``.kiro/hooks/*.json`` files (schema
version ``v1``, PascalCase triggers, regex ``matcher``). A hook command
reaches its implementation in one of two ways, and both have to be
validated or the check degrades into a no-op:

- **Script file**: a token ending in ``.py``, ``.sh`` or ``.js``, which
  must exist relative to the repository root.
- **Console script**: a ``uv run --project <tool> <name>`` invocation,
  where ``<name>`` must be declared in that tool's ``[project.scripts]``
  table.

Validating only the first form is how this check silently passed after
the hooks moved into ``tools/driftcheck``: the commands no longer carry
a ``.py`` token, so nothing was inspected at all. A ``uv run`` command
that resolves to neither form is therefore an error rather than an
implicit pass.

The same check also validates the shape of each hook entry itself: the
``trigger`` must be one of the eleven documented PascalCase trigger
names, the document's ``version`` must be ``"v1"``, and a non-empty
``matcher`` must compile as a regex — hook matchers are regex, unlike
the glob ``match``/``exclude`` patterns validated in
``checks/permissions.py``, and the two must not be conflated. A leftover
v2 trigger casing such as ``preToolUse`` would otherwise never fire and
never be reported, since an unrecognised trigger name is simply ignored
by the runtime rather than rejected.

Coverage of the git-safety hook is checked here too: resolving the
commands a hook file declares says nothing about the agents that never
gained the guardrail, which is the failure mode a hand-wired
allowlisted-tool check actually has. Because standalone hook files are
no longer scoped to a single agent, coverage is evaluated against the
*matcher*: a ``PreToolUse`` hook whose regex matches both shell tool IDs
is treated as covering every shell-capable agent repository-wide, since
v3 hooks fire per matching tool invocation regardless of which agent
issued it.
"""

# Standard libraries
import json
import os
import re
import tomllib
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Final

# Own modules
from driftcheck.types import DriftContext, Finding, Severity

SCRIPT_SUFFIXES: Final[tuple[str, ...]] = (".py", ".sh", ".js")

# hooks.md, "Field reference": schema version currently in force.
HOOKS_SCHEMA_VERSION: Final[str] = "v1"

# hooks.md, "Available triggers": the eleven documented PascalCase
# trigger names. A hook using any other casing or spelling silently
# never fires — the runtime does not reject an unrecognised trigger, it
# simply never matches it, so this allow-list is the only place that
# failure becomes visible.
ALLOWED_TRIGGERS: Final[frozenset[str]] = frozenset(
    (
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
    )
)

# v3 trigger this module cares about for the git-safety guardrail. Other
# triggers (SessionStart, PostToolUse, ...) are still walked for script
# resolution but do not participate in shell-coverage evaluation.
PRE_TOOL_USE: Final[str] = "PreToolUse"

# Shell tool IDs the git-safety matcher must cover. execute_bash is the
# 2.x-era tool; control_bash_process is new in v3 and grouped under the
# same "shell" tag, so a matcher that only names execute_bash would
# silently miss it.
SHELL_TOOL_IDS: Final[tuple[str, ...]] = ("execute_bash", "control_bash_process")

# Guardrail every shell-capable agent must have wired.
GIT_SAFETY_SCRIPT: Final[str] = ".kiro/hooks/git-safety.sh"
SHELL_TAG: Final[str] = "shell"

UV_RUN: Final[tuple[str, str]] = ("uv", "run")
PROJECT_FLAG: Final[str] = "--project"

# `uv run` flags that consume the following token as their value, so it
# must not be mistaken for the command being run.
VALUE_FLAGS: Final[tuple[str, ...]] = (
    PROJECT_FLAG,
    "--python",
    "-p",
    "--with",
    "--with-requirements",
    "--directory",
    "--group",
    "--extra",
    "--index",
)

SECTION_HOOKS: Final[str] = "Hook script path references"
SECTION_GIT_SAFETY: Final[str] = "Git-safety hook coverage"


def _hook_files(root: Path) -> Iterator[tuple[Path, dict[str, Any] | None, str | None]]:
    """
    Iterate standalone hook definition files.

    Args:
        root: Repository root.

    Yields:
        Tuples of (path, decoded document, decode error message). The
        document is None and the error is set when the file is not
        valid JSON, mirroring how AgentConfig reports decode failures.
    """
    hooks_dir = root / ".kiro" / "hooks"
    if not hooks_dir.is_dir():
        return
    for path in sorted(hooks_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            yield path, None, str(error)
            continue
        if not isinstance(data, dict):
            yield path, None, "top level is not an object"
            continue
        yield path, data, None


def _hook_entries(document: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """
    Iterate the hook entries of one decoded standalone hooks document.

    Args:
        document: Decoded ``.kiro/hooks/*.json`` document.

    Yields:
        Each entry of the document's ``hooks`` array.
    """
    entries = document.get("hooks") or []
    if not isinstance(entries, list):
        return
    for entry in entries:
        if isinstance(entry, dict):
            yield entry


def check_hook_scripts(ctx: DriftContext) -> list[Finding]:
    """
    Verify hook documents, entries and commands are well-formed.

    Validates, per standalone hook file: the document's schema
    ``version`` is ``"v1"``; each entry's ``trigger`` is one of the
    eleven documented PascalCase names; a non-empty ``matcher`` compiles
    as a regex; and the ``action.command`` resolves to an existing
    script file or a console script declared in a tool's
    ``[project.scripts]`` table.

    Args:
        ctx: Shared check context.

    Returns:
        An error per violation, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    for path, document, error in _hook_files(ctx.root):
        if document is None:
            findings.append(
                Finding(
                    Severity.ERROR,
                    SECTION_HOOKS,
                    f"{path.name} is not valid JSON: {error}",
                )
            )
            continue
        findings.extend(_version_finding(path.name, document))
        for entry in _hook_entries(document):
            findings.extend(_hook_entry_findings(ctx.root, path.name, entry))
    findings.append(Finding(Severity.OK, SECTION_HOOKS, "Hook script paths checked"))
    return findings


def _version_finding(file_name: str, document: dict[str, Any]) -> list[Finding]:
    """
    Validate a standalone hooks document's schema version.

    Args:
        file_name: Standalone hook file name, used in messages.
        document: Decoded ``.kiro/hooks/*.json`` document.

    Returns:
        A single ERROR finding, or an empty list when the version is
        the current schema version.
    """
    version = document.get("version")
    if version == HOOKS_SCHEMA_VERSION:
        return []
    return [
        Finding(
            Severity.ERROR,
            SECTION_HOOKS,
            f"{file_name} declares version {version!r}, expected "
            f"'{HOOKS_SCHEMA_VERSION}'",
        )
    ]


def _hook_entry_findings(
    root: Path, file_name: str, entry: dict[str, Any]
) -> list[Finding]:
    """
    Validate one hook entry's trigger, matcher and command.

    Args:
        root: Repository root.
        file_name: Standalone hook file name, used in messages.
        entry: Single hook entry from a standalone hooks document.

    Returns:
        One ERROR per violation the entry carries.
    """
    findings: list[Finding] = []
    trigger = entry.get("trigger")
    if trigger not in ALLOWED_TRIGGERS:
        allowed = ", ".join(sorted(ALLOWED_TRIGGERS))
        findings.append(
            Finding(
                Severity.ERROR,
                SECTION_HOOKS,
                f"{file_name} hook {entry.get('name')!r} has trigger "
                f"{trigger!r}, not one of the documented triggers: {allowed}",
            )
        )
    matcher = entry.get("matcher")
    if isinstance(matcher, str) and matcher and not _matcher_compiles(matcher):
        findings.append(
            Finding(
                Severity.ERROR,
                SECTION_HOOKS,
                f"{file_name} hook {entry.get('name')!r} has a matcher "
                f"that does not compile as a regex: {matcher!r}",
            )
        )
    command = entry.get("action", {}).get("command", "")
    if isinstance(command, str) and command:
        finding = _validate_command(root, file_name, command)
        if finding is not None:
            findings.append(finding)
    return findings


def _matcher_compiles(matcher: str) -> bool:
    """
    Report whether a hook matcher compiles as a regex.

    Args:
        matcher: Non-empty raw matcher value from a hook entry.

    Returns:
        True when the matcher is valid regex syntax.
    """
    try:
        re.compile(matcher)
    except re.error:
        return False
    return True


def check_git_safety_hook(ctx: DriftContext) -> list[Finding]:
    """
    Verify shell-capable agents are covered by the git-safety guardrail.

    Standalone hooks are no longer scoped to one agent, so coverage is
    evaluated once against every ``PreToolUse`` hook's matcher rather
    than per agent: if some matcher's regex matches both shell tool IDs
    and runs the git-safety script, every shell-capable agent is
    covered. Missing coverage is an ERROR — destructive git commands
    would run unguarded for every agent granting the ``shell`` tag. A
    matcher wired to the script but too narrow to catch one of the
    shell tool IDs only warns, since it still fires for the other one
    rather than never firing at all.

    Args:
        ctx: Shared check context.

    Returns:
        Findings describing coverage gaps, plus a trailing OK finding.
    """
    shell_agents = [
        config.stem
        for config in ctx.agent_configs
        if isinstance(config.data, dict)
        and isinstance(config.data.get("tools"), list)
        and SHELL_TAG in config.data["tools"]
    ]
    if not shell_agents:
        return [
            Finding(Severity.OK, SECTION_GIT_SAFETY, "Git-safety hook coverage checked")
        ]

    matched_ids, referenced = _git_safety_matcher_coverage(ctx.root)
    findings: list[Finding] = []
    if not referenced:
        findings.append(
            Finding(
                Severity.ERROR,
                SECTION_GIT_SAFETY,
                f"No PreToolUse hook in .kiro/hooks/*.json runs "
                f"{GIT_SAFETY_SCRIPT}, but {len(shell_agents)} agent(s) "
                f"grant the '{SHELL_TAG}' tag ({', '.join(shell_agents)}) — "
                "destructive git commands run unguarded",
            )
        )
    else:
        missing_ids = [tool for tool in SHELL_TOOL_IDS if tool not in matched_ids]
        for tool in missing_ids:
            findings.append(
                Finding(
                    Severity.WARNING,
                    SECTION_GIT_SAFETY,
                    f"The git-safety PreToolUse matcher does not cover "
                    f"'{tool}' — agents invoking it bypass the guardrail",
                )
            )
        findings.extend(_git_safety_script_findings(ctx.root))
    findings.append(
        Finding(Severity.OK, SECTION_GIT_SAFETY, "Git-safety hook coverage checked")
    )
    return findings


def _git_safety_matcher_coverage(root: Path) -> tuple[frozenset[str], bool]:
    """
    Determine which shell tool IDs the git-safety matcher covers.

    Args:
        root: Repository root.

    Returns:
        Tuple of (matched tool ids, whether any hook wires the script at
        all).
    """
    matched: set[str] = set()
    referenced = False
    for _, document, error in _hook_files(root):
        if document is None or error is not None:
            continue
        for entry in _hook_entries(document):
            entry_matched = _git_safety_entry_matches(entry)
            if entry_matched is None:
                continue
            referenced = True
            matched |= entry_matched
    return frozenset(matched), referenced


def _git_safety_entry_matches(entry: dict[str, Any]) -> frozenset[str] | None:
    """
    Report the shell tool ids one PreToolUse entry's matcher covers.

    Args:
        entry: Single hook entry from a standalone hooks document.

    Returns:
        None when the entry does not wire the git-safety script at all;
        otherwise the (possibly empty) set of shell tool ids its matcher
        covers.
    """
    if entry.get("trigger") != PRE_TOOL_USE:
        return None
    command = entry.get("action", {}).get("command", "")
    if not isinstance(command, str) or GIT_SAFETY_SCRIPT not in command:
        return None
    pattern = _compile_matcher(entry.get("matcher", ""))
    if pattern is None:
        return frozenset()
    return frozenset(
        tool_id for tool_id in SHELL_TOOL_IDS if pattern.fullmatch(tool_id)
    )


def _compile_matcher(matcher: object) -> re.Pattern[str] | None:
    """
    Compile a hook's matcher field, tolerating bad input.

    Args:
        matcher: Raw matcher value from a hook entry.

    Returns:
        The compiled pattern, or None when it is empty, not a string, or
        not valid regex.
    """
    if not isinstance(matcher, str) or not matcher:
        return None
    try:
        return re.compile(matcher)
    except re.error:
        return None


def _git_safety_script_findings(root: Path) -> list[Finding]:
    """
    Check the git-safety script exists and is executable.

    Args:
        root: Repository root.

    Returns:
        A single ERROR finding, or an empty list when the script is fine.
    """
    script = root / GIT_SAFETY_SCRIPT
    if not script.is_file():
        return [
            Finding(
                Severity.ERROR,
                SECTION_GIT_SAFETY,
                f"{GIT_SAFETY_SCRIPT} does not exist, but a hook references it",
            )
        ]
    if not os.access(script, os.X_OK):
        return [
            Finding(
                Severity.ERROR,
                SECTION_GIT_SAFETY,
                f"{GIT_SAFETY_SCRIPT} is not executable — the hook would fail to run",
            )
        ]
    return []


def _validate_command(root: Path, file_name: str, command: str) -> Finding | None:
    """
    Validate a single hook command against the repository tree.

    Args:
        root: Repository root.
        file_name: Standalone hook file name, used in messages.
        command: Full shell command declared by the hook action.

    Returns:
        An ERROR finding, or None when the command resolves.
    """
    token = _script_token(command)
    if token is not None:
        if (root / token).exists():
            return None
        return Finding(
            Severity.ERROR,
            SECTION_HOOKS,
            f"{file_name} hook references missing script: {token}",
        )
    if not _is_uv_run(command):
        return None
    return _validate_console_script(root, file_name, command)


def _script_token(command: str) -> str | None:
    """
    Extract the script path from a hook command line.

    Args:
        command: Full shell command declared by the hook action.

    Returns:
        The last token ending in .py, .sh or .js, or None.
    """
    for token in reversed(command.split()):
        if token.endswith(SCRIPT_SUFFIXES):
            return token
    return None


def _is_uv_run(command: str) -> bool:
    """
    Report whether a command is a ``uv run`` invocation.

    Args:
        command: Full shell command declared by the hook action.

    Returns:
        True when the command starts with "uv run".
    """
    return tuple(command.split()[:2]) == UV_RUN


def _validate_console_script(
    root: Path, file_name: str, command: str
) -> Finding | None:
    """
    Validate a ``uv run`` command against a tool's declared scripts.

    Args:
        root: Repository root.
        file_name: Standalone hook file name, used in messages.
        command: Full ``uv run`` command declared by the hook action.

    Returns:
        An ERROR finding, or None when the console script is declared.
    """
    project, script = _console_script_target(command)
    if script is None:
        return Finding(
            Severity.ERROR,
            SECTION_HOOKS,
            f"{file_name} hook command names neither a script file nor a "
            f"console script: {command}",
        )
    manifest = root / project / "pyproject.toml" if project else root / "pyproject.toml"
    relative = manifest.relative_to(root) if manifest.is_relative_to(root) else manifest
    if not manifest.is_file():
        return Finding(
            Severity.ERROR,
            SECTION_HOOKS,
            f"{file_name} hook runs console script '{script}' but "
            f"{relative} does not exist",
        )
    try:
        declared = _declared_scripts(manifest)
    except (OSError, tomllib.TOMLDecodeError) as error:
        return Finding(
            Severity.ERROR,
            SECTION_HOOKS,
            f"{file_name} hook runs console script '{script}' but "
            f"{relative} cannot be read: {error}",
        )
    if script in declared:
        return None
    return Finding(
        Severity.ERROR,
        SECTION_HOOKS,
        f"{file_name} hook runs console script '{script}' not declared in "
        f"{relative} [project.scripts]",
    )


def _console_script_target(command: str) -> tuple[str, str | None]:
    """
    Split a ``uv run`` command into its project and console script.

    Args:
        command: Full ``uv run`` command declared by the hook action.

    Returns:
        Tuple of (project directory, console script name). The name is
        None when the command runs no positional command at all.
    """
    tokens = command.split()[len(UV_RUN) :]
    project = ""
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in VALUE_FLAGS:
            if token == PROJECT_FLAG and index + 1 < len(tokens):
                project = tokens[index + 1]
            index += 2
            continue
        if token.startswith("-"):
            key, separator, value = token.partition("=")
            if separator and key == PROJECT_FLAG:
                project = value
            index += 1
            continue
        return project, token
    return project, None


def _declared_scripts(manifest: Path) -> frozenset[str]:
    """
    Read the ``[project.scripts]`` names declared by a pyproject.toml.

    Args:
        manifest: Path to the tool's pyproject.toml.

    Returns:
        Declared console script names.

    Raises:
        OSError: If the manifest cannot be read.
        tomllib.TOMLDecodeError: If the manifest is not valid TOML.
    """
    with manifest.open("rb") as handle:
        data = tomllib.load(handle)
    scripts = data.get("project", {}).get("scripts", {})
    if not isinstance(scripts, dict):
        return frozenset()
    return frozenset(str(name) for name in scripts)
