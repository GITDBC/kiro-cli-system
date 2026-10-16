---
name: ralph-loop
description: >
  Iterative autonomous loop in two modes: an external time-budgeted loop of fresh
  kiro-cli sessions (ralph.sh) and an in-session loop driven by a Stop hook
  (ralph-session.sh). Triggers: 'ralph loop', 'autonomous loop', 'run for N hours',
  'iterative development', 'start/cancel/status session loop', 'keep working until
  done'. Not for single-shot tasks or judgement-driven work.
---

# Ralph Loop — Iterative Autonomous Development

## Choosing a mode

| Mode                            | Use for                                     | Context               | Driver                      |
| ------------------------------- | ------------------------------------------- | --------------------- | --------------------------- |
| External (`ralph.sh`)           | Long unattended runs (hours), time budgets  | Fresh every iteration | Bash loop over `kiro-cli`   |
| In-session (`ralph-session.sh`) | Short interactive tasks, a few to ~20 turns | Persists across turns | `Stop` hook `ralph-stop.sh` |

Pick the external loop when the run must outlast one context window or run unattended;
fresh context avoids degradation, and the progress file carries memory. Pick the
in-session loop when the user is present and the task benefits from the conversation
history.

## Writing the task prompt

Both modes re-send the same prompt every iteration, so it must stand on its own:

- **Clear completion criteria** — state what "done" means in checkable terms (tests
  green, coverage ≥ X, command Y succeeds), and tie the promise phrase to them.
- **Incremental phases** — list the steps in order, so each iteration can locate the
  next one from the files and test output.
- **Self-correction** — tell the agent to run the tests after every change and fix
  failures before moving on.
- **Escape hatch** — "after N iterations without success, document the blockers, what
  was attempted, and the alternatives considered" — rather than a false promise.

Do not use either loop for judgement or design decisions, one-shot tasks, tasks with
unclear success criteria, or production debugging.

## External loop (`ralph.sh`)

Prerequisites: `kiro-cli` installed and authenticated, `python3`, and an isolated
environment (devcontainer recommended).

```bash
.kiro/skills/ralph-loop/ralph.sh --time 3h "Implement REST API with CRUD and tests"
.kiro/skills/ralph-loop/ralph.sh --max 10 "Fix authentication bug"
.kiro/skills/ralph-loop/ralph.sh --time 2h --agent my-agent --promise "FINISHED" "Task"
```

1. **Implementation phase** — iterate until the agent emits `<promise>DONE</promise>`.
2. **Hardening phase** — with time left, one verification area per iteration (lint,
   coverage, error handling, integration, performance, security).

Each iteration writes `.kiro/ralph-state.json` atomically, runs
`kiro-cli chat --no-interactive --trust-all-tools` with a fresh prompt, and compares the
text of the last `<promise>…</promise>` in the log literally (whitespace normalised)
with the promise phrase. The default agent is `senior-developer`, per the Autonomous
loop row of `routing.md`. Arguments are validated strictly (`--time` grammar
`1h30m`/`45m`/`90s`/bare minutes, numeric `--max`, non-empty prompt and promise).

Safety mechanisms:

- **Stagnation detection**: the tree fingerprint (`fingerprint.sh`: `git diff HEAD` plus
  untracked files, excluding `.kiro/ralph-*`) is compared before and after each
  iteration; 3 consecutive unchanged iterations halt the run. A non-zero `kiro-cli` exit
  is logged and counted, not fatal.
- **Blockers & Lessons**: progress-file section recording failed approaches and
  autonomous decisions; each iteration reads it first.
- **Non-stop conditions and autonomous mode**: `non_stop_rules` and
  `autonomous_mode_rules` are emitted into every iteration prompt, together with the
  rule that the promise is output only when unequivocally true.
- **Test-change warning**: modified test files are listed in
  `.kiro/ralph-test-changes.log` and on stdout; review them before trusting green
  results.

This skill is not loaded inside iteration sessions, so any directive that must govern an
iteration belongs in `build_prompt` in `ralph.sh`. The time budget is soft: the current
iteration always finishes.

## In-session loop (`ralph-session.sh`)

When the user asks to start, check, or cancel a session loop, run the script through the
shell from the repository root:

```bash
.kiro/skills/ralph-loop/ralph-session.sh start "PROMPT" [--max N] [--promise TEXT]
.kiro/skills/ralph-loop/ralph-session.sh status
.kiro/skills/ralph-loop/ralph-session.sh cancel
```

`start` writes `.kiro/ralph-session.local.md` (frontmatter plus the prompt) and prints
the task; begin working on it in the same turn. Each time the turn ends, the `Stop` hook
`.kiro/hooks/ralph-stop.sh` re-submits the same prompt and bumps the iteration. It lets
the turn end, deleting the state, when:

- the iteration limit is reached — `--max` defaults to 20; `--max 0` (unlimited) is
  accepted only together with `--promise` and prints a warning;
- `.kiro/ralph-session.promise` contains `<promise>TEXT</promise>` matching the promise
  literally (whitespace normalised). Write that file only when the statement is
  completely and unequivocally true; never write a false promise to escape the loop;
- 3 consecutive iterations leave the working tree unchanged;
- the state is corrupt or `python3` is missing (fail open, warning on stderr).

`--session ID` binds the loop to one session id (for example `$KIRO_SESSION_ID`); Stop
events carrying another `session_id` are ignored. Unbound by default, because the Stop
payload fields have not been confirmed against a live run. An unbound loop continues
whichever session in this workspace ends a turn next, so start it from the session that
should loop, not from a delegated subagent, and avoid concurrent sessions meanwhile.
