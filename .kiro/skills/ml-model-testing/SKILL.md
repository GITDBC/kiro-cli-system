---
name: ml-model-testing
description: >
  ML model testing strategy and evaluation workflow. Use when designing tests for ML
  models, evaluating model quality, or setting up ML test infrastructure. Triggers:
  'test ML model', 'model evaluation', 'ML test strategy'. Not for general unit testing
  (use the unit-test-generation skill) or data pipeline testing (use data-pipeline
  skill).
---

# ML Model Testing

## Workflow

### Step 1 — Test strategy design → `ai-engineer`

For test-type selection heuristics and model-quality test examples, load
`references/ai-engineer-patterns.md`.

Design a test strategy covering all types below:

**Software tests:**

- **Unit tests**: pure functions for data processing, feature engineering,
  transformations. Maximize deterministic core; minimize side-effect shell.
- **Training smoke tests**: full pipeline with ~10 samples; must complete in 1-2 minutes
  locally.
- **API tests**: contract tests asserting on the complete response object (not piecemeal
  fields).
- **Post-deployment tests**: verify deployed API with real dependencies; do NOT
  duplicate API test logic.

**Model quality tests:**

- **Global metrics**: overall performance against threshold (accuracy, F1, etc.).
- **Stratified metrics**: slice validation data by key dimensions; detect hidden
  stratification (global accuracy improves but a segment drops). Usable for bias
  testing.
- **Invariance tests**: perturb input on invariant dimension; assert prediction
  unchanged.
- **Directional expectation tests**: perturb input on a known-effect dimension; assert
  prediction changes in expected direction.

**Data tests:**

- **Data contract**: schema, attribute names, types, constraints.
- **Data pipeline**: accuracy, completeness, consistency, representativeness,
  timeliness.
- **Data privacy**: no PII (names, IDs, addresses) reaches the model.

For each test type specify: what to test, example assertions, where it runs
(local/CI/post-deploy), expected execution time.

### Step 2 — Results analysis → `qa-engineer`

If test results are available (pytest output, metrics, coverage reports):

- Analyze against the strategy from Step 1.
- Flag any test type with zero coverage.
- Check stratified metrics for hidden performance drops.

Produce a test health report:

| Test type | Status | Coverage | Gaps |
| --------- | ------ | -------- | ---- |

## Output

A single Markdown document with:

1. **Test Strategy** — complete test plan organized by test type
2. **Test Health** (if results available) — current state vs desired state
3. **Priority Gaps** — missing tests ordered by risk
4. **Quick Wins** — tests addable with minimal effort for maximum safety

## Success Criteria

- All 7 test types addressed (even if "not applicable").
- Each recommended test includes a concrete example or pseudocode.
- Gaps prioritized by risk, not just listed.
