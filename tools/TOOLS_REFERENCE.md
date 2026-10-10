# Tools Reference

Implementation detail for the tools under `tools/`: module layout, key types, CLI
argument enumerations, test file names, and cross-tool build conventions. Read this when
modifying a tool rather than invoking it — for routing and delegation decisions, read
`tools/TOOLS_OVERVIEW.md` instead, which stays scoped to what an agent needs to decide
whether and how to invoke a tool.

## Architecture pattern (shared by all tools)

```
cli.py          argparse + TOML config (WORK_AGENTS_CONFIG env var)
  ↓
core module     parser.py / pypi.py / converter.py / jira/
  ↓
report.py       Markdown output generation
  ↓
types.py        dataclasses / TypedDict / TypeAlias
```

All tools: Python ≥3.11, `uv` for deps, `pyproject.toml` as single source of truth,
identical Makefile targets (setup, clean, lint, code-check, test, all).

## Tool summaries

### depschecker (`tools/depschecker/`)

- **Purpose**: Check Python dependency freshness and vulnerabilities via PyPI.
- **Dependencies**: `requests>=2.32,<3`.
- **Modules**: `cli.py`, `parser.py`, `lock.py`, `pypi.py`, `report.py`, `types.py`.
- **Key types**: `DepStatus`, `VulnStatus`, `Advisory` (dataclasses), `PyPIResponse`
  (TypeAlias).
- **CLI args**: `pyproject`, `--lock`, `--output`, `--freshness-only` | `--vulns-only`
  (mutually exclusive), `--timeout`, `--verbose`.
- **Two version sources**: freshness from `pyproject.toml` constraints, vulnerabilities
  from `uv.lock` resolved versions (the only place transitive deps appear). Lock
  inferred beside the pyproject unless `--lock` overrides.
- **Tests**: `tests/test_cli.py`, `test_parser.py`, `test_lock.py`, `test_pypi.py`,
  `test_report.py`.

### jirafetcher (`tools/jirafetcher/`)

- **Purpose**: Fetch, transition, and comment on Jira tickets and their subtasks →
  grouped Markdown files.
- **Dependencies**: `requests>=2.32,<3`.
- **Modules**: `cli.py`, `config.py`, `types.py`, `jira/client.py`, `jira/filters.py`,
  `export/markdown.py`.
- **Key types**: `Config` (dataclass), `JiraClient` (dataclass), `JiraIssue`
  (TypeAlias).
- **Config**: JSON file (primary) or global TOML (fallback). Requires `token`.
- **Subcommands**: `fetch`, `transition`, `comment`.
- **CLI args (all)**: `url`, `--self`, `--include-parent`, `--config`, `--verbose`.
- **CLI args (fetch)**: `--statuses`, `--title-filter`, `--output-dir`, `--dry-run`.
- **CLI args (transition)**: `target_status`, `--statuses`, `--title-filter`,
  `--comment`, `--dry-run`.
- **CLI args (comment)**: `[body]`, `--file`, `--statuses`, `--title-filter`,
  `--dry-run`.
- **Retry**: Automatic retry on 429 and 5xx with exponential backoff (max 3 attempts).
- **Target modes**: Default operates on subtasks. `--self` targets the ticket directly.
  `--include-parent` includes both. Mutually exclusive.
- **Tests**: `tests/test_cli.py`, `test_cmd_comment.py`, `test_config.py`,
  `test_client.py`, `test_filters.py`, `test_markdown.py`.

### doc2md (`tools/doc2md/`)

- **Purpose**: Convert documents (docx, pdf, pptx) and audio → Markdown.
- **Dependencies**: `faster-whisper==1.2.1`, `markitdown[all]==0.1.5`.
- **Modules**: `cli.py`, `converter.py`, `files.py`, `types.py`,
  `converters/markitdown.py`, `converters/whisper.py`.
- **Key types**: `WhisperArgs` (TypedDict), `ConvertResult` / `ResultCallback`
  (TypeAlias).
- **Concurrency**: `ProcessPoolExecutor` for documents, sequential for audio.
- **Security**: Path traversal checks, symlink escape detection, blob size limits,
  `os.umask(0o077)`.
- **CLI args**: `paths`, `--output`, `--exclude`, `--verbose`, `--whisper-model`,
  `--whisper-language`, `--whisper-beam-size`, `--whisper-device`,
  `--whisper-cpu-threads`.
- **Tests**: `tests/test_cli.py`, `test_converter.py`, `test_files.py`,
  `test_markitdown.py`, `test_whisper.py`.

### driftcheck (`tools/driftcheck/`)

- **Repo maintenance — not a routing target.** The orchestrator never delegates work to
  it; it validates this repository's own agent system.
- **Purpose**: Structural checks over agent configs, skills, steering, prompts, hooks —
  resource references, model governance, orphaned files, pattern wiring, and more. The
  check set grows over time; the authoritative, current list is the `CHECKS` tuple in
  `tools/driftcheck/driftcheck/registry.py`.
- **Entry points**: `driftcheck`, plus the lifecycle hooks
  `driftcheck-hook-agent-config`, `driftcheck-hook-state-yaml`,
  `driftcheck-hook-refs-freshness`. `driftcheck-hook-refs-freshness` is wired as
  `agentSpawn` on the orchestrator. `driftcheck-hook-agent-config` and
  `driftcheck-hook-state-yaml` are available, tested console scripts that are
  intentionally NOT wired as `postToolUse` hooks: they duplicated the same validation
  already run at the `make drift-check` gate, at a measured per-write cost (about 405 ms
  combined) on every file write by any agent that had them wired, unrelated to the file
  actually written.
