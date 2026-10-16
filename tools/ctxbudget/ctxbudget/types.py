"""
Shared vocabulary for context-budget measurement.

Holds the artifact taxonomy, the resolved-entry record the resolution
step produces, the per-agent and per-skill measurement records, the
calibration provenance record.

Every record is frozen: a measurement is a snapshot, and a mutable
snapshot invites a caller to "adjust" a figure after the fact, which
would silently detach the reported numbers from the counted ones.
"""

# Standard libraries
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class ArtifactKind(Enum):
    """
    Cost class of one artifact reaching a session.

    The value is the short column label used by the reports, so it is
    part of the output contract.
    """

    PROMPT = "prompt"
    FILE = "file"
    SKILL_FRONTMATTER = "skill_fm"
    KNOWLEDGE_BASE = "kb"
    STEERING_AUTO = "steering_auto"


# Kinds summed into an agent baseline, in report column order. Every
# member of ArtifactKind is a baseline cost, so the tuple is derived
# from the enum rather than restated: a new kind then appears in the
# per-agent table instead of being dropped from the total in silence.
BASELINE_KINDS: tuple[ArtifactKind, ...] = tuple(ArtifactKind)

# Kinds Kiro CLI's `/context show` groups under "Agent files": the
# artifacts an agent's `resources` array declares. Observed directly: a
# live orchestrator session listed its two `file://` resources, its
# `tools/TOOLS_OVERVIEW.md` and its skill frontmatter under that heading,
# and listed neither the agent prompt nor the auto-loaded steering files.
# The distinction is not cosmetic — it is the only artifact set a
# `/context show` reading can be compared against, so it is the set a
# calibration divides by. Dividing the observation by a full baseline
# instead compares a figure against a strict superset of what it covers
# and inverts the direction of the resulting factor.
AGENT_FILES_KINDS: tuple[ArtifactKind, ...] = (
    ArtifactKind.FILE,
    ArtifactKind.SKILL_FRONTMATTER,
    ArtifactKind.KNOWLEDGE_BASE,
)

# Increment `/context show` displays a percentage in. One decimal, so a
# reading is the displayed figure plus or minus half of this, which is
# what bounds a derived factor rather than a bare point value.
DISPLAY_STEP_PCT: float = 0.1


@dataclass(frozen=True)
class AgentConfig:
    """
    One parsed agent configuration file.

    Attributes:
        path: Absolute path to the JSON config.
        data: Decoded top-level mapping.
    """

    path: Path
    data: dict[str, Any]

    @property
    def slug(self) -> str:
        """Return the filename without extension."""
        return self.path.stem

    @property
    def name(self) -> str:
        """Return the declared name, falling back to the file stem."""
        name = self.data.get("name")
        return name if isinstance(name, str) and name else self.slug


@dataclass(frozen=True)
class ResolvedEntry:
    """
    One artifact an agent pays for, before it is counted.

    ``label`` is both the within-agent deduplication key (paired with
    ``kind``) and the aggregation key of the per-file table, so two
    entries naming the same physical file share a label even when their
    kinds differ.

    Attributes:
        kind: Cost class.
        label: Repository-relative identifier, stable across runs.
        path: Source file, or None for a synthetic entry.
        text: Pre-extracted text to count, or None to count the file.
    """

    kind: ArtifactKind
    label: str
    path: Path | None
    text: str | None


@dataclass(frozen=True)
class ResolvedAgent:
    """
    The artifact set one agent loads on every request.

    Attributes:
        agent: Agent name.
        entries: Deduplicated artifacts, in declaration order.
        unresolved: Declared resources that resolved to nothing.
    """

    agent: str
    entries: tuple[ResolvedEntry, ...]
    unresolved: tuple[str, ...]


@dataclass(frozen=True)
class Artifact:
    """
    A counted artifact.

    Attributes:
        kind: Cost class.
        label: Repository-relative identifier.
        tokens: Approximate token count.
    """

    kind: ArtifactKind
    label: str
    tokens: int


@dataclass(frozen=True)
class AgentBaseline:
    """
    The token floor one agent pays on every request of every session.

    Attributes:
        agent: Agent name.
        artifacts: Counted artifacts making up the floor.
        unresolved: Declared resources that resolved to nothing.
    """

    agent: str
    artifacts: tuple[Artifact, ...]
    unresolved: tuple[str, ...]

    @property
    def total(self) -> int:
        """Return the sum over every artifact class."""
        return sum(artifact.tokens for artifact in self.artifacts)

    @property
    def agent_files_total(self) -> int:
        """
        Return the sum over the classes `/context show` calls Agent files.

        This, not ``total``, is what a ``/context show`` observation can
        be compared against: that display covers the declared resources
        and neither the agent prompt nor the auto-loaded steering.
        """
        return sum(self.tokens_for(kind) for kind in AGENT_FILES_KINDS)

    def tokens_for(self, kind: ArtifactKind) -> int:
        """
        Sum the artifacts of one cost class.

        Args:
            kind: Cost class to sum.

        Returns:
            Approximate token count for that class.
        """
        return sum(
            artifact.tokens for artifact in self.artifacts if artifact.kind is kind
        )


