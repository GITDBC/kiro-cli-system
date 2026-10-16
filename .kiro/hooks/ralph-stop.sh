#!/usr/bin/env bash
# The fast path stays first: this hook fires at the end of every turn of every session
# in the workspace, and without an armed loop it must cost one file test and nothing else.
test -f .kiro/ralph-session.local.md || exit 0
#
# ralph-stop.sh — Stop hook that drives the in-session Ralph Loop.
#
# Wiring: registered in .kiro/hooks/hooks.json as an unconditional `Stop` hook (Stop
# hooks take no matcher). The loop is armed by .kiro/skills/ralph-loop/ralph-session.sh,
# which writes the state file tested above. Per
# .kiro/skills/kiro-cli-reference/references/hooks/types.md ("Agent Stop"):
#   exit 0 + {"decision":"block","reason":...} on STDOUT → start another turn;
#   exit 1 → ALSO starts another turn; any other exit → the response stays finished.
# Exit 1 therefore means "keep going", so this script never uses `set -e` or `set -u`
# (both abort with status 1) and every path ends in an explicit `exit 0`.
#
# Decision order, every halt deleting the state (fail open):
#   1. no state file                    → exit 0, silent (the line above)
#   2. state bound to another session   → exit 0, state kept
#   3. state corrupt or python3 missing → warn on STDERR, delete state, exit 0
#   4. iteration >= max_iterations      → delete state, exit 0
#   5. promise file holds the promise   → delete state, exit 0
#   6. 3 unchanged tree fingerprints    → delete state, exit 0
#   7. otherwise                        → bump iteration atomically, emit block JSON
#
# Session ids: the Stop payload was not observable during design (workspace hooks do
# not run in an untrusted workspace), so isolation applies only when BOTH the state
# (`start --session ID`) and the payload carry a session_id. Completion is read from a
# file the agent writes, not from the payload, for the same reason.

STATE_FILE=".kiro/ralph-session.local.md"
PROMISE_FILE=".kiro/ralph-session.promise"
MAX_STALE=3

warn() {
  printf 'ralph-stop: %s\n' "$1" >&2
}

if ! command -v python3 >/dev/null 2>&1; then
  warn "python3 not found; session loop disabled and state removed."
  rm -f -- "$STATE_FILE" "$PROMISE_FILE"
  exit 0
fi

PAYLOAD="$(cat 2>/dev/null)"

FINGERPRINT=""
LIB="$(dirname "${BASH_SOURCE[0]}")/../skills/ralph-loop/fingerprint.sh"
if [[ -f "$LIB" ]] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  # shellcheck source=../skills/ralph-loop/fingerprint.sh
  source "$LIB" 2>/dev/null && FINGERPRINT="$(ralph_snapshot_tree 2>/dev/null)"
fi

read -r -d '' DECIDE <<'PY'
import json
import os
import re
import sys
import tempfile

state_path, promise_path, fingerprint, max_stale = sys.argv[1:5]
max_stale = int(max_stale)
RULES = (
    "Write <promise>{p}</promise> to {f} ONLY when that statement is completely and "
    "unequivocally true. Do not write a false promise to escape the loop, even if you "
    "think you are stuck; the loop is meant to run until the promise is genuinely true."
)


def halt(message, *, drop_promise=True):
    sys.stderr.write(f"ralph-stop: {message}\n")
    for path in (state_path, promise_path) if drop_promise else (state_path,):
        try:
            os.remove(path)
        except OSError:
            pass
    sys.exit(0)


def corrupt(reason):
    halt(f"corrupt state ({reason}); session loop disabled and state removed.")


def normalise(text):
    return " ".join(text.split())


try:
    payload = json.loads(sys.stdin.read() or "{}")
except ValueError:
    payload = {}
if not isinstance(payload, dict):
    payload = {}

try:
    with open(state_path, encoding="utf-8") as handle:
        text = handle.read()
except (OSError, UnicodeDecodeError):
    corrupt("unreadable")

match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
if match is None:
    corrupt("missing frontmatter")
fields = {}
for line in match.group(1).splitlines():
    key, sep, value = line.partition(":")
    if sep:
        fields[key.strip()] = value.strip()
body = match.group(2)
prompt = body.rstrip("\n")

state_session = fields.get("session_id", "")
event_session = payload.get("session_id")
if state_session and isinstance(event_session, str) and event_session:
    if event_session != state_session:
        sys.exit(0)

for key in ("iteration", "max_iterations", "stale_count"):
    if not re.fullmatch(r"[0-9]{1,6}", fields.get(key, "")):
        corrupt(f"{key} is not a number")
if fields.get("active") != "true":
    corrupt("active is not true")
if not prompt.strip():
    corrupt("empty prompt")
iteration = int(fields["iteration"])
max_iterations = int(fields["max_iterations"])
promise = normalise(fields.get("completion_promise", ""))
if max_iterations == 0 and not promise:
    corrupt("unlimited iterations without a completion promise")

if max_iterations > 0 and iteration >= max_iterations:
    halt(f"max iterations ({max_iterations}) reached; session loop finished.")

if promise:
    try:
        with open(promise_path, encoding="utf-8", errors="replace") as handle:
            written = handle.read(65536)
    except OSError:
        written = ""
    found = re.search(r"<promise>(.*?)</promise>", written, re.S)
    if found is not None and normalise(found.group(1)) == promise:
        halt(f"completion promise <promise>{promise}</promise> detected; loop finished.")

stale = int(fields["stale_count"])
last = fields.get("last_fingerprint", "")
stale = stale + 1 if fingerprint and fingerprint == last else 0
if stale >= max_stale:
    halt(
        f"{max_stale} consecutive iterations left the working tree unchanged; "
        "session loop halted as stagnant."
    )

iteration += 1
fields["iteration"] = str(iteration)
fields["last_fingerprint"] = fingerprint
fields["stale_count"] = str(stale)
order = (
    "active", "iteration", "max_iterations", "completion_promise", "session_id",
    "started_at", "last_fingerprint", "stale_count",
)
lines = [f"{key}: {fields.get(key, '')}" for key in order]
lines += [f"{k}: {v}" for k, v in fields.items() if k not in order]
directory = os.path.dirname(state_path) or "."
handle, tmp = tempfile.mkstemp(prefix="ralph-session.tmp.", dir=directory)
with os.fdopen(handle, "w", encoding="utf-8") as out:
    out.write("---\n" + "\n".join(lines) + "\n---\n" + body)
os.replace(tmp, state_path)

limit = f" of {max_iterations}" if max_iterations else " (no limit)"
message = f"Ralph session loop: iteration {iteration}{limit}. "
if promise:
    message += RULES.format(p=promise, f=promise_path)
else:
    message += "No completion promise: the loop ends at the iteration limit."
message += " Cancel: .kiro/skills/ralph-loop/ralph-session.sh cancel"
sys.stdout.write(
    json.dumps({"decision": "block", "reason": prompt, "systemMessage": message})
)
PY

OUTPUT="$(printf '%s' "$PAYLOAD" | python3 -c "$DECIDE" \
  "$STATE_FILE" "$PROMISE_FILE" "$FINGERPRINT" "$MAX_STALE")"
STATUS=$?
if ((STATUS != 0)); then
  warn "internal error (status $STATUS); session loop disabled and state removed."
  rm -f -- "$STATE_FILE" "$PROMISE_FILE"
  exit 0
fi
[[ -n "$OUTPUT" ]] && printf '%s\n' "$OUTPUT"
exit 0
