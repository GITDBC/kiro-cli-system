---
name: self-improvement
description: >
  Analyzes session logs and the state registry to propose concrete improvements to
  agents, skills, and steering. Does not apply changes automatically. Triggers: 'improve
  agents', 'self-improvement', 'feedback loop', 'how to improve', 'mejorar agentes',
  'auto-mejora', 'bucle de mejora', 'suggest improvements'. Not for applying fixes (use
  refactoring or reviewing-code). Assessment and advisory only.
---

# Self-Improvement Loop

## Workflow

### Phase 1 — Collection → `code-reviewer`

Read `memory/state.yaml`. Produce:

```markdown
## Collected Data

### Recurring frictions

- [Pattern that repeats across multiple sessions]

### Agent failures

- [Agent X failed in Y context, N times]

### Successful patterns

- [What worked well and should be reinforced]

### Metrics

- Success rate per agent (steps done vs failed)
- Most used skills
- Agents with most negative feedback
```

### Phase 2 — Analysis → `software-architect`

Given the Phase 1 report, identify: which steering rules cause friction, which skills
have missing/unnecessary steps, which agents need prompt adjustments, patterns that
should become steering rules.

### Phase 3 — Proposals → `software-architect`

Produce:

````markdown
## Improvement Proposals

### Proposal N: [Title]

- **Type**: steering | skill | prompt | agent-config
- **File**: [exact path]
- **Effort**: low | medium | high
- **Impact**: low | medium | high
- **Proposed change**:
  ```diff
  - current line
  + proposed line
  ```
- **Justification**: [Why this improves the system]
- **Risk**: [What could go wrong]
````

## Rules

- NEVER apply changes automatically. Present proposals only.
- NEVER propose a learned-state store that promotes entries into agent context without
  human review — correction detection, episode capture, threshold-based rule promotion,
  lessons auto-injection. A durable learned pattern belongs in a reviewed skill or
  steering file; a registry copy of it drifts from the reviewed original. Reference
  implementations of the pattern have been assessed and rejected: none placed a review
  gate between detection and promotion, and the detection step itself is documented as
  unreliable, missing subtle corrections and dropping rapid ones inside a dedup window.
  The prohibition covers automatic promotion, not persistence — a design with an
  explicit human gate remains open. Do not re-derive.
- Order by impact/effort ratio (high impact + low effort first).
- Maximum 10 proposals per execution.
- Each proposal must be independently applicable.
- If fewer than 3 sessions exist in logs, inform the user and stop.
