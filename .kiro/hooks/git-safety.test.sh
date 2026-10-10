#!/usr/bin/env bash
#
# Regression cases for .kiro/hooks/git-safety.sh.
#
# Each case feeds a synthetic PreToolUse event to the hook and asserts the exit
# code: 2 = blocked, 0 = allowed. Allow cases additionally assert that the hook
# produced no output at all, since a PreToolUse hook must be silent when it
# permits the call.
#
# Usage: .kiro/hooks/git-safety.test.sh

set -uo pipefail

HOOK="$(dirname "$0")/git-safety.sh"
PASS=0
FAIL=0

event() {
	python3 -c '
import json
import sys

print(json.dumps({
    "hook_event_name": "preToolUse",
    "cwd": "/repo",
    "session_id": "test",
    "tool_name": "execute_bash",
    "tool_input": {"command": sys.argv[1]},
}))
' "$1"
}

# expect_block <command>
expect_block() {
	local command="$1" stderr status
	stderr="$(event "${command}" | "${HOOK}" 2>&1 >/dev/null)"
	status=$?
	if ((status == 2)) && [[ -n "${stderr}" ]]; then
		printf '| `%s` | block | blocked (exit 2) | PASS |\n' "${command}"
		PASS=$((PASS + 1))
	else
		printf '| `%s` | block | exit %s | FAIL |\n' "${command}" "${status}"
		FAIL=$((FAIL + 1))
	fi
}

# expect_allow <command>
expect_allow() {
	local command="$1" output status
	output="$(event "${command}" | "${HOOK}" 2>&1)"
	status=$?
	if ((status == 0)) && [[ -z "${output}" ]]; then
		printf '| `%s` | allow | allowed, silent | PASS |\n' "${command}"
		PASS=$((PASS + 1))
	else
		printf '| `%s` | allow | exit %s, output=%q | FAIL |\n' \
			"${command}" "${status}" "${output}"
		FAIL=$((FAIL + 1))
	fi
}

printf '| Command | Expected | Actual | Result |\n'
printf '| --- | --- | --- | --- |\n'

# --- must block --------------------------------------------------------------
expect_block 'git push --force'
expect_block 'git push -f origin main'
expect_block 'git push --force origin feature'
expect_block 'git -C /repo push -f'
expect_block 'git reset --hard'
expect_block 'git reset --hard HEAD~3'
expect_block 'git clean -f'
expect_block 'git clean -fd'
expect_block 'git clean -fx'
expect_block 'git clean -xdf'
expect_block 'git clean --force'
expect_block 'git branch -D feature'
expect_block 'git branch -D old1 old2'
expect_block 'git branch --delete --force feature'
expect_block 'git checkout .'
expect_block 'git checkout -- .'
expect_block 'git checkout HEAD -- .'
expect_block 'git restore .'
expect_block 'git restore --source=HEAD .'
expect_block 'make lint && git push --force'

# --- must NOT block ----------------------------------------------------------
expect_allow 'git push'
expect_allow 'git push -u origin feature'
expect_allow 'git push --force-with-lease'
expect_allow 'git push --force-with-lease=main:abc123 origin main'
expect_allow 'git push --force-if-includes'
expect_allow 'git add src/module.py'
expect_allow 'git add .'
expect_allow 'git commit -m "fix parser"'
expect_allow 'git diff'
expect_allow 'git diff --stat HEAD~1'
expect_allow 'git status --porcelain'
expect_allow 'git log --oneline -20'
expect_allow 'git show HEAD'
expect_allow 'git checkout main'
expect_allow 'git checkout -b feature/new'
expect_allow 'git switch main'
expect_allow 'git switch -c feature/new'
expect_allow 'git stash'
expect_allow 'git stash pop'
expect_allow 'git reset --soft HEAD~1'
expect_allow 'git reset --mixed'
expect_allow 'git reset HEAD src/module.py'
expect_allow 'git checkout -- src/module.py'
expect_allow 'git checkout src/a.py src/b.py'
expect_allow 'git checkout . src/'
expect_allow 'git restore src/module.py'
expect_allow 'git restore --staged .'
expect_allow 'git checkout -p .'
expect_allow 'git branch -d merged-feature'
expect_allow 'git branch --delete merged-feature'
expect_allow 'git branch -a'
expect_allow 'git clean -n'
expect_allow 'git clean --dry-run -d'
# A destructive flag quoted inside a message is text, not a command.
expect_allow 'git commit -m "reset --hard is banned here"'
expect_allow 'git commit -m "do not use git push --force"'
expect_allow 'echo "git push --force"'
# Non-git commands are never inspected.
expect_allow 'make drift-check'
expect_allow 'uv run pytest'
# Unparseable input must fail safe (allowed, silent).
expect_allow 'git push $(cat flags.txt)'

printf '\n%s passed, %s failed\n' "${PASS}" "${FAIL}"
((FAIL == 0))
