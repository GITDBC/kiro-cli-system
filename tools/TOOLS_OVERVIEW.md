# Tools Overview

Quick-reference for the orchestrator. Read this instead of source code when deciding
routing and delegation boundaries. For module layout, key types, CLI argument
enumerations, and test file names, see `tools/TOOLS_REFERENCE.md` — read that when
modifying a tool rather than invoking it.

## Quick Lookup

| Tool        | Purpose                                | Watch out                                                                                                       |
| ----------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| depschecker | Dependency freshness + vulns           | pyproject.toml + uv.lock; vulns need the lock                                                                   |
| jirafetcher | Jira read/transition/comment           | Needs token; use subcommands: `fetch`, `transition`, `comment`                                                  |
| doc2md      | Documents/audio → Markdown             | GPU recommended for audio; slow on CPU                                                                          |
| yt2md       | YouTube → transcript                   | Requires yt-dlp; very slow on CPU                                                                               |
| driftcheck  | Repo maintenance: agent-system drift   | Not a routing target; run via `make drift-check`                                                                |
| ctxbudget   | Repo maintenance: context-token budget | Not a routing target; figures are approximate, deltas are trustworthy; `make context-budget`                    |
| docsync     | Repo maintenance: vendored doc mirrors | Not a routing target; one tool, three sources: `make sync-docs`, `make sync-agentskills`, `make sync-anthropic` |

**All tools**: Use `--output <file>` to avoid flooding context. Use absolute paths.
Export `WORK_AGENTS_CONFIG` first. Tools are independent — safe to parallelize.

## Delegation boundaries

Tools share no Python code imported at runtime, so each remains independently
installable and runnable via `uv run --project tools/<tool>`. Safe to assign different
tools to parallel agents with no file overlap risk. Developer build tooling is exempt:
`tools/tool.mk` is a shared Make include for the common `setup`/`clean`/`lint`/
`code-check`/`test`/`all` targets, since it affects neither installability nor runtime
behaviour — the accepted cost is that a tool directory is no longer self-contained if
copied out of the repository.

## Gotchas

Common mistakes when invoking tools from agents:

- **Always use absolute paths.** If the agent has changed directories during the
  session, relative paths will resolve incorrectly. Prefix all file arguments with the
  full repo path (e.g., `/home/user/project/coverage.xml`, not `coverage.xml`).
- **Export `WORK_AGENTS_CONFIG` before first tool invocation.** Without it, tools fall
  back to built-in defaults and may miss project-specific settings (Jira tokens, custom
  thresholds). Run: `export WORK_AGENTS_CONFIG="$(pwd)/config.toml"`
- **jirafetcher requires a valid token.** If the config file is missing or the token is
  empty, the tool exits with a clear error. Verify config exists before delegating Jira
  tasks. The CLI now uses subcommands (`fetch`, `transition`, `comment`), so always
  prefix the action: `jirafetcher fetch <url>` not `jirafetcher <url>`.
- **doc2md audio conversion needs a GPU or patience.** Whisper transcription on CPU is
  10-50x slower than GPU. For large audio files, warn the user about expected duration
  or suggest `--whisper-device cpu --whisper-beam-size 1` for faster (lower quality)
  results.
- **depschecker needs a `uv.lock` for vulnerability scanning.** It infers one beside the
  given `pyproject.toml` and exits 1 if absent, since advisories are queried per
  resolved version. Use `--lock` for another location, or `--freshness-only` to skip it.
  It cannot parse `requirements.txt`, `setup.py`, or `Pipfile`.
- **All tools write to stdout by default.** Use `--output <file>` to save reports to
  disk. Without it, large reports flood the agent's context window.
- **yt2md transcription is slow on CPU.** A 1-hour video can take 10-30 minutes. For
  videos with available subtitles, consider `yt-dlp --write-subs` as a faster
  alternative. The script requires `yt-dlp` and `imageio-ffmpeg` to be pip-installed in
  the system Python.
