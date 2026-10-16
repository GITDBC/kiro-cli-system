"""
Checks over the always-on steering layer.

Covers steering files that reproduce a skill body, the
enumerated-heading convention COMMON.md forbids, and the two
arrangements that keep ``.kiro/orchestration/`` honest: the
orchestrator-only files staying out of always-on steering, and every
file in that directory remaining reachable from somewhere.

The last two are shipped as separate checks, matching this codebase's
one-concern-per-check convention: a file drifting back into steering and
a file no session can arrive at are unrelated failure modes with
unrelated remedies.
"""

# Standard libraries
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Final

# Own modules
from driftcheck.checks.agents import GLOB_CHARACTERS
from driftcheck.paths import VENDORED_SKILL, read_text
from driftcheck.types import AgentConfig, DriftContext, Finding, Severity

# Duplication heuristics for the steering/skill overlap check.
#
# MIN_SIGNIFICANT_LINE_LENGTH: a line shorter than this is a bullet
# marker, a table separator or a couple of words. Such lines recur across
# unrelated documents and would inflate the overlap score without
# indicating duplicated content.
#
# MIN_SIGNIFICANT_HEADING_LENGTH: markdown headings shorter than this
# ("## Rules", "## Workflow") are shared section names, not duplicated
# prose, so they are excluded even when they clear the line-length bar.
#
# OVERLAP_THRESHOLD: below 0.4 the shared lines are conventional
# boilerplate (identical bullet phrasing, the same stack sentence).
# Above it the steering file is reproducing the skill body, which is the
# code-standards incident this check exists to catch. Steering is
# always-on context, so that duplication is paid on every invocation
# rather than only when the skill loads.
MIN_SIGNIFICANT_LINE_LENGTH: Final[int] = 20
MIN_SIGNIFICANT_HEADING_LENGTH: Final[int] = 30
OVERLAP_THRESHOLD: Final[float] = 0.4

MARKDOWN_FENCES: Final[tuple[str, ...]] = ("```", "~~~")

# Suffix a steering file carries when it condenses a skill of the same
# base name, as in code-standards-summary.md over the code-standards
# skill. Stripping it is what keeps the pairing discoverable: matching
# on the bare stem alone silently exempted every "-summary" file, which
# is precisely the shape most at risk of reproducing its skill body.
SUMMARY_SUFFIX: Final[str] = "-summary"

# Enumerated heading: a digit followed by "." or ")" then a space, as in
# "## 1. Output validation". Proper nouns and standards names such as
# "## 2FA Setup" or "## 3D Rendering" are legitimate and never match.
ENUMERATED_HEADING: Final[re.Pattern[str]] = re.compile(r"^#{1,6} [0-9]+[.)] ")

SECTION_DUPLICATION: Final[str] = "Steering/skill content duplication"
SECTION_NUMBERED_HEADERS: Final[str] = "Numbered markdown headers"
SECTION_ORCHESTRATION_PLACEMENT: Final[str] = "Orchestrator-only file placement"
SECTION_ORCHESTRATION_REACHABILITY: Final[str] = "Orchestration file reachability"

# The orchestrator-only instruction files. They were moved out of
# .kiro/steering/ because Kiro CLI loads every steering file into every
# session, subagent sessions included, regardless of an agent's
# resources list: a probe measured their roughly 1,118 lines filling an
# estimated 70-75% of a specialist's context on every dispatch, for
# content no specialist acts on. Neither half of the arrangement fails
# visibly at runtime — a file back in steering silently re-imposes that
# cost, and a dropped resources entry silently leaves the orchestrator
# without its routing tables — so both are asserted here.
ORCHESTRATION_FILES: Final[tuple[str, ...]] = (
    "routing.md",
    "delegation-lifecycle.md",
)

# Resource URI prefix an agent config uses, and the workspace-root
# relative directory the orchestrator-only files must be declared from.
FILE_URI_PREFIX: Final[str] = "file://"
ORCHESTRATION_PREFIX: Final[str] = ".kiro/orchestration/"


