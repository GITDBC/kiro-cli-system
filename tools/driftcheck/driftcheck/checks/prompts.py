"""
Checks over prompt files.

Covers each agent's file:// prompt resolving on disk, and prompt files
left behind that no agent references.
"""

# Standard libraries
from pathlib import Path
from typing import Final

# Own modules
from driftcheck.types import DriftContext, Finding, Severity

SECTION_PROMPTS: Final[str] = "Prompt file references"
SECTION_ORPHAN_PROMPTS: Final[str] = "Orphan prompt files"


def check_prompt_references(ctx: DriftContext) -> list[Finding]:
    """
    Verify each agent's file:// prompt resolves.

    Args:
        ctx: Shared check context.

    Returns:
        One finding per agent config.
    """
    findings: list[Finding] = []
    for config in ctx.agent_configs:
        if config.data is None:
            findings.append(
                Finding(
                    Severity.ERROR,
                    SECTION_PROMPTS,
                    f"{config.path.name} is not valid JSON: {config.error}",
                )
            )
            continue
        prompt = config.data.get("prompt", "")
        if isinstance(prompt, str) and prompt.startswith("file://"):
            relative = prompt.replace("file://", "")
            if not (config.path.parent / relative).resolve().exists():
                findings.append(
                    Finding(
                        Severity.ERROR,
                        SECTION_PROMPTS,
                        f"{config.path.name} → missing prompt: {relative}",
                    )
                )
                continue
        findings.append(
            Finding(Severity.OK, SECTION_PROMPTS, f"{config.path.name} prompt valid")
        )
    return findings


def check_orphan_prompts(ctx: DriftContext) -> list[Finding]:
    """
    Detect prompt files no agent references.

    Args:
        ctx: Shared check context.

    Returns:
        A warning per orphan prompt, plus a trailing OK finding.
    """
    findings: list[Finding] = []
    if ctx.prompts_dir.is_dir():
        referenced: set[str] = set()
        for config in ctx.agent_configs:
            if config.data is None:
                continue
            prompt = config.data.get("prompt", "")
            if isinstance(prompt, str) and prompt:
                referenced.add(Path(prompt).name)
        for prompt_file in sorted(ctx.prompts_dir.glob("*.md")):
            if prompt_file.name not in referenced:
                findings.append(
                    Finding(
                        Severity.WARNING,
                        SECTION_ORPHAN_PROMPTS,
                        f"Orphan prompt file '{prompt_file.name}' — not "
                        "referenced by any agent's prompt field",
                    )
                )
    findings.append(
        Finding(Severity.OK, SECTION_ORPHAN_PROMPTS, "Orphan prompt files checked")
    )
    return findings
