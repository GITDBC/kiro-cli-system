---
name: debugging
description: >
  Systematic debugging workflow for complex bugs. Use when a bug is reproducible but
  root cause is unclear, test failures have non-obvious origins, or performance
  regressions need isolation. Triggers: 'why is this failing', 'investigate bug', 'root
  cause analysis', 'trace the issue', 'find the bug', 'debug this'. Not for simple typos
  or known fixes. Uses analyst+validator pattern with hypothesis-driven investigation.
---

# Debugging Workflow

Delegate to **senior-developer** using the analyst+validator pattern below.

## Invocation

Use when: bug is reproducible but root cause unclear · test failures have non-obvious
origins · performance regressions need isolation · user asks "why is this failing / find
the bug / root cause analysis".

Do NOT use when: fix is already known · simple typo or config error visible in the error
message · missing feature (not a bug).

## Phase 0 — Evidence Gathering (Analyst, read-only; serves as Preflight)

Collect: error messages, stack traces, logs, relevant source code, recent git changes,
environment/config state.

Produce a **Hypothesis Document**:

```markdown
## Hypothesis Document

**Symptom summary**: [precise description of observed behavior] **Expected behavior**:
[what should happen instead] **Red command**: [deterministic, agent-runnable command
that reproduces the failure, and its observed output] **Evidence collected**:

- [evidence item 1]
- [evidence item 2]

**Hypotheses** (ranked by likelihood):

1. [Hypothesis A] — Likelihood: high/medium/low
   - Supporting evidence: [...]
   - Falsification test: [...]
2. [Hypothesis B] — Likelihood: high/medium/low
   - Supporting evidence: [...]
   - Falsification test: [...]
3. [Hypothesis C] — Likelihood: high/medium/low
   - Supporting evidence: [...]
   - Falsification test: [...]

**Recommended investigation order**: [cheapest falsification first]
```

No code changes during Phase 0.

**Gate — no red-capable command, no hypothesis.** A hypothesis may not be recorded until
a tight, deterministic, agent-runnable command that reproduces the failure exists and
has been run at least once, showing the failure. That command is the Hypothesis
Document's first required entry. Until it exists, the only permitted work is producing
one: narrow the case, fix the environment, or state that the failure is not reproducible
and stop. A hypothesis formed before it is an assertion no falsification test can
settle, and the phases below all assume a red command to work against — Phase 3
isolation halves an input that must fail on one side, and Phase 4 validation compares
before and after on the same command.

For patterns on classifying failures from test output (flaky vs deterministic, error
signatures) when the bug surfaced as a test failure, load
`references/test-results-analysis-patterns.md`.

## Phase 1 — Reproduce and Characterize

- Confirm reproduction steps (minimal case).
- Capture environment: OS, versions, config.
- Collect signals: error messages, logs, stack traces.
- Define "working" vs "broken" boundary conditions.

## Phase 2 — Hypothesize

- Refine hypotheses from Phase 0 using reproduction results.
- For each hypothesis, define a falsification test.
- Identify cheapest test to run first.

## Phase 3 — Isolate

Choose strategy by bug type:

- **Binary search (bisect)**: bug introduced between two known states — use `git bisect`
  or manual halving.
- **Divide and conquer**: disable components until bug disappears.
- **Trace analysis**: follow execution path from input to unexpected output.
- **Differential debugging**: compare working vs broken environments/inputs.

Tag every diagnostic log statement added while isolating with a run-unique marker —
`[DEBUG-<id>]`, as in `logger.debug("[DEBUG-a4f2] cursor=%s", cursor)` — using one id
for the whole investigation. Removal is then a single `grep -rn "\[DEBUG-a4f2\]"`, so no
diagnostic statement reaches the fix by being overlooked.

## Phase 4 — Fix

- Write a failing test capturing the bug.
- Implement the minimal fix.
- Confirm the test passes.
- Remove every `[DEBUG-<id>]` statement, and confirm by grep that none remains.

## Phase 5 — Validation (Validator Role)

The senior-developer switches to validator:

1. Re-read the original symptom from the Hypothesis Document.
2. State the root-cause link explicitly: which line(s) changed, and which falsification
   test from the Hypothesis Document now passes because of that change.
3. Run full regression test suite.
4. Check for side effects in adjacent code paths.
5. Check if same bug pattern exists elsewhere in the codebase.

Verdict: **ACCEPT** or **REJECT** with justification.

## Iterative Loop (Max 3 Iterations)

On **REJECT**: record reason, update Hypothesis Document, return to Phase 3 with refined
hypotheses.

On 3 exhausted iterations: produce report of all attempted fixes and escalate to user.

## Output Format

```markdown
## Debugging Report

**Symptom**: [what was observed] **Root Cause**: [why it happened] **Fix**: [what was
changed] **Iterations**: [N/3] **Validation**: [verdict + justification] **Tests**:
[tests added/passed] **Regression check**: [full suite result] **Prevention**: [how to
avoid recurrence]
```

## Safety

- Do NOT modify production data or state during investigation.
- Phase 0 is strictly read-only.
- Destructive testing requires isolated environments.
