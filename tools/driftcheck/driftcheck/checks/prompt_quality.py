"""
Checks over the quality of the instruction artifacts themselves.

Each check encodes one documented Claude prompting anti-pattern whose
source page is vendored under
``.kiro/skills/claude-prompting-reference/references/``:

- Severity filtering in a review prompt lowers recall: the model
  investigates just as deeply, then withholds findings below the stated
  bar (``prompting-claude-sonnet-5.md``, ``prompting-claude-opus-5.md``,
  ``prompting-claude-opus-4-8.md``).
- An agent prompt with no stated boundary invites out-of-scope work.
  routing.md already publishes a ``never_when`` list per routable agent;
  the prompt is what the agent actually loads, so the boundary has to be
  there too.
- A prompt contradicting its own steering leaves the model to pick a
  side silently, and prompt text competes with steering for attention.

These are deterministic checks run by a tool, and that is the point. The
same guidance says to delete prompt-level instructions that tell a model
to re-verify its own output, and names an external check as the
substitute. No check in this module adds text to any prompt; each one
only reads.
"""

# Standard libraries
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Final

# Own modules
from driftcheck.checks.skills import stale_allowlist_findings
from driftcheck.paths import read_text
from driftcheck.types import DriftContext, Finding, Severity

SECTION_SEVERITY_FILTERING: Final[str] = "Review recall suppression"
SECTION_PROMPT_BOUNDARIES: Final[str] = "Agent prompt scope statements"
SECTION_CONTRADICTIONS: Final[str] = "Known cross-file contradictions"

# Skills whose body asks an agent to enumerate findings and report them.
# The recall anti-pattern only bites on that shape, so the surface is an
# allowlist rather than every skill: "Be conservative with
# interpretation" in a statistics reference is sound advice about
# reading a p-value, not an instruction to withhold findings, and a
# check that flagged it would be switched off within a week. The
# allowlist is validated for staleness like DIRECT_INVOKE_SKILLS, so an
# entry naming a deleted skill cannot sit here silently.
REVIEW_ORIENTED_SKILLS: Final[frozenset[str]] = frozenset(
    {
        "reviewing-code",
        "security-audit",
        "software-design-review",
        "tech-debt-tracking",
    }
)

# Instructions that set a reporting floor by severity. Scoped to the
# reporting verbs (report, flag, emit) on purpose: "Fix Critical and
# High findings" is a *fixing* budget, which is legitimate and is what
# reviewing-code Step 2 says, while "only report high-severity issues"
# suppresses the findings table itself. Verbs such as "surface" and
# "list" were dropped after they matched ordinary prose ("they only
# surface if actively searched for", "a V3-only surface").
SEVERITY_FILTERS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    ("only-report", re.compile(r"\bonly\s+(?:report|flag|emit)\b", re.IGNORECASE)),
    (
        "report-only-severe",
        re.compile(
            r"\b(?:report|flag|emit)\s+only\s+(?:the\s+)?"
            r"(?:critical|high|high-severity|severe|major|important|significant)",
            re.IGNORECASE,
        ),
    ),
    ("be-conservative", re.compile(r"\bbe\s+conservative\b", re.IGNORECASE)),
    (
        "no-nitpicking",
        re.compile(r"\b(?:do\s+not|don'?t|avoid|no)\s+nitpick", re.IGNORECASE),
    ),
    (
        "suppress-minor",
        re.compile(
            r"\b(?:skip|ignore|omit|suppress)\s+(?:the\s+)?"
            r"(?:minor|low-severity|low\s+severity|trivial|cosmetic|nitpick)",
            re.IGNORECASE,
        ),
    ),
)