def check_steering_duplication(ctx: DriftContext) -> list[Finding]:
    """
    Detect steering files that reproduce a skill's body.

    Args:
        ctx: Shared check context.

    Returns:
        A warning per over-threshold pair, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    if ctx.steering_dir.is_dir():
        for steering_file in sorted(ctx.steering_dir.glob("*.md")):
            skill_name = _paired_skill_name(steering_file)
            skill_file = ctx.skills_dir / skill_name / "SKILL.md"
            if not skill_file.is_file():
                continue
            steering_lines = significant_lines(steering_file)
            skill_lines = significant_lines(skill_file)
            if not steering_lines or not skill_lines:
                continue
            shared = steering_lines & skill_lines
            overlap = len(shared) / min(len(steering_lines), len(skill_lines))
            if overlap > OVERLAP_THRESHOLD:
                findings.append(
                    Finding(
                        Severity.WARNING,
                        SECTION_DUPLICATION,
                        f"{steering_file.name} overlaps {overlap:.0%} with "
                        f"skills/{skill_name}/SKILL.md — steering is "
                        "always-on, duplication is paid on every invocation",
                    )
                )
    findings.append(
        Finding(Severity.OK, SECTION_DUPLICATION, "Steering/skill duplication checked")
    )
    return findings


def _paired_skill_name(steering_file: Path) -> str:
    """
    Return the skill a steering file is the counterpart of.

    Args:
        steering_file: Steering markdown file.

    Returns:
        The file stem with a trailing "-summary" removed.
    """
    return steering_file.stem.removesuffix(SUMMARY_SUFFIX)


def significant_lines(path: Path) -> set[str]:
    """
    Collect lines worth comparing for duplication.

    Args:
        path: Markdown file to read.

    Returns:
        Stripped lines that clear the significance heuristics.
    """
    collected: set[str] = set()
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if len(stripped) < MIN_SIGNIFICANT_LINE_LENGTH:
            continue
        if stripped.startswith("#") and len(stripped) < MIN_SIGNIFICANT_HEADING_LENGTH:
            continue
        collected.add(stripped)
    return collected


def check_numbered_headers(ctx: DriftContext) -> list[Finding]:
    """
    Flag enumerated markdown headings, which COMMON.md forbids.

    Only enumeration matches, so proper nouns such as "## 2FA
    Setup" are left alone. Lines inside fenced code blocks are
    skipped because "# 3pps" is this project's import-section-header
    comment convention, not a heading. The vendored kiro-cli-reference
    mirror is excluded.

    Args:
        ctx: Shared check context.

    Returns:
        A warning per numbered heading, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    if ctx.kiro_dir.is_dir():
        for path in sorted(ctx.kiro_dir.rglob("*.md")):
            if VENDORED_SKILL in path.parts:
                continue
            relative = path.relative_to(ctx.root)
            for number, line in _headings_outside_fences(path):
                findings.append(
                    Finding(
                        Severity.WARNING,
                        SECTION_NUMBERED_HEADERS,
                        "Numbered header (COMMON.md forbids it) -> "
                        f"{relative}:{number}: {line}",
                    )
                )
    findings.append(
        Finding(
            Severity.OK, SECTION_NUMBERED_HEADERS, "Numbered markdown headers checked"
        )
    )
    return findings


def _headings_outside_fences(path: Path) -> Iterator[tuple[int, str]]:
    """
    Iterate enumerated headings that are not inside a code fence.

    Args:
        path: Markdown file to scan.

    Yields:
        The 1-based line number and stripped text of each heading.
    """
    inside_fence = False
    for number, line in enumerate(read_text(path).splitlines(), start=1):
        if line.lstrip().startswith(MARKDOWN_FENCES):
            inside_fence = not inside_fence
        elif not inside_fence and ENUMERATED_HEADING.match(line):
            yield number, line.strip()


def check_orchestration_placement(ctx: DriftContext) -> list[Finding]:
    """
    Verify the orchestrator-only files stay out of always-on steering.

    Two halves of one arrangement, so they are asserted together: the
    files must not sit in .kiro/steering/, where every agent would pay
    for them on every turn, and the orchestrator must still name them in
    its resources, which is now the only way they reach any session.

    Args:
        ctx: Shared check context.

    Returns:
        One ERROR per misplaced or unreferenced file, plus a trailing OK.
    """
    findings: list[Finding] = [
        Finding(Severity.ERROR, SECTION_ORCHESTRATION_PLACEMENT, message)
        for message in _misplaced_messages(ctx) + _unreferenced_messages(ctx)
    ]
    findings.append(
        Finding(
            Severity.OK,
            SECTION_ORCHESTRATION_PLACEMENT,
            "Orchestrator-only file placement checked",
        )
    )
    return findings


def _misplaced_messages(ctx: DriftContext) -> list[str]:
    """
    Report each orchestrator-only file found in always-on steering.

    Args:
        ctx: Shared check context.

    Returns:
        Finding messages, empty when the steering layer is clean.
    """
    return [
        f".kiro/steering/{name} re-imposes orchestrator-only content on "
        "every agent — it belongs in .kiro/orchestration/"
        for name in ORCHESTRATION_FILES
        if (ctx.steering_dir / name).is_file()
    ]


def _unreferenced_messages(ctx: DriftContext) -> list[str]:
    """
    Report each orchestrator-only file the orchestrator no longer loads.

    The expected form is workspace-root-relative, which is how Kiro
    resolves a ``resources`` entry: the config-relative
    ``../orchestration/routing.md`` this once accepted resolved outside
    the repository, so the orchestrator declared the file and received
    nothing.

    Args:
        ctx: Shared check context.

    Returns:
        Finding messages, empty when both files are referenced.
    """
    orchestrator = ctx.orchestrator
    if orchestrator is None or orchestrator.data is None:
        return []
    resources = orchestrator.data.get("resources") or []
    declared = {
        resource.removeprefix(FILE_URI_PREFIX)
        for resource in resources
        if isinstance(resource, str)
    }
    return [
        f"orchestrator.json no longer references {ORCHESTRATION_PREFIX}{name} — "
        "the orchestrator loses it entirely, since it is not always-on"
        for name in ORCHESTRATION_FILES
        if f"{ORCHESTRATION_PREFIX}{name}" not in declared
    ]


