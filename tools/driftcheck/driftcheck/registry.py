"""
Ordered registry of every drift check and its execution.

The order of CHECKS is the order of the console output, so it is part of
the tool's observable behaviour and must not be rearranged casually.
Execution is isolated per check: a check that raises is converted into
an ERROR finding naming it, and the remaining checks still run. That
distinction is load-bearing — a crashing validator must never be
mistaken for a validator that merely found warnings, because the run
would then pass in CI.
"""

# Standard libraries
from typing import Final

# Own modules
from driftcheck.checks.agents import (
    SECTION_COST_LABELS,
    SECTION_MODEL_DEFAULTS,
    SECTION_MODELS,
    SECTION_REGISTRY,
    SECTION_RESOURCE_FORM,
    SECTION_RESOURCES,
    SECTION_V2_FIELDS,
    check_agent_registry,
    check_cost_labels,
    check_model_defaults,
    check_model_governance,
    check_resource_path_form,
    check_resource_references,
    check_v2_config_fields,
)
from driftcheck.checks.hooks import (
    SECTION_GIT_SAFETY,
    SECTION_HOOKS,
    check_git_safety_hook,
    check_hook_scripts,
)
from driftcheck.checks.permissions import (
    SECTION_PERMISSION_RULES,
    SECTION_TOOL_TAGS,
    check_permission_rules,
    check_tool_tags,
)
from driftcheck.checks.prompt_quality import (
    SECTION_CONTRADICTIONS,
    SECTION_PROMPT_BOUNDARIES,
    SECTION_SEVERITY_FILTERING,
    check_known_contradictions,
    check_prompt_boundaries,
    check_severity_filtering,
)
from driftcheck.checks.prompts import (
    SECTION_ORPHAN_PROMPTS,
    SECTION_PROMPTS,
    check_orphan_prompts,
    check_prompt_references,
)
from driftcheck.checks.skills import (
    SECTION_ORPHAN_REFS,
    SECTION_PATTERN_WIRING,
    SECTION_SKILL_ROUTING,
    SECTION_STALE_REFS,
    SECTION_STALE_SKILL_MENTIONS,
    check_orphaned_skill_references,
    check_pattern_resource_wiring,
    check_skill_routing,
    check_stale_agent_references,
    check_stale_skill_mentions,
)
from driftcheck.checks.state import (
    SECTION_MEMORY,
    SECTION_STATE,
    check_memory_store,
    check_state_registry,
)
from driftcheck.checks.steering import (
    SECTION_DUPLICATION,
    SECTION_NUMBERED_HEADERS,
    SECTION_ORCHESTRATION_PLACEMENT,
    SECTION_ORCHESTRATION_REACHABILITY,
    check_numbered_headers,
    check_orchestration_placement,
    check_orchestration_reachability,
    check_steering_duplication,
)
from driftcheck.types import CheckFunction, DriftContext, Finding, Severity

CHECKS: Final[tuple[tuple[str, CheckFunction], ...]] = (
    (SECTION_RESOURCES, check_resource_references),
    (SECTION_RESOURCE_FORM, check_resource_path_form),
    (SECTION_REGISTRY, check_agent_registry),
    (SECTION_V2_FIELDS, check_v2_config_fields),
    (SECTION_PERMISSION_RULES, check_permission_rules),
    (SECTION_TOOL_TAGS, check_tool_tags),
    (SECTION_SKILL_ROUTING, check_skill_routing),
    (SECTION_PATTERN_WIRING, check_pattern_resource_wiring),
    (SECTION_STATE, check_state_registry),
    (SECTION_MEMORY, check_memory_store),
    (SECTION_PROMPTS, check_prompt_references),
    (SECTION_HOOKS, check_hook_scripts),
    (SECTION_GIT_SAFETY, check_git_safety_hook),
    (SECTION_DUPLICATION, check_steering_duplication),
    (SECTION_ORCHESTRATION_PLACEMENT, check_orchestration_placement),
    (SECTION_ORCHESTRATION_REACHABILITY, check_orchestration_reachability),
    (SECTION_ORPHAN_PROMPTS, check_orphan_prompts),
    (SECTION_ORPHAN_REFS, check_orphaned_skill_references),
    (SECTION_MODELS, check_model_governance),
    (SECTION_MODEL_DEFAULTS, check_model_defaults),
    (SECTION_COST_LABELS, check_cost_labels),
    (SECTION_NUMBERED_HEADERS, check_numbered_headers),
    (SECTION_STALE_REFS, check_stale_agent_references),
    (SECTION_STALE_SKILL_MENTIONS, check_stale_skill_mentions),
    (SECTION_SEVERITY_FILTERING, check_severity_filtering),
    (SECTION_PROMPT_BOUNDARIES, check_prompt_boundaries),
    (SECTION_CONTRADICTIONS, check_known_contradictions),
)


def run_check(section: str, check: CheckFunction, ctx: DriftContext) -> list[Finding]:
    """
    Run one check, converting a crash into an ERROR finding.

    A check that raises must not be mistaken for a check that merely
    found warnings, and must not prevent later checks from running.

    Args:
        section: Section title used for grouping.
        check: Check function to invoke.
        ctx: Shared check context.

    Returns:
        The check's findings, or a single ERROR describing the crash.
    """
    try:
        return check(ctx)
    except Exception as error:  # noqa: BLE001 - a broken check must not abort the run
        return [
            Finding(
                Severity.ERROR,
                section,
                f"{section} check failed to run: {error!r}",
            )
        ]


def run_checks(ctx: DriftContext) -> list[tuple[str, list[Finding]]]:
    """
    Run every registered check in order.

    Args:
        ctx: Shared check context.

    Returns:
        One (section, findings) pair per registered check.
    """
    return [(section, run_check(section, check, ctx)) for section, check in CHECKS]
