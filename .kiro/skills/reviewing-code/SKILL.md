---
name: reviewing-code
description: >
  Reviews Python code for bugs, enforces project conventions, applies fixes, and
  validates with the project's linters and tests. Use when the user asks for a code
  review, quality check, lint/test validation, or needs code reviewed and fixed.
  Triggers: 'review code', 'code review', 'check quality', 'run linters', 'review and
  fix', 'fix issues'. Not for proactive refactoring (use refactoring skill) or tech debt
  assessment only (use tech-debt-tracking).
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
security issues, missing error handling, convention violations, performance issues. For
Google-docstring convention details, load `references/python-docstrings.md`. For modern
Python idioms (3.11+ syntax, stdlib replacements) worth flagging as `Simplify` findings,
load `references/python-modern-patterns.md`. For the severity and effort anchors, the
frozen value vocabulary, and the parallel-run calibration block, load
`references/finding-calibration.md`.

Work through the Non-Lint-Checkable Checklist below in addition to whatever the linters
report. Every finding must carry `file:line`, a code fragment, and a concrete fix.

### Concrete finding bar

Emit a finding only when it clears this bar: a named `file:line`, a code fragment or
excerpt showing the actual defect, and a concrete proposed change — not a description of
what a fix would generally look like. This is a floor, not a ranking: everything at or
above it goes in the findings table exactly once, at the severity and effort the
calibration anchors in `references/finding-calibration.md` assign it. There is no
separate downstream filter or ranking stage in this skill that defers or re-weighs
findings after Step 1 — Step 2 fixes by severity/effort tier as written below, and
nothing upstream of that narrows the table further. State the scope actually reviewed
(files, or `git diff` range) at the top of the report; do not silently expand review
scope to files outside that stated range, and do not silently narrow it to skip files
inside the range because they looked clean on a first pass.

## Non-Lint-Checkable Checklist

No linter catches these. Each item is one rule from the "Numerical Safety and Data
Integrity" and "I/O and Configuration Boundaries" tables in
`.kiro/skills/code-standards/SKILL.md`, which owns the rule text and the enforcement
mechanism — load it for the exact guard, dtype, retry and re-raise patterns a finding
should propose. They recurred across many isolated reviewer contexts in a large-scale
multi-section review, which is why this is a mandatory active search rather than an
incidental discovery.

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
- **No confidence column, by design.** The frozen columns above are final; do not add a
  `Confidence` field. Anthropic's guidance uses confidence to feed a downstream ranker
  that this skill does not have — Step 2 fixes strictly by the `Severity`/`Effort` tiers
  already in the table, so a qualitative confidence score would have nothing to drive
  and would just reintroduce ranking ambiguity the concrete finding bar exists to
  remove.
- `### Larger opportunities (out of scope)` is a mandatory closing section and the only
  place architectural proposals may appear: 1–3 sentences each, at most five items,
  never numbered into the findings table, never implemented. It is a pressure valve that
  kept scope creep out of the findings in a large multi-section run — keep it, but keep
  it terse.

### Spec compliance

Reported separately from the findings table above — it is a distinct axis (does the
change do what was asked) from standards conformance (is the code correct and
idiomatic), and mixing the two would force a `Category` value the frozen findings
vocabulary does not have. Adapted from mattpocock/skills (MIT), which runs Standards and
Spec as two parallel review axes.

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

A divergence found here is reported in this section only; it is never folded into the
findings table as a new `Category`, and never assigned a `Severity`/`Effort` pair from
that table's frozen vocabulary.

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

- No `Critical`/`High` findings remain → complete.
- Any remain AND iteration < 3 → repeat steps 2–4.
- Any remain AND iteration ≥ 3 → stop, report unresolved items.

## Note Files for Parallel Reviews

One reviewer per section, one file per reviewer, no shared write target:
`notes/<project>-review-<YYYY-MM-DD>/<section-id>.md` plus a single
`IMPROVEMENT_ANALYSIS.md` consolidation in the same directory. `<section-id>` is the
module path with `/` replaced by `-` (e.g. `pipeline-transforms`, `api-handlers`). This
is the convention in the "Notes layout" section of
`.kiro/orchestration/delegation-lifecycle.md`; it makes `<section-id>/F3` a stable,
greppable finding reference.

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

Proposed change: wrap in `pl.when(pl.col("cells") > 0).then(...).otherwise(None)`.
```

When a finding is delivered as an inline review comment rather than a table row, use:

```
**[Critical] Security: SQL Injection Risk**
Line 42: User input is interpolated directly into the query.

**Why:** An attacker could inject malicious SQL through the name parameter.

**Suggestion:**
Use parameterized queries:
`db.query('SELECT * FROM users WHERE name = %s', (name,))`
```

The `Simplify` category keeps its provenance sub-tags: `stdlib:` (hand-rolled logic the
standard library provides), `yagni:` (abstraction with one implementation), `shrink:`
(same logic in fewer lines), `native:` (platform or installed dependency already does
it). See `references/python-modern-patterns.md`.

## Rules

- Always read `pyproject.toml` and `Makefile` before reviewing.
- Priorities: bugs and security over style.
- Never emit a finding without `file:line`, and never emit a finding you then retract.
- Do not refactor unrelated code.
- Use `uv run` for all tool invocations.
- Use `git diff` to scope reviews to changed files only.

## Done when

- Zero `Critical`/`High` findings remain.
- Every emitted finding has `file:line`, a valid `Severity`/`Effort` value, and a
  provenance tag.
- All project validation passes: `make lint-all` and `make test-all` here, or the
  targets detected for the project under review in Step 3.
