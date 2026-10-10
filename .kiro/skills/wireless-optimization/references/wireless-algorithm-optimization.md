# Wireless Algorithm Optimization Framework

Reference document for the wireless-algorithm-designer agent, distilling the
architecture, patterns, and evaluation methodology for wireless algorithm optimization
frameworks.

## Framework Architecture

The optimization framework deploys a swarm of parallel LLM agents to autonomously design
and optimize wireless communication algorithms. The architecture consists of three
layers:

### Orchestration Layer (AgentManager)

The AgentManager coordinates the optimization loop:

- Manages a pool of N worker processes via Python `multiprocessing` (spawn mode for GPU
  compatibility)
- Uses a manager LLM (low temperature, deterministic) for idea generation and solution
  summarization
- Uses agent LLMs (higher temperature, creative) for algorithm implementation
- Maintains a clustered leaderboard tracking all candidates across generations

### Worker Layer (Agent)

Each worker agent operates independently:

- Receives a task query enriched with an assigned algorithmic approach
- Runs in an isolated Docker container with file operations, code execution, and
  optional documentation search tools
- Follows a two-file workflow: `draft.py` (experimentation) and `solution.py` (best
  result vault)
- Evaluated by a task-specific evaluation tool returning structured metrics

### Evaluation Layer (EvalTool)

Task-specific evaluation tools follow a standard interface:

- `run_evaluation(filename: str) -> str` returns `SUCCESS, <metric>` or `FAILURE,`
- Supporting files (evaluation scripts, configuration) are injected into the workspace
  at evaluation time and cleaned up afterward
- Evaluation runs inside the Docker container with configurable timeouts

## Idea-Driven Optimization Loop

### Generation Cycle

```
1. Manager LLM proposes N distinct algorithmic ideas
2. M agents are distributed across ideas (M/N per idea)
3. Each agent implements and iterates on its assigned approach
4. Manager LLM summarizes each completed solution
5. Results are grouped by idea cluster on the leaderboard
6. Manager LLM reviews all summaries and metrics
7. Manager proposes N new ideas for the next generation
8. Repeat from step 2
```

### Idea Generation Prompts

**Initial ideas** (generation 0): The manager receives the task query and produces N
ideas as a JSON array. Each idea is a self-contained description of an algorithmic
approach different in kind from the others.

**Ideas from results** (subsequent generations): The manager receives all previous
generation summaries grouped by cluster, with metrics and workspace IDs. It proposes N
new ideas that can be refinements, combinations, or entirely new approaches. Each idea
can reference workspace IDs from previous generations as starting code.

### Agent Assignment

Each agent receives:

- The full task prompt (problem description, function signature, constraints)
- An assigned approach section containing the idea description and optional reference
  code from previous generations
- An explicit metric target to beat (derived from the best reference code)

## Task Specification Pattern

### Required Files

| File           | Purpose                                                 |
| -------------- | ------------------------------------------------------- |
| `config.json`  | LLM settings, workspace config, optimization parameters |
| `prompt.md`    | Task description for agents                             |
| `eval_tool.py` | Evaluation tool with `EvalTool` class                   |
| `docker/`      | Dockerfile and build script for agent containers        |

### Optional Files

| File              | Purpose                                                        |
| ----------------- | -------------------------------------------------------------- |
| `tool_factory.py` | Additional tools (e.g., documentation search via vector store) |

### Configuration Parameters

| Parameter           | Description                        | Typical Value  |
| ------------------- | ---------------------------------- | -------------- |
| `num_workers`       | Parallel agent workers             | 5–10           |
| `population_size`   | Total candidates per generation    | 20             |
| `num_ideas`         | Distinct approaches per generation | 5              |
| `num_generations`   | Optimization generations           | 5–10           |
| `timeout`           | Seconds per agent                  | 900–1200       |
| `task_submit_delay` | Rate limiting between submissions  | 30s            |
| `higher_is_better`  | Metric direction                   | task-dependent |

### Prompt Structure

A well-designed task prompt includes:

