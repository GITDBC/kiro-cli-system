# Tools Overview

Quick-reference for deciding whether and how to invoke a tool. For maintainer detail
(boundaries, pins, per-tool invariants), read `tools/TOOLS_REFERENCE.md`; for behaviour
and options, the README in each tool directory or `--help`.

This directory holds the repository maintenance tools. Every tool is a separate uv
project: run it with `uv run --project tools/<tool> <cli>`, which needs no active
environment. Tools are independent, so they are safe to parallelize.

Tools that a skill uses live inside that skill and are invoked through it:

| Tool        | Location                                         | Skill        |
| ----------- | ------------------------------------------------ | ------------ |
| depschecker | `.kiro/skills/deps-audit/references/depschecker` | `deps-audit` |
| jirafetcher | `.kiro/skills/jira/references/jirafetcher`       | `jira`       |
| doc2md      | `.kiro/skills/doc2md/references/doc2md`          | `doc2md`     |

Run them with `uv run --project <location> <cli>`; the skill documents the exact call.

## Quick Lookup

| Tool       | Purpose                                | Watch out                                                                                                       |
| ---------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| driftcheck | Repo maintenance: agent-system drift   | Not a routing target; run via `make drift-check`                                                                |
| ctxbudget  | Repo maintenance: context-token budget | Not a routing target; figures are approximate, deltas are trustworthy; `make context-budget`                    |
| docsync    | Repo maintenance: vendored doc mirrors | Not a routing target; one tool, three sources: `make sync-docs`, `make sync-agentskills`, `make sync-anthropic` |

## Gotchas

Common mistakes when invoking tools from agents (tool-specific ones are in the skills
listed above):

- **Always use absolute paths.** If the agent has changed directories during the
  session, relative paths will resolve incorrectly. Prefix all file arguments with the
  full repo path (e.g., `/home/user/project/coverage.xml`, not `coverage.xml`).
- **Export `WORK_AGENTS_CONFIG` before the first tool invocation.** Without it, tools
  fall back to built-in defaults and may miss project-specific settings (Jira token,
  custom thresholds). Run: `export WORK_AGENTS_CONFIG="$(pwd)/config.toml"`. A malformed
  config file makes the tool exit 1 with a message.
- **Mind where each tool writes its output.** driftcheck writes to stdout, so redirect
  it, or large reports flood the agent's context window. ctxbudget writes
  `tmp/context-budget-report.md` by default. For the skill-owned tools, send output to a
  file (`depschecker --output`, `doc2md -o`, `jirafetcher fetch -o`).
