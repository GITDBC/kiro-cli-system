#!/usr/bin/env bash
# Tests for ralph.sh option handling: engine pinning and the optional --model/--effort
# overrides. A stub kiro-cli on PATH records its arguments, so no model is ever called.
set -uo pipefail

SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/ralph.sh"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$WORK/bin" "$WORK/repo"
cat >"$WORK/bin/kiro-cli" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "$@" >"$STUB_ARGS_FILE"
echo "<promise>DONE</promise>"
STUB
chmod +x "$WORK/bin/kiro-cli"
git -C "$WORK/repo" init -q

PASS=0
FAIL=0

check() {
  local name="$1" condition="$2"
  if eval "$condition"; then
    PASS=$((PASS + 1))
    echo "| $name | PASS |"
  else
    FAIL=$((FAIL + 1))
    echo "| $name | FAIL |"
  fi
}

# Runs ralph.sh once in the scratch repo; the recorded kiro-cli arguments land in args.txt.
run_ralph() {
  (
    cd "$WORK/repo" || exit 1
    STUB_ARGS_FILE="$WORK/args.txt" PATH="$WORK/bin:$PATH" "$SCRIPT" --max 1 "$@" "task"
  ) >"$WORK/out.txt" 2>&1
}

has_arg() { grep -qxF -- "$1" "$WORK/args.txt"; }

run_ralph
check "engine is passed explicitly" "has_arg '--agent-engine' && has_arg 'v3'"
check "no shorthand harness flag" "! has_arg '--v3' && ! has_arg '--v2'"
check "no model override by default" "! has_arg '--model' && ! has_arg '--effort'"

run_ralph --model claude-haiku-5.5 --effort low
check "model override is forwarded" "has_arg '--model' && has_arg 'claude-haiku-5.5'"
check "effort override is forwarded" "has_arg '--effort' && has_arg 'low'"

run_ralph --effort turbo
check "invalid effort is rejected" "grep -q 'effort must be' '$WORK/out.txt'"

run_ralph --model 'bad model'
check "invalid model is rejected" "grep -q 'unsupported characters' '$WORK/out.txt'"

echo
echo "$PASS passed, $FAIL failed"
[[ "$FAIL" -eq 0 ]]
