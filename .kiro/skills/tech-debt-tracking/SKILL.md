---
name: tech-debt-tracking
description: >
  Parallel workflow for systematic tech debt assessment and improvement suggestions. Use
  when evaluating code-level, architectural, or operational debt, or when looking for
  optimization opportunities and missing automations. Triggers: 'tech debt', 'debt
  assessment', 'what needs fixing', 'suggest improvements', 'what can be improved',
  'optimization opportunities'. Not for applying fixes (use refactoring or
  reviewing-code). Assessment and advisory only.
---

# Tech Debt & Improvement Tracking

Two workflows: **debt assessment** (what's broken) and **improvement suggestions** (what
could be better). Both are assessment-only — no changes applied.

## Workflow 1: Debt Assessment

Execute three agents **in parallel**:

### Track 1 — Code debt → `code-reviewer`

- **Duplication**: copy-pasted logic, repeated business rules
- **Complexity**: cyclomatic >10, nesting >3 levels, methods >50 lines, classes >500
  lines
- **Quality**: deprecated APIs, coverage <80% on critical paths, inconsistent error
  handling, dead code
- **Naming**: unclear names, inconsistent conventions, missing docs on public APIs

### Track 2 — Architectural debt → `software-architect`

- **Coupling**: tight coupling, circular dependencies, dependency direction violations
- **Design**: missing bounded contexts, patterns that don't fit scale, missing ADRs,
  leaky abstractions
- **Evolution**: outdated patterns for backward compat, incomplete migrations,
  inconsistent approaches

### Track 3 — Operational debt → `platform-engineer`

- **Observability**: missing monitoring/alerting, stale alerts, missing tracing
- **Automation**: manual toil >30 min/week, missing runbooks, manual deployment steps
- **Reliability**: missing SLOs, no capacity planning, single points of failure
- **Security-ops**: unrotated secrets, missing audit logging, insecure defaults

### Scoring

> **Priority = Impact (1–5) × Effort (1–5)**
>
> - Impact: how much this hurts quality, velocity, or reliability.
> - Effort: engineer-days to resolve (1 = hours, 5 = weeks).

### Output

Match section length to what the finding set warrants; an empty track states so in one
line rather than padding to match the others.

Combine into `tech-debt/debt_register_<YYYY-MM-DD>.md`:

1. **Executive Summary** — total items, breakdown by track, top-3 priority, health
   rating (🟢 / 🟡 / 🔴)
2. **Debt Register** — table sorted by priority descending
3. **Quick Wins** — Effort ≤ 2 AND Impact ≥ 3
4. **Trend** — compare with previous register if exists
5. **Sprint Allocation** — 🟢: 10–15%, 🟡: 20–25%, 🔴: 30–40%

## Workflow 2: Improvement Suggestions

For the full improvement-suggestions workflow (parallel agents, system self-analysis,
output format), load `references/improvement-suggestions.md`. Use when the user asks
'suggest improvements', 'what can be improved', or 'optimization opportunities' rather
than a debt assessment.

## Rules

- Always read `pyproject.toml` and `Makefile` before assessing.
- Score every debt item with Impact × Effort.
- Do not apply fixes — assessment only.
- Use `uv run` for all tool invocations.
- Run periodically (suggested: monthly) for improvement suggestions.

## Done when

- All tracks completed (3 parallel analyses).
- Output file created with all required sections.
- Items sorted by priority descending.
- Quick wins identified.
