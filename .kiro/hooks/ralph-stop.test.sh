#!/usr/bin/env bash
#
# Regression cases for .kiro/hooks/ralph-stop.sh and
# .kiro/skills/ralph-loop/ralph-session.sh.
#
# Every case runs inside a throwaway git repository under a temp directory, feeds the
# hook a synthetic Stop event, and asserts the exit code, STDOUT, and the state file
# left behind. No network and no kiro-cli: the hook is a plain script.
#
# Usage: .kiro/hooks/ralph-stop.test.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK="$REPO_ROOT/.kiro/hooks/ralph-stop.sh"
SESSION="$REPO_ROOT/.kiro/skills/ralph-loop/ralph-session.sh"
STATE=".kiro/ralph-session.local.md"
PROMISE=".kiro/ralph-session.promise"
PASS=0
FAIL=0

WORK="$(mktemp -d "${TMPDIR:-/tmp}/ralph-stop-test.XXXXXX")"
trap 'rm -r -- "$WORK"' EXIT

record() {
  local name="$1" ok="$2" detail="${3:-}"
  if ((ok)); then
    printf '| %s | PASS |\n' "$name"
    PASS=$((PASS + 1))
  else
    printf '| %s | FAIL %s |\n' "$name" "$detail"
    FAIL=$((FAIL + 1))
  fi
}

# Fresh git repository with one commit; the hook and its library are reached through
# absolute paths, exactly as hooks.json resolves them from the workspace root.
new_repo() {
  local dir="$WORK/$1"
  mkdir -p "$dir/.kiro/hooks" "$dir/.kiro/skills/ralph-loop"
  cp "$HOOK" "$dir/.kiro/hooks/ralph-stop.sh"
  cp "$REPO_ROOT/.kiro/skills/ralph-loop/fingerprint.sh" "$dir/.kiro/skills/ralph-loop/"
  git -C "$dir" init -q
  git -C "$dir" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
  printf '%s' "$dir"
}

write_state() {
  local dir="$1" iteration="$2" max="$3" promise="$4" session="${5:-}"
  local fingerprint="${6:-}" stale="${7:-0}" prompt="${8:-Build the thing.}"
  cat >"$dir/$STATE" <<EOF
---
active: true
iteration: $iteration
max_iterations: $max
completion_promise: $promise
session_id: $session
started_at: 2026-01-01T00:00:00Z
last_fingerprint: $fingerprint
stale_count: $stale
---
$prompt
EOF
}

field() {
  sed -n "/^---$/,/^---$/{s/^$2: //p}" "$1/$STATE" | head -n 1
}

# run_hook <dir> [session_id] — sets OUT, ERR, CODE.
run_hook() {
  local dir="$1" session="${2:-}" payload
  payload="{\"hook_event_name\":\"Stop\",\"cwd\":\"$dir\",\"session_id\":\"$session\"}"
  OUT="$(cd "$dir" && printf '%s' "$payload" | ./.kiro/hooks/ralph-stop.sh 2>"$WORK/err")"
  CODE=$?
  ERR="$(cat "$WORK/err")"
}

json_get() {
  printf '%s' "$1" | python3 -c 'import json,sys; print(json.load(sys.stdin).get(sys.argv[1], ""))' "$2"
}

printf '| Case | Result |\n'
printf '| --- | --- |\n'

# --- ralph-stop.sh ---------------------------------------------------------------
d="$(new_repo no-state)"
run_hook "$d"
record "no state: exit 0, silent" "$((CODE == 0 && ${#OUT} == 0 && ${#ERR} == 0))" "code=$CODE"

d="$(new_repo other-session)"
write_state "$d" 1 5 "" "sess_A"
run_hook "$d" "sess_B"
record "other session: exit 0, silent, state kept" \
  "$((CODE == 0 && ${#OUT} == 0))" "code=$CODE out=$OUT"
[[ "$(field "$d" iteration)" == 1 ]]
record "other session: iteration untouched" "$((! $?))"