- **Invoke**: `make drift-check`. Exit 1 on errors, 0 on warnings.

### docsync (`tools/docsync/`)

- **Repo maintenance — not a routing target.**
- **Purpose**: mirror the repository's vendored documentation sets. One engine, one CLI,
  one source adapter per upstream: `kiro` mirrors the kiro.dev CLI docs into
  `.kiro/skills/kiro-cli-reference/references/`, `agentskills` mirrors the 6-page Agent
  Skills standard (format specification plus the five skill-creation guides) into
  `.kiro/skills/agent-creation/references/agentskills/`, and `anthropic` mirrors
  Anthropic's prompting documentation into
  `.kiro/skills/claude-prompting-reference/references/`.
- **Dependencies**: none — fetch uses `urllib` from the standard library.
- **Modules**: `cli.py`, `sync.py` (engine), `net.py`, `orphans.py`, `paths.py`,
  `types.py`, `sources/base.py` (the `DocSource` contract), `sources/kiro.py`,
  `sources/anthropic.py`, `sources/agentskills/` (`source.py`, `pages.py`,
  `convert.py`).
- **Source differences**: `kiro` discovers pages from the sitemap; `anthropic` discovers
  them from the upstream `llms.txt` catalogue, by prefix for the prompt-engineering
  subtree plus an exact-slug list whose removal upstream is an error rather than a
  deletion; both enumerate the upstream, so both support `--prune` and share
  `orphans.py`. `agentskills` reads a fixed catalogue and converts upstream `.mdx` to
  Markdown, so it cannot recognise an orphan and refuses `--prune`. `agentskills` and
  `anthropic` treat any unmirrorable page as a failed run that suppresses the marker;
  `kiro` tolerates a gap.
- **Invoke**: `make sync-docs` / `make sync-agentskills` / `make sync-anthropic`, or the
  `-check` variants for a dry run that exits 1 when updates are pending.
- **CLI args**: `source` (`kiro` | `agentskills` | `anthropic`), `--dry-run`, `--prune`,
  `--root`.

### ctxbudget (`tools/ctxbudget/`)

- **Repo maintenance — not a routing target.**
- **Purpose**: measure what the agent system costs in context tokens. `baseline(agent)`
  is the floor paid on every request of every session (prompt + deduplicated `file://`
  resources + auto-loaded steering + skill frontmatter + knowledge-base metadata);
  `activation(skill)` is the one-off cost of a SKILL.md body. A weighted per-file table
  ranks always-on artifacts by tokens × agents loading them, which is the order a
  reduction backlog is worked in.
- **Dependencies**: `tiktoken==0.13.0` (pinned exactly), `pyyaml>=6.0,<7`.
- **Modules**: `cli.py`, `resolve.py`, `count.py`, `model.py`, `report.py`, `types.py`.
- **Subcommands**: `report`, `check`, `calibrate`. Invoke via `make context-budget` and
  `make context-budget-check`.
- **Approximate by construction**: the backend is `tiktoken/o200k_base`, not the
  tokenizer Anthropic bills on, and there is no exact backend — this repository has no
  API key. Before/after **deltas** are trustworthy (tiktoken is deterministic);
  **absolute totals** are not, until calibrated. Never quote one as a share of the
  context window.
- **Resolution rules it encodes**: a `resources` entry resolves against the workspace
  root (`file://.kiro/orchestration/routing.md`), only `prompt` resolves against the
  agent config's own directory, and `.kiro/steering/*.md` reaches every agent once by
  workspace auto-load rather than by declaration. All three are observed, not assumed;
  the earlier `--steering-mode` switch hedged a question that is now answered and has
  been removed.
- **Boundary with driftcheck**: `ctxbudget` measures quantities, `driftcheck` validates
  structure. An unresolvable resource is counted as zero and named in the report, not
  failed. Glob resolution deliberately duplicates `driftcheck/checks/agents.py`, so the
  two can now disagree about glob semantics — recorded in the module docstring and
  README.

### yt2md (`tools/yt2md.sh`)

- **Purpose**: Download YouTube video audio and transcribe to Markdown via Whisper.
- **Dependencies**: `yt-dlp`, `imageio-ffmpeg` (pip-installable), plus `doc2md` venv.
- **Not a Python package** — standalone Bash script that chains `yt-dlp` → `doc2md`.
  Absent from the Makefile's `TOOLS` variable for that reason: `TOOLS` lists the Python
  packages under `tools/` that share the common `setup`/`clean`/`lint`/`code-check`/
  `test` targets, and a bare script has none of those targets to wire.
- **CLI args**: `<youtube-url>` (required), `[output-dir]` (default: `tmp/`).
- **Output**: `<output-dir>/<video-title>.md` with transcription.

## Cross-tool conventions

- TOML config via `WORK_AGENTS_CONFIG` env var, each tool reads its own `[tool_name]`
  section.
- CLI args always override TOML values.
- Argparse defaults are `None` for args resolved in `main()` via TOML fallback.
- Logging uses `%(levelname)s: %(message)s` format, messages end with `.`.
- `__init__.py` exports `__all__` in tools with library API (depschecker, jirafetcher).
