"""
Rendering: Markdown and JSON reports, the committed budget, check output.

Every report ends with the same provenance footer, and the footer is not
optional decoration. The figures are approximations produced by a
tokenizer that is not the one Anthropic bills on, over an artifact set
that excludes a remainder nothing local can measure. A reader who sees
the numbers without those facts will treat an approximation as a
measurement, which is the specific failure this footer exists to prevent.
"""

# Standard libraries
import json
from collections.abc import Sequence
from dataclasses import asdict
from typing import Final

# Own modules
from ctxbudget.model import (
    AGENT_PREFIX,
    AGENT_SEPARATOR,
    CALIBRATION_PREFIX,
    CAVEAT_PREFIX,
    META_PREFIX,
    OBSERVATION_PREFIX,
    SKILL_PREFIX,
    extra_metric_rows,
)
from ctxbudget.types import (
    BASELINE_KINDS,
    ArtifactKind,
    BudgetViolation,
    Calibration,
    Measurement,
)

TITLE: Final[str] = "# Context Budget Report"

# Cost sources no local tool can reach. Listed verbatim in every footer
# so an absolute total is never mistaken for the whole prompt.
UNMEASURABLE: Final[tuple[str, ...]] = (
    "Kiro CLI's own base system prompt",
    "tool-definition schemas for the tools each agent enables",
    "hook output injected at agentSpawn or postToolUse",
    "state slices the runtime injects (conversation summary, todo lists, "
    "environment context)",
)

# How steering reaches a session, and therefore how it is counted.
# Settled by observation rather than assumed: see the report footer.
STEERING_NOTE: Final[str] = (
    "every `.kiro/steering/*.md` file is injected into every session by "
    "workspace auto-load, subagent sessions included, regardless of what an "
    "agent's `resources` array lists"
)

KIND_HEADERS: Final[dict[ArtifactKind, str]] = {
    ArtifactKind.PROMPT: "prompt",
    ArtifactKind.FILE: "file://",
    ArtifactKind.SKILL_FRONTMATTER: "skill_fm",
    ArtifactKind.KNOWLEDGE_BASE: "kb",
    ArtifactKind.STEERING_AUTO: "steering_auto",
}


def _table(headers: tuple[str, ...], rows: Sequence[Sequence[str]]) -> list[str]:
    """
    Render a Markdown table.

    Args:
        headers: Column headers.
        rows: Row cells, already rendered as strings.

    Returns:
        The table's lines, without a trailing blank.
    """
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def _agent_section(measurement: Measurement) -> list[str]:
    """
    Render the per-agent baseline table.

    Args:
        measurement: Completed measurement.

    Returns:
        Section lines.
    """
    headers = ("Agent", *(KIND_HEADERS[kind] for kind in BASELINE_KINDS), "Baseline")
    rows = [
        (
            baseline.agent,
            *(f"{baseline.tokens_for(kind):,}" for kind in BASELINE_KINDS),
            f"{baseline.total:,}",
        )
        for baseline in measurement.baselines
    ]
    total = sum(baseline.total for baseline in measurement.baselines)
    lines = [
        "## Per-agent baseline",
        "",
        "Tokens paid on every request of every session with that agent.",
        "",
        *_table(headers, rows),
        "",
        f"Sum over all agents: {total:,} tokens ({len(measurement.baselines)} agents).",
    ]
    unresolved = [
        f"- `{baseline.agent}` → `{declaration}`"
        for baseline in measurement.baselines
        for declaration in baseline.unresolved
    ]
    if unresolved:
        lines.extend(
            [
                "",
                "Declared resources that resolved to nothing and are therefore "
                "counted as zero (`driftcheck` owns the verdict on whether that "
                "is a defect):",
                "",
                *unresolved,
            ]
        )
    return lines


def _file_section(measurement: Measurement) -> list[str]:
    """
    Render the weighted per-file table.

    Args:
        measurement: Completed measurement.

    Returns:
        Section lines.
    """
    rows = [
        (
            f"`{load.label}`",
            f"{load.tokens:,}",
            str(len(load.agents)),
            str(load.loads),
            f"{load.weighted:,}",
        )
        for load in measurement.files
    ]
    weighted = sum(load.weighted for load in measurement.files)
    return [
        "## Always-on artifacts, weighted",
        "",
        "Sorted by weighted total, which is the order a reduction backlog "
        "should be worked in: a token removed from a file thirteen agents "
        "load is worth thirteen. `Loads` exceeds `Agents` only when one "
        "agent pays for the same file twice, which no resolution rule in "
        "force does today.",
        "",
        *_table(("Artifact", "Tokens", "Agents", "Loads", "Weighted"), rows),
        "",
        f"Weighted total across all agents: {weighted:,} tokens.",
    ]


