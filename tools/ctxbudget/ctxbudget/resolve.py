"""
Resolution of declared agent resources into a concrete artifact set.

Turns an agent config's ``prompt``, ``file://`` resources, ``skill://``
resources and ``knowledgeBase`` entries into the deduplicated list of
artifacts that reaches a session, and locates the repository root and
the skill and steering directories the model needs.

TWO RESOLUTION BASES, AND THEY ARE NOT THE SAME. Kiro CLI resolves a
``resources`` entry — ``file://`` or ``skill://`` — against the
**workspace root**, and the ``prompt`` field against the **agent config
file's own directory**. The asymmetry is documented, not inferred:
``custom-agents/configuration-reference.md`` states the prompt rule
verbatim under "File URI path resolution", and every ``resources``
example in the same file and in ``chat/context.md`` is workspace-root
relative (``file://README.md``, ``file://.kiro/steering/**/*.md``).
Resolving a ``resources`` entry config-relative here once made the
model count 16,803 tokens of files that reached no session: the
config-relative form ``file://../orchestration/routing.md`` happens to
name a real file when based on ``.kiro/agents/``, so it measured as a
cost while Kiro was resolving it outside the repository and loading
nothing.

DELIBERATE DUPLICATION. The ``file://`` and ``skill://`` glob-resolution
logic here restates ``driftcheck/checks/agents.py``
(``missing_resources``, ``_skill_uri_resolves``). ``TOOLS_OVERVIEW.md``
states that tools share no runtime Python, so the copy is the price of
that boundary rather than an oversight. The consequence is real and is
recorded here so it is not discovered by surprise: the two copies can
now disagree about glob semantics — which wildcards are recognised, how
a home-directory or bare-name ``skill://`` target is treated, and
whether a glob matching nothing is an error. ``driftcheck`` owns the
pass/fail verdict on resolution; this module only needs a set of paths
to count, so it degrades to "counts nothing" where the other errors.
"""

# Standard libraries
import json
import logging
from pathlib import Path
from typing import Any, Final

# 3pps
import yaml

# Own modules
from ctxbudget.types import (
    AgentConfig,
    ArtifactKind,
    ResolvedAgent,
    ResolvedEntry,
)

logger = logging.getLogger(__name__)

FILE_URI_PREFIX: Final[str] = "file://"
SKILL_URI_PREFIX: Final[str] = "skill://"

# Characters making a resource target a glob rather than a literal path.
GLOB_CHARACTERS: Final[str] = "*?["

# Directories that together identify the repository root; either alone
# is too common to be conclusive. Mirrors driftcheck's marker pair.
ROOT_MARKERS: Final[tuple[str, ...]] = (".kiro", "tools")

FRONTMATTER_FENCE: Final[str] = "---"

# Frontmatter fields Kiro injects at startup for every available skill.
# Anything else in the block (author metadata, colours) is not part of
# the startup cost and is excluded from the skill_fm figure.
FRONTMATTER_FIELDS: Final[tuple[str, ...]] = ("name", "description")

# Suffix marking the synthetic label of a knowledge-base entry, which
# has no file of its own: the cost is the name and description text
# Kiro injects so the model knows the base is searchable.
KB_LABEL_PREFIX: Final[str] = "knowledgeBase://"

# Suffix appended to a skill's SKILL.md label for the frontmatter-only
# artifact, so the per-file table never charges an agent the whole body
# for what is a name-and-description injection.
FRONTMATTER_SUFFIX: Final[str] = "#frontmatter"


def is_repo_root(path: Path) -> bool:
    """
    Report whether a directory looks like the repository root.

    Args:
        path: Candidate directory.

    Returns:
        True when every root marker exists inside the directory.
    """
    return all((path / marker).is_dir() for marker in ROOT_MARKERS)


