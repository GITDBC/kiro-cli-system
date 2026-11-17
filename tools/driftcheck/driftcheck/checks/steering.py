"""
Checks over the always-on steering layer.

Covers steering files that reproduce a skill body, the
enumerated-heading convention COMMON.md forbids, and the two
arrangements that keep the orchestrator-only material honest: the
orchestrator prompt keeping its routing and delegation sections while
nothing orchestrator-only sits in always-on steering or in any
dispatcher's inherited resources, and every file in ``docs/`` remaining
reachable from somewhere.

The last two are shipped as separate checks, matching this codebase's
one-concern-per-check convention: orchestrator content drifting back
into steering and a document no session can arrive at are unrelated
failure modes with unrelated remedies.
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
SECTION_DOCS_REACHABILITY: Final[str] = "Docs file reachability"

# The orchestrator-only instruction files. Their content now lives in
# the orchestrator prompt, which only the orchestrator loads. They must
# not come back as separate files in .kiro/steering/, because Kiro CLI
# loads every steering file into every session, subagent sessions
# included, regardless of an agent's resources list: a probe measured
# their roughly 1,118 lines filling an estimated 70-75% of a
# specialist's context on every dispatch, for content no specialist acts
# on. They are also kept out of the orchestrator's own file:// resources,
# because a subagent that declares none inherits its parent's
# (custom-agents/configuration-reference.md, "File resources"): the same
# cost, paid on every dispatch. Neither half of the arrangement fails
# visibly at runtime — a file back in steering or in the dispatcher's
# resources silently re-imposes the cost — so both are asserted here.
ORCHESTRATION_FILES: Final[tuple[str, ...]] = (
    "routing.md",
    "delegation-lifecycle.md",
)

# The sections the orchestrator prompt must keep. A section dropped from
# the prompt silently leaves the orchestrator without its routing tables
# or delegation machinery, since nothing else carries them any more.
ORCHESTRATOR_SECTIONS: Final[tuple[str, ...]] = (
    "Routing",
    "Delegation",
    "Harness gates",
    "Conductor",
)

# Resource URI prefix an agent config uses.
FILE_URI_PREFIX: Final[str] = "file://"


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

    Three halves of one arrangement, so they are asserted together: the
    former orchestrator-only files must not sit in .kiro/steering/,
    where every agent would pay for them on every turn; no agent that
    dispatches subagents may declare a file:// resource, which every
    subagent without its own would inherit; and the orchestrator prompt
    must keep the sections that now carry that content.

    Args:
        ctx: Shared check context.

    Returns:
        One ERROR per misplaced or unreferenced file, plus a trailing OK.
    """
    findings: list[Finding] = [
        Finding(Severity.ERROR, SECTION_ORCHESTRATION_PLACEMENT, message)
        for message in (
            _misplaced_messages(ctx)
            + _missing_section_messages(ctx)
            + _inherited_resource_messages(ctx)
        )
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
        "every agent — it belongs in .kiro/prompts/orchestrator.md"
        for name in ORCHESTRATION_FILES
        if (ctx.steering_dir / name).is_file()
    ]


def _missing_section_messages(ctx: DriftContext) -> list[str]:
    """
    Report each required section the orchestrator prompt lacks.

    The prompt is the single source of the routing and delegation
    rules, so a missing section leaves the orchestrator without them.

    Args:
        ctx: Shared check context.

    Returns:
        Finding messages, empty when the prompt has every section.
    """
    text = _orchestrator_prompt_text(ctx)
    if text is None:
        return []
    headings = {
        line.removeprefix("## ").strip()
        for line in text.splitlines()
        if line.startswith("## ")
    }
    return [
        f"orchestrator prompt has no '## {name}' section — the orchestrator "
        "would run without it, since no other file carries that content"
        for name in ORCHESTRATOR_SECTIONS
        if name not in headings
    ]


def _orchestrator_prompt_text(ctx: DriftContext) -> str | None:
    """
    Read the orchestrator's prompt file.

    Args:
        ctx: Shared check context.

    Returns:
        The prompt text, or None when there is no orchestrator or the
        prompt is inline or missing, which other checks report.
    """
    orchestrator = ctx.orchestrator
    if orchestrator is None or orchestrator.data is None:
        return None
    prompt = orchestrator.data.get("prompt")
    if not isinstance(prompt, str) or not prompt.startswith(FILE_URI_PREFIX):
        return None
    path = orchestrator.path.parent / prompt.removeprefix(FILE_URI_PREFIX)
    if not path.is_file():
        return None
    return read_text(path)


def _inherited_resource_messages(ctx: DriftContext) -> list[str]:
    """
    Report file:// resources declared by an agent that dispatches subagents.

    A subagent that declares no file:// resource inherits its parent's,
    so every such resource of a dispatcher is loaded again into each
    dispatched session.

    Args:
        ctx: Shared check context.

    Returns:
        One message per offending dispatcher resource.
    """
    messages: list[str] = []
    for config in ctx.agent_configs:
        if not _dispatches_subagents(config):
            continue
        messages.extend(
            f"{config.path.name} declares file:// resource {target} — every "
            "subagent without its own file:// resources inherits it on each "
            "dispatch; read the file on demand instead"
            for target in _file_resource_targets(config)
        )
    return messages