# What turns a severity instruction from a recall leak into a governed
# threshold: an explicit emission bar, a calibration document the
# severities are anchored in, or Anthropic's own remedy of reporting
# everything and filtering downstream. Presence anywhere in the same
# artifact group (a skill plus its references, or one prompt file)
# exempts that group — the bar does not have to sit on the same line as
# the instruction it governs.
CONCRETE_BAR_MARKERS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"\bfinding bar\b", re.IGNORECASE),
    re.compile(r"finding-calibration\.md"),
    re.compile(r"\breport everything\b", re.IGNORECASE),
    re.compile(
        r"\bfilter\s+(?:it\s+|them\s+)?in\s+a\s+separate\s+pass\b", re.IGNORECASE
    ),
)

# A routing-YAML agent entry in routing.md ("      - id: code-reviewer").
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


@dataclass(frozen=True)
class ContradictionPair:
    """
    One curated contradiction between two instruction files.

    Both phrases have to be present for a finding: the pair describes a
    disagreement, so if either side has been rewritten there is nothing
    left to report.

    Attributes:
        label: Short handle for the contradiction, used in the message.
        left: Repository-relative path of the first file.
        left_phrase: Pattern locating the claim inside ``left``.
        right: Repository-relative path of the second file.
        right_phrase: Pattern locating the opposing claim in ``right``.
        explanation: Why the two claims cannot both be followed.
    """

    label: str
    left: str
    left_phrase: re.Pattern[str]
    right: str
    right_phrase: re.Pattern[str]
    explanation: str


# Deliberately narrow and curated, in the spirit of
# DIRECT_INVOKE_SKILLS: a general-purpose contradiction detector over
# prose would be wrong often enough to get disabled, and a disabled
# check protects nothing. Entries are added only for contradictions that
# were actually found and cost something, and each one is phrased so it
# stops firing once the contradiction is resolved rather than needing to
# be deleted by hand.
#
# Empty on purpose. The seed entry ("unbounded subagent fan-out": the
# orchestrator prompt used to authorise spawning as many subagents as a
# task required, contradicting delegation-lifecycle.md's four-subagent
# cap) was retired once ``_pair_findings`` below started reporting it as
# resolved rather than live: ``left_phrase`` no longer matches
# orchestrator.md, which now names the cap and defers to the "Delegation
# floor" section, while ``right_phrase`` still matches the steering
# unchanged. That is the one-side-flipped shape ``_pair_findings``
# classifies as "resolved", and re-adding the old phrase to make the
# check pass again would reintroduce the contradiction it exists to
# catch. A future entry should look exactly like the retired one:
#
#   ContradictionPair(
#       label="short handle for the disagreement",
#       left="path/to/file/a.md",
#       left_phrase=re.compile(r"claim made in file a", re.IGNORECASE),
#       right="path/to/file/b.md",
#       right_phrase=re.compile(r"opposing claim made in file b", re.IGNORECASE),
#       explanation="why the two claims cannot both be followed",
#   ),
KNOWN_CONTRADICTIONS: Final[tuple[ContradictionPair, ...]] = ()


def check_severity_filtering(ctx: DriftContext) -> list[Finding]:
    """
    Flag severity-filtering instructions in review-oriented artifacts.

    An instruction such as "only report high-severity issues" is
    followed literally by Claude Sonnet 5 and Opus 5: the model does the
    same depth of investigation and then withholds the findings it
    judges below the bar, so measured recall drops while the underlying
    bug-finding ability is unchanged. The instruction is only a problem
    when nothing defines the bar, so a group carrying an explicit
    finding bar or a calibration reference is exempt.

    Args:
        ctx: Shared check context.

    Returns:
        A warning per unmitigated instruction, plus a trailing OK.
    """
    findings: list[Finding] = []
    for group in _review_surfaces(ctx):
        if _has_concrete_bar(group):
            continue
        findings.extend(
            Finding(
                Severity.WARNING,
                SECTION_SEVERITY_FILTERING,
                f"{path.relative_to(ctx.root)}:{number} filters findings by "
                f"severity ({label}: {snippet!r}) with no concrete finding bar "
                "or calibration reference — Claude Sonnet 5 / Opus 5 follow "
                "such a bar literally and stop reporting below it, lowering "
                "review recall",
            )
            for path, number, label, snippet in _filtering_matches(group)
        )
    findings.extend(
        stale_allowlist_findings(
            ctx,
            SECTION_SEVERITY_FILTERING,
            "REVIEW_ORIENTED_SKILLS",
            REVIEW_ORIENTED_SKILLS,
        )
    )
    findings.append(
        Finding(
            Severity.OK, SECTION_SEVERITY_FILTERING, "Review recall suppression checked"
        )
    )
    return findings


