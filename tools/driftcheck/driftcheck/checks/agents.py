"""
Checks over the agent configuration files themselves.

Covers resource resolution (both file:// and skill:// URIs, resolved the
way Kiro resolves them — against the workspace root), the form those
resource paths must take, registration in the orchestrator's
subagent tool entries, the Anthropic-only model allow-list and the
accuracy of the cost labels routing.md publishes for each agent. The
workspace-level model defaults in .kiro/settings/cli.json are validated
here too, against the same allow-list and against the set of models the
agents actually use.
"""

# Standard libraries
import json
import re
from pathlib import Path
from typing import Any, Final

# Own modules
from driftcheck.paths import read_text
from driftcheck.types import AgentConfig, DriftContext, Finding, Severity

# Model governance allow-list (D3: Anthropic/Claude ONLY, no non-Anthropic
# provider may ever be configured). "auto" is explicitly rejected because
# Auto routing may select non-Anthropic models. Update this list when new
# Claude models are approved for use in this project.
ALLOWED_MODELS: Final[tuple[str, ...]] = (
    "claude-opus-5.5",
    "claude-opus-5",
    "claude-opus-4.8",
    "claude-opus-4.7",
    "claude-opus-4.6",
    "claude-opus-4.5",
    "claude-sonnet-5.5",
    "claude-sonnet-5",
    "claude-sonnet-4.6",
    "claude-sonnet-4.5",
    "claude-sonnet-4",
    "claude-haiku-5.5",
    "claude-haiku-4.5",
)

# Rejected outright rather than checked against the allow-list.
AUTO_MODEL: Final[str] = "auto"

# Real credit multipliers per model family, mapped to the cost label
# routing.md is expected to publish for agents backed by that family.
# Matched by prefix in insertion order, so an exact id whose multiplier
# departs from its family must precede the family entry: Kiro's
# models.md and `kiro-cli chat --list-models` both put Claude Opus 5.5 at
# 2.0x while every other Opus model is 2.2x, and Claude Haiku 5.5 at 0.06x
# (up to 100K tokens) against 0.4x for Haiku 4.5.
MODEL_COST_LABELS: Final[dict[str, tuple[str, str]]] = {
    "claude-opus-5.5": ("high", "2.0x"),
    "claude-opus-": ("high", "2.2x"),
    "claude-sonnet-": ("medium", "1.3x"),
    "claude-haiku-5.5": ("low", "0.06x"),
    "claude-haiku-": ("low", "0.4x"),
}

COST_MULTIPLIER: Final[re.Pattern[str]] = re.compile(r"[0-9]+\.[0-9]+x")

# Resource URI schemes. Both a file:// and a skill:// entry in
# `resources` resolve against the repository root and may be a glob; the
# `prompt` field is the only file:// form Kiro resolves against the
# config file's own directory, and it is checked elsewhere.
FILE_URI_PREFIX: Final[str] = "file://"
SKILL_URI_PREFIX: Final[str] = "skill://"

# Characters that make a resource target a glob rather than a literal
# path, so it must be matched with glob() instead of exists().
GLOB_CHARACTERS: Final[str] = "*?["

# Prefixes marking a resource target as written relative to the agent
# config file rather than to the workspace root. Kiro resolves a
# `resources` entry against the workspace root, so "../steering/X.md"
# lands outside the repository and silently loads nothing — while still
# naming a real file when joined to .kiro/agents/, which is how thirteen
# broken configs passed this check green.
CONFIG_RELATIVE_PREFIXES: Final[tuple[str, ...]] = ("./", "../")

