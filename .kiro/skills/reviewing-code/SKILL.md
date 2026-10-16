---
name: reviewing-code
description: >
  Reviews Python code for bugs and convention violations, applies fixes, and validates
  with the project's linters and tests. Triggers: 'review code', 'code review', 'check
  quality', 'run linters', 'review and fix', 'fix issues'. Not for proactive refactoring
  (delegate to senior-developer) or tech debt assessment (the orchestrator's Tech debt
  assessment pattern).
---

# Reviewing and Fixing Code

## Workflow

```
- [ ] Step 1: Review and report findings
- [ ] Step 2: Fix critical and major issues
- [ ] Step 3: Validate with project tooling
- [ ] Step 4: Re-review changed files (convergence loop)
```

**Step 1** → `code-reviewer`: Read `pyproject.toml` and `Makefile`. Review for bugs,
security issues, missing error handling, convention violations, performance issues, and
work through the Non-Lint-Checkable Checklist below. Load on demand:
`references/python-docstrings.md` (Google-docstring conventions),
`references/python-modern-patterns.md` (3.13-baseline idioms worth a `Simplify`
finding), and `references/finding-calibration.md` (severity and effort anchors, frozen
vocabulary, parallel-run calibration block).

**Step 2** → `code-reviewer`: Fix `Critical` and `High` findings, plus `Medium` ones
whose effort is `XS` or `S`. Don't refactor unrelated code. For large codebases (>15
files with findings), split into batches of 7–12 files.

**Step 3** → `code-reviewer`: Run project validation. In this repository the gate is
`make lint-all` and `make test-all`, narrowed to `make lint-<tool>` / `make test-<tool>`
while iterating on one tool under `tools/`, plus `make drift-check` when the review
touched the agent system; no bare `make lint`, `make test`, or `make code-check` target
exists. In another project, detect targets from its `Makefile` per the tooling-detection
table in `.kiro/steering/COMMON.md`, and fall back to `uv run ruff check .`,
`uv run mypy .` and `uv run pytest` where no Makefile provides them. Only run unit tests
— integration tests require external services.

**Step 4** → `code-reviewer`: Re-review only changed files (`git diff`).

- No `Critical`/`High` findings remain → complete; do not emit the trigger.
- Any remain → end the review output with the literal line `NEEDS_CHANGES`. The native
  loop (target: fix, max 3 iterations) re-runs steps 2–4 only when that exact token is
  present.
- After the third iteration → stop and report unresolved items.

### Concrete finding bar

Emit a finding only when it has a named `file:line`, a code fragment showing the actual
defect, and a concrete proposed change. This is a floor, not a ranking: everything at or
above it goes in the findings table exactly once, at the severity and effort the anchors
in `references/finding-calibration.md` assign; no later stage re-weighs it. State the
scope reviewed (files, or `git diff` range) at the top of the report, and neither expand
nor silently narrow it.

## Non-Lint-Checkable Checklist

No linter catches these. Each item is one rule from the "Numerical Safety and Data
Integrity" and "I/O and Configuration Boundaries" tables in
`.kiro/skills/code-standards/SKILL.md`, which owns the rule text and the patterns a
finding should propose. This list is the canonical copy; other files point here. It is a
mandatory active search.

```
- [ ] C1 Division: every `/` with a runtime denominator is guarded. `.fill_nan()` does
      not count — `x / 0` is `inf`, not `NaN`.
- [ ] C2 Fallbacks: no `value or default` for optional numeric/boolean fields.
- [ ] C3 Joins and row-dropping filters on a KPI / SLA / model-input path log
      `before -> after` row counts.
- [ ] C4 Sentinel values are written with an explicit `dtype=`.
- [ ] C5 Bracketed severity tags match the logger method — no `[WARNING]` through
      `logger.debug()`.
- [ ] C6 External JSON/dict key access re-raises as `ValueError ... from error`.
- [ ] C7 Remote I/O (S3, HTTP, subprocess) has capped-backoff retry and `logger.error`
      before any raise.
- [ ] C8 No directory creation, file writes, or network calls at import time.
- [ ] C9 The same 4–8 line validation or boilerplate block repeated verbatim in 3+
      sibling classes or modules is flagged as a shared-helper candidate.
```

## Findings Table (frozen format)

Emit exactly these columns, in this order:

