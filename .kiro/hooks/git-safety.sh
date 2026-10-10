#!/usr/bin/env bash
#
# git-safety.sh — PreToolUse hook that blocks destructive git operations.
#
# Wiring: attached as a `preToolUse` hook with matcher `execute_bash` in every
# agent config whose `tools` list includes `shell`. Per
# .kiro/skills/kiro-cli-reference/references/hooks.md, exit code 2 blocks the
# tool call and returns STDERR to the LLM; exit code 0 allows it silently.
#
# The deny-list concept is adapted from github.com/mattpocock/skills (MIT).
# No code was copied: that implementation matches by substring, which
# over-blocks legitimate multi-path checkouts. This script matches on argument
# boundaries instead.
#
# Design rules:
#   * FAIL SAFE. Anything that cannot be parsed with confidence is allowed
#     silently. A hook that blocks legitimate work is worse than no hook.
#   * Silent on the allow path: exit 0, no output on STDOUT or STDERR.
#   * Only the first word of each shell segment is treated as a command, so a
#     commit message that mentions a destructive flag is never blocked.
#
# Blocked operations:
#   git push --force / -f (NOT --force-with-lease)
#   git reset --hard
#   git clean -f / -fd / -fx (any short cluster containing f) / --force
#   git branch -D (any short cluster containing D) / --delete --force
#   git checkout . / git restore . — whole-tree discard with no other pathspec

set -uo pipefail

# Without python3 the hook event cannot be parsed; allow silently.
command -v python3 >/dev/null 2>&1 || exit 0

readonly PAYLOAD="$(cat)"
[[ -n "${PAYLOAD}" ]] || exit 0

# --------------------------------------------------------------------------- #
# Hook event parsing
# --------------------------------------------------------------------------- #

COMMAND_LINE="$(
	printf '%s' "${PAYLOAD}" | python3 -c '
import json
import sys

try:
    event = json.load(sys.stdin)
except Exception:
    sys.exit(0)

if not isinstance(event, dict):
    sys.exit(0)

tool_input = event.get("tool_input")
if not isinstance(tool_input, dict):
    sys.exit(0)

command = tool_input.get("command")
if isinstance(command, str):
    sys.stdout.write(command)
' 2>/dev/null
)" || exit 0

[[ -n "${COMMAND_LINE}" ]] || exit 0

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

# Emits the block message on STDERR and exits 2 so the tool call is refused.
block() {
	local operation="$1" reason="$2" alternative="$3"
	{
		printf 'BLOCKED by the git-safety hook: %s\n' "${operation}"
		printf 'Why: %s\n' "${reason}"
		printf 'Required: ask the user for explicit confirmation before running this command.\n'
		printf 'Safer alternative: %s\n' "${alternative}"
	} >&2
	exit 2
}

# True when the token is a short-option cluster (e.g. -fd) containing $2.
has_short_flag() {
	local token="$1" letter="$2"
	[[ "${token}" =~ ^-[A-Za-z]+$ ]] || return 1
	[[ "${token}" == *"${letter}"* ]]
}

# True when the token appears verbatim in the remaining arguments.
has_exact_arg() {
	local needle="$1"
	shift
	local token
	for token in "$@"; do
		[[ "${token}" == "${needle}" ]] && return 0
	done
	return 1
}

# --------------------------------------------------------------------------- #
# Per-subcommand checks
# --------------------------------------------------------------------------- #

check_push() {
	local token
	for token in "$@"; do
		# --force-with-lease and --force-if-includes are distinct tokens and
		# are deliberately not matched here.
		if [[ "${token}" == "--force" ]] || has_short_flag "${token}" f; then
			block 'git push --force' \
				'a force push can permanently overwrite remote history shared with others' \
				'git push --force-with-lease, which refuses to clobber unseen remote commits'
		fi
	done
}

check_reset() {
	local token
	for token in "$@"; do
		if [[ "${token}" == "--hard" ]]; then
			block 'git reset --hard' \
				'it discards all uncommitted work in the index and working tree irrecoverably' \
				'git stash to park the changes, or git reset --soft / --mixed to keep them'
		fi
	done
}

check_clean() {
	local token
	for token in "$@"; do
		if [[ "${token}" == "--force" ]] || has_short_flag "${token}" f; then
			block 'git clean -f' \
				'it deletes untracked files from the working tree with no way to recover them' \
				'git clean -n first to list exactly what would be removed'
		fi
	done
}

check_branch() {
	local token
	for token in "$@"; do
		if has_short_flag "${token}" D; then
			block 'git branch -D' \
				'it force-deletes a branch even when its commits are unmerged' \
				'git branch -d, which refuses to delete unmerged work'
		fi
	done
	if has_exact_arg --delete "$@" && has_exact_arg --force "$@"; then
		block 'git branch --delete --force' \
			'it force-deletes a branch even when its commits are unmerged' \
			'git branch --delete alone, which refuses to delete unmerged work'
	fi
}

