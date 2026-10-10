"""
The Agent Skills documentation source.

Three concerns live in three modules: the fixed page catalogue, the MDX
to Markdown conversion, and the adapter that joins them for the engine.
The catalogue is a separate module because the converter needs the
route table to rewrite cross-references, and importing it from the
adapter instead would close an import cycle.
"""

# Own modules
from docsync.sources.agentskills.source import AgentSkillsSource

__all__: list[str] = ["AgentSkillsSource"]
