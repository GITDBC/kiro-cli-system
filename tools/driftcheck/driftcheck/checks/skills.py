"""
Checks over the skill tree.

Covers collaboration-pattern coverage in routing.md, the wiring of those
patterns into the agents' own resources, reference files no SKILL.md can
reach, reference files named after an agent that no longer exists, and
prose mentions of a skill that no longer exists.
"""

# Standard libraries
import re
from collections.abc import Iterator
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Final

# Own modules
from driftcheck.checks.agents import SKILL_URI_PREFIX
from driftcheck.paths import VENDORED_SKILL, contains_word, read_text
from driftcheck.types import AgentConfig, DriftContext, Finding, Severity

# Direct-invoke skills that do not need a collaboration pattern because
# they are invoked on their own rather than as a workflow stage.
DIRECT_INVOKE_SKILLS: Final[frozenset[str]] = frozenset(
    {
        "code-standards",
        "commit-message",
        "concise-communication",
        "mermaid-diagrams",
        "data-to-md",
        "jira-fetcher",
        "kiro-cli-reference",
        "claude-prompting-reference",
        "exploratory-data-analysis",
        "statistical-analysis",
        "unit-test-generation",
    }
)

# Skills a pattern row may name next to an agent without that agent
# needing to declare them. The criterion is that the skill body is
# exclusively meta-content — topology, sequencing, invocation mechanics —
# with nothing addressed to the specialist that executes the work, so
# loading it into the specialist's context would buy nothing. ralph-loop
# drives a standalone shell process and commit-message documents a
# convention the orchestrator applies itself.
ORCHESTRATOR_ONLY_SKILLS: Final[frozenset[str]] = frozenset(
    {
        "ralph-loop",
        "commit-message",
    }
)

# Role suffixes that make a "<role>-patterns.md" filename look like it is
# named after an agent rather than after its content.
ROLE_SUFFIXES: Final[tuple[str, ...]] = (
    "engineer",
    "developer",
    "architect",
    "analyst",
    "writer",
    "reviewer",
    "manager",
    "automator",
    "analyzer",
    "evaluator",
    "orchestrator",
)
PATTERNS_FILE: Final[re.Pattern[str]] = re.compile(r"(?P<role>.+)-patterns\.md")

# Any markdown heading, and the Collaboration Patterns heading whose
# section holds the pattern table.
MARKDOWN_HEADING: Final[re.Pattern[str]] = re.compile(r"^(#{1,6}) ")
COLLABORATION_HEADING: Final[re.Pattern[str]] = re.compile(
    r"^(#{1,6}) .*Collaboration Patterns", re.IGNORECASE
)

# A table row made only of dashes, colons and pipes: the header rule,
# which carries no data.
TABLE_SEPARATOR: Final[re.Pattern[str]] = re.compile(r"^\|[\s:|-]*\|$")

SECTION_SKILL_ROUTING: Final[str] = "Skill routing coverage"
SECTION_PATTERN_WIRING: Final[str] = "Pattern-to-resources wiring"
SECTION_ORPHAN_REFS: Final[str] = "Orphaned skill reference files"
SECTION_STALE_REFS: Final[str] = "Stale agent-named reference files"
SECTION_STALE_SKILL_MENTIONS: Final[str] = "Stale skill-name mentions"

# A hyphenated slug: two or more lowercase-alphanumeric segments joined
# by hyphens. Single-word names such as "debugging" are deliberately
# excluded — they are indistinguishable from ordinary prose without the
# hyphen, and every retired skill this check has to catch so far
# (lint-validate, tool-evaluator, jira-safety, dynamic-orchestration) is
# multi-segment.
SLUG: Final[str] = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+"