# Blocks `checkout .` / `restore .` — a whole-tree discard — while allowing
# every form that names explicit paths, switches branches, or is interactive.
check_worktree_discard() {
	local subcommand="$1"
	shift

	local -a value_taking
	if [[ "${subcommand}" == "checkout" ]]; then
		value_taking=(-b -B -t --track --orphan --conflict --source --pathspec-from-file)
	else
		value_taking=(-s --source --conflict --pathspec-from-file)
	fi

	local -a positional=() after_separator=()
	local separator_seen=0 interactive=0 staged=0 worktree=0
	local token expect_value=0 candidate

	for token in "$@"; do
		if ((expect_value)); then
			expect_value=0
			continue
		fi
		if ((separator_seen)); then
			after_separator+=("${token}")
			continue
		fi
		case "${token}" in
			--)
				separator_seen=1
				continue
				;;
			-p | --patch)
				interactive=1
				continue
				;;
			-S | --staged)
				staged=1
				continue
				;;
			-W | --worktree)
				worktree=1
				continue
				;;
		esac
		if [[ "${token}" == -* ]]; then
			for candidate in "${value_taking[@]}"; do
				if [[ "${token}" == "${candidate}" ]]; then
					expect_value=1
					break
				fi
			done
			continue
		fi
		positional+=("${token}")
	done

	# Interactive discards prompt per hunk, so the user is already in the loop.
	((interactive)) && return 0
	# `restore --staged .` only unstages; the file contents survive.
	if ((staged)) && ((worktree == 0)); then
		return 0
	fi

	local -a pathspec
	if ((separator_seen)); then
		pathspec=("${after_separator[@]}")
	else
		pathspec=("${positional[@]}")
	fi

	if ((${#pathspec[@]} == 1)) && [[ "${pathspec[0]}" == "." ]]; then
		block "git ${subcommand} ." \
			'it discards every uncommitted change in the working tree at once' \
			"git stash, or git ${subcommand} with the explicit paths to revert"
	fi
}

# --------------------------------------------------------------------------- #
# Segment scanning
# --------------------------------------------------------------------------- #

# Split the command on shell separators so each simple command is inspected on
# its own. Longest operators first, so && does not degrade into two & splits.
normalised="${COMMAND_LINE}"
normalised="${normalised//&&/$'\n'}"
normalised="${normalised//||/$'\n'}"
normalised="${normalised//|/$'\n'}"
normalised="${normalised//;/$'\n'}"
normalised="${normalised//&/$'\n'}"

while IFS= read -r segment; do
	[[ -n "${segment//[[:space:]]/}" ]] || continue

	# Command substitution or parameter expansion: the effective arguments are
	# unknown at hook time, so allow.
	case "${segment}" in
		*'$('* | *'`'* | *'${'*) continue ;;
	esac

	# Unbalanced quotes mean the separator split cut through a quoted string;
	# the token stream cannot be trusted, so allow.
	quotes="${segment//[^\"]/}"
	((${#quotes} % 2 == 0)) || continue
	quotes="${segment//[^\']/}"
	((${#quotes} % 2 == 0)) || continue

	# Word-split without glob or variable expansion.
	read -r -a tokens <<<"${segment}" || continue
	((${#tokens[@]} > 0)) || continue

	# Drop leading environment assignments and command wrappers.
	index=0
	while ((index < ${#tokens[@]})); do
		case "${tokens[index]}" in
			[A-Za-z_]*=*) index=$((index + 1)) ;;
			sudo | command | env) index=$((index + 1)) ;;
			*) break ;;
		esac
	done
	((index < ${#tokens[@]})) || continue

	[[ "${tokens[index]##*/}" == "git" ]] || continue
	index=$((index + 1))

	# Skip git's global options to reach the subcommand.
	subcommand=""
	while ((index < ${#tokens[@]})); do
		token="${tokens[index]}"
		case "${token}" in
			-C | -c | --git-dir | --work-tree | --namespace | --exec-path)
				index=$((index + 2))
				;;
			-*)
				index=$((index + 1))
				;;
			*)
				subcommand="${token}"
				index=$((index + 1))
				break
				;;
		esac
	done
	[[ -n "${subcommand}" ]] || continue

	args=("${tokens[@]:index}")

	case "${subcommand}" in
		push) check_push "${args[@]+"${args[@]}"}" ;;
		reset) check_reset "${args[@]+"${args[@]}"}" ;;
		clean) check_clean "${args[@]+"${args[@]}"}" ;;
		branch) check_branch "${args[@]+"${args[@]}"}" ;;
		checkout | restore)
			check_worktree_discard "${subcommand}" "${args[@]+"${args[@]}"}"
			;;
	esac
done <<<"${normalised}"

exit 0