def _review_surfaces(ctx: DriftContext) -> Iterator[tuple[Path, ...]]:
    """
    Iterate the artifact groups the recall anti-pattern applies to.

    A group is evaluated as a unit because the mitigation and the
    instruction it governs need not live in the same file: an allowlisted
    skill contributes its SKILL.md plus every reference file, and each
    agent prompt is a group of its own. Prompts need no allowlist —
    every agent prompt is a plausible place for a reporting instruction,
    and the patterns were calibrated against all of them.

    Args:
        ctx: Shared check context.

    Yields:
        The existing files of each group, in a stable order.
    """
    for skill in sorted(REVIEW_ORIENTED_SKILLS):
        skill_dir = ctx.skills_dir / skill
        if not skill_dir.is_dir():
            continue
        candidates = [
            skill_dir / "SKILL.md",
            *sorted((skill_dir / "references").rglob("*.md")),
        ]
        group = tuple(path for path in candidates if path.is_file())
        if group:
            yield group
    if ctx.prompts_dir.is_dir():
        for prompt in sorted(ctx.prompts_dir.glob("*.md")):
            yield (prompt,)


def _has_concrete_bar(group: tuple[Path, ...]) -> bool:
    """
    Report whether a group defines the bar its severities refer to.

    Args:
        group: Files forming one artifact group.

    Returns:
        True when any marker appears anywhere in the group.
    """
    text = "\n".join(read_text(path) for path in group)
    return any(marker.search(text) is not None for marker in CONCRETE_BAR_MARKERS)


def _filtering_matches(
    group: tuple[Path, ...],
) -> Iterator[tuple[Path, int, str, str]]:
    """
    Locate every severity-filtering instruction inside a group.

    Args:
        group: Files forming one artifact group.

    Yields:
        The file, 1-based line number, pattern label and matched text.
    """
    for path in group:
        for number, line in enumerate(read_text(path).splitlines(), start=1):
            for label, pattern in SEVERITY_FILTERS:
                match = pattern.search(line)
                if match is not None:
                    yield path, number, label, match.group(0)


