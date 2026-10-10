"""
Shared vocabulary for the drift checks.

Holds the severity scale, the finding record, the parsed agent config
and the pre-resolved context every check receives. Context assembly
lives here too, because it exists only to construct these types.
"""

# Standard libraries
import json
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, TypeAlias


class Severity(Enum):
    """Classification of a finding."""

    OK = "OK"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class Finding:
    """
    A single result produced by a check.

    Attributes:
        severity: ERROR and WARNING are counted; OK is informational.
        check: Section name, used to group console output.
        message: Actionable description naming the offending file.
    """

    severity: Severity
    check: str
    message: str

    def render(self) -> str:
        """Format the finding as a "SEVERITY: message" console line."""
        return f"{self.severity.value}: {self.message}"


@dataclass(frozen=True)
class AgentConfig:
    """
    A parsed (or unparseable) agent configuration file.

    Attributes:
        path: Absolute path to the JSON config.
        data: Decoded mapping, or None when the file is not valid JSON.
        error: Decoding error message when data is None.
    """

    path: Path
    data: dict[str, Any] | None
    error: str | None

    @property
    def stem(self) -> str:
        """Return the filename without extension, the agent slug."""
        return self.path.stem

    @property
    def name(self) -> str | None:
        """Return the declared name, or None when it is unusable."""
        if self.data is None:
            return None
        name = self.data.get("name")
        return name if isinstance(name, str) else None

    @property
    def model(self) -> str:
        """
        Return the configured model, empty when unavailable.

        An unparseable config reports an empty model, matching the
        behaviour of a failed extraction: the model-governance check
        then reports a missing field rather than a bad model.
        """
        if self.data is None:
            return ""
        model = self.data.get("model")
        return model if isinstance(model, str) else ""


@dataclass(frozen=True)
class DriftContext:
    """
    Shared, pre-resolved inputs for every check.

    Attributes:
        root: Repository root the checks are evaluated against.
        agent_configs: Every agent config, parsed once and reused.
    """

    root: Path
    agent_configs: tuple[AgentConfig, ...]

    @property
    def kiro_dir(self) -> Path:
        """Return the .kiro directory."""
        return self.root / ".kiro"

    @property
    def agents_dir(self) -> Path:
        """Return the .kiro/agents directory."""
        return self.kiro_dir / "agents"

    @property
    def skills_dir(self) -> Path:
        """Return the .kiro/skills directory."""
        return self.kiro_dir / "skills"

    @property
    def steering_dir(self) -> Path:
        """Return the always-on .kiro/steering directory."""
        return self.kiro_dir / "steering"

    @property
    def orchestration_dir(self) -> Path:
        """
        Return the .kiro/orchestration directory.

        Orchestrator-only instruction files live here rather than in
        steering_dir because Kiro CLI loads every steering file into
        every session, subagent sessions included. The two directories
        are distinct places and must not be conflated.
        """
        return self.kiro_dir / "orchestration"

    @property
    def prompts_dir(self) -> Path:
        """Return the .kiro/prompts directory."""
        return self.kiro_dir / "prompts"

    @property
    def orchestrator_path(self) -> Path:
        """Return the orchestrator config path."""
        return self.agents_dir / "orchestrator.json"

    @property
    def routing_md(self) -> Path:
        """Return the .kiro/orchestration/routing.md agent-routing table."""
        return self.orchestration_dir / "routing.md"

    @property
    def state_yaml(self) -> Path:
        """Return the memory/state.yaml path."""
        return self.root / "memory" / "state.yaml"

    @property
    def cli_settings(self) -> Path:
        """Return the optional .kiro/settings/cli.json path."""
        return self.kiro_dir / "settings" / "cli.json"

    @property
    def gitignore(self) -> Path:
        """Return the repository-root .gitignore path."""
        return self.root / ".gitignore"

    @property
    def orchestrator(self) -> AgentConfig | None:
        """Return the orchestrator config, or None when absent."""
        for config in self.agent_configs:
            if config.path == self.orchestrator_path:
                return config
        return None

    def skill_dirs(self) -> Iterator[Path]:
        """
        Iterate skill directories in a stable order.

        Yields:
            Each direct subdirectory of .kiro/skills, sorted by name.
        """
        if not self.skills_dir.is_dir():
            return
        for path in sorted(self.skills_dir.iterdir()):
            if path.is_dir():
                yield path


CheckFunction: TypeAlias = Callable[[DriftContext], list[Finding]]


def load_agent_configs(agents_dir: Path) -> tuple[AgentConfig, ...]:
    """
    Parse every agent config once, recording decode failures.

    A malformed config is preserved as an AgentConfig with data set to
    None so that each check can classify it the way it needs to instead
    of aborting the whole run.

    Args:
        agents_dir: Directory holding the agent JSON files.

    Returns:
        Configs sorted by path.
    """
    configs: list[AgentConfig] = []
    if not agents_dir.is_dir():
        return ()
    for path in sorted(agents_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            configs.append(AgentConfig(path=path, data=None, error=str(error)))
            continue
        if not isinstance(data, dict):
            configs.append(
                AgentConfig(path=path, data=None, error="top level is not an object")
            )
            continue
        configs.append(AgentConfig(path=path, data=data, error=None))
    return tuple(configs)


def build_context(root: Path) -> DriftContext:
    """
    Assemble the shared context for a repository tree.

    Args:
        root: Repository root to validate.

    Returns:
        A context with every agent config parsed once.
    """
    resolved = root.resolve()
    return DriftContext(
        root=resolved,
        agent_configs=load_agent_configs(resolved / ".kiro" / "agents"),
    )