def _skill_section(measurement: Measurement) -> list[str]:
    """
    Render the per-skill activation table, descending by body cost.

    Args:
        measurement: Completed measurement.

    Returns:
        Section lines.
    """
    activations = sorted(
        measurement.activations, key=lambda item: (-item.body_tokens, item.skill)
    )
    rows = [
        (
            activation.skill,
            f"{activation.body_tokens:,}",
            f"{activation.frontmatter_tokens:,}",
            (
                "not measured"
                if activation.refs_upper_bound is None
                else f"{activation.refs_upper_bound:,}"
            ),
            str(activation.reference_files),
        )
        for activation in activations
    ]
    body_total = sum(activation.body_tokens for activation in activations)
    note = (
        "Reference upper bounds were not measured; pass `--with-references` "
        "to include them."
        if not measurement.with_references
        else "Reference upper bounds are an upper bound only: reference files "
        "are read selectively, so the column is never summed into an "
        "activation cost or into any session estimate."
    )
    return [
        "## Skill activation costs",
        "",
        "One-off cost of activating a skill: the SKILL.md body with its "
        "frontmatter excluded. The frontmatter column is the startup cost "
        "already counted in the baseline of every agent declaring the skill, "
        "and is repeated here only so the two are comparable.",
        "",
        *_table(
            ("Skill", "Body", "Frontmatter", "refs upper bound", "Ref files"), rows
        ),
        "",
        f"Sum of all skill bodies: {body_total:,} tokens "
        f"({len(activations)} skills). {note}",
    ]


def _extra_sections(measurement: Measurement) -> list[str]:
    """
    Render whatever the registered extension metric families produced.

    Args:
        measurement: Completed measurement.

    Returns:
        Section lines, empty when no family is registered.
    """
    lines: list[str] = []
    for title, rows in extra_metric_rows(measurement):
        lines.extend(
            [
                f"## {title}",
                "",
                *_table(
                    ("Subject", "Metric", "Value", "Note"),
                    [(row.subject, row.metric, row.value, row.note) for row in rows],
                ),
                "",
            ]
        )
    return lines


def _calibration_lines(measurement: Measurement) -> list[str]:
    """
    Render the calibration part of the footer.

    Args:
        measurement: Completed measurement.

    Returns:
        Footer lines naming the factor, its band, its basis and its
        caveats, or stating that no observation has been recorded.
    """
    calibration = measurement.calibration
    if calibration is None:
        return [
            "- **Calibration**: uncalibrated. No `/context show` observation has "
            "been recorded, so the absolute totals carry an unquantified "
            "approximation error. Record one with `ctxbudget calibrate`.",
        ]
    agents = ", ".join(calibration.agents)
    window = (
        f"a {calibration.window:,}-token window"
        if calibration.window > 0
        else "a window the stored block does not record"
    )
    lines = [
        f"- **Calibration**: factor {calibration.factor}, within "
        f"{calibration.factor_low}-{calibration.factor_high} at the precision "
        "the observation was read to — multiply an absolute total by it to "
        "approximate the real tokenizer, and treat the result as indicative "
        f"rather than as a measurement. Observed {calibration.observed_at} "
        f"from {agents}, against {window}, with tiktoken "
        f"{calibration.tiktoken_version}.",
        f"  - Basis: {calibration.basis}",
    ]
    lines.extend(f"  - {line}" for line in calibration.observations)
    lines.extend(f"  - Caveat: {caveat}" for caveat in calibration.caveats)
    if calibration.tiktoken_version != measurement.tiktoken_version:
        lines.append(
            f"  - WARNING: this run used tiktoken {measurement.tiktoken_version}, "
            "so the factor was derived against a different tokenizer."
        )
    return lines