d="$(new_repo same-session)"
write_state "$d" 1 5 "" "sess_A"
run_hook "$d" "sess_A"
record "same session: loop continues" "$(( $(json_get "$OUT" decision | grep -c '^block$') ))"

for bad in "iteration: x" "max_iterations: -1" "stale_count: abc"; do
  d="$(new_repo "corrupt-${bad%%:*}")"
  write_state "$d" 1 5 ""
  key="${bad%%:*}"
  sed -i "s/^$key: .*/$bad/" "$d/$STATE"
  run_hook "$d"
  ok=$((CODE == 0 && ${#OUT} == 0))
  [[ ! -f "$d/$STATE" && "$ERR" == *corrupt* ]] || ok=0
  record "corrupt ($bad): warn, delete, exit 0" "$ok" "code=$CODE err=$ERR"
done

d="$(new_repo corrupt-prompt)"
write_state "$d" 1 5 "" "" "" 0 "   "
run_hook "$d"
ok=$((CODE == 0 && ${#OUT} == 0))
[[ ! -f "$d/$STATE" ]] || ok=0
record "corrupt (empty prompt): delete, exit 0" "$ok"

d="$(new_repo corrupt-frontmatter)"
printf 'no frontmatter here\n' >"$d/$STATE"
run_hook "$d"
ok=$((CODE == 0 && ${#OUT} == 0))
[[ ! -f "$d/$STATE" ]] || ok=0
record "corrupt (no frontmatter): delete, exit 0" "$ok"

d="$(new_repo max-reached)"
write_state "$d" 3 3 "DONE"
run_hook "$d"
ok=$((CODE == 0 && ${#OUT} == 0))
[[ ! -f "$d/$STATE" && "$ERR" == *"max iterations"* ]] || ok=0
record "max reached: delete, exit 0" "$ok" "err=$ERR"

d="$(new_repo promise-match)"
write_state "$d" 1 10 "ALL TESTS PASS"
printf 'Finished.\n<promise>ALL TESTS PASS</promise>\n' >"$d/$PROMISE"
run_hook "$d"
ok=$((CODE == 0 && ${#OUT} == 0))
[[ ! -f "$d/$STATE" && ! -f "$d/$PROMISE" ]] || ok=0
record "promise matched: delete, exit 0" "$ok" "out=$OUT"

d="$(new_repo promise-whitespace)"
write_state "$d" 1 10 "ALL TESTS PASS"
printf '<promise>\n  ALL   TESTS\tPASS \n</promise>' >"$d/$PROMISE"
run_hook "$d"
ok=$((CODE == 0 && ${#OUT} == 0))
[[ ! -f "$d/$STATE" ]] || ok=0
record "promise whitespace-normalised: match" "$ok"

d="$(new_repo promise-nomatch)"
prompt_text='Fix "parser" bug; keep $HOME and `ticks` literal.'
write_state "$d" 2 10 "DONE" "" "" 0 "$prompt_text"
printf '<promise>DONE*</promise>\n' >"$d/$PROMISE"
run_hook "$d"
ok=$((CODE == 0))
[[ "$(json_get "$OUT" decision)" == block ]] || ok=0
[[ "$(json_get "$OUT" reason)" == "$prompt_text" ]] || ok=0
[[ "$(json_get "$OUT" systemMessage)" == *"iteration 3 of 10"* ]] || ok=0
[[ "$(field "$d" iteration)" == 3 ]] || ok=0
record "promise not matched (no glob): block, same prompt, iteration+1" "$ok" "out=$OUT"
printf '<promise>NOT DONE</promise>\n' >"$d/$PROMISE"
run_hook "$d"
[[ "$(json_get "$OUT" decision)" == block ]]
record "promise substring does not match" "$((! $?))"
[[ -z "$(ls "$d/.kiro" | grep -E '\.tmp\.|local\.md\.')" ]]
record "atomic write leaves no temp files" "$((! $?))"

d="$(new_repo stagnation)"
write_state "$d" 1 20 "DONE"
run_hook "$d"
run_hook "$d"
run_hook "$d"
first_three="$(field "$d" stale_count)"
run_hook "$d"
ok=$((CODE == 0 && ${#OUT} == 0))
[[ ! -f "$d/$STATE" && "$ERR" == *stagnant* && "$first_three" == 2 ]] || ok=0
record "stagnation: halts after 3 unchanged iterations" "$ok" "stale=$first_three err=$ERR"

d="$(new_repo progress)"
write_state "$d" 1 20 "DONE"
run_hook "$d"
for n in 1 2 3; do
  printf '%s\n' "$n" >"$d/work.txt"
  run_hook "$d"
done
ok=1
[[ -f "$d/$STATE" && "$(field "$d" stale_count)" == 0 ]] || ok=0
record "tree changes reset the stagnation counter" "$ok"

d="$(new_repo no-python)"
write_state "$d" 1 5 "DONE"
bin="$WORK/bin-no-python"
mkdir -p "$bin"
for tool in bash env cat rm git dirname mktemp; do
  ln -s "$(command -v "$tool")" "$bin/$tool"
done
OUT="$(cd "$d" && printf '{}' | PATH="$bin" ./.kiro/hooks/ralph-stop.sh 2>"$WORK/err")"
CODE=$?
ok=$((CODE == 0 && ${#OUT} == 0))
[[ ! -f "$d/$STATE" ]] || ok=0
record "python3 missing: fail open, exit 0" "$ok" "code=$CODE"

d="$(new_repo garbage-payload)"
write_state "$d" 1 5 ""
OUT="$(cd "$d" && printf 'not json' | ./.kiro/hooks/ralph-stop.sh 2>/dev/null)"
[[ "$(json_get "$OUT" decision)" == block ]]
record "unparseable payload: treated as empty" "$((! $?))"

# --- ralph-session.sh --------------------------------------------------------------
d="$(new_repo session)"
expect_start_error() {
  local name="$1"
  shift
  (cd "$d" && "$SESSION" start "$@" >/dev/null 2>&1)
  local code=$?
  local ok=$((code != 0))
  [[ ! -f "$d/$STATE" ]] || ok=0
  record "start rejects $name" "$ok" "code=$code"
}
expect_start_error "empty prompt" "   "
expect_start_error "non-numeric --max" "task" --max 3x
expect_start_error "negative --max" "task" --max -1
expect_start_error "--max 0 without promise" "task" --max 0
expect_start_error "promise with tags" "task" --promise "<b>"
expect_start_error "missing --max value" "task" --max
expect_start_error "unknown option" "task" --bogus

msg="$(cd "$d" && "$SESSION" start "Do it." 2>&1)"
ok=1
[[ "$(field "$d" max_iterations)" == 20 && "$(field "$d" iteration)" == 1 ]] || ok=0
[[ "$msg" == *"Max iterations: 20"* ]] || ok=0
record "start defaults --max to 20" "$ok"
(cd "$d" && "$SESSION" start "again" >/dev/null 2>&1)
record "start refuses a second active loop" "$(( $? != 0 ))"
(cd "$d" && "$SESSION" cancel >/dev/null)
[[ ! -f "$d/$STATE" ]]
record "cancel removes the state" "$((! $?))"

msg="$(cd "$d" && "$SESSION" start "Unlimited." --max 0 --promise "  SHIP   IT " 2>&1)"
ok=1
[[ "$msg" == *WARNING* && "$(field "$d" completion_promise)" == "SHIP IT" ]] || ok=0
[[ "$msg" == *"unequivocally true"* ]] || ok=0
record "--max 0 with promise: warns, normalises promise" "$ok"
status="$(cd "$d" && "$SESSION" status)"
record "status reports the loop" "$( [[ "$status" == *"1 of unlimited"* ]] && echo 1 || echo 0)"
run_hook "$d"
record "hook continues a loop armed by start" \
  "$( [[ "$(json_get "$OUT" reason)" == Unlimited. ]] && echo 1 || echo 0)"
(cd "$d" && "$SESSION" cancel >/dev/null)
status="$(cd "$d" && "$SESSION" status)"
record "status after cancel" "$( [[ "$status" == "No active session loop." ]] && echo 1 || echo 0)"

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
((FAIL == 0))
