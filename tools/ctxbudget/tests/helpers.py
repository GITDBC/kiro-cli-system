"""
Shared fixture data and helpers for the ctxbudget test suite.

Every test builds a synthetic repository tree under ``tmp_path`` rather
than measuring the real one: the real figures change with every edit to
`.kiro/`, so an assertion against them would either be vacuous or would
fail on unrelated prose changes.

Token counts are asserted through ``FakeCounter``, whose unit is the
whitespace-delimited word. That keeps a cost-model assertion readable —
an expected figure can be counted by eye in the fixture — and keeps the
model tests independent of the tokenizer, which is exercised separately.
"""

# Standard libraries
import json
from pathlib import Path
from typing import Any

ALPHA_PROMPT = """# Alpha

alpha prompt body words here
"""

BETA_PROMPT = """# Beta

beta prompt body
"""

COMMON_MD = """# Common

common steering one two
"""

EXTRA_STEERING_MD = """# Extra

extra steering words
"""

SKILL_ONE = """---
name: one
description: First fixture skill.
---

# One

one body words here now
"""

SKILL_TWO = """---
name: two
description: Second fixture skill.
---

# Two

two body words
"""

REFERENCE_MD = """# Reference

reference words not counted in the body
"""

# A knowledge-base resource in the object form agent configs use.
KNOWLEDGE_BASE: dict[str, Any] = {
    "type": "knowledgeBase",
    "source": "file://.kiro/skills/one/references",
    "name": "FixtureDocs",
    "description": "fixture knowledge base",
    "indexType": "best",
    "autoUpdate": False,
}


class FakeCounter:
    """
    Counter stand-in whose token is one whitespace-delimited word.

    Satisfies the ``Counter`` protocol structurally, which is the point
    of the protocol existing: the model can be tested without loading a
    tokenizer or reaching the network.
    """

    @property
    def backend(self) -> str:
        """Return a backend identifier distinguishable from the real one."""
        return "fake/words"

    @property
    def version(self) -> str:
        """Return a fixed version."""
        return "0.0.0"

    def count(self, text: str) -> int:
        """
        Count whitespace-delimited words.

        Args:
            text: Text to count.

        Returns:
            Number of words.
        """
        return len(text.split())

    def count_path(self, path: Path) -> int:
        """
        Count the words of a file, 0 when it cannot be read.

        Args:
            path: File to count.

        Returns:
            Number of words.
        """
        if not path.is_file():
            return 0
        return self.count(path.read_text(encoding="utf-8"))


def write(path: Path, text: str) -> Path:
    """
    Write a text file, creating parent directories.

    Args:
        path: Destination file.
        text: Content to write.

    Returns:
        The written path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_agent(
    root: Path,
    name: str,
    *,
    prompt: str | None = None,
    resources: list[Any] | None = None,
    **extra: Any,
) -> Path:
    """
    Write one synthetic agent config.

    Args:
        root: Repository root.
        name: Agent slug, also the declared name.
        prompt: Prompt resource, defaulting to the matching prompt file.
        resources: Resource array, defaulting to empty.
        **extra: Additional top-level config fields.

    Returns:
        Path to the written config.
    """
    data: dict[str, Any] = {
        "name": name,
        "prompt": f"file://../prompts/{name}.md" if prompt is None else prompt,
        "tools": ["read", "write"],
        "permissions": {"rules": [{"capability": "fs_read", "match": ["./**"]}]},
        "resources": resources if resources is not None else [],
        "model": "claude-opus-5",
        **extra,
    }
    return write(
        root / ".kiro" / "agents" / f"{name}.json", json.dumps(data, indent=2) + "\n"
    )


def build_tree(tmp_path: Path) -> Path:
    """
    Build the synthetic repository every test measures.

    Two agents, two steering files, two skills (one with a reference
    file), one knowledge base. ``alpha`` declares one steering file and
    both skills; ``beta`` declares both steering files through a glob
    plus the knowledge base, so glob expansion, deduplication and the
    steering auto-injection dedupe are all reachable.

    Every ``resources`` entry uses the workspace-root-relative form Kiro
    actually resolves, while ``prompt`` stays config-relative, which is
    the one field documented that way.

    Args:
        tmp_path: Pytest-provided temporary directory.

    Returns:
        Root of the synthetic repository.
    """
    root = tmp_path / "repo"
    (root / "tools").mkdir(parents=True, exist_ok=True)
    write(root / ".kiro" / "prompts" / "alpha.md", ALPHA_PROMPT)
    write(root / ".kiro" / "prompts" / "beta.md", BETA_PROMPT)
    write(root / ".kiro" / "steering" / "COMMON.md", COMMON_MD)
    write(root / ".kiro" / "steering" / "extra.md", EXTRA_STEERING_MD)
    write(root / ".kiro" / "skills" / "one" / "SKILL.md", SKILL_ONE)
    write(root / ".kiro" / "skills" / "one" / "references" / "deep.md", REFERENCE_MD)
    write(root / ".kiro" / "skills" / "two" / "SKILL.md", SKILL_TWO)
    write_agent(
        root,
        "alpha",
        resources=[
            "file://.kiro/steering/COMMON.md",
            "skill://.kiro/skills/*/SKILL.md",
        ],
    )
    write_agent(
        root,
        "beta",
        resources=[
            "file://.kiro/steering/*.md",
            "file://.kiro/steering/COMMON.md",
            "skill://.kiro/skills/two/SKILL.md",
            KNOWLEDGE_BASE,
        ],
    )
    return root