# Field shapes the v3 agent engine removed or ignores. This project is
# v3-only, so any of them under .kiro/agents/ is a regression rather than
# a legacy config: the migration rewrote every config by hand precisely
# so that no legitimate one carries them, which is what makes this check
# writable. The remedy is part of the constant because a finding has to
# say where the removed field's behaviour moved to, not merely that it is
# removed. toolsSettings is listed whole: v3 reads none of its blocks,
# the former subagent block included (custom-agents/subagents.md).
V2_FIELD_REMEDIES: Final[dict[str, str]] = {
    "allowedTools": "express trusted tools as tag-based 'tools' plus "
    "'permissions.rules' allow entries",
    "hooks": "move it to a standalone .kiro/hooks/*.json file using the v1 schema",
    "toolsSettings": "v3 ignores it; express shell and file rules as "
    "'permissions.rules' entries and subagent access as 'subagent/<name>' "
    "entries in 'tools' plus a 'subagent' capability allow rule",
}

# Entries of the orchestrator's `tools` array that name one spawnable
# agent, and the selectors that let it spawn any agent regardless
# (custom-agents/subagents.md, "Configuring sub-agent access").
SUBAGENT_TOOL_PREFIX: Final[str] = "subagent/"
UNRESTRICTED_SUBAGENT_SELECTORS: Final[tuple[str, ...]] = ("subagent", "@builtin", "*")

SECTION_RESOURCES: Final[str] = "Resource references"
SECTION_RESOURCE_FORM: Final[str] = "Resource path form"
SECTION_REGISTRY: Final[str] = "Agent registry consistency"
SECTION_V2_FIELDS: Final[str] = "Legacy v2 agent config fields"
SECTION_MODELS: Final[str] = "Model governance (Anthropic-only)"
SECTION_MODEL_DEFAULTS: Final[str] = "Workspace model defaults"
SECTION_COST_LABELS: Final[str] = "routing.md cost label accuracy"
SECTION_AGENT_ENGINE: Final[str] = "Agent engine (v3-only)"

# Relative label used in findings, so the message names the offending
# file the same way regardless of which root was validated.
CLI_SETTINGS_LABEL: Final[str] = ".kiro/settings/cli.json"

# The project runs on the v3 engine only. The setting pins it for
# interactive sessions; headless runs also pass it explicitly, because
# an unattended run must not depend on a user-level configuration.
ENGINE_SETTING: Final[str] = "chat.agentEngine"
ENGINE_VALUE: Final[str] = "v3"
RALPH_SCRIPT: Final[tuple[str, ...]] = (".kiro", "skills", "ralph-loop", "ralph.sh")
RALPH_ENGINE_ARGUMENT: Final[str] = "--agent-engine v3"
HARNESS_SHORTHAND_FLAGS: Final[tuple[str, ...]] = ("--v3", "--v2")


def check_resource_references(ctx: DriftContext) -> list[Finding]:
    """
    Verify every resource in an agent config resolves on disk.

    Reports every unresolvable resource of a config rather than only the
    first: during a bulk resource move a config typically breaks in
    several places at once, and a checker that stops at the first one
    understates the damage exactly when the count matters.

    Args:
        ctx: Shared check context.

    Returns:
        One OK finding per clean config, one ERROR per missing resource.
    """
    findings: list[Finding] = []
    for config in ctx.agent_configs:
        if config.data is None:
            findings.append(
                Finding(
                    Severity.ERROR,
                    SECTION_RESOURCES,
                    f"{config.path.name} is not valid JSON: {config.error}",
                )
            )
            continue
        missing = missing_resources(config, ctx.root)
        if missing:
            findings.extend(
                Finding(
                    Severity.ERROR,
                    SECTION_RESOURCES,
                    f"{config.path.name} → missing resource: {resource}",
                )
                for resource in missing
            )
        else:
            findings.append(
                Finding(
                    Severity.OK,
                    SECTION_RESOURCES,
                    f"{config.path.name} resources valid",
                )
            )
    return findings


