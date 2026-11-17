"""
Shared fixtures data and helpers for the driftcheck test suite.

Every test builds a minimal synthetic repository tree under tmp_path
rather than asserting against the real repository, which is currently
clean and would make every assertion vacuous.
"""

# Standard libraries
import json
from pathlib import Path

# Own modules
from driftcheck.types import Finding, Severity

COMMON_MD = """# Common Directives

Every agent applies these directives before doing anything else here.
"""

# The orchestrator declares no file:// resource: every subagent that
# declares none inherits its parent's, so a dispatcher's file resources
# would be paid again on each dispatch. Its prompt carries the routing
# tables, the collaboration patterns and the delegation rules itself.
ORCHESTRATOR_RESOURCES: list[str] = []

ORCHESTRATOR_PROMPT = """# Orchestrator

## Orchestration core

### Routing Quick Lookup

| Agent            | When to pick           | Cost        | Fallback      |
| ---------------- | ---------------------- | ----------- | ------------- |
| senior-developer | implement, refactor    | high (2.0x) | code-reviewer |

### Delivery modes

| Agent            | Mode    |
| ---------------- | ------- |
| senior-developer | combined |

## Routing

### Agent Capabilities Matrix

| Agent            | Capabilities      |
| ---------------- | ----------------- |
| senior-developer | implement, refactor |

### Routing Rules

```yaml
routing:
  - group: core
    agents:
      - id: senior-developer
        trigger_when:
          - implementing features or writing application code
        never_when:
          - high-level architecture decisions
```

### Collaboration Patterns

| Task            | Skill              | Agents           |
| --------------- | ------------------ | ---------------- |
| Review          | reviewing-code     | senior-developer |
| Autonomous      | ralph-loop         | senior-developer |
| Security audit  | security-audit     | —                |

## Delegation

Orchestrator-only delegation machinery, carried by this prompt.

## Harness gates

Orchestrator-only verification gates.

## Conductor

Orchestrator-only ad-hoc workflow composition.
"""

# Minimal prompt for a routable agent: it has to carry the boundary
# section the prompt-quality check expects, because ORCHESTRATOR_PROMPT
# above declares never_when entries for this agent.
SENIOR_DEVELOPER_PROMPT = """# Senior developer

## Boundaries

Do NOT use this agent when the task is purely architectural.
"""

SKILL_MD = """# Reviewing code

Iterative review loop driven by the code-reviewer agent role here.
"""

STATE_YAML = """decisions:
  - id: D1
    date: 2026-01-01
    scope: global
"""

# What a framework repository ships: valid, and empty because the
# registry records the state of a consuming project, not of the
# framework. STATE_YAML above stands in for a filled consuming-project
# registry, which the hook tests need and the memory-store check
# forbids here.
EMPTY_STATE_YAML = """decisions: []

agent_feedback: []
"""

GIT_SAFETY_SH = """#!/usr/bin/env bash
exit 0
"""

# The marker that makes the memory-store check applicable: a framework
# tree ignores memory/ contents except the shipped template. A consuming
# project drops these two lines to track its own memory/, which is what
# disables the check there.
GITIGNORE = """tmp/
notes/

memory/*
!memory/state.yaml
"""

# The same tree as a consuming project sees it: no rule ignoring
# memory/ contents, so the framework boundary does not apply.
GITIGNORE_WITHOUT_MEMORY_RULE = """tmp/
notes/
"""

# Minimal stand-in for tools/driftcheck/pyproject.toml. Its presence
# also makes the synthetic tree a discoverable repository root, since
# discovery looks for a directory holding both .kiro/ and tools/.
DRIFTCHECK_PYPROJECT = """[project]
name = "work-driftcheck"

[project.scripts]
driftcheck = "driftcheck.cli:main"
driftcheck-hook-refs-freshness = "driftcheck.hooks.references_freshness:main"
"""


def write(path: Path, content: str) -> Path:
    """
    Write text to a path, creating parent directories.

    Args:
        path: Destination file.
        content: Text to write.

    Returns:
        The written path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_git_safety_hook(root: Path) -> Path:
    """
    Write an executable stand-in for the git-safety hook script.

    Args:
        root: Repository root.

    Returns:
        Path to the written script.
    """
    path = write(root / ".kiro" / "hooks" / "git-safety.sh", GIT_SAFETY_SH)
    path.chmod(0o755)
    return path


def git_safety_hook_document(
    matcher: str = "execute_bash|control_bash_process",
) -> dict[str, object]:
    """
    Build a standalone v1 hooks document wiring the git-safety script.

    Args:
        matcher: PreToolUse matcher regex to use.

    Returns:
        A document ready to serialize into .kiro/hooks/*.json.
    """
    return {
        "version": "v1",
        "hooks": [
            {
                "name": "git-safety",
                "trigger": "PreToolUse",
                "matcher": matcher,
                "action": {
                    "type": "command",
                    "command": ".kiro/hooks/git-safety.sh",
                },
                "timeout": 5,
                "enabled": True,
            }
        ],
    }


def write_hooks_file(
    root: Path, name: str = "hooks", document: dict[str, object] | None = None
) -> Path:
    """
    Write a standalone .kiro/hooks/<name>.json file.

    Args:
        root: Repository root.
        name: Hook file stem.
        document: Document to write, defaulting to the git-safety hook
            covering both shell tool ids.

    Returns:
        Path to the written file.
    """
    path = root / ".kiro" / "hooks" / f"{name}.json"
    payload = document if document is not None else git_safety_hook_document()
    return write(path, json.dumps(payload, indent=2))


def write_agent(
    root: Path,
    slug: str,
    **overrides: object,
) -> Path:
    """
    Write an agent config with sensible defaults.

    Args:
        root: Repository root.
        slug: Agent slug, used as filename and default name.
        overrides: Fields replacing or extending the defaults.

    Returns:
        Path to the written config.
    """
    config: dict[str, object] = {
        "name": slug,
        "model": "claude-opus-5.5",
        "prompt": f"file://../prompts/{slug}.md",
        "resources": [
            "file://.kiro/steering/COMMON.md",
            "skill://.kiro/skills/reviewing-code/SKILL.md",
        ],
    }
    config.update(overrides)
    path = root / ".kiro" / "agents" / f"{slug}.json"
    return write(path, json.dumps(config, indent=2))


def severities(findings: list[Finding]) -> list[Severity]:
    """
    Extract the severities of a finding list.

    Args:
        findings: Findings to inspect.

    Returns:
        Severity of each finding, in order.
    """
    return [finding.severity for finding in findings]


def problems(findings: list[Finding]) -> list[Finding]:
    """
    Filter out informational findings.

    Args:
        findings: Findings to inspect.

    Returns:
        Only the ERROR and WARNING findings.
    """
    return [finding for finding in findings if finding.severity is not Severity.OK]