def find_repo_root(start: Path | None = None) -> Path:
    """
    Locate the repository root by walking upward from a starting point.

    Marker-based rather than a fixed parent count, for the same reason
    ``driftcheck`` is: the package is installed under ``tools/``, so a
    depth count breaks silently whenever a module moves. When the
    default origin yields nothing — a non-editable install, where the
    package lives inside a virtualenv — the search retries from the
    working directory.

    Args:
        start: Path to walk up from. Defaults to this module's file.

    Returns:
        Absolute path to the repository root.

    Raises:
        ValueError: If no ancestor holds the marker directories.
    """
    origins: list[Path] = [(start or Path(__file__)).resolve()]
    if start is None:
        origins.append(Path.cwd().resolve())
    for origin in origins:
        for candidate in (origin, *origin.parents):
            if is_repo_root(candidate):
                return candidate
    markers = ", ".join(f"{marker}/" for marker in ROOT_MARKERS)
    searched = ", ".join(str(origin) for origin in origins)
    message = (
        f"cannot locate the repository root: no ancestor of {searched} "
        f"contains all of {markers}. Pass --root explicitly."
    )
    raise ValueError(message)


def load_agent_configs(root: Path) -> tuple[AgentConfig, ...]:
    """
    Parse every agent config under ``.kiro/agents/``.

    An unparseable config is logged and skipped instead of failing the
    run: ``driftcheck`` owns the verdict on malformed JSON, and a
    measurement tool that refuses to measure the other nine agents
    because one file is broken helps nobody.

    Args:
        root: Repository root.

    Returns:
        Configs sorted by path.
    """
    configs: list[AgentConfig] = []
    agents_dir = root / ".kiro" / "agents"
    if not agents_dir.is_dir():
        logger.warning("No agent directory at %s.", agents_dir)
        return ()
    for path in sorted(agents_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            logger.warning("Skipping %s: %s.", path.name, error)
            continue
        if not isinstance(data, dict):
            logger.warning("Skipping %s: top level is not an object.", path.name)
            continue
        configs.append(AgentConfig(path=path, data=data))
    return tuple(configs)


def steering_files(root: Path) -> tuple[Path, ...]:
    """
    List the always-on steering files, sorted by name.

    Args:
        root: Repository root.

    Returns:
        Every ``.kiro/steering/*.md`` path.
    """
    steering_dir = root / ".kiro" / "steering"
    if not steering_dir.is_dir():
        return ()
    return tuple(sorted(steering_dir.glob("*.md")))


def skill_dirs(root: Path) -> tuple[Path, ...]:
    """
    List the skill directories holding a SKILL.md, sorted by name.

    Args:
        root: Repository root.

    Returns:
        Every ``.kiro/skills/<name>/`` directory with a SKILL.md.
    """
    skills_dir = root / ".kiro" / "skills"
    if not skills_dir.is_dir():
        return ()
    return tuple(
        sorted(
            path
            for path in skills_dir.iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        )
    )


def reference_files(skill_dir: Path) -> tuple[Path, ...]:
    """
    List every reference file of one skill, sorted by path.

    Args:
        skill_dir: Skill directory.

    Returns:
        Every file under ``references/``, recursively.
    """
    references = skill_dir / "references"
    if not references.is_dir():
        return ()
    return tuple(sorted(path for path in references.rglob("*") if path.is_file()))


def relative_label(path: Path, root: Path) -> str:
    """
    Render a path as a stable repository-relative label.

    Args:
        path: Path to label.
        root: Repository root.

    Returns:
        POSIX-style relative path, or the absolute path when the target
        lies outside the tree.
    """
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def split_frontmatter(text: str) -> tuple[str, str]:
    """
    Split a Markdown document into its frontmatter block and body.

    Args:
        text: Full file contents.

    Returns:
        The frontmatter block without its fences, and the body. The
        frontmatter is empty when the document does not open with one.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_FENCE:
        return "", text
    for index in range(1, len(lines)):
        if lines[index].strip() == FRONTMATTER_FENCE:
            front = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            return front, body.lstrip("\n")
    return "", text


def frontmatter_summary(text: str) -> str:
    """
    Extract the name and description Kiro injects for a skill.

    Falls back to the raw frontmatter block when the block is not valid
    YAML or carries neither field, since counting nothing would
    understate a cost that is demonstrably paid.

    Args:
        text: Full SKILL.md contents.

    Returns:
        The text whose token count is the startup cost of the skill.
    """
    front, _ = split_frontmatter(text)
    if not front:
        return ""
    try:
        data = yaml.safe_load(front)
    except yaml.YAMLError as error:
        logger.warning("Frontmatter is not valid YAML, counting it raw: %s.", error)
        return front
    if not isinstance(data, dict):
        return front
    parts = [
        str(data[field]).strip()
        for field in FRONTMATTER_FIELDS
        if isinstance(data.get(field), str)
    ]
    return "\n".join(parts) if parts else front


def _expand(base: Path, target: str) -> list[Path]:
    """
    Expand one resource target against a base directory.

    Args:
        base: Directory the target is relative to.
        target: Relative path, possibly a glob.

    Returns:
        Matching files, sorted. Empty when nothing matches.
    """
    if any(character in target for character in GLOB_CHARACTERS):
        return sorted(path for path in base.glob(target) if path.is_file())
    candidate = base / target
    return [candidate] if candidate.is_file() else []


def _prompt_entries(config: AgentConfig, root: Path) -> tuple[list[ResolvedEntry], str]:
    """
    Resolve an agent's ``prompt`` field, relative to the config file.

    The only place a config-relative base is correct: Kiro documents the
    ``prompt`` field's ``file://`` form as resolved against the agent
    configuration file's directory, unlike a ``resources`` entry.

    Args:
        config: Parsed agent config.
        root: Repository root.

    Returns:
        The prompt entries and the offending declaration when it
        resolved to nothing (empty string otherwise).
    """
    prompt = config.data.get("prompt")
    if not isinstance(prompt, str) or not prompt:
        return [], ""
    target = prompt.removeprefix(FILE_URI_PREFIX)
    paths = _expand(config.path.parent, target)
    if not paths:
        return [], prompt
    return [
        ResolvedEntry(
            kind=ArtifactKind.PROMPT,
            label=relative_label(path, root),
            path=path,
            text=None,
        )
        for path in paths
    ], ""


def _file_entries(root: Path, uri: str) -> list[ResolvedEntry]:
    """
    Resolve one ``file://`` resource against the workspace root.

    Args:
        root: Repository root, which the URI is relative to and which
            labels are rendered against.
        uri: The declared resource string.

    Returns:
        One entry per matching file.
    """
    target = uri.removeprefix(FILE_URI_PREFIX)
    return [
        ResolvedEntry(
            kind=ArtifactKind.FILE,
            label=relative_label(path, root),
            path=path,
            text=None,
        )
        for path in _expand(root, target)
    ]


def _skill_entries(root: Path, uri: str) -> list[ResolvedEntry]:
    """
    Resolve one ``skill://`` resource to frontmatter-only entries.

    A ``skill://`` resource makes a skill available; only its name and
    description are injected at startup, so the artifact counted here is
    the frontmatter rather than the file. Home-directory and bare-name
    forms are not paths into this tree and are skipped — flagging them
    would be a guess, and it is ``driftcheck`` that owns such verdicts.

    Args:
        root: Repository root.
        uri: The declared resource string.

    Returns:
        One entry per matching SKILL.md.
    """
    target = uri.removeprefix(SKILL_URI_PREFIX)
    if target.startswith("~") or "/" not in target:
        logger.info("Skipping non-path skill resource %s.", uri)
        return []
    entries: list[ResolvedEntry] = []
    for path in _expand(root, target):
        text = path.read_text(encoding="utf-8", errors="replace")
        entries.append(
            ResolvedEntry(
                kind=ArtifactKind.SKILL_FRONTMATTER,
                label=f"{relative_label(path, root)}{FRONTMATTER_SUFFIX}",
                path=path,
                text=frontmatter_summary(text),
            )
        )
    return entries


def _knowledge_base_entry(resource: dict[str, Any]) -> ResolvedEntry | None:
    """
    Resolve a ``knowledgeBase`` resource to its metadata cost.

    A knowledge base is searched on demand, so the always-on cost is the
    name and description Kiro injects to advertise it, not the indexed
    corpus.

    Args:
        resource: The declared resource object.

    Returns:
        The metadata entry, or None when the object is not a knowledge
        base or carries no name.
    """
    if resource.get("type") != "knowledgeBase":
        return None
    name = resource.get("name")
    if not isinstance(name, str) or not name:
        return None
    description = resource.get("description")
    text = name if not isinstance(description, str) else f"{name}\n{description}"
    return ResolvedEntry(
        kind=ArtifactKind.KNOWLEDGE_BASE,
        label=f"{KB_LABEL_PREFIX}{name}",
        path=None,
        text=text,
    )


def _steering_entries(root: Path, declared: frozenset[str]) -> list[ResolvedEntry]:
    """
    Add the steering files the workspace injects into every session.

    Steering reaches an agent by workspace auto-load, not by
    declaration: every ``.kiro/steering/*.md`` file is injected into
    every session, subagent sessions included, whatever ``resources``
    says. A file that is also declared is charged once, on the
    assumption that Kiro does not inject the same path twice; no agent
    in this repository declares one, so the branch is defensive.

    Args:
        root: Repository root.
        declared: Labels already resolved from ``resources``.

    Returns:
        The auto-injected steering entries.
    """
    return [
        ResolvedEntry(
            kind=ArtifactKind.STEERING_AUTO,
            label=relative_label(path, root),
            path=path,
            text=None,
        )
        for path in steering_files(root)
        if relative_label(path, root) not in declared
    ]


def _resource_entries(
    config: AgentConfig, root: Path
) -> tuple[list[ResolvedEntry], list[str]]:
    """
    Resolve every entry of an agent's ``resources`` array.

    Args:
        config: Parsed agent config.
        root: Repository root.

    Returns:
        The resolved entries and the declarations that matched nothing.
    """
    resources = config.data.get("resources")
    if not isinstance(resources, list):
        return [], []
    entries: list[ResolvedEntry] = []
    unresolved: list[str] = []
    for resource in resources:
        if isinstance(resource, dict):
            entry = _knowledge_base_entry(resource)
            if entry is not None:
                entries.append(entry)
            continue
        if not isinstance(resource, str):
            continue
        if resource.startswith(SKILL_URI_PREFIX):
            resolved = _skill_entries(root, resource)
        else:
            resolved = _file_entries(root, resource)
        if not resolved:
            unresolved.append(resource)
        entries.extend(resolved)
    return entries, unresolved


def _dedupe(entries: list[ResolvedEntry]) -> tuple[ResolvedEntry, ...]:
    """
    Drop repeated artifacts, preserving declaration order.

    The key is (kind, label) rather than label alone, so a file that is
    both declared and auto-injected keeps whichever entry survives the
    steering dedupe without the two kinds colliding.

    Args:
        entries: Resolved entries in declaration order.

    Returns:
        The entries with duplicates removed.
    """
    seen: set[tuple[ArtifactKind, str]] = set()
    unique: list[ResolvedEntry] = []
    for entry in entries:
        key = (entry.kind, entry.label)
        if key in seen:
            continue
        seen.add(key)
        unique.append(entry)
    return tuple(unique)


def resolve_agent(config: AgentConfig, root: Path) -> ResolvedAgent:
    """
    Resolve one agent config to the artifact set it loads every request.

    The agent JSON's ``permissions``, ``tools`` and ``toolsSettings``
    blocks are deliberately excluded: they configure the runtime and
    never reach the model as prompt text. What the tool definitions
    themselves cost inside the assembled prompt is part of the
    unmeasurable remainder the report footer declares.

    Args:
        config: Parsed agent config.
        root: Repository root.

    Returns:
        The deduplicated artifact set, with unresolved declarations.
    """
    prompt_entries, missing_prompt = _prompt_entries(config, root)
    resource_entries, unresolved = _resource_entries(config, root)
    if missing_prompt:
        unresolved.insert(0, missing_prompt)
    declared = frozenset(
        entry.label for entry in resource_entries if entry.kind is ArtifactKind.FILE
    )
    entries = [
        *prompt_entries,
        *resource_entries,
        *_steering_entries(root, declared),
    ]
    return ResolvedAgent(
        agent=config.name,
        entries=_dedupe(entries),
        unresolved=tuple(unresolved),
    )
