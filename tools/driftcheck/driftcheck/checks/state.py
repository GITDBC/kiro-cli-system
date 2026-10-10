"""
Checks over the memory/ store and the state.yaml registry.

The first check validates that the file parses, is a mapping, respects
the section entry cap from the harness state-protection rules and holds
unique ids. The second asserts the framework boundary: a framework tree
is installed into other projects, so memory/ is per-consuming-project
runtime state and ships holding nothing but an empty state.yaml.

That boundary holds only for the framework repository itself. A
consuming project's memory/ is legitimately populated, so the second
check is gated on a marker the tree already carries — see
check_memory_store — and reports nothing at all when the tree is not a
framework tree.

PyYAML is imported inside the check rather than at module scope. The
hook console scripts import this package transitively, and a hook must
still start in an environment where the dependency is unavailable — an
eager import here would crash the hook before it could degrade.
"""

# Standard libraries
import re
from pathlib import Path
from typing import Any, Final

# Own modules
from driftcheck.paths import read_text
from driftcheck.types import DriftContext, Finding, Severity

# state.yaml section cap from the harness state-protection rules.
MAX_STATE_ENTRIES: Final[int] = 20

# Sections holding a list of entries, each subject to the cap and to the
# unique-id rule. `project_state` is a single mapping and is excluded.
ENTRY_SECTIONS: Final[tuple[str, ...]] = ("decisions", "agent_feedback")

# The only name memory/ may hold in this repository. A leftover
# state.yaml.bak from the state-protection backup step is a violation
# too: the protocol requires deleting it once validation passes.
MEMORY_TEMPLATE: Final[str] = "state.yaml"

# Marker that declares memory/ to be framework-empty: a .gitignore rule
# ignoring the directory's contents. Recognised forms are the bare
# directory (``memory/``) and the single- or double-star globs
# (``memory/*``, ``memory/**``), each optionally anchored with a leading
# slash, and each tolerating surrounding whitespace. Deliberately NOT
# recognised: commented-out lines, negations such as
# ``!memory/state.yaml``, narrower globs such as ``memory/*.md``, and
# rules coming from anywhere other than the root .gitignore. This is a
# narrow textual match, not an implementation of gitignore semantics.
MEMORY_IGNORE_RULE: Final[re.Pattern[str]] = re.compile(r"/?memory/\*{0,2}")

SECTION_STATE: Final[str] = "State registry integrity"

SECTION_MEMORY: Final[str] = "Memory store framework boundary"


def check_state_registry(ctx: DriftContext) -> list[Finding]:
    """
    Verify state.yaml parses and respects the entry cap.

    Args:
        ctx: Shared check context.

    Returns:
        A single finding describing the registry's state.
    """
    path = ctx.state_yaml
    if not path.is_file():
        return [
            Finding(
                Severity.OK,
                SECTION_STATE,
                "No state.yaml (will be created on first workflow)",
            )
        ]
    try:
        # 3pps
        import yaml
    except ImportError:
        return [
            Finding(
                Severity.ERROR,
                SECTION_STATE,
                "PyYAML is not installed, state.yaml cannot be validated",
            )
        ]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return [
            Finding(Severity.ERROR, SECTION_STATE, f"state.yaml is malformed: {error}")
        ]
    problem = _first_problem(data)
    if problem is not None:
        return [Finding(Severity.ERROR, SECTION_STATE, problem)]
    return [Finding(Severity.OK, SECTION_STATE, "state.yaml is valid")]


def _first_problem(data: Any) -> str | None:
    """
    Return the first structural problem found in the registry.

    Args:
        data: Parsed YAML document.

    Returns:
        An error message, or None when the document is valid.
    """
    if not isinstance(data, dict):
        return "state.yaml is not a mapping"
    for section in ENTRY_SECTIONS:
        problem = _section_problem(section, data.get(section) or [])
        if problem is not None:
            return problem
    return None


def _section_problem(section: str, entries: Any) -> str | None:
    """
    Validate one entry-list section against the structural rules.

    Args:
        section: Name of the section being validated.
        entries: Value found under that section.

    Returns:
        An error message, or None when the section is valid.
    """
    if not isinstance(entries, list):
        return f"{section} is not a list"
    if len(entries) > MAX_STATE_ENTRIES:
        return f"{section} has {len(entries)} entries (max {MAX_STATE_ENTRIES})"
    ids = [entry.get("id") for entry in entries if isinstance(entry, dict)]
    if len(ids) != len(set(ids)):
        return f"{section} has duplicate IDs"
    return None


