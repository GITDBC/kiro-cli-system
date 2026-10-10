"""Fixtures shared by the driftcheck test suite."""

# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from driftcheck.checks.prompt_quality import (
    KNOWN_CONTRADICTIONS,
    REVIEW_ORIENTED_SKILLS,
)
from driftcheck.checks.skills import DIRECT_INVOKE_SKILLS, ORCHESTRATOR_ONLY_SKILLS
from driftcheck.types import DriftContext, build_context
from tests.helpers import (
    ROUTING_MD,
    COMMON_MD,
    DELEGATION_LIFECYCLE_MD,
    DRIFTCHECK_PYPROJECT,
    EMPTY_STATE_YAML,
    GITIGNORE,
    ORCHESTRATOR_RESOURCES,
    SENIOR_DEVELOPER_PROMPT,
    SKILL_MD,
    write,
    write_agent,
)


@pytest.fixture()
def valid_root(tmp_path: Path) -> Path:
    """
    Build a minimal repository tree that passes every check.

    Every allowlisted skill is materialised, because driftcheck asserts
    that its own exemption lists name skills that exist: an entry for a
    deleted skill is dead configuration. The same holds for the files a
    curated contradiction pair names. Deriving the tree from those
    collections keeps the fixture from rotting when they change.

    The tree is a framework tree, so it carries the .gitignore rule
    that declares memory/ framework-empty and thereby makes the
    memory-store check applicable.

    Orchestrator-only instruction files are placed under
    .kiro/orchestration/ and named in the orchestrator's resources,
    which is the layout the placement check asserts.

    Args:
        tmp_path: Pytest-provided temporary directory.

    Returns:
        Root of the synthetic repository.
    """
    root = tmp_path / "repo"
    write(root / ".gitignore", GITIGNORE)
    write(root / ".kiro" / "orchestration" / "routing.md", ROUTING_MD)
    write(
        root / ".kiro" / "orchestration" / "delegation-lifecycle.md",
        DELEGATION_LIFECYCLE_MD,
    )
    write(root / ".kiro" / "steering" / "COMMON.md", COMMON_MD)
    allowlisted = DIRECT_INVOKE_SKILLS | ORCHESTRATOR_ONLY_SKILLS
    for skill in allowlisted | REVIEW_ORIENTED_SKILLS:
        write(root / ".kiro" / "skills" / skill / "SKILL.md", f"# {skill}\n")
    write(root / ".kiro" / "skills" / "reviewing-code" / "SKILL.md", SKILL_MD)
    write(
        root / ".kiro" / "prompts" / "senior-developer.md",
        SENIOR_DEVELOPER_PROMPT,
    )
    write(root / ".kiro" / "prompts" / "orchestrator.md", "# Orchestrator\n")
    for pair in KNOWN_CONTRADICTIONS:
        for relative in (pair.left, pair.right):
            target = root / relative
            if not target.exists():
                write(target, f"# {target.stem}\n")
    write(root / "memory" / "state.yaml", EMPTY_STATE_YAML)
    write(root / "tools" / "driftcheck" / "pyproject.toml", DRIFTCHECK_PYPROJECT)
    write_agent(root, "senior-developer")
    write_agent(
        root,
        "orchestrator",
        model="claude-sonnet-5",
        resources=ORCHESTRATOR_RESOURCES,
        toolsSettings={"subagent": {"availableAgents": ["senior-developer"]}},
    )
    return root


@pytest.fixture()
def ctx(valid_root: Path) -> DriftContext:
    """
    Build a drift context over the valid synthetic tree.

    Args:
        valid_root: Root of the synthetic repository.

    Returns:
        Context ready to hand to a check function.
    """
    return build_context(valid_root)
