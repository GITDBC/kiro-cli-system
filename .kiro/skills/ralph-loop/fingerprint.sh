#!/usr/bin/env bash
# Shared working-tree fingerprint for both Ralph Loop modes.
# Sourced by ralph.sh (external loop) and .kiro/hooks/ralph-stop.sh (in-session loop).
#
# The fingerprint covers tracked changes against HEAD (staged and unstaged) plus the
# names and contents of untracked files. Every Ralph runtime file (.kiro/ralph-*) is
# excluded, because the loops rewrite them on every iteration. Comparing fingerprints
# detects progress even on a tree that was already dirty when the loop started.

RALPH_FINGERPRINT_EXCLUDES=(
  ":(exclude,glob).kiro/ralph-*"
  ":(exclude,glob).kiro/ralph-*/**"
)

ralph_snapshot_tree() {
  {
    git diff HEAD -- . "${RALPH_FINGERPRINT_EXCLUDES[@]}" 2>/dev/null || true
    git ls-files --others --exclude-standard -z -- . "${RALPH_FINGERPRINT_EXCLUDES[@]}" \
      2>/dev/null | tr '\0' '\n' || true
    git ls-files --others --exclude-standard -z -- . "${RALPH_FINGERPRINT_EXCLUDES[@]}" \
      2>/dev/null | xargs -0 git hash-object -- 2>/dev/null || true
  } | git hash-object --stdin 2>/dev/null
}