def missing_resources(config: AgentConfig, root: Path) -> list[str]:
    """
    Collect every unresolvable resource of a config, in order.

    Every entry of ``resources`` — file:// and skill:// alike — resolves
    against the repository root, which is what Kiro does and what this
    check once got wrong. Entries that are not strings (the
    knowledgeBase object form) carry no path and are skipped.

    Args:
        config: Parsed agent config.
        root: Repository root every resource URI resolves against.

    Returns:
        The offending paths or URIs, empty when everything resolves.
    """
    data = config.data or {}
    resources = data.get("resources") or []
    if not isinstance(resources, list):
        return []
    missing: list[str] = []
    for resource in resources:
        if not isinstance(resource, str):
            continue
        if resource.startswith(SKILL_URI_PREFIX):
            if not _skill_uri_resolves(root, resource):
                missing.append(resource)
            continue
        relative = resource.removeprefix(FILE_URI_PREFIX)
        if not _target_resolves(root, relative):
            missing.append(relative)
    return missing


def _target_resolves(root: Path, target: str) -> bool:
    """
    Report whether a root-relative resource target names something.

    A glob is satisfied by a single match, so ``.kiro/steering/**/*.md``
    is valid while a wildcard matching nothing is not. An absolute or
    home-directory target is used as-is, since Kiro takes those
    verbatim.

    Args:
        root: Repository root.
        target: Resource path with its URI scheme stripped.

    Returns:
        True when the target resolves to at least one existing path.
    """
    if target.startswith("~") or Path(target).is_absolute():
        return Path(target).expanduser().exists()
    if any(character in target for character in GLOB_CHARACTERS):
        return any(root.glob(target))
    return (root / target).exists()


def check_resource_path_form(ctx: DriftContext) -> list[Finding]:
    """
    Reject a file:// resource written relative to the config file.

    ERROR, and separate from resolution: a config-relative entry such as
    ``file://../steering/COMMON.md`` names a real file when joined to
    ``.kiro/agents/``, so a checker that only asks "does this path
    exist somewhere" passes it while Kiro resolves it outside the
    workspace and loads nothing at all. Nothing fails at runtime — the
    agent simply never receives the file — which is what this check
    substitutes for.

    The ``prompt`` field is deliberately out of scope: Kiro documents
    it as resolved against the agent config file's own directory, so
    the config-relative form is correct there and only there.

    Args:
        ctx: Shared check context.

    Returns:
        One ERROR per offending entry, plus a trailing OK finding.
    """
    findings: list[Finding] = [
        Finding(Severity.ERROR, SECTION_RESOURCE_FORM, message)
        for config in ctx.agent_configs
        for message in _resource_form_messages(config)
    ]
    findings.append(
        Finding(Severity.OK, SECTION_RESOURCE_FORM, "Resource path form checked")
    )
    return findings


def _resource_form_messages(config: AgentConfig) -> list[str]:
    """
    Collect every config-relative file:// resource one config declares.

    Args:
        config: Parsed agent config.

    Returns:
        Finding messages, empty when every entry is root-relative.
    """
    data = config.data or {}
    resources = data.get("resources") or []
    if not isinstance(resources, list):
        return []
    return [
        f"{config.path.name} declares '{resource}' relative to the config "
        "file — a resources entry resolves against the workspace root, so "
        "write the path as it reads from the repository root (for example "
        "'file://.kiro/orchestration/routing.md')"
        for resource in resources
        if isinstance(resource, str)
        and resource.startswith(FILE_URI_PREFIX)
        and resource.removeprefix(FILE_URI_PREFIX).startswith(CONFIG_RELATIVE_PREFIXES)
    ]


def _skill_uri_resolves(root: Path, uri: str) -> bool:
    """
    Report whether a skill:// URI names something that exists.

    A glob is satisfied by a single match, so the wildcard form
    ``skill://.kiro/skills/*/SKILL.md`` is valid while a wildcard that
    matches nothing is not. Targets that cannot be checked against this
    tree — a home-directory path, or the bare-name form ``skill://name``
    that Kiro resolves through its skill registry rather than as a path
    — are treated as resolving, since flagging them would be a guess.

    Args:
        root: Repository root.
        uri: Full skill:// URI declared by the config.

    Returns:
        True when the URI resolves, or is not a repository-relative path.
    """
    target = uri.removeprefix(SKILL_URI_PREFIX)
    if target.startswith("~") or "/" not in target:
        return True
    if any(character in target for character in GLOB_CHARACTERS):
        return any(root.glob(target))
    return (root / target).exists()


