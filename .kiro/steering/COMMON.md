# Common Directives for All Agents

Behavioral rules for every agent. Coding standards and every numeric threshold:
`.kiro/steering/code-standards-summary.md`. Rationale for orchestration decisions:
`docs/orchestration-rationale.md`, read only when a settled decision is challenged.

## Technology Stack

Python 3.13 with uv, pytest, SonarQube, Jenkins/GitLab CI/CD.

## Available Tools (tools/)

Invoke CLIs with `shell`; usage in `tools/TOOLS_OVERVIEW.md`, read when a tool is
needed.

- `gh` CLI is NOT installed. Push the branch, provide the compare URL, hand the merge to
  the user.
- Docker is available; GPU access depends on the host.

## Documentation Verification

- Academic, professional, impersonal tone, third person. No numbered headers, no `---`
  section separators. Mermaid for diagrams.
- **Language**: all project artifacts MUST be written in English.
- Before recommending an API, library, or pattern, verify it is not deprecated in the
  target Python version, will not be removed within 2 versions, and follows the official
  recommendations (Python, Docker, GitLab CI, Jenkins, SonarQube).

## Preflight Protocol (mandatory)

Every agent runs a preflight analysis before implementing. The orchestrator states the
**delivery mode** and expected depth on dispatch:

| Declared mode | Agent obligation                                                    |
| ------------- | ------------------------------------------------------------------- |
| Preflight     | Produce the Preflight Report and stop. Read-only, no modifications. |
| Execute       | Implement the approved preflight plan; report the files modified.   |
| Combined      | Open with a 2-3 line preflight, then implement in the same turn.    |

The report's shape is in the `preflight` skill (`.kiro/skills/preflight/SKILL.md`): load
it first in a separate preflight turn; combined mode does not need it. Report blockers
clearly instead of working around them silently; escalate high-risk assumptions,
document low-risk ones and proceed. When the dispatch says `mode: autonomous`, follow
`## Autonomous Mode` in the same skill (the rules also arrive inline in `ralph.sh`
prompts).

## Verification First

The agent that made a change validates it before reporting the task complete: `pytest`
passes after implementing, configuration syntax is valid, documentation code examples
are valid, and the check that revealed a bug is re-run after the fix. Fix failures
before proceeding; never pass unverified work downstream. For code that can be run,
built, or type-checked, a syntax-only check or one that failed to start does not count.
If no real check can run, name the check not run and why instead of reporting the change
as done; missing environments or dependencies are reported, not installed (see
`python-environment.md`).

### Tooling detection

Detect what the project provides before writing code, then run its own targets after the
change; a `Makefile` target wins over the raw command it wraps. Prefix every invocation
with `uv run`.

| Marker in the project        | Command                                                     |
| ---------------------------- | ----------------------------------------------------------- |
| `Makefile` with `lint-*`     | `make lint-all` (full gate), `make lint-<tool>` (iterating) |
| `Makefile` with `test-*`     | `make test-all` (full gate), `make test-<tool>` (iterating) |
| `Makefile` with `fmt` target | `make fmt` (Markdown and JSON formatting)                   |
| `pyproject.toml` with ruff   | `ruff check . --fix && ruff format --check .`               |
| `pyproject.toml` with mypy   | `mypy .`                                                    |
| `.pre-commit-config.yaml`    | `pre-commit run --all-files`                                |

`<tool>` is a tool directory (under `tools/` or a skill's `references/`); check the
Makefile for the forms it exposes. Run in order and stop on the first failure: format
check, lint, type check (when configured), tests covering the changed files at minimum.
Fix auto-fixable findings and re-run. Fix lint, type, and test failures in the code
(update a test only when behavior changed on purpose); no bare `# type: ignore`, no
suppression without a justification confirmed with the user, no project-wide linter
disabling, no deleting a failing test.

Report in prose the commands actually run and their outcome; a fixed template invites
rows that were never run.

## Continuous Improvement

Report improvement opportunities met during a task (automatable manual steps, missing
abstractions, workflow friction) in a **Recommendations** section: what, estimated
effort (low/medium/high), and who benefits.

## Communication

Always-on directives for every agent.

- **Length**: calibrate to task complexity; spend the response on the main answer and
  keep caveats short. An explanation request gets a high-level summary unless depth was
  asked for.
- **Narration**: interactive sessions say in one sentence what is about to happen before
  the first tool call; a dispatched subagent skips it, since only its final response
  reaches the orchestrator. While working, report only an important finding or a change
  of direction. Lead the final message with the outcome.
- **Scope**: deliver what was asked at the scope intended. Make routine judgment calls
  directly; check in only where different readings lead to materially different work. If
  the request appears mistaken, say so in one sentence and continue as asked. In a
  dispatched run (Combined, Execute, or autonomous) nobody answers mid-turn: keep
  working until everything asked is done, never end with a summary that announces the
  next step or offers to continue, and stop early only when nothing can advance without
  the user or before a risky or irreversible action. When the work is done and checked,
  stop: add no unrequested features, tests, files, docs, or refactors (mention a
  worthwhile one at the end). Tests and docstrings the code standards require are part
  of the work.
- **Corrections**: correct an earlier statement when the error would change the user's
  code, conclusions, or decisions; fix inconsequential slips silently.

## Output Guidelines

- **Substantial deliverables** (reports, reviews, analyses, multi-step implementations):
  open with a 3-5 line executive summary (key result, decisions, blockers), then the
  detail under a Markdown header. A short answer stays short: a one-line question gets a
  one-line reply.
- Tables and lists for enumerable content; prose for reasoning and trade-offs.
- **Files written to disk**: match length to what the task needs, with no filler
  sections, redundant summaries, or boilerplate.