```
| ID | File:Line | Category | Severity | Effort | Summary |
|----|-----------|----------|----------|--------|---------|
| F1 | pipeline/transforms/rates.py:258-264 | Bug [code-standards: numerical-safety] | High | XS | Unguarded division by the denominator column yields `inf` in the computed rate |
| F2 | pipeline/transforms/__init__.py:1 | Docs [code-standards: docstrings] | Low | XS | No module docstring |
```

- `Severity` ∈ `{Critical, High, Medium, Low}`, `Effort` ∈ `{XS, S, M, L}` — Title Case
  and upper case respectively. Anchors for both in `references/finding-calibration.md`.
- `File:Line` is mandatory on every row. A finding without a line reference is not
  actionable and must not be emitted.
- Tag the `Category` cell with its provenance: `[code-standards: <section>]` when a
  documented rule is violated, `[preference]` when it is reviewer opinion. A
  `[preference]` finding may not exceed `Low`.
- **Self-retracted findings are forbidden.** If the detail paragraph concludes "not a
  defect", "no functional issue", "optional", or "can be skipped", delete the row
  instead of emitting it and arguing against it.
- **No confidence column**: Step 2 fixes by `Severity`/`Effort` alone, so there is
  nothing for a confidence score to drive.
- `### Larger opportunities (out of scope)` is a mandatory closing section and the only
  place architectural proposals may appear: 1–3 sentences each, at most five items,
  never numbered into the findings table, never implemented.

### Spec compliance

Reported separately from the findings table: it asks whether the change does what was
asked, a distinct axis from standards conformance. Adapted from mattpocock/skills (MIT).

Run this axis when a ticket, spec, or design document is available (Jira key, linked
issue, design doc referenced in the PR description, or explicit user-supplied
requirements). When none is available, state that the axis is skipped and why — do not
guess at unstated intent.

Report shape, prose or short bullets, not the findings table:

- **What the ticket/spec asked**: a compressed restatement of the acceptance criteria or
  stated requirement.
- **What the diff does**: a compressed restatement of the actual behavior change.
- **Divergence**: where the two disagree — scope gaps (criteria not implemented), scope
  overreach (behavior beyond what was asked), or silent reinterpretation (implementation
  satisfies a different reading of the requirement than the obvious one). State "no
  divergence found" explicitly when the diff matches the spec.

A divergence is reported in this section only, never as a findings-table row.

## Note Files for Parallel Reviews

One reviewer per section, one file per reviewer, no shared write target:
`notes/reviewing-code_<YYYY-MM-DD>/<section-id>.md` plus a single
`IMPROVEMENT_ANALYSIS.md` consolidation in the same directory — the
`notes/<skill>_<YYYY-MM-DD>/<section-id>.md` shape in the "Notes layout" section of
`.kiro/orchestration/delegation-lifecycle.md`. `<section-id>` is the module path with
`/` replaced by `-` (e.g. `pipeline-transforms`), which makes `<section-id>/F3` a
stable, greppable finding reference.

## Output Format

Each section note carries, in order: `## <section-id>` heading → `**Scope reviewed**` →
`**Overall assessment**` → `### Findings` (the frozen table) → `### Findings detail`
(deep dive on `Medium` and above) → `### Spec compliance` (see above) →
`### Larger opportunities (out of scope)`.

A findings-detail entry uses:

```
**F1 — Bug [code-standards: numerical-safety], High, XS**
`pipeline/transforms/rates.py:258-264`

What: `pl.col("volume") / pl.col("units")` is unguarded; `units` is 0 for a newly
registered entity, so the rate becomes `inf` and propagates into downstream planning
with no log.

Proposed change: wrap in `pl.when(pl.col("units") > 0).then(...).otherwise(None)`.
```

The `Simplify` category keeps its provenance sub-tags: `stdlib:` (hand-rolled logic the
standard library provides), `yagni:` (abstraction with one implementation), `shrink:`
(same logic in fewer lines), `native:` (platform or installed dependency already does
it). See `references/python-modern-patterns.md`.

## Rules

- Priorities: bugs and security over style.
- Use `uv run` for all tool invocations.

## Done when

- Zero `Critical`/`High` findings remain.
- Every emitted finding has `file:line`, a valid `Severity`/`Effort` value, and a
  provenance tag.
- All project validation passes: `make lint-all` and `make test-all` here, or the
  targets detected for the project under review in Step 3.
