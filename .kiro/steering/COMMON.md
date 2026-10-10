# Common Directives for All Agents

Behavioral rules for every agent. For coding standards and every numeric threshold, see
`.kiro/steering/code-standards-summary.md`. Rationale for these rules, and for the
`.kiro/orchestration/` layout, is in `.kiro/orchestration/orchestration-rationale.md` —
read it only when a settled decision is being challenged.

## Technology Stack

Python 3.11 with uv, pytest, SonarQube, Jenkins/GitLab CI/CD.

## Available Tools (tools/)

Invoke CLIs with `shell`. See `tools/TOOLS_OVERVIEW.md` for usage.

- `gh` CLI is NOT installed. Push branch, provide compare URL, hand off merge to user.
- Docker is available; GPU access depends on host configuration.

## Documentation Verification

- Academic, professional, impersonal tone. Third person.
- Never start headers with numbers. Do not use "---" to separate sections.
- Use Mermaid for diagrams. See the `mermaid-diagrams` skill for syntax rules.
- **Language**: All project artifacts MUST be written in English.

Before recommending any API, library, or pattern, verify it is not deprecated in the
target Python version, will not be removed in the next 2 versions, and follows official
recommendations (Python, Docker, GitLab CI, Jenkins, SonarQube docs).

## Preflight Protocol (mandatory)

Every agent MUST run a preflight analysis before implementation. The orchestrator states
the **delivery mode** and the expected depth when it delegates; the agent's obligation
per mode is:

| Declared mode | Agent obligation                                                        |
| ------------- | ----------------------------------------------------------------------- |
| Preflight     | Produce the Preflight Report and stop. Read-only — no modifications.    |
| Execute       | Implement following the approved preflight plan; report files modified. |
| Combined      | Open with a 2-3 line preflight, then implement in the same turn.        |

### Preflight Report Format

`## Preflight Report`, then task understanding, complexity (trivial | low | medium |
high) and feasibility, followed by `### Can do`, `### Risks (I can handle)`,
`### Blockers (need help)` (name a suggested agent),
`### Ambiguities (need clarification)`, `### Execution plan` (ordered steps, files to
read or modify). In a separate preflight turn, read
`.kiro/orchestration/preflight-report-format.md` first; combined mode does not need it.

### Rules

- Report blockers clearly — do NOT work around them silently.
- Escalate high-risk assumptions; document low-risk ones and proceed.

### Autonomous Mode

For non-interactive workflows (Ralph Loop, CI-triggered tasks):

| Situation                     | Autonomous mode                                   |
| ----------------------------- | ------------------------------------------------- |
| Ambiguity                     | Assume most conservative option, document it      |
| Blocker (needs another agent) | Attempt alternative; if impossible, mark deferred |
| High-risk assumption          | Choose the reversible option, document the risk   |
| Scope unclear                 | Implement the minimal interpretation              |

- **Never block on missing input.**
- **Document every assumption** under `### Autonomous Decisions`.
- **Prefer reversible over optimal.**
- **Defer, don't fail.** Skip blocked subtasks, report them at the end.

## Verification First

Validation runs after every change, before reporting a task complete. The agent that
made the change runs it.

- After implementing: run `pytest`, confirm tests pass.
- After modifying configuration: validate syntactic correctness.
- After writing documentation: verify code examples are syntactically valid.
- After applying fixes: re-run the check that revealed the original problem.
- If verification fails, fix before proceeding. Never pass unverified work downstream.

### Tooling detection

Before writing code, detect what the project provides — `Makefile`, `pyproject.toml`,
`.pre-commit-config.yaml` — then run its own targets after the change. A `Makefile`
target always wins over the raw command it wraps.

| Marker in the project                      | Tool       | Command                                       |
| ------------------------------------------ | ---------- | --------------------------------------------- |
| `Makefile` with `lint-all` / `lint-<tool>` | Make       | `make lint-all`, or `make lint-<tool>`        |
| `Makefile` with `test-all` / `test-<tool>` | Make       | `make test-all`, or `make test-<tool>`        |
| `Makefile` with `fmt` target               | Make       | `make fmt` (Markdown and JSON formatting)     |
| `pyproject.toml` with ruff                 | Ruff       | `ruff check . --fix && ruff format --check .` |
| `pyproject.toml` with mypy                 | MyPy       | `mypy .`                                      |
| `.pre-commit-config.yaml`                  | Pre-commit | `pre-commit run --all-files`                  |

`<tool>` is a directory name under `tools/`. This repository exposes no bare `make lint`
or `make test` target; use the `-all` form for the full gate and the per-tool form while
iterating.

Every invocation is prefixed with `uv run` (see `python-environment.md`).

### Validation order

Run in sequence, stopping on the first failure: format check → lint → type check (when
configured) → tests covering the changed files at minimum.

### Handling failures

| Failure class                           | Action                                                          |
| --------------------------------------- | --------------------------------------------------------------- |
| Auto-fixable (formatting, import order) | Fix and re-run                                                  |
| Lint error                              | Fix the code; do not suppress without justification             |
| Type error                              | Fix the types; no bare `# type: ignore`                         |
| Test failure                            | Fix the code, or update the test if behavior changed on purpose |

Never disable a linter project-wide, and never delete a failing test, to reach green. A
legitimate suppression is documented inline and confirmed with the user.

### Reporting

- State, in prose, the validation commands actually run and their outcome — for example
  "ran `make lint-driftcheck` and `make test-driftcheck`; both passed". No fixed
  template: the commands differ per project, and a template invites reporting rows that
  were never run.

## Code Intelligence

Use the `code` tool for AST-based understanding; its own tool description enumerates the
operations. Use `grep` instead for literal text in strings and comments. Before
modifying unfamiliar code: run `get_document_symbols`, then `search_symbols`, then read
specific sections with `read`.

## Continuous Improvement

Note and report improvement opportunities encountered during any task:

- Repetitive manual steps that could be automated.
- Missing abstractions causing duplication.
- Workflow friction slowing delivery.

Include a **Recommendations** section with: what, estimated effort (low/medium/high),
and which agents/workflows benefit.

## Communication

The directives below are always-on. The `concise-communication` skill carries the
detailed patterns (banned phrases, reference codes, compression aliases) on demand.

- **Length**: calibrate to task complexity. Spend the response on the main answer and
  keep caveats short; an explanation request gets a high-level summary unless depth was
  asked for.
- **Narration**: before the first tool call, say in one sentence what is about to
  happen. While working, report an important finding or a change of direction, nothing
  else. On finishing, lead with the outcome — the first sentence answers what happened
  or what was found, supporting detail after it.
- **Scope**: deliver what was asked at the scope intended. Make routine judgment calls
  directly; check in only where different readings lead to materially different work. If
  the request appears mistaken, say so in one sentence and continue with it as asked.
- **Corrections**: correct an earlier statement when the error would change the user's
  code, conclusions, or decisions, then continue. Fix inconsequential slips silently.

## Output Guidelines

- **Substantial deliverables** (reports, reviews, analyses, multi-step implementations):
  open with an executive summary of 3-5 lines — key result, decisions, blockers — then
  the detail under a Markdown header. A short answer stays short: a one-line question
  gets a one-line reply, with no summary and no header around it.
- Use tables and lists for genuinely enumerable content; let prose carry reasoning and
  trade-offs.
- **Files written to disk** (notes, reports, specs, docs): match length to what the task
  needs — cover the substance, and do not pad with filler sections, redundant summaries,
  or boilerplate. Conversational density is a separate concern, owned by the
  `concise-communication` skill.
