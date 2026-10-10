---
name: ralph-loop
description: >
  Autonomous iterative development loop with time budget. Executes a task via kiro-cli
  in repeated sessions, discarding context each iteration to avoid degradation. Supports
  time-based budgets (e.g. 3 hours) where the agent implements first, then uses
  remaining time for verification, testing, and hardening. Triggers: 'ralph loop',
  'autonomous loop', 'run for N hours', 'iterative development'. Not for single-shot
  tasks or interactive work.
---

# Ralph Loop — Time-Budgeted Autonomous Development

## Prerequisites

- `kiro-cli` installed and authenticated
- Bash shell with `date` command
- Run in an isolated environment (devcontainer recommended)

## Usage

```bash
.kiro/skills/ralph-loop/ralph.sh --time 3h "Implement REST API with CRUD and tests"
.kiro/skills/ralph-loop/ralph.sh --max 10 "Fix authentication bug"
.kiro/skills/ralph-loop/ralph.sh --time 3h --max 20 "Build feature X"
.kiro/skills/ralph-loop/ralph.sh --time 2h --agent my-agent "Task description"
.kiro/skills/ralph-loop/ralph.sh --time 1h --promise "FINISHED" "Task description"
```

## Two-Phase Time Budget

1. **Implementation phase** — Implement iteratively until agent signals
   `<promise>DONE</promise>`.
2. **Hardening phase** — Remaining time: run tests, create new tests, check edge cases,
   verify conventions, hunt bugs, improve coverage.

## Per-Iteration Behavior

1. Write state to `.kiro/ralph-state.json`.
2. Run `kiro-cli chat --no-interactive --trust-all-tools`.
3. Verify prior work (tests/lints) before writing new code — fix failures before
   advancing.
4. Check output for completion promise.
5. If done + time remaining → switch to hardening prompt.
6. If time/iterations exhausted → stop.

## Safety Mechanisms

- **Stagnation detection**: if 3 consecutive iterations produce no file changes
  (`git diff`), halt with warning.
- **Blockers & Lessons**: progress file section recording failed approaches; each
  iteration reads it first and never repeats a failed approach.
- **Circuit breaker**: max 3 retry attempts per agent task before escalation.
- **Non-stop conditions**: a failing test, a lint error, "I don't know how", an approach
  already tried twice, or a shrinking time budget are problems to work through, not
  reasons to stop. The loop halts only on the completion promise, budget exhaustion, or
  stagnation detection. Genuine infrastructure failure (missing interpreter or CLI,
  unavailable credentials) is the sole exception and is recorded as a blocker. These
  conditions are emitted into every iteration prompt by `non_stop_rules` in `ralph.sh`;
  the bullet here documents them for the reader.
- **Test-change warning**: every iteration lists modified test files to
  `.kiro/ralph-test-changes.log` and warns on stdout. The guard warns, never blocks —
  authoring tests is the purpose of the hardening phase — so the surfaced diffs must be
  reviewed before a green report is trusted.

## State File

`.kiro/ralph-state.json` read by the agent each iteration:

```json
{
  "phase": "implement",
  "iteration": 3,
  "startedAt": "2026-05-18T08:00:00Z",
  "timeBudgetSeconds": 10800,
  "timeRemainingSeconds": 7200,
  "completedAt": null,
  "prompt": "Build REST API...",
  "completionPromise": "DONE"
}
```

## Agent Steering

The script conveys per-iteration guidance through two channels, and no temporary
steering file is involved. This skill file is not loaded inside iteration sessions
either: skills activate by matching their description against the request, and each
iteration's request concerns the user's task rather than the loop. Any directive that
must govern an iteration therefore belongs in `build_prompt`.

| Channel                                                 | Carries                                                                                                                                             |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Iteration prompt (`build_prompt`, passed to `kiro-cli`) | Phase instructions, iteration count, time remaining, task prompt, critical rules, the non-stop conditions, and the autonomous-mode resolution rules |
| `.kiro/ralph-state.json` and `.kiro/ralph-progress.md`  | Phase, iteration, budget, completion promise, prior-iteration log and the Blockers & Lessons section, read first each iteration                     |

## Rules

- Always run in an isolated environment.
- `--trust-all-tools` means the agent can execute ANY command — do not leave unattended
  on production systems.
- Agent must output `<promise>DONE</promise>` to signal implementation complete.
- Time budget is soft — current iteration always finishes.

## Done when

- Time budget exhausted, OR max iterations reached, OR hardening phase signals DONE
  again.