def check_orchestration_reachability(ctx: DriftContext) -> list[Finding]:
    """
    Verify every .kiro/orchestration/ file can still be reached.

    A file in that directory arrives in a session one of two ways: an
    agent declares it in ``resources``, or an always-on file names it and
    sends a reader there on demand. A file doing neither is content
    nothing can arrive at, and no other check notices — the orphaned
    skill-reference check walks a skill's own ``references/`` directory
    and never looks here, so deleting a single pointer line silently
    strands a whole decision archive.

    ERROR rather than WARNING, matching the placement check beside it:
    both guard content whose loss is invisible at runtime, which is
    precisely what makes it a defect rather than a smell.

    Args:
        ctx: Shared check context.

    Returns:
        One ERROR per unreachable file, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    if ctx.orchestration_dir.is_dir():
        declared = _declared_resource_paths(ctx)
        corpus = _always_on_corpus(ctx, declared)
        for path in sorted(ctx.orchestration_dir.glob("*.md")):
            relative = path.relative_to(ctx.root).as_posix()
            if relative in declared or _is_named_in(corpus, path, relative):
                continue
            findings.append(
                Finding(
                    Severity.ERROR,
                    SECTION_ORCHESTRATION_REACHABILITY,
                    f"{relative} is in no agent's resources and named by no "
                    "always-on file — nothing can reach it",
                )
            )
    findings.append(
        Finding(
            Severity.OK,
            SECTION_ORCHESTRATION_REACHABILITY,
            "Orchestration file reachability checked",
        )
    )
    return findings


def _declared_resource_paths(ctx: DriftContext) -> set[str]:
    """
    Collect every workspace-relative file:// path the agents declare.

    Args:
        ctx: Shared check context.

    Returns:
        Root-relative POSIX paths, empty when nothing is declared.
    """
    declared: set[str] = set()
    for config in ctx.agent_configs:
        for target in _file_resource_targets(config):
            declared.update(_expand_target(ctx.root, target))
    return declared


def _file_resource_targets(config: AgentConfig) -> Iterator[str]:
    """
    Iterate the file:// resource targets of one agent config.

    Non-string entries (the knowledgeBase object form) carry no path, and
    skill:// entries name a skill rather than a plain file, so neither is
    yielded.

    Args:
        config: Parsed agent config.

    Yields:
        Each resource path with its ``file://`` prefix stripped.
    """
    resources = (config.data or {}).get("resources") or []
    if not isinstance(resources, list):
        return
    for resource in resources:
        if isinstance(resource, str) and resource.startswith(FILE_URI_PREFIX):
            yield resource.removeprefix(FILE_URI_PREFIX)


def _expand_target(root: Path, target: str) -> set[str]:
    """
    Resolve a resource target to the root-relative paths it names.

    A glob is expanded to the paths it actually matches, so a file
    covered by a wildcard counts as declared just as an explicit entry
    does.

    Args:
        root: Repository root the target resolves against.
        target: Resource path with its URI scheme stripped.

    Returns:
        Root-relative POSIX paths, empty when a glob matches nothing.
    """
    if not any(character in target for character in GLOB_CHARACTERS):
        return {target}
    return {match.relative_to(root).as_posix() for match in root.glob(target)}


def _always_on_corpus(ctx: DriftContext, declared: set[str]) -> list[tuple[Path, str]]:
    """
    Read every file whose text reaches a session unprompted.

    Two sources qualify: the ``.kiro/steering/`` files Kiro loads into
    every session, and any file an agent declares as a ``file://``
    resource, which that agent loads on every turn. A pointer sitting in
    either is followed by whoever is reading.

    Args:
        ctx: Shared check context.
        declared: Root-relative paths the agents declare as resources.

    Returns:
        One (path, text) pair per always-on file, deduplicated.
    """
    paths: list[Path] = sorted(ctx.steering_dir.glob("*.md"))
    seen = set(paths)
    for relative in sorted(declared):
        path = ctx.root / relative
        if path.is_file() and path not in seen:
            seen.add(path)
            paths.append(path)
    return [(path, read_text(path)) for path in paths]


def _is_named_in(corpus: list[tuple[Path, str]], target: Path, relative: str) -> bool:
    """
    Report whether any always-on file points at a target file.

    Both the root-relative path and the bare filename count, because a
    pointer written either way still sends a reader to the right file.
    The target never vouches for itself: a file naming its own path
    proves nothing about how anyone gets to it.

    Args:
        corpus: Always-on (path, text) pairs.
        target: File whose reachability is in question.
        relative: The target's root-relative POSIX path.

    Returns:
        True when at least one other always-on file names it.
    """
    return any(
        relative in text or target.name in text
        for path, text in corpus
        if path != target
    )
