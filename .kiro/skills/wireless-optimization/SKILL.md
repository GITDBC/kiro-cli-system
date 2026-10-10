---
name: wireless-optimization
description: >
  Sequential workflow for designing and optimizing wireless communication algorithms.
  Use when designing beamforming, scheduling, power control, or signal processing
  algorithms. Triggers: 'wireless algorithm', 'optimize radio', 'beamforming design'.
  Not for general software optimization or network configuration tasks.
---

# Wireless Algorithm Optimization Workflow

```
/wireless-optimization <description of the wireless algorithm task to solve>
```

## Workflow

### Phase 1 — Task Analysis & Idea Generation → `telecom-engineer`

For network fundamentals (channel models, standards constraints, propagation basics)
needed to ground idea generation, load `references/telecom-network-fundamentals.md`.

Produce:

- **Task decomposition**: metric to optimize, direction, baseline, constraints.
- **3–5 algorithmic ideas**: distinct approaches differing in algorithm family/paradigm
  (not just hyperparameters).
- **Evaluation criteria**: success threshold, failure conditions, expected metric range.
- **Implementation plan**: concrete description per idea for an implementer to follow.

Output a structured spec with ideas ranked by expected impact.

### Phase 2 — Domain Validation → `telecom-engineer`

Review ideas for:

- **Physical-layer correctness**: signal propagation, Shannon's theorem, spectrum
  constraints.
- **Standards compliance**: 3GPP/ITU assumptions for the target system (LTE, 5G NR).
- **Feasibility**: computational complexity and latency realistic for target deployment.
- **Missing considerations**: channel models, interference patterns, edge cases.

Flag issues as CRITICAL (blocks implementation) or ADVISORY.

### Phase 3 — Implementation → `telecom-engineer`

For iterative optimization strategies and evaluation-metric patterns (NVE, BLER, BER),
load `references/wireless-algorithm-optimization.md`.

- Implement top-ranked idea (adjusted per Phase 2 feedback) using `draft.py` /
  `solution.py`.
- Evaluate against the task metric; iterate (refine parameters, try variations).
- Document final approach, metric achieved, and iteration history.
- If first idea fails after reasonable iteration, move to the next.

### Phase 4 — Code Review → `code-reviewer`

Review for: code quality/readability (COMMON.md), numerical stability, edge cases,
performance (copies, vectorization, complexity), self-containedness (no cross-file
imports).

## Quality Criteria

- Final solution beats the stated baseline metric.
- All code is self-contained and compatible with the evaluation pipeline.
- Domain assumptions validated by telecom-engineer.
- Iteration history documented with metrics at each step.