def _dispatches_subagents(config: AgentConfig) -> bool:
    """
    Tell whether an agent lists spawnable subagents in its tools.

    Args:
        config: Parsed agent config.

    Returns:
        True when any ``tools`` entry is a ``subagent/<name>`` selector.
    """
    tools = (config.data or {}).get("tools")
    if not isinstance(tools, list):
        return False
    return any(isinstance(tool, str) and tool.startswith("subagent/") for tool in tools)


def check_docs_reachability(ctx: DriftContext) -> list[Finding]:
    """
    Verify every docs/ file can still be reached.

    A file in that directory arrives in a session one of two ways: an
    agent declares it in ``resources``, or a file the session already
    holds names it and sends a reader there on demand. Files read on
    demand pass the pointer on: a file named by a reachable docs file is
    reachable too. A file doing neither is content nothing can
    arrive at, and no other check notices — the orphaned skill-reference
    check walks a skill's own ``references/`` directory and never looks
    here, so deleting a single pointer line silently strands a whole
    decision archive.

    ERROR rather than WARNING, matching the placement check beside it:
    both guard content whose loss is invisible at runtime, which is
    precisely what makes it a defect rather than a smell.

    Args:
        ctx: Shared check context.

    Returns:
        One ERROR per unreachable file, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    if ctx.docs_dir.is_dir():
        reachable = _reachable_docs_files(ctx)
        for path in sorted(ctx.docs_dir.glob("*.md")):
            relative = path.relative_to(ctx.root).as_posix()
            if relative in reachable:
                continue
            findings.append(
                Finding(
                    Severity.ERROR,
                    SECTION_DOCS_REACHABILITY,
                    f"{relative} is in no agent's resources and named by no "
                    "reachable file — nothing can reach it",
                )
            )
    findings.append(
        Finding(
            Severity.OK,
            SECTION_DOCS_REACHABILITY,
            "Docs file reachability checked",
        )
    )
    return findings


def _reachable_docs_files(ctx: DriftContext) -> set[str]:
    """
    Compute the docs files a session can arrive at.

    Starts from the files that reach a session unprompted and follows
    every pointer to a docs file, including pointers written inside the
    docs files reached on the way.

    Args:
        ctx: Shared check context.

    Returns:
        Root-relative POSIX paths of the reachable docs files.
    """
    declared = _declared_resource_paths(ctx)
    texts = [text for _, text in _always_on_corpus(ctx, declared)]
    files = {
        path.relative_to(ctx.root).as_posix(): path
        for path in ctx.docs_dir.glob("*.md")
    }
    found = {relative for relative in files if relative in declared}
    found |= _named_among(texts, files, set())
    reachable: set[str] = set()
    while found:
        reachable |= found
        texts.extend(read_text(files[relative]) for relative in found)
        found = _named_among(texts, files, reachable)
    return reachable


def _named_among(
    texts: list[str], files: dict[str, Path], reached: set[str]
) -> set[str]:
    """
    Pick the not-yet-reached files that some text names.

    Args:
        texts: Texts of the files already reached.
        files: Every docs file, keyed by root-relative path.
        reached: Root-relative paths already known reachable.

    Returns:
        The newly named root-relative paths.
    """
    return {
        relative
        for relative, path in files.items()
        if relative not in reached and _is_named(texts, relative, path.name)
    }


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

    Three sources qualify: the ``.kiro/steering/`` files Kiro loads into
    every session, the agent prompts, which their agent receives on
    every turn, and any file an agent declares as a ``file://``
    resource. A pointer sitting in any of them is followed by whoever is
    reading.

    Args:
        ctx: Shared check context.
        declared: Root-relative paths the agents declare as resources.

    Returns:
        One (path, text) pair per always-on file, deduplicated.
    """
    paths: list[Path] = sorted(ctx.steering_dir.glob("*.md"))
    if ctx.prompts_dir.is_dir():
        paths.extend(sorted(ctx.prompts_dir.glob("*.md")))
    seen = set(paths)
    for relative in sorted(declared):
        path = ctx.root / relative
        if path.is_file() and path not in seen:
            seen.add(path)
            paths.append(path)
    return [(path, read_text(path)) for path in paths]


def _is_named(texts: list[str], relative: str, name: str) -> bool:
    """
    Report whether any text points at a target file.

    Both the root-relative path and the bare filename count, because a
    pointer written either way still sends a reader to the right file.
    A file never vouches for itself: the caller only offers the texts of
    files already reached, and the target is not among them.

    Args:
        texts: Texts of the files already reached.
        relative: The target's root-relative POSIX path.
        name: The target's bare filename.

    Returns:
        True when at least one text names the target.
    """
    return any(relative in text or name in text for text in texts)