def _footer(measurement: Measurement) -> list[str]:
    """
    Render the provenance footer required on every report.

    Args:
        measurement: Completed measurement.

    Returns:
        Footer lines.
    """
    lines = [
        "## Provenance and limits",
        "",
        f"- **Backend**: `{measurement.backend}` (tiktoken "
        f"{measurement.tiktoken_version}). There is no exact backend: this "
        "repository has no Anthropic API key, so no figure here was produced "
        "by the tokenizer Anthropic bills on.",
        "- **Every figure is APPROXIMATE.** tiktoken is deterministic, so "
        "before/after deltas are trustworthy; absolute totals are not, and a "
        "calibration only makes them indicative rather than exact.",
        *_calibration_lines(measurement),
        f"- **Steering**: {STEERING_NOTE}. Confirmed by `/context show` on a "
        "live session and by a subagent session that received all three files "
        "while its config declared two, so no agent declares steering in "
        "`resources` and none is charged for it twice.",
        "- **Resource resolution**: a `file://` or `skill://` entry in "
        "`resources` is resolved against the workspace root; only the "
        "`prompt` field resolves against the agent config's own directory. "
        "Counting a `resources` entry config-relative once charged agents for "
        "files that reached no session.",
        "- **Unverified**: one session observed all skill descriptions "
        "injected rather than only those the agent declares. If that holds, "
        "the `skill_fm` column understates what every agent pays. It is left "
        "as measured rather than assumed, and needs a `/context show` "
        "confirmation.",
        "- **Unmeasurable remainder**, excluded from every figure above and not "
        "estimated anywhere in this report:",
    ]
    lines.extend(f"  - {item}" for item in UNMEASURABLE)
    lines.extend(
        [
            "- **Excluded by design**: each agent JSON's `permissions`, `tools` "
            "and `toolsSettings` blocks, which configure the runtime and never "
            "reach the model as prompt text. What the resulting tool-definition "
            "schemas cost is part of the unmeasurable remainder above.",
            "- **Never summed**: `references/**` upper bounds. Reference files "
            "are read selectively, so adding them would report a cost no "
            "session pays.",
        ]
    )
    return lines


def render_markdown(measurement: Measurement) -> str:
    """
    Render the full Markdown report.

    Args:
        measurement: Completed measurement.

    Returns:
        The report text, newline-terminated.
    """
    sections = [
        TITLE,
        "",
        f"Generated {measurement.generated_at} over `{measurement.root}`.",
        "",
        *_agent_section(measurement),
        "",
        *_file_section(measurement),
        "",
        *_skill_section(measurement),
        "",
        *_extra_sections(measurement),
        *_footer(measurement),
        "",
    ]
    return "\n".join(sections)


def render_json(measurement: Measurement) -> str:
    """
    Render the full report as JSON.

    Nested, unlike the committed budget: this is a report payload for
    other tooling, not a file whose diff a human reads. ``agents[].
    baseline`` is that agent's per-agent total — the same figure the
    Markdown prints in its `Baseline` column — and ``totals`` carries
    the aggregates the Markdown states in prose, so a consumer never has
    to re-sum a section to reproduce a figure the report already gives.

    Args:
        measurement: Completed measurement.

    Returns:
        Pretty-printed JSON, newline-terminated.
    """
    calibration = measurement.calibration
    document = {
        "generated_at": measurement.generated_at,
        "root": str(measurement.root),
        "backend": measurement.backend,
        "tiktoken_version": measurement.tiktoken_version,
        "approximate": True,
        "with_references": measurement.with_references,
        "calibration": None if calibration is None else asdict(calibration),
        "unmeasurable_remainder": list(UNMEASURABLE),
        "totals": {
            "agent_baselines": sum(
                baseline.total for baseline in measurement.baselines
            ),
            "agents": len(measurement.baselines),
            "files_weighted": sum(load.weighted for load in measurement.files),
            "skill_bodies": sum(
                activation.body_tokens for activation in measurement.activations
            ),
            "skills": len(measurement.activations),
        },
        "agents": [
            {
                "agent": baseline.agent,
                "baseline": baseline.total,
                "by_kind": {
                    KIND_HEADERS[kind]: baseline.tokens_for(kind)
                    for kind in BASELINE_KINDS
                },
                "unresolved": list(baseline.unresolved),
                "artifacts": [
                    {
                        "kind": artifact.kind.value,
                        "label": artifact.label,
                        "tokens": artifact.tokens,
                    }
                    for artifact in baseline.artifacts
                ],
            }
            for baseline in measurement.baselines
        ],
        "files": [
            {
                "label": load.label,
                "tokens": load.tokens,
                "agents": list(load.agents),
                "loads": load.loads,
                "weighted": load.weighted,
            }
            for load in measurement.files
        ],
        "skills": [
            {
                "skill": activation.skill,
                "body_tokens": activation.body_tokens,
                "frontmatter_tokens": activation.frontmatter_tokens,
                "refs_upper_bound": activation.refs_upper_bound,
                "reference_files": activation.reference_files,
            }
            for activation in measurement.activations
        ],
    }
    return json.dumps(document, indent=2, sort_keys=True, default=str) + "\n"


