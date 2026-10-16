"""
The cost model: two metrics, one weighted aggregation, one comparison.

``baseline(agent)`` is the floor paid on every request of every session
with that agent: its prompt, its deduplicated ``file://`` resources, the
frontmatter of every skill it makes available, and the metadata of every
knowledge base it declares. ``activation(skill)`` is the one-off cost of
a skill body, reported with an upper bound over its reference files that
is never summed into it.

The per-file aggregation is what drives reduction work: a token removed
from a file ten agents load is worth ten, so the weighted
column, not the raw size, is the ranking that matters.

Budget comparison lives here too, as arithmetic over a measurement. It
deliberately stops at "this figure grew": a structural assertion about
the agent system belongs in ``driftcheck``, which owns that verdict.
"""

# Standard libraries
import logging
from collections import defaultdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Final

# Own modules
from ctxbudget.count import Counter
from ctxbudget.resolve import (
    frontmatter_summary,
    load_agent_configs,
    reference_files,
    resolve_agent,
    skill_dirs,
    split_frontmatter,
)
from ctxbudget.types import (
    AgentBaseline,
    Artifact,
    BudgetViolation,
    Calibration,
    FileLoad,
    Measurement,
    Observation,
    ResolvedAgent,
    ResolvedEntry,
    SkillActivation,
)

logger = logging.getLogger(__name__)

# Budget-key prefixes. Flat keys with a prefix keep the committed budget
# a single-level document that diffs cleanly, while still separating the
# two metric families and the provenance block.
AGENT_PREFIX: Final[str] = "agent:"
SKILL_PREFIX: Final[str] = "skill:"
META_PREFIX: Final[str] = "meta:"
CALIBRATION_PREFIX: Final[str] = "calibration:"

# The multi-item calibration fields, spread over numbered scalar keys.
# The budget holds no arrays at all: Prettier formats it with the rest of
# the repository and inlines a short array while expanding a long one, so
# an array this tool writes cannot also satisfy `make fmt-check`.
CAVEAT_PREFIX: Final[str] = f"{CALIBRATION_PREFIX}caveat:"
OBSERVATION_PREFIX: Final[str] = f"{CALIBRATION_PREFIX}observation:"
AGENT_SEPARATOR: Final[str] = ", "

# What both sides of a calibration ratio cover, stored with the factor
# so a reader never has to reconstruct it. The observation covers the
# declared resources only, so the estimate must too; the factor is then
# extrapolated when applied to a full baseline, which the note says.
CALIBRATION_BASIS: Final[str] = (
    'the artifact classes `/context show` groups as "Agent files": declared '
    "`file://` resources, skill frontmatter and knowledge-base metadata. The "
    "agent prompt and the auto-loaded steering files are excluded from both "
    "sides of the ratio because that display does not cover them, so applying "
    "the factor to a full baseline extrapolates it to two classes no "
    "observation has reached."
)

# The residual this factor does not explain. Reported wherever the
# factor is, because a single aggregate factor reads as settled unless
# the disagreement underneath it is stated.
CALIBRATION_RESIDUAL: Final[str] = (
    "the per-file figures do not reconcile with any single factor: on the "
    "orchestrator observation the implied per-file factors span 0.89 "
    "(`tools/TOOLS_OVERVIEW.md`) to 1.41 (`.kiro/orchestration/routing.md`), a "
    "spread too wide for the display's rounding to explain. A constant "
    "per-file framing overhead does not explain it either: no tokens*f+c fits "
    "all three rows inside display precision, since the two larger rows alone "
    "force f <= 0.96 and the smallest row then contradicts it. What remains is "
    "the display's own semantics, which nothing local can settle, so the "
    "aggregate factor is indicative rather than settled."
)


def measure(
    root: Path,
    counter: Counter,
    with_references: bool,
    calibration: Calibration | None,
) -> Measurement:
    """
    Measure one repository tree end to end.

    Args:
        root: Repository root to measure.
        counter: Token counting backend.
        with_references: Whether to measure reference upper bounds.
        calibration: Stored calibration, or None when uncalibrated.

    Returns:
        A complete measurement snapshot.
    """
    baselines = tuple(
        sorted(
            (
                agent_baseline(resolve_agent(config, root), counter)
                for config in load_agent_configs(root)
            ),
            key=lambda baseline: baseline.agent,
        )
    )
    activations = tuple(
        skill_activation(skill_dir, counter, with_references)
        for skill_dir in skill_dirs(root)
    )
    return Measurement(
        root=root,
        backend=counter.backend,
        tiktoken_version=counter.version,
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
        baselines=baselines,
        activations=activations,
        files=file_loads(baselines),
        calibration=calibration,
        with_references=with_references,
    )


def agent_baseline(resolved: ResolvedAgent, counter: Counter) -> AgentBaseline:
    """
    Count every artifact of one resolved agent.

    Args:
        resolved: Resolved artifact set for the agent.
        counter: Token counting backend.

    Returns:
        The agent's per-request floor.
    """
    artifacts = tuple(
        Artifact(
            kind=entry.kind,
            label=entry.label,
            tokens=_entry_tokens(entry, counter),
        )
        for entry in resolved.entries
    )
    return AgentBaseline(
        agent=resolved.agent,
        artifacts=artifacts,
        unresolved=resolved.unresolved,
    )