1. **Objective**: what to optimize and the metric
2. **Context**: domain background and why the task matters
3. **Function signature**: exact interface the solution must implement
4. **Configuration objects**: what imports are available and their shapes/types
5. **Technical constraints**: graph-mode compilation compatibility, no hardcoded values,
   complexity limits
6. **Evaluation description**: how the metric is computed
7. **Baseline code**: a working reference implementation with its metric value
8. **Hints**: optional guidance toward promising directions

### Evaluation Tool Pattern

```python
from tool_lib.base import ToolProvider
from langchain_core.tools import tool, BaseTool

class EvalTool(ToolProvider):
    def __init__(self, eval_timeout: int = 120):
        self._eval_timeout = eval_timeout
        self._workspace = None

    def run_evaluation(self, filename: str) -> str:
        """Evaluate the given file. Return 'SUCCESS, <metric>' or 'FAILURE,'."""
        # 1. Copy supporting files into workspace
        # 2. Run evaluation script with filename as argument
        # 3. Capture output
        # 4. Clean up supporting files
        # 5. Return result string
        ...

    def get_tools(self) -> list[BaseTool]:
        return [tool(self._evaluate)]

    def set_workspace(self, workspace):
        self._workspace = workspace
```

## Bundled Task Examples

### Channel Estimation (MIMO NVE)

- **Metric**: Normalized Validation Error (lower is better)
- **Baseline**: LS estimator with linear interpolation, NVE ≈ 94
- **Function**: `mimo_detector(y, no) -> llr`
- **Constraints**: graph-mode compilation compatible, uses LMMSE equalizer and APP
  demapper
- **Key objects**: `ResourceGrid` (pilot patterns), `StreamManagement` (MIMO streams)
- **Channel estimate shape**: 7D tensor
  `[batch, num_rx, num_rx_ant, num_tx, streams_per_tx, ofdm_symbols, fft_size]`

### Channel Estimation with Covariance

- Same as above but with access to channel covariance information
- Enables LMMSE-based estimation approaches that exploit second-order statistics

### Link Adaptation (MCS Selection)

- **Metric**: Average spectral efficiency in bits/s/Hz (higher is better)
- **Constraint**: Long-term BLER must remain ≤ 10%
- **Function**: `mcs_selection(is_nack_hist, mcs_ackned_hist, bler_target) -> int`
- **Helper functions**: `get_bler(sinr)` and `bler_2_mcs(bler, bler_target)` injected at
  evaluation time
- **Key challenge**: balancing aggressive MCS selection (high throughput) with
  reliability (low BLER)

## Docker Workspace Isolation

Each agent runs in an isolated Docker container:

- Mounted workspace directory for file I/O
- Configurable memory limit (default 16 GB) and PID limit (default 2048)
- Optional GPU access (falls back to CPU if unavailable)
- Runs as current user to avoid permission issues
- Tools: `read_file`, `write_file`, `edit_file`, `copy_file`, `run_python_code`,
  `run_python_script`, `install_package`, `list_dir`, `create_dir`, `delete`

## Leaderboard Structure

Candidates are organized in a clustered leaderboard:

- Each cluster corresponds to one algorithmic idea
- Candidates within a cluster are sorted by metric (best first, failures at end)
- The leaderboard persists as JSON and supports resume after interruption
- Cluster descriptions record the idea that generated each group
- Cross-generation tracking enables the manager to reference previous results

## Documentation Search (RAG)

For tasks that benefit from API documentation lookup, a vector-store-based search tool
provides:

- Semantic search over domain-specific API documentation
- Embedding via any OpenAI-compatible endpoint
- Optional cross-encoder reranking for precision
- One-time index build cached to disk
- Configurable retrieval depth and reranking top-N

## Key Design Principles

1. **Diversity over depth**: N genuinely different algorithmic approaches explore the
   solution space more effectively than N variations of the same approach
2. **Save early, iterate often**: the two-file workflow protects against timeouts and
   failed experiments
3. **Structured evaluation**: machine-parseable first line (`SUCCESS/FAILURE, metric`)
   enables automated leaderboard tracking
4. **Isolation**: Docker containers prevent agents from interfering with each other or
   the host system
5. **Resumability**: leaderboard persistence and generation tracking allow interrupted
   runs to continue from the last completed generation
