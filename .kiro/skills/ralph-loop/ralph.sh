#!/usr/bin/env bash
# Ralph Loop — Time-budgeted autonomous development loop.
# Runs kiro-cli iteratively, discarding context each session.
# Supports time budgets (--time 3h) and/or iteration limits (--max 20).
# Uses .kiro/ralph-progress.md as persistent memory between iterations.
set -euo pipefail

# --- Defaults ---
TIME_BUDGET=""
MAX_ITERATIONS=0
AGENT="senior-developer"  # routing.md: Autonomous loop → senior-developer
PROMISE="DONE"
STATE_FILE=".kiro/ralph-state.json"
PROGRESS_FILE=".kiro/ralph-progress.md"
LOG_DIR=".kiro/ralph-logs"
TAMPER_LOG=".kiro/ralph-test-changes.log"

# --- Parse arguments ---
usage() {
  cat <<EOF
Usage: ralph.sh [OPTIONS] "TASK PROMPT"

Options:
  --time TIME       Time budget (e.g. 30m, 2h, 1h30m, 90s; a bare number is minutes).
                    Required unless --max is set.
  --max N           Maximum iterations (0=unlimited). Default: 0.
  --agent NAME      Kiro agent name. Default: senior-developer.
  --promise PHRASE  Completion signal phrase. Default: DONE.
  -h, --help        Show this help.

Examples:
  ralph.sh --time 3h "Implement user authentication with tests"
  ralph.sh --max 10 "Fix the parsing bug in src/parser.py"
  ralph.sh --time 2h --max 15 "Build data pipeline"
EOF
  exit "${1:-0}"
}

die() {
  echo "Error: $1" >&2
  exit 1
}

