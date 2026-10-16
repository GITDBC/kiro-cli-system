# Tools Overview

Quick-reference for deciding whether and how to invoke a tool. For maintainer detail
(boundaries, pins, per-tool invariants), read `tools/TOOLS_REFERENCE.md`; for behaviour
and options, the README in each tool directory or `--help`.

Every tool is a separate uv project: run it with `uv run --project tools/<tool> <cli>`,
which needs no active environment. Tools are independent, so they are safe to
parallelize.

## Quick Lookup

| Tool        | Purpose                                | Watch out                                                                                                       |
| ----------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| depschecker | Dependency freshness + vulns           | pyproject.toml + uv.lock; vulns need the lock                                                                   |
| jirafetcher | Jira read/transition/comment           | Needs token; subcommands `fetch`, `transition`, `comment`                                                       |
| doc2md      | Documents/audio → Markdown             | GPU recommended for audio; slow on CPU                                                                          |
| driftcheck  | Repo maintenance: agent-system drift   | Not a routing target; run via `make drift-check`                                                                |
| ctxbudget   | Repo maintenance: context-token budget | Not a routing target; figures are approximate, deltas are trustworthy; `make context-budget`                    |
| docsync     | Repo maintenance: vendored doc mirrors | Not a routing target; one tool, three sources: `make sync-docs`, `make sync-agentskills`, `make sync-anthropic` |

## Gotchas

Common mistakes when invoking tools from agents:

- **Always use absolute paths.** If the agent has changed directories during the
  session, relative paths will resolve incorrectly. Prefix all file arguments with the
  full repo path (e.g., `/home/user/project/coverage.xml`, not `coverage.xml`).
- **Export `WORK_AGENTS_CONFIG` before the first tool invocation.** Without it, tools
  fall back to built-in defaults and may miss project-specific settings (Jira token,
  custom thresholds). Run: `export WORK_AGENTS_CONFIG="$(pwd)/config.toml"`. A malformed
  config file makes the tool exit 1 with a message.
- **jirafetcher requires a valid token.** If the config file is missing or the token is
  empty, the tool exits with a clear error; verify the config exists before delegating
  Jira tasks. Always prefix the subcommand: `jirafetcher fetch <url>`, not
  `jirafetcher <url>`.
- **doc2md audio conversion needs a GPU or patience.** Whisper transcription on CPU is
  10-50x slower than GPU. For large audio files, warn the user about expected duration
  or suggest `--whisper-device cpu --whisper-beam-size 1` for faster (lower quality)
  results.
- **depschecker needs a `uv.lock` for vulnerability scanning.** It infers one beside the
  given `pyproject.toml` and exits 1 if absent, since advisories are queried per
  resolved version. Use `--lock` for another location, or `--freshness-only` to skip it.
  It cannot parse `requirements.txt`, `setup.py`, or `Pipfile`.
- **Mind where each tool writes its output.** depschecker and driftcheck write to
  stdout, so use `depschecker --output <file>` or redirect driftcheck, or large reports
  flood the agent's context window. ctxbudget writes `tmp/context-budget-report.md` by
  default; doc2md and jirafetcher write files under `--output` and `--output-dir`.