# A slug used as a skill reference. Conservative by construction, mirror
# of the phrasing that recurs across every SKILL.md negative-boundary
# sentence and steering routing note:
#   - `<slug>` skill / `<slug>` skill)   -> backtick-quoted, "skill" after
#   - use <slug> skill                  -> bare, "use ... skill"
#   - (use <slug>) / (use `<slug>`)      -> parenthetical "use" cross-ref
# A slug is a *candidate* only inside one of these three shapes; it is
# reported only when it additionally fails to resolve to a skill
# directory or a current agent slug, so a token such as "use case" never
# reaches the resolution step at all because it never matches SLUG.
SKILL_MENTION: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(rf"`(?P<slug>{SLUG})`\s+skill\b"),
    re.compile(rf"\buse\s+(?P<slug>{SLUG})\s+skill\b"),
    re.compile(rf"\(use\s+`?(?P<slug>{SLUG})`?\)"),
)


def check_skill_routing(ctx: DriftContext) -> list[Finding]:
    """
    Verify each skill has a collaboration pattern in routing.md.

    Both the YAML form (``skill: name``) and the table form
    (``| name |``) count as coverage. Direct-invoke utility skills are
    exempt, and that exemption list is itself validated: an entry naming
    a deleted skill is dead configuration that would mask a future gap.

    Args:
        ctx: Shared check context.

    Returns:
        A warning per uncovered skill, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    routing_md = read_text(ctx.routing_md)
    for skill_dir in ctx.skill_dirs():
        skill_name = skill_dir.name
        if skill_name in DIRECT_INVOKE_SKILLS:
            continue
        escaped = re.escape(skill_name)
        pattern = rf"(skill: {escaped}|\|[ \t]*{escaped}[ \t]*\|)"
        if re.search(pattern, routing_md) is None:
            findings.append(
                Finding(
                    Severity.WARNING,
                    SECTION_SKILL_ROUTING,
                    f"Skill '{skill_name}' has no collaboration pattern in routing.md",
                )
            )
    findings.extend(
        stale_allowlist_findings(
            ctx, SECTION_SKILL_ROUTING, "DIRECT_INVOKE_SKILLS", DIRECT_INVOKE_SKILLS
        )
    )
    findings.append(
        Finding(Severity.OK, SECTION_SKILL_ROUTING, "Skill routing checked")
    )
    return findings


def check_pattern_resource_wiring(ctx: DriftContext) -> list[Finding]:
    """
    Verify pattern-named skills are wired into the agents' resources.

    A custom agent loads no skill unless its config declares it, so a
    Collaboration Patterns row that pairs a skill with an agent whose
    resources omit it documents a capability the agent cannot reach.
    That is an ERROR: the workflow is published but silently disabled.

    Parsing assumption, deliberately conservative to avoid false
    accusations: only rows of a markdown table inside the routing.md
    "Collaboration Patterns" section are considered, a row contributes a
    skill only when one of its cells is *exactly* the name of an existing
    skill directory, and it contributes an agent only when a current
    agent slug appears in the row as a whole word. Rows whose skill cell
    is prose ("— (pattern only, no skill)") therefore claim nothing, and
    a skill named only inside a longer sentence is ignored.

    Known asymmetry, intentionally not closed: this check only verifies
    that every agent NAMED in a pattern row declares the skill in its
    resources; it never checks the converse, i.e. it does not flag an
    agent that declares a skill while appearing in no pattern row
    alongside it (or in no pattern row at all). That gap let the
    Debugging pattern row list only senior-developer while
    qa-engineer.json legitimately also declares `debugging` for its own
    test-failure-analysis trigger, with nothing raising a warning. This
    is deliberate rather than an oversight: several skills (notably
    code-standards, declared by eleven agents, plus
    concise-communication and mermaid-diagrams) are legitimately
    cross-cutting and declared by many agents while being named in no
    pattern row at all, so a converse check would need an allowlist of
    such cross-cutting skills to avoid flagging all of them as errors.
    Building that allowlist is a design change beyond the scope of a
    single wiring check and should not be added incidentally.

    Args:
        ctx: Shared check context.

    Returns:
        An error per unwired pair, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    skills = {skill_dir.name for skill_dir in ctx.skill_dirs()}
    configs = {config.stem: config for config in ctx.agent_configs}
    pairs = _pattern_pairs(read_text(ctx.routing_md), skills, sorted(configs))
    for skill, slug in pairs:
        if skill in ORCHESTRATOR_ONLY_SKILLS:
            continue
        if declares_skill(configs[slug], skill):
            continue
        findings.append(
            Finding(
                Severity.ERROR,
                SECTION_PATTERN_WIRING,
                f"routing.md pairs skill '{skill}' with agent '{slug}' but "
                f"{slug}.json does not declare it in resources — a custom "
                "agent cannot discover a skill it is not given",
            )
        )
    findings.extend(
        stale_allowlist_findings(
            ctx,
            SECTION_PATTERN_WIRING,
            "ORCHESTRATOR_ONLY_SKILLS",
            ORCHESTRATOR_ONLY_SKILLS,
        )
    )
    findings.append(
        Finding(
            Severity.OK, SECTION_PATTERN_WIRING, "Pattern-to-resources wiring checked"
        )
    )
    return findings


