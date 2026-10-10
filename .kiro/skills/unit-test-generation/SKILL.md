---
name: unit-test-generation
description: >
  Deep test-scenario enumeration for a target module or function: happy path, edge
  cases, error handling, input validation, and state management, using the AAA pattern
  and disciplined mocking. Use when a unit under test needs systematic scenario coverage
  beyond a quick pytest pass, or when test cases feel incomplete or ad-hoc. Triggers:
  'generate unit tests', 'enumerate test cases', 'cover edge cases', 'write
  comprehensive tests for this function'. Not for the baseline pytest workflow (naming,
  fixtures, coverage target) — that is covered by `senior-developer`'s implementation
  steps and the `code-standards` skill. Not for integration/e2e tests, fixing failing
  tests (use `debugging`), or ML model quality tests (use `ml-model-testing`).
---

# Unit Test Generation

Language-agnostic scenario enumeration technique. Assumes the baseline pytest
conventions (naming, fixtures, 80% coverage target) from `code-standards` are already in
effect — this skill adds systematic scenario coverage on top of that baseline, not a
replacement for it.

## Scenario Categories

For each unit under test, enumerate scenarios in all five categories before writing any
test:

1. **Happy path** — expected inputs produce correct outputs.
2. **Edge cases** — boundary values, empty inputs, nulls, max/min limits.
3. **Error handling** — invalid inputs throw or return the appropriate errors.
4. **Input validation** — malformed, missing, or out-of-range parameters.
5. **State management** — side effects, mutations, and state transitions behave
   correctly.

If a function has N distinct code paths (branches), aim for at least N tests — one per
path, not one test asserting on multiple paths.

## Test Structure

- **Naming**: `test_<action>_<scenario>_<expected>` (e.g.
  `test_parse_config_missing_key_raises_value_error`).
- **AAA pattern**: each test has a distinct Arrange, Act, Assert — no interleaving.
- **Independent and isolated**: no shared mutable state; tests must pass in any
  execution order.
- **One behavior per test**: prefer several focused tests over one large test with
  multiple assertions on unrelated behaviors.

## Mocking Discipline

- Mock external dependencies only: I/O, network calls, time (`datetime.now`), random
  sources, third-party APIs.
- Never mock the unit under test itself, or internal collaborators that are cheap and
  deterministic to run for real.
- Assert on interaction (call args, call count) only when the interaction itself is the
  behavior being tested — not as a substitute for asserting on output.
- Before finalizing a suite, check it against the anti-patterns in
  `references/testing-anti-patterns.md` — tautological tests (expected value recomputed
  the same way the code computes it) and implementation-detail tests (coupled to
  internal structure rather than observable behavior) are the two that recur most.

## Workflow

1. Read the target module's source: public API surface and internal branching logic.
2. Enumerate scenarios per category above; skip categories genuinely not applicable
   (state management for a pure function) and say so explicitly rather than omitting
   silently.
3. Write tests following the naming and AAA structure, using the project's existing test
   framework and fixtures (see `code-standards` for conventions).
4. Run the test suite; confirm all new tests pass and no regressions were introduced.

## Critical Rules

- Never modify production code — only produce test files.
- Never hardcode secrets or real credentials in test fixtures; use synthetic data.
- Do not import or execute code with destructive side effects during test discovery.

## Owning agents

`senior-developer` (application code) and `ai-engineer` (ML pipeline / feature
engineering code). For ML model quality tests (stratified metrics, invariance tests),
use `ml-model-testing` instead — this skill covers deterministic unit-level code only.