def check_agent_registry(ctx: DriftContext) -> list[Finding]:
    """
    Verify every agent is listed in the orchestrator's subagent tools.

    v3 limits the agents an agent may spawn through ``subagent/<name>``
    entries in its ``tools`` array. A bare ``subagent`` tag (or ``*`` or
    ``@builtin``, which include it) lets the orchestrator spawn any
    agent, so it defeats the registry and is reported as well.

    Args:
        ctx: Shared check context.

    Returns:
        Findings for unparseable, unregistered agents and open selectors.
    """
    tools = _orchestrator_tools(ctx)
    available = [
        tool.removeprefix(SUBAGENT_TOOL_PREFIX)
        for tool in tools
        if tool.startswith(SUBAGENT_TOOL_PREFIX)
    ]
    findings = [
        Finding(
            Severity.WARNING,
            SECTION_REGISTRY,
            f"Orchestrator tools contain '{selector}', which lets it spawn any "
            f"agent; list '{SUBAGENT_TOOL_PREFIX}<name>' entries instead",
        )
        for selector in UNRESTRICTED_SUBAGENT_SELECTORS
        if selector in tools
    ]
    for config in ctx.agent_configs:
        if config.path != ctx.orchestrator_path:
            findings.extend(_registration_findings(config, available))
    findings.append(Finding(Severity.OK, SECTION_REGISTRY, "Agent registry checked"))
    return findings


def _orchestrator_tools(ctx: DriftContext) -> list[str]:
    """
    Read the string entries of the orchestrator's tools array.

    Args:
        ctx: Shared check context.

    Returns:
        The entries, empty when the orchestrator or the field is absent.
    """
    orchestrator = ctx.orchestrator
    if orchestrator is None or orchestrator.data is None:
        return []
    raw = orchestrator.data.get("tools", [])
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, str)]


def _registration_findings(config: AgentConfig, available: list[str]) -> list[Finding]:
    """
    Check that one agent has a matching subagent tool entry.

    Args:
        config: Parsed config of a non-orchestrator agent.
        available: Agent names the orchestrator's tools list.

    Returns:
        An ERROR for an unnamed config, a WARNING for an unlisted agent.
    """
    name = config.name
    if name is None:
        message = f"{config.path.name} is not valid JSON or has no 'name' field"
        return [Finding(Severity.ERROR, SECTION_REGISTRY, message)]
    if name in available:
        return []
    message = (
        f"Agent '{name}' exists but the orchestrator's tools have no "
        f"'{SUBAGENT_TOOL_PREFIX}{name}' entry"
    )
    return [Finding(Severity.WARNING, SECTION_REGISTRY, message)]