def check_memory_store(ctx: DriftContext) -> list[Finding]:
    """
    Verify memory/ holds nothing but an empty state.yaml template.

    The invariant exists because the same mistake was made twice in one
    day: durable framework documentation was filed under memory/, which
    is not the framework's to fill. It is framework-scoped: a consuming
    project's memory/ is legitimately populated, so enforcing it there
    would fail the check in the very situation the framework exists to
    serve.

    Scope is determined by the marker the tree already carries — a root
    .gitignore rule ignoring memory/ contents, which exists precisely
    because the framework ships that directory empty. Absent the rule,
    the check reports nothing at all: not a pass, not a warning, simply
    inapplicable. The marker cannot drift out of sync with what it
    describes, because a project that wants its memory/ tracked has to
    remove the rule to get it tracked, and that same act disables the
    check. A separate switch could disagree with .gitignore; this
    cannot. MEMORY_IGNORE_RULE documents which spellings count.

    Args:
        ctx: Shared check context.

    Returns:
        One finding per violation, a single informational finding when
        the tree is clean, or no findings at all when the invariant does
        not apply to this tree.
    """
    if not _ignores_memory_contents(ctx.gitignore):
        return []
    memory_dir = ctx.state_yaml.parent
    if not memory_dir.is_dir():
        return [Finding(Severity.OK, SECTION_MEMORY, "No memory/ directory")]
    findings = [
        Finding(Severity.ERROR, SECTION_MEMORY, _stray_message(path))
        for path in sorted(memory_dir.iterdir())
        if path.name != MEMORY_TEMPLATE
    ]
    findings.extend(_populated_section_findings(ctx.state_yaml))
    if findings:
        return findings
    return [
        Finding(
            Severity.OK,
            SECTION_MEMORY,
            f"memory/ holds only an empty {MEMORY_TEMPLATE} template",
        )
    ]


def _ignores_memory_contents(gitignore: Path) -> bool:
    """
    Report whether .gitignore declares memory/ framework-empty.

    Args:
        gitignore: Path to the repository-root .gitignore.

    Returns:
        True when an uncommented line matches MEMORY_IGNORE_RULE. A
        missing or unreadable file yields False, which makes the
        memory-store check inapplicable rather than failing it.
    """
    for line in read_text(gitignore).splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if MEMORY_IGNORE_RULE.fullmatch(stripped):
            return True
    return False


def _stray_message(path: Path) -> str:
    """
    Describe a path that must not exist under memory/.

    Args:
        path: Offending entry inside the memory directory.

    Returns:
        An error message explaining the framework boundary.
    """
    suffix = "/" if path.is_dir() else ""
    return (
        f"memory/{path.name}{suffix} must not exist here: this is a framework "
        "repository installed into other projects, and memory/ is "
        "per-consuming-project runtime state, so it ships holding only an "
        f"empty {MEMORY_TEMPLATE} template. Content that documents the "
        "framework itself belongs in a versioned location such as docs/"
    )


def _populated_section_findings(path: Path) -> list[Finding]:
    """
    Report every registry section that ships with entries.

    Args:
        path: Path to the state.yaml template.

    Returns:
        One finding per non-empty entry section.
    """
    data = _parse_registry(path)
    if not isinstance(data, dict):
        return []
    findings: list[Finding] = []
    for section in ENTRY_SECTIONS:
        entries = data.get(section) or []
        if isinstance(entries, list) and entries:
            findings.append(
                Finding(
                    Severity.ERROR,
                    SECTION_MEMORY,
                    f"{MEMORY_TEMPLATE} carries {len(entries)} {section} "
                    "entries: the registry records the state of a consuming "
                    "project, and this framework repository ships it empty so "
                    "that no project inherits another project's decisions",
                )
            )
    return findings


def _parse_registry(path: Path) -> Any:
    """
    Parse state.yaml, returning None when it cannot be read.

    A malformed file, an unreadable one and a missing PyYAML are all
    reported by check_state_registry already, so this loader stays
    silent rather than duplicating the error under a second section.

    Args:
        path: Path to the state.yaml template.

    Returns:
        The parsed document, or None when parsing was not possible.
    """
    try:
        # 3pps
        import yaml
    except ImportError:
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