# Changed: strict whole-string grammar - Reason: the previous substring regexes accepted
# inputs such as "abc5m" or "2h30x" and silently ignored the junk.
parse_time() {
  local input="$1" hours=0 minutes=0
  if [[ "$input" =~ ^[0-9]{1,6}$ ]]; then
    echo $((10#$input * 60))
  elif [[ "$input" =~ ^[0-9]{1,6}s$ ]]; then
    echo $((10#${input%s}))
  elif [[ "$input" =~ ^(([0-9]{1,4})h)?(([0-9]{1,6})m)?$ && -n "$input" ]]; then
    [[ -n "${BASH_REMATCH[2]}" ]] && hours=$((10#${BASH_REMATCH[2]}))
    [[ -n "${BASH_REMATCH[4]}" ]] && minutes=$((10#${BASH_REMATCH[4]}))
    echo $((hours * 3600 + minutes * 60))
  else
    echo 0
  fi
}

# Collapses whitespace runs to one space and trims, so promise comparison is literal
# but insensitive to line wrapping.
normalise() {
  local text
  text="$(printf '%s' "$1" | tr -s '[:space:]' ' ')"
  text="${text#' '}"
  printf '%s' "${text%' '}"
}

require_value() {
  [[ $# -ge 2 && -n "$2" ]] || die "$1 requires a value."
}

PROMPT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --time) require_value "$@"; TIME_BUDGET="$2"; shift 2 ;;
    --max) require_value "$@"; MAX_ITERATIONS="$2"; shift 2 ;;
    --agent) require_value "$@"; AGENT="$2"; shift 2 ;;
    --promise) require_value "$@"; PROMISE="$2"; shift 2 ;;
    -h|--help) usage ;;
    -*) die "unknown option: $1" ;;
    *)
      [[ -z "$PROMPT" ]] || die "the task prompt must be a single quoted argument."
      PROMPT="$1"; shift ;;
  esac
done

if [[ -z "${PROMPT//[[:space:]]/}" ]]; then
  echo "Error: task prompt is required." >&2
  usage 1
fi

# --- Calculate time budget ---
BUDGET_SECONDS=0
if [[ -n "$TIME_BUDGET" ]]; then
  BUDGET_SECONDS=$(parse_time "$TIME_BUDGET")
  if [[ "$BUDGET_SECONDS" -eq 0 ]]; then
    die "invalid time format '$TIME_BUDGET'. Use e.g. 30m, 2h, 1h30m, 90s."
  fi
fi

if ! [[ "$MAX_ITERATIONS" =~ ^[0-9]{1,6}$ ]]; then
  die "--max must be an integer from 0 to 999999, got '$MAX_ITERATIONS'."
fi
MAX_ITERATIONS=$((10#$MAX_ITERATIONS))  # "010" must not be read as octal

[[ "$AGENT" =~ ^[A-Za-z0-9_.-]+$ ]] || die "--agent contains unsupported characters."

PROMISE="$(normalise "$PROMISE")"
[[ -n "$PROMISE" ]] || die "--promise must not be empty."
if [[ "$PROMISE" == *"<"* || "$PROMISE" == *">"* ]]; then
  die "--promise must not contain '<' or '>'."
fi

if [[ "$BUDGET_SECONDS" -eq 0 && "$MAX_ITERATIONS" -eq 0 ]]; then
  die "must specify --time or --max (or both)."
fi

command -v python3 >/dev/null 2>&1 || die "python3 is required (state file and promise check)."

# --- Setup ---
START_EPOCH=$(date +%s)
START_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
mkdir -p "$LOG_DIR" "$(dirname "$STATE_FILE")"
rm -f "$TAMPER_LOG"  # Always fresh: the log is a per-run timeline

# Initialize progress file (always fresh for new loop)
cat > "$PROGRESS_FILE" <<MD
# Ralph Loop Progress

## Task
$PROMPT

## Environment Notes
- Prefix every Python and CLI invocation with uv run
- Do NOT run git commit — only git add

## Blockers & Lessons
<!-- Record what went wrong, what you tried that didn't work, and key learnings.
     Future iterations MUST read this before starting. -->

## Iteration Log
MD

echo "╔══════════════════════════════════════════════════════════╗"
echo "║              RALPH LOOP — Starting                       ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║ Task: ${PROMPT:0:50}"
[[ -n "$TIME_BUDGET" ]] && echo "║ Time budget: $TIME_BUDGET ($BUDGET_SECONDS seconds)"
[[ "$MAX_ITERATIONS" -gt 0 ]] && echo "║ Max iterations: $MAX_ITERATIONS"
echo "║ Agent: $AGENT"
echo "║ Promise: <promise>$PROMISE</promise>"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# --- Helper: time remaining ---
time_remaining() {
  if [[ "$BUDGET_SECONDS" -eq 0 ]]; then
    echo "999999"
    return
  fi
  local now
  now=$(date +%s)
  local elapsed=$((now - START_EPOCH))
  local remaining=$((BUDGET_SECONDS - elapsed))
  echo "$remaining"
}

# --- Helper: write state file ---
write_state() {
  local phase="$1"
  local iteration="$2"
  local completed_at="${3:-null}"
  local remaining
  remaining=$(time_remaining)

  # Changed: JSON-escape every string and write via tmp + mv - Reason: an unescaped
  # promise could corrupt the JSON, and a reader must never see a half-written file.
  local tmp
  tmp="$(mktemp "${STATE_FILE}.XXXXXX")"
  cat > "$tmp" <<JSON
{
  "phase": "$phase",
  "iteration": $iteration,
  "startedAt": "$START_ISO",
  "timeBudgetSeconds": $BUDGET_SECONDS,
  "timeRemainingSeconds": $remaining,
  "completedAt": $completed_at,
  "prompt": $(json_string "$PROMPT"),
  "completionPromise": $(json_string "$PROMISE"),
  "progressFile": "$PROGRESS_FILE"
}
JSON
  mv -f -- "$tmp" "$STATE_FILE"
}

json_string() {
  printf '%s' "$1" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))"
}

# --- Helper: exact completion-promise check ---
# Changed: literal comparison of the LAST <promise>…</promise> in the log, whitespace
# normalised and ANSI-stripped - Reason: the former `grep -qi "<promise>$PROMISE…"` was a
# case-insensitive regex substring match, so metacharacters in the phrase or a merely
# similar phrase could end the loop.
promise_found() {
  python3 - "$1" "$PROMISE" <<'PY'
import re
import sys

log_path, promise = sys.argv[1:3]
try:
    with open(log_path, encoding="utf-8", errors="replace") as handle:
        text = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", handle.read())
except OSError:
    sys.exit(1)
tags = re.findall(r"<promise>(.*?)</promise>", text, re.S)
sys.exit(0 if tags and " ".join(tags[-1].split()) == promise else 1)
PY
}

# --- Helper: non-stop conditions (injected into every iteration prompt) ---
# The iteration prompt is the only channel that reliably reaches the agent: skills load
# by model-side description matching, so ralph-loop/SKILL.md cannot be relied on inside
# the sessions it governs. These rules are therefore stated inline in both phases.
non_stop_rules() {
  cat <<'RULES'
## Non-stop conditions
The following are problems to work through, not reasons to stop or idle:
- A failing test or a lint error — diagnose and fix it. That is the work.
- "I don't know how" — read the code, read the docs, run the smallest experiment.
- An approach already tried twice — switch to a different approach rather than retrying it.
- A shrinking time budget — do the smallest useful piece of work now, then report it.

Do not end an iteration having only reported that something is blocked. Take the next
concrete action and leave the tree closer to green than you found it.

A message with no tool call ends the iteration. Avoid these early stops while work is
still owed: a summary that announces the next step instead of taking it; an offer to
continue unless told otherwise; a list of decisions when none of them blocks the rest of
the work; deciding this is a good place to report because the turn was long or a
milestone is done. Put status notes in the same message as your next tool call.

The single exception is genuine infrastructure failure (interpreter or CLI missing,
credentials unavailable, no network for a required install): record it under
"Blockers & Lessons" and stop, because no amount of iteration resolves it. Nothing here
overrides caution on risky or irreversible actions: take the reversible option or mark
the step deferred.

This loop halts only on the completion promise, budget exhaustion, or stagnation
detection — not on your own assessment that the remaining work is hard.
RULES
}

# --- Helper: autonomous mode (injected into every iteration prompt) ---
# delegation-lifecycle.md mandates `mode: autonomous` for non-interactive workflows and
# `.kiro/orchestration/preflight-report-format.md` (`## Autonomous Mode`) defines the
# resolution rules, but neither reaches the agent on its own, so
# they are compressed inline alongside the non-stop conditions. Decisions are routed to
# "Blockers & Lessons" because that is the only progress-file section this script
# creates and the only one every iteration is required to read before starting.
autonomous_mode_rules() {
  cat <<'RULES'
## AUTONOMOUS MODE
This session is non-interactive and unattended: no user can answer a question, so asking
one is not an available action. Resolve the uncertainty yourself and proceed.
- Ambiguity → take the most conservative option.
- Blocker needing another agent or capability → take an alternative route; if none
  exists, mark the item deferred and carry on with the next one instead of failing.
- High-risk assumption → take the reversible option.
- Unclear scope → implement the minimal interpretation.

Record each such decision and its reasoning under "Blockers & Lessons" in
.kiro/ralph-progress.md, so the next iteration inherits it rather than re-deciding.
RULES
}

# --- Helper: build prompt for phase ---
build_prompt() {
  local phase="$1"
  local iteration="$2"
  local remaining
  remaining=$(time_remaining)
  local remaining_min=$((remaining / 60))
  # Elapsed-vs-budget line for the implement phase; the model paces against it.
  local time_line=""
  if [[ "$BUDGET_SECONDS" -gt 0 ]]; then
    local elapsed_min=$((($(date +%s) - START_EPOCH) / 60))
    time_line="Time: ${elapsed_min} of $((BUDGET_SECONDS / 60)) minutes elapsed (~${remaining_min} remaining)."
  fi

  if [[ "$phase" == "implement" ]]; then
    cat <<PROMPT
You are in a Ralph Loop (iteration $iteration). Read .kiro/ralph-progress.md for context.
$time_line

## Your Task
$PROMPT

## Instructions (in order)
1. Read .kiro/ralph-progress.md to see what was done in previous iterations.
   - Pay special attention to the "Blockers & Lessons" section.
   - If a previous iteration reported a blocker or failed approach, do not repeat it.
2. Verify previous work first (required when iteration > 1):
   - Run tests/lints on all code produced in prior iterations.
   - If any test fails, a lint error exists, or previous work is broken, fix it first.
   - Move on to step 3 only once all prior work passes verification.
   - Log what you verified and the results in the progress file.
3. Only after prior work is verified green: identify what remains to be done.
4. Implement the next piece of work.
5. Run tests to verify your new changes work (together with prior work).
6. If tests fail, fix immediately. Do not leave broken code for the next iteration.
7. Stage your changes with git add (do not commit — the user will review and commit).
8. Update .kiro/ralph-progress.md with:
   - Verification results from step 2 (what passed, what you fixed).
   - What you implemented in step 4.
   - Test results from step 5.
   - If something failed or you hit a dead end, add it to the "Blockers & Lessons"
     section so future iterations avoid the same mistake.

## Rules
- Do not run git commit. Only git add to stage changes.
- Do not run persistent/blocking commands (servers, watchers).
- Prefix every Python and CLI invocation with uv run.
- Do not assume prior work is correct — run the verification commands.
- If you find yourself implementing new features while tests from prior iterations fail, stop and fix those first.

$(non_stop_rules)

$(autonomous_mode_rules)

## Completion
When the task is complete (all requirements met, all tests passing):
- Run the full test suite one final time to confirm everything is green.
- Output: <promise>$PROMISE</promise>

Do not output the promise if work remains or if any test is failing. Output it only when
the statement is completely and unequivocally true. Never output a false promise to
escape the loop, even if you believe you are stuck: record the blocker under
"Blockers & Lessons" and keep working instead.
PROMPT
  else
    cat <<PROMPT
You are in a Ralph Loop hardening phase (iteration $iteration). Time remaining: ~${remaining_min} minutes.
Read .kiro/ralph-progress.md for context.

## Original Task (already implemented)
$PROMPT

## Hardening Instructions
The implementation is complete. Read .kiro/ralph-progress.md to see what was already verified.
Do not repeat checks that previous iterations already performed.

Pick one of these areas that has not been done yet (check progress file):

1. **Run linters/formatters**: Execute make lint, ruff, mypy, or equivalent. Fix issues found.
2. **Improve test coverage**: Write new tests for uncovered edge cases. Run them.
3. **Check error handling**: Test with invalid inputs, verify error messages are clear.
4. **Verify integration**: Import the module from another script, verify it works in context.
5. **Performance check**: Time the main code path on a representative input. Report numbers.
6. **Security review**: Check for injection, hardcoded secrets, unsafe operations.

Every hardening iteration executes at least one command (test, lint, benchmark).
Reading code and saying "looks good" is not sufficient; show it with execution.

After completing your check, update .kiro/ralph-progress.md with what you verified and the results.
Stage any new/modified files with git add (do not commit).

## Rules
- Do not run git commit. Only git add to stage changes.
- Do not repeat work already logged in .kiro/ralph-progress.md.
- Prefix every Python and CLI invocation with uv run.
- Focus on one area per iteration.
- Run at least one verification command per iteration.

$(non_stop_rules)

$(autonomous_mode_rules)

## Completion
Output <promise>$PROMISE</promise> after completing your verification check, and only if
that check actually ran in this iteration. Never output a false promise.
There are ~${remaining_min} minutes remaining.
PROMPT
  fi
}

# --- Circuit breaker: stagnation detection ---
CONSECUTIVE_NO_PROGRESS=0
MAX_NO_PROGRESS=3  # Halt after 3 iterations without file changes

# Fingerprint the working tree with the logic shared with the in-session Stop hook
# (fingerprint.sh): tracked changes against HEAD plus untracked files, excluding every
# .kiro/ralph-* runtime file the loop rewrites each iteration.
# shellcheck source=fingerprint.sh
source "$(dirname "${BASH_SOURCE[0]}")/fingerprint.sh"

snapshot_tree() {
  ralph_snapshot_tree
}

detect_progress() {
  local before="$1"
  [[ "$before" != "$(snapshot_tree)" ]]
}

# --- Guard: flag modifications to test files ---
# The agent grades itself against the repository's own suite. A weakened assertion
# produces a green report indistinguishable from real progress, so every touched test
# file is surfaced each iteration and in the final summary. Warns, never blocks:
# authoring tests is the point of the hardening phase.
# Range is HEAD because the loop forbids git commit — staged and unstaged changes are
# both relative to the pre-run commit, so a bare `git diff` would miss staged files.
report_test_changes() {
  local iteration="$1"
  local touched
  touched=$(git diff --name-only HEAD 2>/dev/null \
    | grep -E '(^|/)tests?/|(^|/)test_[^/]*\.py$|_test\.py$' || true)
  if [[ -n "$touched" ]]; then
    printf 'iteration %s:\n%s\n' "$iteration" "$touched" >> "$TAMPER_LOG"
    echo "⚠️  Test files modified in this run — review before trusting green results:"
    echo "$touched" | sed 's/^/     /'
  fi
}

# --- Main loop ---
ITERATION=0
PHASE="implement"
COMPLETED_AT="null"

trap 'echo ""; echo "Interrupted at iteration $ITERATION (phase: $PHASE)"; write_state "$PHASE" "$ITERATION" "$COMPLETED_AT"; exit 1' INT TERM

while true; do
  ITERATION=$((ITERATION + 1))

  # Check time budget
  REMAINING=$(time_remaining)
  if [[ "$BUDGET_SECONDS" -gt 0 && "$REMAINING" -le 0 ]]; then
    echo ""
    echo "⏰ Time budget exhausted after $ITERATION iterations."
    break
  fi

  # Check iteration limit
  if [[ "$MAX_ITERATIONS" -gt 0 && "$ITERATION" -gt "$MAX_ITERATIONS" ]]; then
    echo ""
    echo "🔄 Max iterations ($MAX_ITERATIONS) reached."
    break
  fi

  # Circuit breaker check
  if [[ "$CONSECUTIVE_NO_PROGRESS" -ge "$MAX_NO_PROGRESS" ]]; then
    echo ""
    echo "🚨 CIRCUIT BREAKER: $MAX_NO_PROGRESS consecutive iterations without progress."
    echo "   The agent may be stuck. Review logs in $LOG_DIR/"
    echo "   and .kiro/ralph-progress.md for blockers."
    break
  fi

  # Snapshot before iteration
  BEFORE_SNAPSHOT=$(snapshot_tree)

  # Write state
  write_state "$PHASE" "$ITERATION" "$COMPLETED_AT"

  # Build prompt
  ITER_PROMPT=$(build_prompt "$PHASE" "$ITERATION")

  # Log
  REMAINING_DISPLAY=""
  if [[ "$BUDGET_SECONDS" -gt 0 ]]; then
    REMAINING_MIN=$((REMAINING / 60))
    REMAINING_DISPLAY=" | ${REMAINING_MIN}m remaining"
  fi
  STAGNATION_DISPLAY=""
  if [[ "$CONSECUTIVE_NO_PROGRESS" -gt 0 ]]; then
    STAGNATION_DISPLAY=" | ⚠️  no-progress: $CONSECUTIVE_NO_PROGRESS/$MAX_NO_PROGRESS"
  fi
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "▶ Iteration $ITERATION | Phase: $PHASE$REMAINING_DISPLAY$STAGNATION_DISPLAY"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  # Run kiro-cli. A non-zero exit (crash, auth hiccup, timeout) must not abort the run
  # under `set -e`: log it, count the iteration, and let the stagnation breaker decide.
  LOGFILE="$LOG_DIR/iteration-${ITERATION}.log"
  set +e
  kiro-cli chat \
    --agent "$AGENT" \
    --no-interactive \
    --trust-all-tools \
    --v3 \
    "$ITER_PROMPT" 2>&1 | tee "$LOGFILE"
  CLI_STATUS=${PIPESTATUS[0]}
  set -e
  if [[ "$CLI_STATUS" -ne 0 ]]; then
    echo "⚠️  kiro-cli exited with status $CLI_STATUS (iteration $ITERATION)." \
      | tee -a "$LOGFILE"
  fi

  # Detect progress (file changes)
  if detect_progress "$BEFORE_SNAPSHOT"; then
    CONSECUTIVE_NO_PROGRESS=0
  else
    CONSECUTIVE_NO_PROGRESS=$((CONSECUTIVE_NO_PROGRESS + 1))
    echo "⚠️  No file changes detected this iteration ($CONSECUTIVE_NO_PROGRESS/$MAX_NO_PROGRESS)."
  fi

  # Surface test-file modifications (warning only)
  report_test_changes "$ITERATION"

  # Check for completion promise
  if promise_found "$LOGFILE"; then
    if [[ "$PHASE" == "implement" ]]; then
      COMPLETED_AT="\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
      REMAINING=$(time_remaining)

      if [[ "$BUDGET_SECONDS" -gt 0 && "$REMAINING" -gt 60 ]]; then
        REMAINING_MIN=$((REMAINING / 60))
        echo ""
        echo "✅ Implementation complete! Switching to HARDENING phase."
        echo "   Time remaining: ~${REMAINING_MIN} minutes"
        echo ""
        PHASE="harden"
        CONSECUTIVE_NO_PROGRESS=0  # Reset for hardening phase
      else
        echo ""
        echo "✅ Task complete! (no time remaining for hardening)"
        break
      fi
    else
      # Hardening phase: only stop if time is nearly exhausted
      REMAINING=$(time_remaining)
      if [[ "$REMAINING" -le 60 ]]; then
        echo ""
        echo "✅ Hardening complete."
        break
      fi
      # Otherwise continue — the agent completed one check, start next
      CONSECUTIVE_NO_PROGRESS=0  # Successful hardening check = progress
    fi
  fi
done

# --- Final state ---
write_state "$PHASE" "$ITERATION" "$COMPLETED_AT"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              RALPH LOOP — Finished                       ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║ Iterations: $ITERATION"
echo "║ Phase reached: $PHASE"
ELAPSED=$(($(date +%s) - START_EPOCH))
echo "║ Total time: $((ELAPSED / 60)) minutes"
echo "║ Logs: $LOG_DIR/"
echo "║ Progress: $PROGRESS_FILE"
if [[ -s "$TAMPER_LOG" ]]; then
  echo "║ ⚠️  Test files were modified — audit them: $TAMPER_LOG"
fi
echo "║"
echo "║ Review changes: git diff --staged"
echo "║ Commit when ready: git commit"
echo "╚══════════════════════════════════════════════════════════╝"
