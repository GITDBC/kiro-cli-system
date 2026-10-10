---
name: tech-evaluation
description: >
  Technology evaluation and adoption workflow. Use when comparing tools, libraries, or
  platforms and planning their adoption. Produces a structured comparison with scoring
  matrix, TCO analysis, and migration plan. Not for implementing the chosen technology
  or writing migration code.
---

# Technology Evaluation Workflow

## Invocation

Use when: choosing between tools/libraries/platforms, evaluating new technology
adoption, assessing migration cost, or building a business case.

Do NOT use when: decision is already made (`senior-developer`/`platform-engineer`),
quick library lookup, or purely security evaluation (`security-audit`).

## Workflow

1. **qa-engineer** — Structured comparison:
   - Define weighted evaluation criteria.
   - Research candidates: features, maturity, community, licensing.
   - Build scoring matrix with evidence per score. For weighting methodology and
     evidence-scoring examples, load `references/weighted-scoring-tco-patterns.md`.
   - Analyze TCO: licensing, training, migration, maintenance.
   - Produce recommendation with confidence level.

2. **software-architect** — Architecture fit:
   - Evaluate integration with existing system.
   - Identify architectural changes required.
   - Assess risk: vendor lock-in, scalability limits, deprecation risk.
   - Validate recommendation fits long-term direction.

3. **platform-engineer** — Adoption plan (if approved):
   - Define migration steps and timeline.
   - Identify infrastructure changes needed.
   - Plan rollback strategy.
   - Estimate effort per phase.

## Output Format

```
## Technology Evaluation: [Subject]

### Scoring Matrix
| Criterion (weight) | Option A | Option B | Option C |
|---------------------|----------|----------|----------|

### TCO Comparison (3-year)
| Cost category | Option A | Option B |
|---------------|----------|----------|

### Recommendation
[Choice] with [confidence level]. Rationale: [why].

### Adoption Plan
Phase 1: [scope, timeline, effort]
Phase 2: [scope, timeline, effort]
Rollback: [strategy]
```

## Success Criteria

- All candidates evaluated against the same criteria with evidence-backed scores.
- TCO includes hidden costs (training, migration, maintenance).
- Architecture fit validated. Adoption plan includes rollback strategy.