def check_v2_config_fields(ctx: DriftContext) -> list[Finding]:
    """
    Reject removed Kiro CLI 2.x field shapes in agent configs.

    ERROR rather than WARNING: this project targets the v3 engine only,
    so a v2 field is dead configuration that the runtime ignores while
    reading as intentional authorization to a maintainer — a config
    granting shell access through ``allowedTools`` looks permissioned
    and is not. The failure is silent at runtime, which is what the
    check substitutes for.

    Scoped to ``.kiro/agents/`` rather than extended to the JSON
    templates in skill documentation. Documentation legitimately names
    these fields — the vendored kiro.dev mirror documents the 2.x shape
    in full, and this repository's own migration record and
    agent-creation reference both name the removed fields in order to
    forbid them. Distinguishing a forbidding mention from a teaching one
    needs a per-file allowlist, which is the drift surface the check is
    meant to remove.

    Args:
        ctx: Shared check context.

    Returns:
        One ERROR per offending field, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    for config in ctx.agent_configs:
        if config.data is None:
            continue
        findings.extend(
            Finding(Severity.ERROR, SECTION_V2_FIELDS, message)
            for message in _v2_field_messages(config)
        )
    findings.append(
        Finding(Severity.OK, SECTION_V2_FIELDS, "Legacy v2 agent config fields checked")
    )
    return findings


def _v2_field_messages(config: AgentConfig) -> list[str]:
    """
    Collect every removed v2 field shape one config carries.

    Args:
        config: Parsed agent config.

    Returns:
        Finding messages, empty when the config is v3-clean.
    """
    data = config.data or {}
    name = config.path.name
    return [
        f"{name} carries removed v2 field '{field}' — {remedy}"
        for field, remedy in V2_FIELD_REMEDIES.items()
        if field in data
    ]


def check_model_governance(ctx: DriftContext) -> list[Finding]:
    """
    Enforce the Anthropic-only model allow-list.

    Errors rather than warnings, because a non-Anthropic model is a hard
    project constraint violation. "auto" is rejected outright since Auto
    routing may select a non-Anthropic provider.

    Args:
        ctx: Shared check context.

    Returns:
        Findings per agent, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    allowed = " ".join(ALLOWED_MODELS)
    for config in ctx.agent_configs:
        name = config.stem
        model = config.model
        if not model:
            findings.append(
                Finding(
                    Severity.WARNING,
                    SECTION_MODELS,
                    f"{name}.json has no 'model' field set",
                )
            )
            continue
        if model == AUTO_MODEL:
            findings.append(
                Finding(
                    Severity.ERROR,
                    SECTION_MODELS,
                    f"{name}.json uses model 'auto' — Auto routing may select "
                    "non-Anthropic models, violating the Anthropic-only "
                    "constraint",
                )
            )
            continue
        if model not in ALLOWED_MODELS:
            findings.append(
                Finding(
                    Severity.ERROR,
                    SECTION_MODELS,
                    f"{name}.json uses unapproved model '{model}' — only "
                    f"Anthropic/Claude models are allowed: {allowed}",
                )
            )
    findings.append(Finding(Severity.OK, SECTION_MODELS, "Model governance checked"))
    return findings


def check_model_defaults(ctx: DriftContext) -> list[Finding]:
    """
    Validate the workspace-level chat.modelDefaults settings.

    The file is optional, so its absence is reported as OK. A model that
    is not on the Anthropic allow-list, or "auto", is an ERROR for the
    same reason it is on an agent config. A model that is approved but
    used by no agent is dead configuration, so it only warns.

    Args:
        ctx: Shared check context.

    Returns:
        Findings per configured model, plus a trailing OK finding.
    """
    path = ctx.cli_settings
    if not path.is_file():
        return [
            Finding(
                Severity.OK,
                SECTION_MODEL_DEFAULTS,
                f"No {CLI_SETTINGS_LABEL} (optional), skipping",
            )
        ]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return [
            Finding(
                Severity.ERROR,
                SECTION_MODEL_DEFAULTS,
                f"{CLI_SETTINGS_LABEL} is not valid JSON: {error}",
            )
        ]
    defaults = _model_defaults(data)
    if isinstance(defaults, str):
        return [Finding(Severity.ERROR, SECTION_MODEL_DEFAULTS, defaults)]
    in_use = frozenset(config.model for config in ctx.agent_configs if config.model)
    findings: list[Finding] = []
    for model in defaults:
        finding = _model_default_finding(model, in_use)
        if finding is not None:
            findings.append(finding)
    findings.append(
        Finding(
            Severity.OK,
            SECTION_MODEL_DEFAULTS,
            "Workspace model defaults checked",
        )
    )
    return findings


