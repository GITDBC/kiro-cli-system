#!/usr/bin/env bash
# Ralph Loop — in-session mode.
#
# Arms, inspects, or cancels a loop that keeps the CURRENT Kiro session working on one
# prompt. The loop itself is driven by the Stop hook .kiro/hooks/ralph-stop.sh: every
# time the agent tries to finish a turn, the hook re-submits the stored prompt until the
# completion promise is written, the iteration limit is reached, the tree stagnates, or
# the loop is cancelled. Context persists across iterations (unlike ralph.sh, which
# starts a fresh session per iteration).
#
# Usage:
#   ralph-session.sh start "PROMPT" [--max N] [--promise TEXT] [--session ID]
#   ralph-session.sh status
#   ralph-session.sh cancel
set -euo pipefail

STATE_FILE=".kiro/ralph-session.local.md"
PROMISE_FILE=".kiro/ralph-session.promise"
DEFAULT_MAX=20
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Usage:
  ralph-session.sh start "PROMPT" [--max N] [--promise TEXT] [--session ID]
  ralph-session.sh status
  ralph-session.sh cancel

start options:
  --max N          Iteration limit (positive integer). Default: $DEFAULT_MAX.
                   --max 0 means unlimited and is accepted only with --promise.
  --promise TEXT   Completion phrase. The loop ends when the agent writes
                   <promise>TEXT</promise> into $PROMISE_FILE.
  --session ID     Bind the loop to one Kiro session id; Stop events that carry a
                   different session_id are ignored. Default: unbound.

Run from the repository root.
EOF
}

die() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

# Collapses every whitespace run to one space and trims both ends.
normalise() {
  local text
  text="$(printf '%s' "$1" | tr -s '[:space:]' ' ')"
  text="${text#' '}"
  printf '%s' "${text%' '}"
}

read_field() {
  sed -n "/^---$/,/^---$/{s/^$1: //p}" "$STATE_FILE" | head -n 1
}

cmd_start() {
  local prompt="" max="$DEFAULT_MAX" promise="" session=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --max)
        [[ $# -ge 2 ]] || die "--max requires a value."
        max="$2"; shift 2 ;;
      --promise)
        [[ $# -ge 2 ]] || die "--promise requires a value."
        promise="$2"; shift 2 ;;
      --session)
        [[ $# -ge 2 ]] || die "--session requires a value."
        session="$2"; shift 2 ;;
      -h | --help) usage; exit 0 ;;
      -*) die "unknown option '$1'." ;;
      *)
        [[ -z "$prompt" ]] || die "the prompt must be a single quoted argument."
        prompt="$1"; shift ;;
    esac
  done

  [[ -n "${prompt//[[:space:]]/}" ]] || die "the prompt must not be empty."
  [[ "$max" =~ ^[0-9]{1,6}$ ]] || die "--max must be an integer from 0 to 999999, got '$max'."
  max=$((10#$max))
  promise="$(normalise "$promise")"
  if [[ "$promise" == *"<"* || "$promise" == *">"* ]]; then
    die "--promise must not contain '<' or '>'."
  fi
  [[ "$session" =~ ^[A-Za-z0-9_.-]*$ ]] || die "--session contains unsupported characters."
  # The default is bounded, so max == 0 can only come from an explicit --max 0.
  if ((max == 0)); then
    [[ -n "$promise" ]] || die "--max 0 (unlimited) requires --promise, otherwise nothing ends the loop."
    printf 'WARNING: unlimited iterations; only the promise, stagnation, or cancel stop the loop.\n' >&2
  fi
  [[ -d .kiro ]] || die "run from the repository root (no .kiro/ directory here)."
  if [[ -f "$STATE_FILE" ]]; then
    die "a session loop is already active ($STATE_FILE). Run 'ralph-session.sh cancel' first."
  fi

  local fingerprint=""
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    && [[ -f "$SCRIPT_DIR/fingerprint.sh" ]]; then
    # shellcheck source=fingerprint.sh
    source "$SCRIPT_DIR/fingerprint.sh"
    fingerprint="$(ralph_snapshot_tree || true)"
  fi

  rm -f -- "$PROMISE_FILE"
  local tmp
  tmp="$(mktemp "${STATE_FILE}.XXXXXX")"
  cat >"$tmp" <<EOF
---
active: true
iteration: 1
max_iterations: $max
completion_promise: $promise
session_id: $session
started_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
last_fingerprint: $fingerprint
stale_count: 0
---
$prompt
EOF
  mv -f -- "$tmp" "$STATE_FILE"

  local limit="$max"
  ((max > 0)) || limit="unlimited"
  cat <<EOF
Ralph session loop activated.

Iteration: 1
Max iterations: $limit
Completion promise: ${promise:-none (runs until the iteration limit)}
State file: $STATE_FILE

When you try to end your turn, the Stop hook feeds the SAME prompt back. Your previous
work stays in the files and in this conversation. The loop also halts after 3
consecutive iterations that leave the working tree unchanged.
To stop early: .kiro/skills/ralph-loop/ralph-session.sh cancel
EOF
  if [[ -n "$promise" ]]; then
    cat <<EOF

COMPLETION PROMISE
To finish, write exactly this line to $PROMISE_FILE:
  <promise>$promise</promise>
Write it ONLY when the statement is completely and unequivocally true. Do not write a
false promise to escape the loop, even if you believe you are stuck or the loop should
end; the loop is designed to run until the promise is genuinely true.
EOF
  fi
  printf '\nTask:\n%s\n' "$prompt"
}

cmd_status() {
  if [[ ! -f "$STATE_FILE" ]]; then
    echo "No active session loop."
    return 0
  fi
  local max
  max="$(read_field max_iterations)"
  [[ "$max" != "0" ]] || max="unlimited"
  printf 'Active session loop (%s)\n' "$STATE_FILE"
  printf '  iteration:   %s of %s\n' "$(read_field iteration)" "$max"
  printf '  promise:     %s\n' "$(read_field completion_promise)"
  printf '  session:     %s\n' "$(read_field session_id)"
  printf '  started_at:  %s\n' "$(read_field started_at)"
  printf '  stale_count: %s of 3\n' "$(read_field stale_count)"
}

cmd_cancel() {
  if [[ ! -f "$STATE_FILE" ]]; then
    echo "No active session loop."
    return 0
  fi
  local iteration
  iteration="$(read_field iteration)"
  rm -f -- "$STATE_FILE" "$PROMISE_FILE"
  printf 'Cancelled session loop (was at iteration %s).\n' "${iteration:-?}"
}

[[ $# -ge 1 ]] || { usage >&2; exit 1; }
subcommand="$1"
shift
case "$subcommand" in
  start) cmd_start "$@" ;;
  status) cmd_status ;;
  cancel) cmd_cancel ;;
  -h | --help) usage ;;
  *) usage >&2; exit 1 ;;
esac
