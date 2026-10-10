"""
Checks over agent-declared permission rules and tool tags.

CLI 3.0 replaced 2.x trust flags with the capability-based
``permissions.rules`` policy and separated tool *visibility* (the
``tools`` tag array) from tool *authorization* (``permissions.rules``).
Neither ``kiro-cli agent validate`` nor ``kiro-cli diagnostic`` performs
real v3 validation on this project's installed CLI, so this module is
the only automated enforcement of either shape:

- :func:`check_permission_rules` validates each ``permissions.rules``
  entry's ``capability``, ``effect``, and glob ``match``/``exclude``
  patterns against the documented vocabulary (v3/permissions.md,
  "Available capabilities" and the behavioral-changes table).
- :func:`check_tool_tags` validates each ``tools`` array entry against
  the documented tag vocabulary (v3/agent-config.md, "Tags vs
  Capabilities").

The two are shipped as separate checks, matching this codebase's
one-concern-per-check convention: a bad capability and a bad tag are
unrelated failure modes with unrelated remedies.
"""

# Standard libraries
import re
from typing import Any, Final

# Own modules
from driftcheck.types import AgentConfig, DriftContext, Finding, Severity

# v3/permissions.md, "Available capabilities": plain capabilities plus
# the three documented meta-capabilities (all, builtin, filesystem).
ALLOWED_CAPABILITIES: Final[frozenset[str]] = frozenset(
    (
        "fs_read",
        "fs_write",
        "shell",
        "web_fetch",
        "web_search",
        "mcp",
        "subagent",
        "skill",
        "power",
        "context",
        "diagnostics",
        "sandbox_network",
        "all",
        "builtin",
        "filesystem",
    )
)

# v3/permissions.md, scopes table: an agent-scoped permissions block may
# declare any of the three effects.
ALLOWED_EFFECTS: Final[frozenset[str]] = frozenset(("allow", "deny", "ask"))

# v3/agent-config.md, "Tags vs Capabilities": the documented tools tag
# vocabulary. @mcp and @builtin are meta-tags naming every tool of a
# kind rather than a literal tool id.
ALLOWED_TOOL_TAGS: Final[frozenset[str]] = frozenset(
    (
        "read",
        "write",
        "shell",
        "web",
        "subagent",
        "knowledge",
        "todo_list",
        "@mcp",
        "@builtin",
        "*",
    )
)

# v3/permissions.md, behavioral-changes table: regex syntax that glob
# does not support. ``^`` and ``$`` have no meaning in glob syntax at
# all, so their presence is unambiguous. A backslash escape is the same
# — glob has no escape mechanism, so a leftover ``\.`` or ``\d`` is
# always a regex fragment. ``.*`` is deliberately not matched on its
# own: unlike a regex, glob treats ``.`` as a literal character, so
# ``**/.env.*`` is valid glob (literal ``.env.`` followed by a
# wildcard) and must not be confused with the regex quantifier. The
# anchor and escape checks below already catch the pattern that
# actually indicates a v2 leftover: an anchored quantifier such as
# ``^.*$``.
REGEX_SMELL_PATTERNS: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (re.compile(r"\^"), "'^' (regex start anchor — glob has no anchors)"),
    (re.compile(r"\$"), "'$' (regex end anchor — glob has no anchors)"),
    (re.compile(r"\\[^\\]"), "backslash escape (not meaningful in glob syntax)"),
)

# Capabilities where a literal '?' single-char wildcard is valid, per
# the behavioral-changes table: "File path patterns (fs_read, fs_write)
# still support ?". Every other capability is shell/URL-shaped, where
# '?' is unsupported and therefore a smell like the other regex leftovers.
QUESTION_MARK_CAPABILITIES: Final[frozenset[str]] = frozenset(("fs_read", "fs_write"))

SECTION_PERMISSION_RULES: Final[str] = "permissions.rules validation"
SECTION_TOOL_TAGS: Final[str] = "tools tag validation"


def _rules(data: dict[str, Any]) -> list[Any]:
    """
    Extract the permissions.rules array of a config, tolerating shape.

    Args:
        data: Parsed agent config document.

    Returns:
        The rules list, empty when absent or the wrong shape.
    """
    permissions = data.get("permissions")
    if not isinstance(permissions, dict):
        return []
    rules = permissions.get("rules")
    if not isinstance(rules, list):
        return []
    return rules


def _pattern_smells(pattern: str) -> list[str]:
    """
    Collect the regex-smell descriptions one glob pattern exhibits.

    ``*`` and ``**`` are valid glob wildcards and never flagged here.
    ``?`` is deliberately absent from REGEX_SMELL_PATTERNS: it is valid
    for filesystem capabilities and invalid otherwise, so it is
    capability-scoped and checked by the caller instead.

    Args:
        pattern: A single match/exclude glob pattern.

    Returns:
        One description per distinct smell found, in table order.
    """
    return [
        description
        for regex, description in REGEX_SMELL_PATTERNS
        if regex.search(pattern)
    ]