def _model_defaults(data: Any) -> list[str] | str:
    """
    Extract the model ids configured under chat.modelDefaults.

    Args:
        data: Decoded cli.json document.

    Returns:
        The configured model ids, or an error message when the document
        or the modelDefaults entry has the wrong shape.
    """
    if not isinstance(data, dict):
        return f"{CLI_SETTINGS_LABEL} top level is not an object"
    if "chat.modelDefaults" not in data:
        return []
    defaults = data["chat.modelDefaults"]
    if not isinstance(defaults, dict):
        return f"{CLI_SETTINGS_LABEL} 'chat.modelDefaults' is not an object"
    return [key for key in defaults if isinstance(key, str)]


def _model_default_finding(model: str, in_use: frozenset[str]) -> Finding | None:
    """
    Classify one configured default model.

    Args:
        model: Model id configured under chat.modelDefaults.
        in_use: Models actually configured on the agents.

    Returns:
        A finding when the model is unapproved or unused, else None.
    """
    if model == AUTO_MODEL:
        return Finding(
            Severity.ERROR,
            SECTION_MODEL_DEFAULTS,
            f"{CLI_SETTINGS_LABEL} configures 'auto' — Auto routing may "
            "select non-Anthropic models, violating the Anthropic-only "
            "constraint",
        )
    if model not in ALLOWED_MODELS:
        allowed = " ".join(ALLOWED_MODELS)
        return Finding(
            Severity.ERROR,
            SECTION_MODEL_DEFAULTS,
            f"{CLI_SETTINGS_LABEL} configures unapproved model '{model}' "
            f"— only Anthropic/Claude models are allowed: {allowed}",
        )
    if model not in in_use:
        return Finding(
            Severity.WARNING,
            SECTION_MODEL_DEFAULTS,
            f"{CLI_SETTINGS_LABEL} configures '{model}' but no agent uses "
            "it — dead configuration",
        )
    return None


def check_agent_engine(ctx: DriftContext) -> list[Finding]:
    """
    Verify the project is pinned to the v3 agent engine.

    The workspace settings must set chat.agentEngine to v3, so that no
    launch flag is needed, and ralph.sh must select the engine with
    the explicit --agent-engine v3 argument rather than a shorthand.
    A missing settings file is optional and skipped; malformed JSON is
    left to the model-defaults check so it is reported only once.

    Args:
        ctx: Shared check context.

    Returns:
        Findings per violation, or a single OK finding.
    """
    path = ctx.cli_settings
    if not path.is_file():
        return [
            Finding(
                Severity.OK,
                SECTION_AGENT_ENGINE,
                f"No {CLI_SETTINGS_LABEL} (optional), skipping",
            )
        ]
    findings = _engine_setting_findings(path)
    findings.extend(_ralph_engine_findings(ctx.root.joinpath(*RALPH_SCRIPT)))
    if not findings:
        findings.append(Finding(Severity.OK, SECTION_AGENT_ENGINE, "v3 engine pinned"))
    return findings


