# Wireless Algorithm Optimization Patterns

Iteration and evaluation patterns for the implementation step of the
`wireless-optimization` workflow, run by `telecom-engineer`.

## Two-File Workflow

- `draft.py` — experimentation; overwrite freely.
- `solution.py` — the best result so far; update only when the metric improves.

Saving the best candidate early protects the result against timeouts and failed
experiments.

## Evaluation Contract

The evaluation step returns a machine-parseable first line, `SUCCESS, <metric>` or
`FAILURE,`, so iterations can be compared automatically. Record every evaluated
candidate with its idea, metric, and change from the previous iteration; this is the
iteration history the Quality Criteria require.

## Task Specification

A task prompt for an implementer states:

1. **Objective**: what to optimize and the metric, with its direction.
2. **Context**: domain background and why the task matters.
3. **Function signature**: the exact interface the solution implements.
4. **Configuration objects**: available imports and their shapes and types.
5. **Technical constraints**: graph-mode compilation compatibility, no hardcoded values,
   complexity limits.
6. **Evaluation description**: how the metric is computed.
7. **Baseline code**: a working reference implementation with its metric value.
8. **Hints**: optional guidance toward promising directions.

## Iteration Strategy

1. Implement the top-ranked idea against the baseline target.
2. Refine parameters and variations within the same algorithm family while the metric
   improves.
3. When an idea plateaus below the baseline, move to the next idea rather than tuning
   further; a later idea may start from an earlier idea's `solution.py`.
4. Combine ideas only after each has been evaluated on its own.

## Example Tasks and Metrics

| Task                               | Metric (direction)                   | Baseline / constraint                                 |
| ---------------------------------- | ------------------------------------ | ----------------------------------------------------- |
| MIMO channel estimation            | Normalized Validation Error (lower)  | LS estimator with linear interpolation, NVE ≈ 94      |
| Channel estimation with covariance | NVE (lower)                          | Second-order statistics enable LMMSE-based approaches |
| Link adaptation (MCS selection)    | Average spectral efficiency (higher) | Long-term BLER must remain ≤ 10%                      |

- Channel estimation: `mimo_detector(y, no) -> llr`, using an LMMSE equalizer and APP
  demapper; the channel estimate is a 7D tensor
  `[batch, num_rx, num_rx_ant, num_tx, streams_per_tx, ofdm_symbols, fft_size]`.
- Link adaptation: `mcs_selection(is_nack_hist, mcs_ackned_hist, bler_target) -> int`,
  with `get_bler(sinr)` and `bler_2_mcs(bler, bler_target)` provided at evaluation time.
  The challenge is balancing aggressive MCS selection against reliability.

## Principles

- **Diversity over depth**: genuinely different algorithm families explore the solution
  space better than variations of one approach.
- **Structured evaluation**: every iteration produces a comparable metric.
- **Self-contained solutions**: no cross-file imports beyond the provided objects.
