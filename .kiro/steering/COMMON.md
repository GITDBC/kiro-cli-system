# Common Directives for All Agents

Behavioral rules for every agent. Coding standards and every numeric threshold:
`.kiro/steering/code-standards-summary.md`. Rationale for these rules and the
`.kiro/orchestration/` layout: `.kiro/orchestration/orchestration-rationale.md` — read
it only when a settled decision is being challenged.

## Technology Stack

Python 3.13 with uv, pytest, SonarQube, Jenkins/GitLab CI/CD.

## Available Tools (tools/)

Invoke CLIs with `shell`; usage in `tools/TOOLS_OVERVIEW.md`.

- `gh` CLI is NOT installed. Push branch, provide compare URL, hand off merge to user.
- Docker is available; GPU access depends on host configuration.

## Documentation Verification

- Academic, professional, impersonal tone. Third person.
- Never start headers with numbers. Do not use "---" to separate sections.
- Use Mermaid for diagrams.
- **Language**: All project artifacts MUST be written in English.

Before recommending any API, library, or pattern, verify it is not deprecated in the
target Python version, will not be removed in the next 2 versions, and follows official
recommendations (Python, Docker, GitLab CI, Jenkins, SonarQube docs).

## Preflight Protocol (mandatory)

Every agent MUST run a preflight analysis before implementation. The orchestrator states
the **delivery mode** and expected depth when it delegates:

| Declared mode | Agent obligation                                                        |
| ------------- | ----------------------------------------------------------------------- |
| Preflight     | Produce the Preflight Report and stop. Read-only — no modifications.    |
| Execute       | Implement following the approved preflight plan; report files modified. |
| Combined      | Open with a 2-3 line preflight, then implement in the same turn.        |

The report's shape lives in `.kiro/orchestration/preflight-report-format.md`: read it
first in a separate preflight turn; combined mode does not need it.

### Rules

- Report blockers clearly — do NOT work around them silently.
- Escalate high-risk assumptions; document low-risk ones and proceed.

### Autonomous Mode

When the dispatch says `mode: autonomous`, read `## Autonomous Mode` in
`.kiro/orchestration/preflight-report-format.md`; the rules also arrive inline in
`ralph.sh` prompts.

## Verification First

Validation runs after every change, before reporting a task complete, by the agent that
made the change: after implementing, `pytest` passes; after configuration changes, the
syntax is valid; after documentation, code examples are syntactically valid; after
fixes, re-run the check that revealed the problem. If verification fails, fix before
proceeding; never pass unverified work downstream. For code that can be run, built, or
type-checked, a syntax-only check or a check that failed to start does not count as
verification. If no real check can run, name the check not run and why instead of
reporting the change as done; missing environments or dependencies are reported, not
installed (see `python-environment.md`).

### Tooling detection

Before writing code, detect what the project provides, then run its own targets after
the change. A `Makefile` target always wins over the raw command it wraps.

| Marker in the project        | Command                                                     |
| ---------------------------- | ----------------------------------------------------------- |
| `Makefile` with `lint-*`     | `make lint-all` (full gate), `make lint-<tool>` (iterating) |
| `Makefile` with `test-*`     | `make test-all` (full gate), `make test-<tool>` (iterating) |
| `Makefile` with `fmt` target | `make fmt` (Markdown and JSON formatting)                   |
| `pyproject.toml` with ruff   | `ruff check . --fix && ruff format --check .`               |
| `pyproject.toml` with mypy   | `mypy .`                                                    |
| `.pre-commit-config.yaml`    | `pre-commit run --all-files`                                |

`<tool>` is a directory name under `tools/`. Some repositories expose only the `-all`
and per-tool forms, with no bare `make lint` or `make test`; check the Makefile. Every
invocation is prefixed with `uv run` (see `python-environment.md`).

### Validation order

Run in sequence, stopping on the first failure: format check → lint → type check (when
configured) → tests covering the changed files at minimum.

### Handling failures

Auto-fixable (formatting, import order): fix and re-run. Lint error: fix the code; do
not suppress without justification. Type error: fix the types; no bare `# type: ignore`.
Test failure: fix the code, or update the test if behavior changed on purpose. Never
disable a linter project-wide or delete a failing test to reach green. A legitimate
suppression is documented inline and confirmed with the user.

### Reporting

State in prose the validation commands actually run and their outcome — e.g. "ran
`make lint-driftcheck` and `make test-driftcheck`; both passed". No fixed template: a
template invites reporting rows that were never run.

## Continuous Improvement

Report improvement opportunities met during any task — automatable manual steps, missing
abstractions causing duplication, workflow friction — in a **Recommendations** section:
what, estimated effort (low/medium/high), and which agents/workflows benefit.

## Communication

Always-on directives; the `concise-communication` skill carries the detailed patterns
(banned phrases, reference codes, worked do/don't examples) on demand.

- **Length**: calibrate to task complexity. Spend the response on the main answer, keep
  caveats short; an explanation request gets a high-level summary unless depth was asked
  for.
- **Narration**: in an interactive session, say in one sentence what is about to happen
  before the first tool call; a dispatched subagent skips that line, since only its
  final response reaches the orchestrator. While working, report only an important
  finding or a change of direction. On finishing, lead with the outcome — the first
  sentence answers what happened or was found, supporting detail after it.
- **Scope**: deliver what was asked at the scope intended. Make routine judgment calls
  directly; check in only where different readings lead to materially different work. If
  the request appears mistaken, say so in one sentence and continue as asked. In a
  dispatched run (Combined, Execute, or autonomous mode) nobody answers mid-turn: keep
  working until everything asked for is done, and never end a turn with a summary that
  announces the next step or offers to continue. Stop early only when nothing can
  advance without the user, or before a risky or irreversible action. When the work is
  done and checked, stop and report: add no unrequested features, tests, files, docs, or
  refactors — mention a worthwhile one at the end instead. Tests and docstrings the code
  standards require for the change are part of the work, not additions.
- **Corrections**: correct an earlier statement when the error would change the user's
  code, conclusions, or decisions, then continue. Fix inconsequential slips silently.

## Output Guidelines

- **Substantial deliverables** (reports, reviews, analyses, multi-step implementations):
  open with a 3-5 line executive summary — key result, decisions, blockers — then the
  detail under a Markdown header. A short answer stays short: a one-line question gets a
  one-line reply, with no summary or header.
- Tables and lists for genuinely enumerable content; prose for reasoning and trade-offs.
- **Files written to disk** (notes, reports, specs, docs): match length to what the task
  needs — cover the substance, no filler sections, redundant summaries, or boilerplate.
  Conversational density is owned by the `concise-communication` skill.
