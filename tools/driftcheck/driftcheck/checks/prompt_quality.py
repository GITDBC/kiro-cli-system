"""
Checks over the quality of the instruction artifacts themselves.

The remaining check encodes one documented agent-prompt practice: an
agent prompt with no stated boundary invites out-of-scope work.
The orchestrator prompt already publishes a ``never_when`` list per
routable agent in its Routing Rules; an agent's own prompt is what that
agent actually loads, so the boundary has to be there too.

The check is deterministic and run by a tool, and that is the point:
it adds no text to any prompt and only reads.
"""

# Standard libraries
import re
from pathlib import Path
from typing import Final

# Own modules
from driftcheck.paths import read_text
from driftcheck.types import DriftContext, Finding, Severity

SECTION_PROMPT_BOUNDARIES: Final[str] = "Agent prompt scope statements"

# A routing-YAML agent entry in the orchestrator prompt
# ("      - id: code-reviewer").
# Every such entry carries a never_when list, which is the boundary this
# check expects the agent's own prompt to mirror. The orchestrator has
# no entry because it is not a delegation target, so its prompt is not
# required to carry one.
ROUTABLE_AGENT: Final[re.Pattern[str]] = re.compile(
    r"^\s*-\s+id:\s+(?P<slug>[a-z][a-z0-9-]*)\s*$", re.MULTILINE
)

# A heading that opens a negative-scope section. "## Boundaries" is the
# house form; the alternatives are accepted so a rename does not read as
# a regression.
BOUNDARY_HEADING: Final[re.Pattern[str]] = re.compile(
    r"^#{1,6} .*\b(?:boundaries|when not to use|do not use)\b",
    re.IGNORECASE | re.MULTILINE,
)

FILE_URI_PREFIX: Final[str] = "file://"


def check_prompt_boundaries(ctx: DriftContext) -> list[Finding]:
    """
    Verify every routable agent's prompt states its own boundaries.

    The orchestrator prompt publishes a ``never_when`` list per routable
    agent, but routing lives with the orchestrator while the specialist
    loads its own prompt. Without the boundary in the prompt, an
    agent invoked directly — or handed a task that drifted during a
    workflow — has nothing telling it to hand the work back.

    A prompt that cannot be resolved is skipped rather than reported:
    ``check_prompt_references`` owns missing prompt files, and reporting
    them twice would make one broken path look like two problems.

    Args:
        ctx: Shared check context.

    Returns:
        A warning per prompt with no boundary section, plus a trailing
        OK finding.
    """
    findings: list[Finding] = []
    for slug in sorted(_routable_agents(read_text(ctx.orchestrator_prompt))):
        prompt = _prompt_path(ctx, slug)
        if prompt is None:
            continue
        if BOUNDARY_HEADING.search(read_text(prompt)) is not None:
            continue
        findings.append(
            Finding(
                Severity.WARNING,
                SECTION_PROMPT_BOUNDARIES,
                f"{prompt.relative_to(ctx.root)} has no boundary section — "
                f"orchestrator.md declares never_when entries for '{slug}' that the "
                "prompt never states, so the agent itself cannot tell when to "
                "hand work back",
            )
        )
    findings.append(
        Finding(
            Severity.OK,
            SECTION_PROMPT_BOUNDARIES,
            "Agent prompt scope statements checked",
        )
    )
    return findings


def _routable_agents(prompt_text: str) -> set[str]:
    """
    Collect the agent slugs the routing YAML declares.

    Args:
        prompt_text: Full orchestrator prompt text.

    Returns:
        Every slug appearing as a routing-YAML ``- id:`` entry.
    """
    return {match.group("slug") for match in ROUTABLE_AGENT.finditer(prompt_text)}


def _prompt_path(ctx: DriftContext, slug: str) -> Path | None:
    """
    Resolve the prompt file of an agent slug.

    Prefers the agent config's own ``prompt`` field so the check follows
    the same path the runtime does, and falls back to the conventional
    ``.kiro/prompts/<slug>.md`` when no config declares one.

    Args:
        ctx: Shared check context.
        slug: Agent slug from the routing YAML.

    Returns:
        The existing prompt file, or None when none resolves.
    """
    for config in ctx.agent_configs:
        if config.stem != slug:
            continue
        prompt = (config.data or {}).get("prompt", "")
        if isinstance(prompt, str) and prompt.startswith(FILE_URI_PREFIX):
            relative = prompt.removeprefix(FILE_URI_PREFIX)
            resolved = (config.path.parent / relative).resolve()
            return resolved if resolved.is_file() else None
    fallback = ctx.prompts_dir / f"{slug}.md"
    return fallback if fallback.is_file() else None
