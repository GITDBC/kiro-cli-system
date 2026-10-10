"""
Registry of the documentation sources the tool can mirror.

Adding a source means implementing the DocSource contract and listing it
here; nothing in the engine or the CLI needs to know its name.
"""

# Standard libraries
from typing import Final

# Own modules
from docsync.sources.agentskills import AgentSkillsSource
from docsync.sources.anthropic import AnthropicSource
from docsync.sources.base import DocSource
from docsync.sources.kiro import KiroSource

SOURCES: Final[dict[str, DocSource]] = {
    source.name: source
    for source in (KiroSource(), AgentSkillsSource(), AnthropicSource())
}

__all__: list[str] = [
    "SOURCES",
    "AgentSkillsSource",
    "AnthropicSource",
    "DocSource",
    "KiroSource",
]