def _match_findings(
    name: str, rule_index: int, capability: str, field: str, patterns: Any
) -> list[Finding]:
    """
    Validate one rule's match/exclude pattern list.

    Args:
        name: Config filename, for the finding message.
        rule_index: Zero-based position of the rule, for the message.
        capability: The rule's declared capability.
        field: Either "match" or "exclude".
        patterns: Raw value of the rule's match/exclude field.

    Returns:
        One ERROR per offending pattern, empty when the field is absent
        or holds only clean glob patterns.
    """
    if not isinstance(patterns, list):
        return []
    findings: list[Finding] = []
    for pattern in patterns:
        if not isinstance(pattern, str):
            continue
        smells = _pattern_smells(pattern)
        if capability not in QUESTION_MARK_CAPABILITIES and "?" in pattern:
            smells.append(
                "'?' (unsupported outside fs_read/fs_write patterns — use "
                "'*' or spell out alternatives)"
            )
        for smell in smells:
            findings.append(
                Finding(
                    Severity.ERROR,
                    SECTION_PERMISSION_RULES,
                    f"{name} permissions.rules[{rule_index}].{field} entry "
                    f"'{pattern}' looks like a v2 regex leftover: {smell}",
                )
            )
    return findings


def _rule_findings(name: str, index: int, rule: Any) -> list[Finding]:
    """
    Validate a single permissions.rules entry.

    Args:
        name: Config filename, for the finding message.
        index: Zero-based position of the rule in the array.
        rule: Raw rule entry, expected to be a mapping.

    Returns:
        One ERROR per violation the rule carries.
    """
    if not isinstance(rule, dict):
        return [
            Finding(
                Severity.ERROR,
                SECTION_PERMISSION_RULES,
                f"{name} permissions.rules[{index}] is not an object",
            )
        ]
    findings: list[Finding] = []
    capability = rule.get("capability")
    if not isinstance(capability, str) or capability not in ALLOWED_CAPABILITIES:
        allowed = ", ".join(sorted(ALLOWED_CAPABILITIES))
        findings.append(
            Finding(
                Severity.ERROR,
                SECTION_PERMISSION_RULES,
                f"{name} permissions.rules[{index}].capability "
                f"{capability!r} is not a documented capability: {allowed}",
            )
        )
        capability = ""
    effect = rule.get("effect")
    if effect not in ALLOWED_EFFECTS:
        allowed = ", ".join(sorted(ALLOWED_EFFECTS))
        findings.append(
            Finding(
                Severity.ERROR,
                SECTION_PERMISSION_RULES,
                f"{name} permissions.rules[{index}].effect {effect!r} is "
                f"not one of: {allowed}",
            )
        )
    findings.extend(
        _match_findings(name, index, capability, "match", rule.get("match"))
    )
    findings.extend(
        _match_findings(name, index, capability, "exclude", rule.get("exclude"))
    )
    return findings


def check_permission_rules(ctx: DriftContext) -> list[Finding]:
    """
    Validate every agent's permissions.rules entries.

    Reports an ERROR for an undocumented capability, an effect outside
    allow/deny/ask, and any match/exclude pattern carrying regex syntax
    glob does not support. A leftover v2 anchor such as ``^git status$``
    degrades silently to a literal glob matching nothing, which is why
    this is an ERROR rather than a WARNING: the rule looks like it grants
    or denies access and instead does nothing.

    Args:
        ctx: Shared check context.

    Returns:
        One ERROR per violation, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    for config in ctx.agent_configs:
        findings.extend(_config_permission_findings(config))
    findings.append(
        Finding(Severity.OK, SECTION_PERMISSION_RULES, "permissions.rules checked")
    )
    return findings


def _config_permission_findings(config: AgentConfig) -> list[Finding]:
    """
    Validate the permissions.rules array of one config.

    Args:
        config: Parsed agent config.

    Returns:
        One ERROR per violation the config's rules carry.
    """
    if config.data is None:
        return []
    findings: list[Finding] = []
    for index, rule in enumerate(_rules(config.data)):
        findings.extend(_rule_findings(config.path.name, index, rule))
    return findings


def check_tool_tags(ctx: DriftContext) -> list[Finding]:
    """
    Validate every agent's tools array against the documented tags.

    A typo such as ``"shel"`` silently grants no tools today rather
    than failing loudly, since the runtime simply does not recognise an
    undocumented tag.

    Args:
        ctx: Shared check context.

    Returns:
        One ERROR per undocumented tag, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    for config in ctx.agent_configs:
        findings.extend(_config_tool_tag_findings(config))
    findings.append(Finding(Severity.OK, SECTION_TOOL_TAGS, "tools tags checked"))
    return findings


def _config_tool_tag_findings(config: AgentConfig) -> list[Finding]:
    """
    Validate the tools array of one config.

    Args:
        config: Parsed agent config.

    Returns:
        One ERROR per undocumented tag entry.
    """
    if config.data is None:
        return []
    tools = config.data.get("tools")
    if not isinstance(tools, list):
        return []
    findings: list[Finding] = []
    allowed = ", ".join(sorted(ALLOWED_TOOL_TAGS))
    for tag in tools:
        if tag in ALLOWED_TOOL_TAGS:
            continue
        findings.append(
            Finding(
                Severity.ERROR,
                SECTION_TOOL_TAGS,
                f"{config.path.name} tools entry {tag!r} is not a "
                f"documented tag: {allowed}",
            )
        )
    return findings