def _engine_setting_findings(path: Path) -> list[Finding]:
    """
    Check the chat.agentEngine value of a settings file.

    Args:
        path: Existing settings file.

    Returns:
        An ERROR when the engine is not pinned to v3, else nothing.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(data, dict):
        return []
    value = data.get(ENGINE_SETTING)
    if value == ENGINE_VALUE:
        return []
    message = (
        f"{CLI_SETTINGS_LABEL} must pin '{ENGINE_SETTING}' to "
        f"'{ENGINE_VALUE}' (found {value!r})"
    )
    return [Finding(Severity.ERROR, SECTION_AGENT_ENGINE, message)]


def _ralph_engine_findings(script: Path) -> list[Finding]:
    """
    Check how ralph.sh selects the agent engine.

    Args:
        script: Expected ralph.sh path; ignored when absent.

    Returns:
        ERROR findings for shorthand flags or a missing explicit engine.
    """
    if not script.is_file():
        return []
    text = script.read_text(encoding="utf-8")
    findings: list[Finding] = [
        Finding(
            Severity.ERROR,
            SECTION_AGENT_ENGINE,
            f"ralph.sh uses {flag}; select the engine with "
            f"'{RALPH_ENGINE_ARGUMENT}' instead",
        )
        for flag in HARNESS_SHORTHAND_FLAGS
        if re.search(rf"(?<![\w-]){re.escape(flag)}(?![\w-])", text)
    ]
    if RALPH_ENGINE_ARGUMENT not in text:
        findings.append(
            Finding(
                Severity.ERROR,
                SECTION_AGENT_ENGINE,
                f"ralph.sh must pass '{RALPH_ENGINE_ARGUMENT}' so unattended "
                "runs do not depend on user-level settings",
            )
        )
    return findings


def check_cost_labels(ctx: DriftContext) -> list[Finding]:
    """
    Verify routing.md cost labels match each agent's real model.

    Tolerant of table whitespace and of both the legacy label format
    ("high") and the corrected one ("high (2.2x)"). Warns rather than
    errors: this is a documentation-accuracy smell, not breakage.

    Args:
        ctx: Shared check context.

    Returns:
        Warnings for mismatched rows, plus trailing OK findings.
    """
    findings: list[Finding] = []
    if not ctx.routing_md.is_file():
        findings.append(
            Finding(Severity.OK, SECTION_COST_LABELS, "No routing.md found, skipping")
        )
    else:
        routing_lines = read_text(ctx.routing_md).splitlines()
        for config in ctx.agent_configs:
            if config.path == ctx.orchestrator_path:
                continue
            mismatch = _cost_label_mismatch(routing_lines, config)
            if mismatch is not None:
                findings.append(mismatch)
    findings.append(
        Finding(
            Severity.OK, SECTION_COST_LABELS, "routing.md cost label accuracy checked"
        )
    )
    return findings


def _cost_label_mismatch(
    routing_lines: list[str], config: AgentConfig
) -> Finding | None:
    """
    Compare one agent's routing.md row against its configured model.

    Args:
        routing_lines: routing.md content split into lines.
        config: Parsed agent config.

    Returns:
        A WARNING finding, or None when the row agrees with the model
        or there is nothing to compare.
    """
    expected = _expected_cost(config.model)
    if expected is None:
        return None
    label, multiplier = expected
    row = _routing_md_row(routing_lines, config.stem)
    if row is None:
        return None
    if label not in row.lower():
        return Finding(
            Severity.WARNING,
            SECTION_COST_LABELS,
            f"routing.md cost label for '{config.stem}' does not "
            f"match its model ({config.model} → expected "
            f"'{label} ({multiplier})'). Row: {row}",
        )
    if COST_MULTIPLIER.search(row) and multiplier not in row:
        return Finding(
            Severity.WARNING,
            SECTION_COST_LABELS,
            f"routing.md cost multiplier for '{config.stem}' does "
            f"not match its model ({config.model} → expected "
            f"'{multiplier}'). Row: {row}",
        )
    return None


def _expected_cost(model: str) -> tuple[str, str] | None:
    """
    Map a model identifier to its documented cost label.

    Args:
        model: Configured model identifier.

    Returns:
        The (label, multiplier) pair, or None for unknown families.
    """
    for prefix, expected in MODEL_COST_LABELS.items():
        if model.startswith(prefix):
            return expected
    return None


def _routing_md_row(lines: list[str], name: str) -> str | None:
    """
    Find the routing.md table row whose first cell names an agent.

    Args:
        lines: routing.md content split into lines.
        name: Agent slug to look for.

    Returns:
        The first matching row, or None when the agent has no row.
    """
    pattern = re.compile(rf"^\|[ \t]*{re.escape(name)}[ \t]*\|")
    for line in lines:
        if pattern.match(line):
            return line
    return None