def check_prompt_boundaries(ctx: DriftContext) -> list[Finding]:
    """
    Verify every routable agent's prompt states its own boundaries.

    routing.md publishes a ``never_when`` list per routable agent, but
    routing lives with the orchestrator while the prompt is what the
    specialist itself loads. Without the boundary in the prompt, an
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
    for slug in sorted(_routable_agents(read_text(ctx.routing_md))):
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
                f"routing.md declares never_when entries for '{slug}' that the "
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


def _routable_agents(routing_md: str) -> set[str]:
    """
    Collect the agent slugs the routing YAML declares.

    Args:
        routing_md: Full routing.md text.

    Returns:
        Every slug appearing as a routing-YAML ``- id:`` entry.
    """
    return {match.group("slug") for match in ROUTABLE_AGENT.finditer(routing_md)}


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


def check_known_contradictions(ctx: DriftContext) -> list[Finding]:
    """
    Report curated contradictions between two instruction files.

    Args:
        ctx: Shared check context.

    Returns:
        A warning per live contradiction or stale pair, plus a trailing
        OK finding.
    """
    findings: list[Finding] = []
    for pair in KNOWN_CONTRADICTIONS:
        findings.extend(_pair_findings(ctx, pair))
    findings.append(
        Finding(
            Severity.OK,
            SECTION_CONTRADICTIONS,
            "Known cross-file contradictions checked",
        )
    )
    return findings


def _pair_findings(ctx: DriftContext, pair: ContradictionPair) -> list[Finding]:
    """
    Evaluate one curated contradiction pair.

    A pair naming a file that no longer exists is dead configuration —
    it can never fire again — so it is reported the way a stale allowlist
    entry is, rather than passing silently. The file-existence guard is
    necessary but not sufficient: a pair whose files both still exist but
    whose phrases no longer both match is just as dead, and nothing else
    in this module would surface it (``check_prompt_references`` and
    ``stale_allowlist_findings`` do not cover contradiction phrases).

    A pair with exactly one phrase missing is reported separately from a
    pair with neither phrase present. One side missing plausibly means
    the contradiction was fixed on purpose — a resolved pair is the
    intended end state described in ``KNOWN_CONTRADICTIONS``' docstring,
    so it is good news, not a defect. Neither side present is more
    likely a phrase invalidated by an unrelated rewrite of both files —
    still dead configuration, but not necessarily evidence the
    disagreement itself was settled. Both cases stay at ``WARNING``: like
    a stale allowlist entry, this is a defect in the check's own
    configuration, never in the repository content it inspects, so
    failing the build with an ``ERROR`` would be the wrong signal for
    what is arguably good news in the resolved case.

    Args:
        ctx: Shared check context.
        pair: Curated pair to evaluate.

    Returns:
        The findings the pair produces, empty when it does not fire.
    """
    missing = [
        relative
        for relative in (pair.left, pair.right)
        if not (ctx.root / relative).is_file()
    ]
    if missing:
        return [
            Finding(
                Severity.WARNING,
                SECTION_CONTRADICTIONS,
                f"KNOWN_CONTRADICTIONS pair '{pair.label}' names "
                f"{', '.join(missing)}, which does not exist — stale pair, it "
                "can no longer fire",
            )
        ]
    left = _locate(ctx.root / pair.left, pair.left_phrase)
    right = _locate(ctx.root / pair.right, pair.right_phrase)
    if left is not None and right is not None:
        return [
            Finding(
                Severity.WARNING,
                SECTION_CONTRADICTIONS,
                f"{pair.label}: {pair.left}:{left[0]} says {left[1]!r} while "
                f"{pair.right}:{right[0]} says {right[1]!r} — {pair.explanation}",
            )
        ]
    if left is None and right is None:
        return [
            Finding(
                Severity.WARNING,
                SECTION_CONTRADICTIONS,
                f"KNOWN_CONTRADICTIONS pair '{pair.label}' matches neither "
                f"phrase in {pair.left} nor {pair.right} — stale pair, likely "
                "invalidated by an unrelated rewrite rather than resolved on "
                "purpose",
            )
        ]
    resolved_side = pair.left if left is None else pair.right
    return [
        Finding(
            Severity.WARNING,
            SECTION_CONTRADICTIONS,
            f"KNOWN_CONTRADICTIONS pair '{pair.label}' no longer matches its "
            f"phrase in {resolved_side} — stale pair, likely resolved on "
            "purpose; remove it or replace it with the next contradiction",
        )
    ]


def _locate(path: Path, phrase: re.Pattern[str]) -> tuple[int, str] | None:
    """
    Find a phrase in a file, tolerating line wrapping.

    Matching runs against the whole text with whitespace-flexible
    patterns, because prose in this repository is reflowed to a fixed
    width and a claim can land on either side of a line break.

    Args:
        path: File to search.
        phrase: Pattern locating the claim.

    Returns:
        The 1-based line number and the matched text with whitespace
        collapsed, or None when the phrase is absent.
    """
    text = read_text(path)
    match = phrase.search(text)
    if match is None:
        return None
    number = text.count("\n", 0, match.start()) + 1
    return number, " ".join(match.group(0).split())