def _entry_tokens(entry: ResolvedEntry, counter: Counter) -> int:
    """
    Count one resolved entry, preferring its pre-extracted text.

    Args:
        entry: Resolved entry.
        counter: Token counting backend.

    Returns:
        Approximate token count, 0 for an entry carrying neither text
        nor a readable path.
    """
    if entry.text is not None:
        return counter.count(entry.text)
    if entry.path is not None:
        return counter.count_path(entry.path)
    return 0


def skill_activation(
    skill_dir: Path, counter: Counter, with_references: bool
) -> SkillActivation:
    """
    Count the activation cost of one skill.

    Args:
        skill_dir: Skill directory holding SKILL.md.
        counter: Token counting backend.
        with_references: Whether to measure the reference upper bound.

    Returns:
        The skill's activation cost, with the reference bound alongside.
    """
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    _, body = split_frontmatter(text)
    references = reference_files(skill_dir) if with_references else ()
    bound = (
        sum(counter.count_path(path) for path in references)
        if with_references
        else None
    )
    return SkillActivation(
        skill=skill_dir.name,
        body_tokens=counter.count(body),
        frontmatter_tokens=counter.count(frontmatter_summary(text)),
        refs_upper_bound=bound,
        reference_files=len(references),
    )


def file_loads(baselines: tuple[AgentBaseline, ...]) -> tuple[FileLoad, ...]:
    """
    Aggregate always-on artifacts across the agents that load them.

    Sorted by weighted total descending, because that is the order a
    reduction backlog should be worked in.

    Args:
        baselines: Per-agent floors.

    Returns:
        One row per distinct artifact label.
    """
    tokens: dict[str, int] = {}
    agents: defaultdict[str, set[str]] = defaultdict(set)
    loads: defaultdict[str, int] = defaultdict(int)
    for baseline in baselines:
        for artifact in baseline.artifacts:
            tokens[artifact.label] = artifact.tokens
            agents[artifact.label].add(baseline.agent)
            loads[artifact.label] += 1
    rows = [
        FileLoad(
            label=label,
            tokens=count,
            agents=tuple(sorted(agents[label])),
            loads=loads[label],
        )
        for label, count in tokens.items()
    ]
    return tuple(sorted(rows, key=lambda row: (-row.weighted, row.label)))


def derive_calibration(
    observations: tuple[Observation, ...],
    measurement: Measurement,
) -> Calibration:
    """
    Derive a calibration factor from ``/context show`` observations.

    No network call is involved and none is possible: the ground truth is
    a percentage a human read off Kiro CLI's own context display, which
    the real tokenizer computed over the real assembled prompt.

    The comparison is deliberately narrow. ``/context show`` reports the
    declared resources under "Agent files" and reports neither the agent
    prompt nor the auto-loaded steering, so the estimate it is divided by
    is ``agent_files_total`` rather than the full baseline. Dividing by
    the full baseline compares the observation against a strict superset
    of what it covers, which understates the factor enough to invert its
    direction — reading as "tiktoken overestimates" when it undercounts.

    The result is a band, not a point: the display's one decimal is worth
    a thousand tokens at a 1M window, so the low and high ends of that
    precision are carried alongside the midpoint.

    Args:
        observations: Ground-truth figures, at least one.
        measurement: Measurement supplying the estimate per agent.

    Returns:
        The derived factor with its band, basis, caveats and provenance.

    Raises:
        ValueError: If no observation names a measured agent, or an
            estimate is zero and so cannot be divided by.
    """
    estimates = {
        baseline.agent: baseline.agent_files_total for baseline in measurement.baselines
    }
    factors: list[tuple[float, float, float]] = []
    lines: list[str] = []
    agents: list[str] = []
    used: list[Observation] = []
    for observation in observations:
        estimated = estimates.get(observation.agent)
        if estimated is None:
            logger.warning(
                "Observation names unknown agent %s, ignoring it.", observation.agent
            )
            continue
        if estimated == 0:
            message = (
                f"agent {observation.agent} declares 0 tokens of resources, "
                "cannot calibrate"
            )
            raise ValueError(message)
        factors.append(
            (
                observation.observed_tokens / estimated,
                observation.observed_low / estimated,
                observation.observed_high / estimated,
            )
        )
        agents.append(observation.agent)
        used.append(observation)
        lines.append(_provenance_line(observation, estimated))
    if not factors:
        message = "no observation names a measured agent, nothing to calibrate"
        raise ValueError(message)
    window = max(observation.window for observation in used)
    step_pct = max(observation.display_step_pct for observation in used)
    return Calibration(
        factor=_mean(index=0, factors=factors),
        factor_low=_mean(index=1, factors=factors),
        factor_high=_mean(index=2, factors=factors),
        observed_at=date.today().isoformat(),
        agents=tuple(sorted(set(agents))),
        tiktoken_version=measurement.tiktoken_version,
        window=window,
        basis=CALIBRATION_BASIS,
        caveats=(_precision_note(window, step_pct), CALIBRATION_RESIDUAL),
        observations=tuple(lines),
    )


