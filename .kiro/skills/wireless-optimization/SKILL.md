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

1. **telecom-engineer — ideas and validation.** Decompose the task (metric, direction,
   baseline, constraints) and propose 3–5 ideas from distinct algorithm families, ranked
   by expected impact. Validate each against physical-layer correctness, 3GPP/ITU
   assumptions, and deployment latency; flag issues CRITICAL or ADVISORY.
2. **telecom-engineer — implementation.** Load
   `references/wireless-algorithm-optimization.md`: it holds the two-file workflow
   (`draft.py` / `solution.py`), the `SUCCESS, <metric>` evaluation contract, the task
   specification shape, the iteration strategy, and the reference tasks with their
   baselines and signatures.
3. **code-reviewer — review.** Code quality per `COMMON.md`, numerical stability, edge
   cases, vectorization, and self-containedness (no cross-file imports beyond the
   provided objects).

## Quality Criteria

- Final solution beats the stated baseline metric.
- Code is self-contained and compatible with the evaluation pipeline.
- Iteration history documents the metric at every step.