def calibration_keys(calibration: Calibration) -> dict[str, object]:
    """
    Flatten a calibration into its ``calibration:*`` budget keys.

    One function rather than one per writer: ``check --write-budget`` and
    ``calibrate`` both persist this block, and two copies would let the
    two commands record different provenance for the same factor.

    Every value is a scalar, and the multi-item fields become one indexed
    key each. The budget is formatted by Prettier along with the rest of
    the repository, and Prettier inlines a short JSON array but expands a
    long one, so a document holding arrays cannot be written by this tool
    and pass ``make fmt-check`` at the same time. Indexed scalars also
    keep the promise the document is built on: one changed figure is one
    changed line.

    Args:
        calibration: Calibration to serialize.

    Returns:
        The flat mapping, unsorted; the caller sorts the whole document.
    """
    keys: dict[str, object] = {
        f"{CALIBRATION_PREFIX}factor": calibration.factor,
        f"{CALIBRATION_PREFIX}factor_low": calibration.factor_low,
        f"{CALIBRATION_PREFIX}factor_high": calibration.factor_high,
        f"{CALIBRATION_PREFIX}observed_at": calibration.observed_at,
        f"{CALIBRATION_PREFIX}agents": AGENT_SEPARATOR.join(calibration.agents),
        f"{CALIBRATION_PREFIX}tiktoken_version": calibration.tiktoken_version,
        f"{CALIBRATION_PREFIX}window": calibration.window,
        f"{CALIBRATION_PREFIX}basis": calibration.basis,
    }
    keys.update(_indexed(CAVEAT_PREFIX, calibration.caveats))
    keys.update(_indexed(OBSERVATION_PREFIX, calibration.observations))
    return keys


def _indexed(prefix: str, items: tuple[str, ...]) -> dict[str, object]:
    """
    Spread a sequence over one numbered scalar key per item.

    Args:
        prefix: Full key prefix, ending in a separator.
        items: Items to number, from one.

    Returns:
        The numbered mapping.
    """
    return {f"{prefix}{index}": item for index, item in enumerate(items, start=1)}


def budget_document(measurement: Measurement) -> dict[str, object]:
    """
    Build the committed budget document.

    Flat and sorted on purpose: the file is reviewed as a diff, and a
    nested document turns a one-figure change into a multi-line hunk.

    Args:
        measurement: Completed measurement.

    Returns:
        The budget mapping, ready to serialize.
    """
    document: dict[str, object] = {
        f"{AGENT_PREFIX}{baseline.agent}": baseline.total
        for baseline in measurement.baselines
    }
    document.update(
        {
            f"{SKILL_PREFIX}{activation.skill}": activation.body_tokens
            for activation in measurement.activations
        }
    )
    document[f"{META_PREFIX}backend"] = measurement.backend
    document[f"{META_PREFIX}tiktoken_version"] = measurement.tiktoken_version
    document[f"{META_PREFIX}recorded_at"] = measurement.generated_at
    document[f"{META_PREFIX}approximate"] = True
    if measurement.calibration is not None:
        document.update(calibration_keys(measurement.calibration))
    return dict(sorted(document.items()))


def render_budget(measurement: Measurement) -> str:
    """
    Serialize the committed budget.

    Args:
        measurement: Completed measurement.

    Returns:
        Pretty-printed JSON with sorted keys, newline-terminated.
    """
    return json.dumps(budget_document(measurement), indent=2, sort_keys=True) + "\n"


def render_check(
    violations: tuple[BudgetViolation, ...], warnings: tuple[str, ...]
) -> str:
    """
    Render the console output of a budget check.

    Args:
        violations: Figures exceeding their budget beyond tolerance.
        warnings: Non-fatal disagreements with the recorded budget.

    Returns:
        The console text, newline-terminated.
    """
    lines = ["=== Context Budget Check ===", ""]
    lines.extend(f"WARNING: {warning}" for warning in warnings)
    if warnings:
        lines.append("")
    for violation in violations:
        lines.append(
            f"ERROR: {violation.subject} is {violation.measured:,} tokens, "
            f"budget {violation.budget:,} "
            f"(+{violation.excess_pct:.1f}%, tolerance "
            f"{violation.tolerance_pct:g}%)"
        )
    if violations:
        lines.extend(
            [
                "",
                f"FAIL: {len(violations)} figure(s) over budget. Reduce them, or "
                "re-record the budget deliberately with `check --write-budget`.",
            ]
        )
    else:
        lines.append("PASS: every recorded figure is within tolerance.")
    return "\n".join(lines) + "\n"