@dataclass(frozen=True)
class SkillActivation:
    """
    The one-off cost of activating one skill.

    ``refs_upper_bound`` is never added to ``body_tokens``: reference
    files are read selectively, so summing them would report a cost no
    session actually pays.

    Attributes:
        skill: Skill directory name.
        body_tokens: SKILL.md body, frontmatter excluded.
        frontmatter_tokens: Name plus description, the startup cost.
        refs_upper_bound: Total of ``references/**``, or None when the
            run did not measure them.
        reference_files: Number of reference files behind that bound.
    """

    skill: str
    body_tokens: int
    frontmatter_tokens: int
    refs_upper_bound: int | None
    reference_files: int


@dataclass(frozen=True)
class FileLoad:
    """
    One always-on artifact, aggregated across the agents loading it.

    ``loads`` and ``agents`` differ only when one agent pays for the
    same file more than once. No resolution rule in force does that
    today; the distinction is kept because the weighted total must use
    ``loads``, which is what a removed token is actually multiplied by.

    Attributes:
        label: Repository-relative identifier.
        tokens: Approximate token count of the artifact itself.
        agents: Distinct agents paying for it, sorted.
        loads: Number of times it is paid across all agents.
    """

    label: str
    tokens: int
    agents: tuple[str, ...]
    loads: int

    @property
    def weighted(self) -> int:
        """Return tokens multiplied by the number of loads."""
        return self.tokens * self.loads


@dataclass(frozen=True)
class Observation:
    """
    One ground-truth figure read from Kiro CLI's ``/context show``.

    ``/context show`` reports each resource group as a percentage of the
    context window, computed by the real tokenizer over the real
    assembled prompt. That percentage times the window is the only
    ground truth available without an API key.

    The percentage covers the "Agent files" group, which is the agent's
    declared resources and nothing else, so it is comparable with
    ``AgentBaseline.agent_files_total`` rather than with a full baseline.

    Attributes:
        agent: Agent whose session was observed.
        context_files_pct: Percentage the "Agent files" group occupied.
        window: Context window size in tokens, a per-model property.
        display_step_pct: Increment the percentage was displayed in, so
            that the true figure lies within half a step of it. Zero
            when the figure was supplied as an exact token count.
    """

    agent: str
    context_files_pct: float
    window: int
    display_step_pct: float = DISPLAY_STEP_PCT

    @property
    def observed_tokens(self) -> int:
        """Return the ground-truth token count the percentage implies."""
        return self._tokens(self.context_files_pct)

    @property
    def observed_low(self) -> int:
        """Return the lowest token count the displayed figure allows."""
        return self._tokens(self.context_files_pct - self.display_step_pct / 2.0)

    @property
    def observed_high(self) -> int:
        """Return the highest token count the displayed figure allows."""
        return self._tokens(self.context_files_pct + self.display_step_pct / 2.0)

    def _tokens(self, percentage: float) -> int:
        """
        Convert a percentage of the window into tokens.

        Args:
            percentage: Share of the context window, clamped at zero so
                a low bound below zero cannot produce negative tokens.

        Returns:
            The token count that percentage of the window implies.
        """
        return round(self.window * max(percentage, 0.0) / 100.0)


@dataclass(frozen=True)
class Calibration:
    """
    A stored correction factor and its provenance.

    The factor is a band rather than a point value. ``/context show``
    displays one decimal, which at a 1M-token window is a thousand
    tokens of granularity, so a single reading pins the factor only to
    within a few percent. Reporting ``factor`` without ``factor_low``
    and ``factor_high`` would present that as precision it does not have.

    Attributes:
        factor: observed / estimated at the displayed percentage.
        factor_low: Same ratio at the low end of the display precision.
        factor_high: Same ratio at the high end of it.
        observed_at: ISO date the observation was taken.
        agents: Agents the observations came from, sorted.
        tiktoken_version: tiktoken version that produced the estimate.
        window: Context window the percentages referred to.
        basis: Artifact classes both sides of the ratio cover.
        caveats: Documented limits, reported wherever the factor is.
        observations: Human-readable provenance, one line per figure.
    """

    factor: float
    factor_low: float
    factor_high: float
    observed_at: str
    agents: tuple[str, ...]
    tiktoken_version: str
    window: int
    basis: str
    caveats: tuple[str, ...]
    observations: tuple[str, ...]


@dataclass(frozen=True)
class Measurement:
    """
    A complete measurement of one repository tree.

    Attributes:
        root: Repository root measured.
        backend: Counting backend identifier.
        tiktoken_version: Version of the installed tokenizer.
        generated_at: ISO timestamp of the run.
        baselines: Per-agent floors, sorted by agent name.
        activations: Per-skill activation costs, sorted by skill name.
        files: Always-on artifacts aggregated across agents.
        calibration: Stored calibration, or None when uncalibrated.
        with_references: Whether reference upper bounds were measured.
    """

    root: Path
    backend: str
    tiktoken_version: str
    generated_at: str
    baselines: tuple[AgentBaseline, ...]
    activations: tuple[SkillActivation, ...]
    files: tuple[FileLoad, ...]
    calibration: Calibration | None
    with_references: bool


@dataclass(frozen=True)
class BudgetViolation:
    """
    One figure exceeding its recorded budget beyond tolerance.

    Attributes:
        subject: Budget key, e.g. ``agent:senior-developer``.
        budget: Recorded figure.
        measured: Figure measured by this run.
        tolerance_pct: Tolerance the comparison allowed.
    """

    subject: str
    budget: int
    measured: int
    tolerance_pct: float

    @property
    def excess_pct(self) -> float:
        """Return the overshoot as a percentage of the budget."""
        if self.budget == 0:
            return 100.0
        return (self.measured - self.budget) / self.budget * 100.0