def stale_allowlist_findings(
    ctx: DriftContext, section: str, label: str, entries: frozenset[str]
) -> list[Finding]:
    """
    Flag allowlist entries that name no existing skill directory.

    An exemption for a deleted skill is silent staleness: it never fires
    again, and it will wrongly exempt a future skill that reuses the
    name.

    Args:
        ctx: Shared check context.
        section: Section the findings belong to.
        label: Name of the allowlist, for the message.
        entries: Skill names the allowlist exempts.

    Returns:
        A warning per entry with no matching skill directory.
    """
    return [
        Finding(
            Severity.WARNING,
            section,
            f"{label} exempts '{skill}' but .kiro/skills/{skill}/ does not "
            "exist — stale allowlist entry",
        )
        for skill in sorted(entries)
        if not (ctx.skills_dir / skill).is_dir()
    ]


def declares_skill(config: AgentConfig, skill: str) -> bool:
    """
    Report whether a config declares a skill in its resources.

    Accepts the literal path form, the bare-name form and any glob that
    matches the skill's SKILL.md, so an agent loading
    ``skill://.kiro/skills/*/SKILL.md`` counts as declaring every skill.

    Args:
        config: Parsed agent config.
        skill: Skill directory name.

    Returns:
        True when a skill:// resource of the config covers the skill.
    """
    data = config.data or {}
    resources = data.get("resources") or []
    if not isinstance(resources, list):
        return False
    candidates = (f".kiro/skills/{skill}/SKILL.md", f".kiro/skills/{skill}")
    for resource in resources:
        if not isinstance(resource, str) or not resource.startswith(SKILL_URI_PREFIX):
            continue
        target = resource.removeprefix(SKILL_URI_PREFIX).lstrip("~").lstrip("/")
        if target == skill:
            return True
        if any(fnmatchcase(candidate, target) for candidate in candidates):
            return True
    return False


def _pattern_pairs(
    routing_md: str, skills: set[str], slugs: list[str]
) -> Iterator[tuple[str, str]]:
    """
    Iterate the (skill, agent) pairs the pattern table claims.

    Args:
        routing_md: Full routing.md text.
        skills: Names of the existing skill directories.
        slugs: Slugs of the current agent configs.

    Yields:
        One pair per skill and agent named in the same row.
    """
    for cells in _collaboration_rows(routing_md):
        yield from _row_pairs(cells, skills, slugs)


def _row_pairs(
    cells: list[str], skills: set[str], slugs: list[str]
) -> Iterator[tuple[str, str]]:
    """
    Pair the skills and agents named in one table row.

    Args:
        cells: Stripped cells of the row.
        skills: Names of the existing skill directories.
        slugs: Slugs of the current agent configs.

    Yields:
        Every combination of a skill cell and an agent named in the row.
    """
    row = " ".join(cells)
    named_skills = [cell for cell in cells if cell in skills]
    named_agents = [slug for slug in slugs if contains_word(row, slug)]
    for skill in named_skills:
        for slug in named_agents:
            yield skill, slug