def _mean(index: int, factors: list[tuple[float, float, float]]) -> float:
    """
    Average one element of the per-observation factor triples.

    Args:
        index: Element to average: midpoint, low bound or high bound.
        factors: One (factor, low, high) triple per observation.

    Returns:
        The mean, rounded to the four decimals the budget records.
    """
    return round(sum(item[index] for item in factors) / len(factors), 4)


def _provenance_line(observation: Observation, estimated: int) -> str:
    """
    Render one observation as a human-readable provenance line.

    Args:
        observation: The ground-truth figure.
        estimated: Declared-resource estimate it was compared against.

    Returns:
        One line naming both figures, the band and the derived factor.
    """
    factor = observation.observed_tokens / estimated
    return (
        f"{observation.agent}: {observation.context_files_pct}% of "
        f"{observation.window} = {observation.observed_tokens} observed "
        f"({observation.observed_low}-{observation.observed_high} at display "
        f"precision) vs {estimated} estimated over declared resources "
        f"(factor {factor:.4f})"
    )


def _precision_note(window: int, step_pct: float) -> str:
    """
    State how precisely the observation could be read.

    Args:
        window: Context window the percentages referred to.
        step_pct: Increment the percentage was displayed in.

    Returns:
        The caveat line, adapted to whether the figure was a displayed
        percentage or an exact token count.
    """
    if step_pct <= 0.0:
        return (
            "the figures were supplied as exact token counts, so they carry no "
            "display rounding of their own; whatever produced them does bound "
            "the factor, and nothing here can check that bound."
        )
    step = round(window * step_pct / 100.0)
    return (
        f"`/context show` displays {step_pct:g}% increments, which against a "
        f"{window:,}-token window is about {step:,} tokens. The aggregate is "
        "therefore the only quantity it can calibrate: a single file's "
        "displayed percentage carries an error of the same order as the file, "
        "so per-file observations are not supported."
    )


def compare_budget(
    measurement: Measurement, budget: dict[str, object], tolerance_pct: float
) -> tuple[tuple[BudgetViolation, ...], tuple[str, ...]]:
    """
    Compare a measurement against a recorded budget.

    Tolerance absorbs jitter: a tokenizer upgrade or a whitespace-only
    reformat moves a figure by a fraction of a percent, and a gate that
    fires on that gets switched off.

    Args:
        measurement: Current measurement.
        budget: Decoded budget document.
        tolerance_pct: Percentage a figure may exceed its budget by.

    Returns:
        The violations, and warning lines for provenance mismatches and
        for measured subjects the budget does not record.
    """
    measured = measured_figures(measurement)
    violations = [
        BudgetViolation(
            subject=subject,
            budget=int(recorded),
            measured=measured[subject],
            tolerance_pct=tolerance_pct,
        )
        for subject, recorded in sorted(budget.items())
        if isinstance(recorded, int)
        and subject in measured
        and measured[subject] > int(recorded) * (1.0 + tolerance_pct / 100.0)
    ]
    return tuple(violations), _budget_warnings(measurement, budget, measured)


def measured_figures(measurement: Measurement) -> dict[str, int]:
    """
    Flatten a measurement into the budget's key space.

    Args:
        measurement: Current measurement.

    Returns:
        Budget key to measured figure.
    """
    figures = {
        f"{AGENT_PREFIX}{baseline.agent}": baseline.total
        for baseline in measurement.baselines
    }
    figures.update(
        {
            f"{SKILL_PREFIX}{activation.skill}": activation.body_tokens
            for activation in measurement.activations
        }
    )
    return figures


def _budget_warnings(
    measurement: Measurement, budget: dict[str, object], measured: dict[str, int]
) -> tuple[str, ...]:
    """
    Collect non-fatal disagreements between run and recorded budget.

    Args:
        measurement: Current measurement.
        budget: Decoded budget document.
        measured: Flattened current figures.

    Returns:
        Warning lines, empty when the two agree.
    """
    warnings: list[str] = []
    expected = {
        f"{META_PREFIX}backend": measurement.backend,
        f"{META_PREFIX}tiktoken_version": measurement.tiktoken_version,
    }
    for key, current in expected.items():
        recorded = budget.get(key)
        if recorded is not None and recorded != current:
            warnings.append(
                f"{key}: budget records {recorded!r}, this run used {current!r} "
                "— the comparison crosses measurement settings"
            )
    warnings.extend(
        f"{subject} is not recorded in the budget (new since it was written)"
        for subject in sorted(measured)
        if subject not in budget
    )
    warnings.extend(
        f"{subject} is recorded in the budget but was not measured (removed?)"
        for subject in sorted(budget)
        if subject.startswith((AGENT_PREFIX, SKILL_PREFIX)) and subject not in measured
    )
    return tuple(warnings)
