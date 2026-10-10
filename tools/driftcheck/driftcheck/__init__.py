"""
Public API of the drift-detection package.

Re-exports the pieces an embedder needs (context construction, the
check registry, the console reporter) without requiring imports from
individual submodules.
"""

# Own modules
from driftcheck.paths import find_repo_root
from driftcheck.registry import CHECKS, run_check, run_checks
from driftcheck.report import count_by_severity
from driftcheck.types import (
    AgentConfig,
    CheckFunction,
    DriftContext,
    Finding,
    Severity,
    build_context,
    load_agent_configs,
)

# The console renderer is reached as ``driftcheck.report.report``:
# re-exporting a function named after its own module would shadow the
# module attribute.
__all__: list[str] = [
    "CHECKS",
    "AgentConfig",
    "CheckFunction",
    "DriftContext",
    "Finding",
    "Severity",
    "build_context",
    "count_by_severity",
    "find_repo_root",
    "load_agent_configs",
    "run_check",
    "run_checks",
]