def _collaboration_rows(routing_md: str) -> Iterator[list[str]]:
    """
    Iterate the table rows of the Collaboration Patterns section.

    Args:
        routing_md: Full routing.md text.

    Yields:
        The stripped cells of each data row, header rule excluded.
    """
    for line in _collaboration_section(routing_md):
        stripped = line.strip()
        if not stripped.startswith("|") or TABLE_SEPARATOR.match(stripped):
            continue
        yield [cell.strip() for cell in stripped.strip("|").split("|")]


def _collaboration_section(routing_md: str) -> Iterator[str]:
    """
    Iterate the lines under the Collaboration Patterns heading.

    The section ends at the next heading of the same or a higher level,
    so nested subsections such as "### Pattern details" stay inside it.

    Args:
        routing_md: Full routing.md text.

    Yields:
        Each line of the section, headings excluded.
    """
    level = 0
    for line in routing_md.splitlines():
        heading = MARKDOWN_HEADING.match(line)
        if heading is None:
            if level:
                yield line
            continue
        if level and len(heading.group(1)) <= level:
            return
        opening = COLLABORATION_HEADING.match(line)
        if opening is not None:
            level = len(opening.group(1))


def check_orphaned_skill_references(ctx: DriftContext) -> list[Finding]:
    """
    Detect reference files no sibling SKILL.md mentions.

    Kiro loads references/*.md only when a SKILL.md directs it to, so an
    unmentioned reference file is unreachable. The vendored
    kiro-cli-reference mirror is excluded: it is indexed differently and
    its pages are not cited individually.

    Args:
        ctx: Shared check context.

    Returns:
        A warning per unreachable file, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    for skill_dir in ctx.skill_dirs():
        if skill_dir.name == VENDORED_SKILL:
            continue
        ref_dir = skill_dir / "references"
        skill_md = skill_dir / "SKILL.md"
        if not ref_dir.is_dir() or not skill_md.is_file():
            continue
        skill_text = read_text(skill_md)
        for ref_file in sorted(ref_dir.rglob("*.md")):
            if not ref_file.is_file():
                continue
            if ref_file.name not in skill_text:
                findings.append(
                    Finding(
                        Severity.WARNING,
                        SECTION_ORPHAN_REFS,
                        f"Reference file 'skills/{skill_dir.name}/references/"
                        f"{ref_file.name}' not mentioned in sibling SKILL.md "
                        "— unreachable",
                    )
                )
    findings.append(
        Finding(
            Severity.OK, SECTION_ORPHAN_REFS, "Orphaned skill reference files checked"
        )
    )
    return findings


def check_stale_agent_references(ctx: DriftContext) -> list[Finding]:
    """
    Flag "<role>-patterns.md" files naming a retired agent.

    Deliberately conservative: only filenames whose role segment looks
    like an agent role AND matches no current agent name are flagged.
    Content-based filenames do not rot when the roster changes, so a
    stale file named after content slips past by design.

    Args:
        ctx: Shared check context.

    Returns:
        A warning per stale file, plus a trailing OK finding.

    Raises:
        ValueError: If the agent roster cannot be determined.
    """
    findings: list[Finding] = []
    roster = current_agent_names(ctx.agent_configs)
    for path in sorted(ctx.skills_dir.glob("*/references/*.md")):
        match = PATTERNS_FILE.fullmatch(path.name)
        if match is None:
            continue
        role = match.group("role")
        looks_like_an_agent = "-" in role and role.endswith(ROLE_SUFFIXES)
        if looks_like_an_agent and role not in roster:
            findings.append(
                Finding(
                    Severity.WARNING,
                    SECTION_STALE_REFS,
                    "Reference named after a non-existent agent: "
                    f"{path.relative_to(ctx.root)} (no agent named '{role}')",
                )
            )
    findings.append(
        Finding(
            Severity.OK,
            SECTION_STALE_REFS,
            "Stale agent-named reference files checked",
        )
    )
    return findings


def current_agent_names(configs: tuple[AgentConfig, ...]) -> set[str]:
    """
    Collect the names of every agent currently in the roster.

    Args:
        configs: Parsed agent configs.

    Returns:
        Declared agent names.

    Raises:
        ValueError: If any config cannot be parsed or has no name, since
            an incomplete roster would produce false accusations of
            staleness.
    """
    names: set[str] = set()
    for config in configs:
        name = config.name
        if name is None:
            message = (
                f"cannot determine the current agent roster: "
                f"{config.path.name} is not valid JSON or has no 'name' field"
            )
            raise ValueError(message)
        names.add(name)
    return names


def check_stale_skill_mentions(ctx: DriftContext) -> list[Finding]:
    """
    Flag prose mentions of a skill that no longer exists.

    A skill's frontmatter ``description`` is a routing surface: it is
    what the model matches against when deciding which skill to
    activate, so a mention of a deleted skill there silently advertises
    a route to a capability that cannot be reached. Steering files carry
    the same risk in their routing prose. Neither surface is an entry in
    an agent config's ``resources`` array, so no other check reaches
    them.

    Parsing assumption, deliberately conservative to avoid false
    accusations, mirroring ``check_pattern_resource_wiring``: a slug is
    a candidate only inside one of the three ``SKILL_MENTION`` shapes
    (backtick-quoted followed by "skill", bare "use ... skill", or a
    parenthetical "(use ...)" cross-reference), and it is reported only
    when it then resolves to neither an existing skill directory nor a
    current agent slug. A hyphenated slug that never named a skill or an
    agent, and that appears outside those three shapes, is never
    reported — the check prefers under-claiming to false positives.

    Args:
        ctx: Shared check context.

    Returns:
        A warning per unresolved mention, plus a trailing OK finding.

    Raises:
        ValueError: If the agent roster cannot be determined.
    """
    findings: list[Finding] = []
    skills = {skill_dir.name for skill_dir in ctx.skill_dirs()}
    agents = current_agent_names(ctx.agent_configs)
    known = skills | agents
    for path in _mentionable_files(ctx):
        relative = path.relative_to(ctx.root)
        for number, line in enumerate(read_text(path).splitlines(), start=1):
            for slug in _mentioned_slugs(line):
                if slug in known:
                    continue
                findings.append(
                    Finding(
                        Severity.ERROR,
                        SECTION_STALE_SKILL_MENTIONS,
                        f"{relative}:{number} references skill '{slug}', "
                        "which does not exist — a description or steering "
                        "note routes to a capability that cannot be reached",
                    )
                )
    findings.append(
        Finding(
            Severity.OK,
            SECTION_STALE_SKILL_MENTIONS,
            "Stale skill-name mentions checked",
        )
    )
    return findings


def _mentionable_files(ctx: DriftContext) -> Iterator[Path]:
    """
    Iterate the files whose prose can carry a skill-name mention.

    Every skill's SKILL.md (frontmatter and body alike, since the
    negative-boundary sentences that name other skills are almost always
    in the body) plus every always-on steering file and every
    orchestrator-only file under .kiro/orchestration/. The latter matter
    most of the three: routing.md names every skill in its Collaboration
    Patterns table, so a deleted skill leaves a stale mention there
    first. The vendored kiro-cli-reference mirror is excluded, matching
    the other prose-scanning checks in this module.

    Args:
        ctx: Shared check context.

    Yields:
        Each candidate file, in a stable order.
    """
    for skill_dir in ctx.skill_dirs():
        if skill_dir.name == VENDORED_SKILL:
            continue
        skill_md = skill_dir / "SKILL.md"
        if skill_md.is_file():
            yield skill_md
    for directory in (ctx.steering_dir, ctx.orchestration_dir):
        if directory.is_dir():
            yield from sorted(directory.glob("*.md"))


def _mentioned_slugs(line: str) -> Iterator[str]:
    """
    Extract the skill-reference candidates named on one line.

    Args:
        line: Single line of prose.

    Yields:
        The slug captured by each matching ``SKILL_MENTION`` pattern.
    """
    for pattern in SKILL_MENTION:
        for match in pattern.finditer(line):
            yield match.group("slug")
