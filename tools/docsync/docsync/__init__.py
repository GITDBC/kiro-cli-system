"""
Public API of the documentation-sync package.

Re-exports the pieces an embedder needs (the source registry and
contract, the mirror types, the engine helpers) without requiring
imports from individual submodules.
"""

# Own modules
from docsync.paths import find_repo_root
from docsync.sources import SOURCES, AgentSkillsSource, DocSource, KiroSource
from docsync.sync import content_hash
from docsync.types import MirrorPaths, Page, Slug, SyncCounts

# The engine itself is reached as ``docsync.sync.sync``: re-exporting a
# function named after its own module would shadow the module attribute.
__all__: list[str] = [
    "SOURCES",
    "AgentSkillsSource",
    "DocSource",
    "KiroSource",
    "MirrorPaths",
    "Page",
    "Slug",
    "SyncCounts",
    "content_hash",
    "find_repo_root",
]
