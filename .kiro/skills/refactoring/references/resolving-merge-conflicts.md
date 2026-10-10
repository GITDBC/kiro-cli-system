# Resolving Merge Conflicts

Procedure for resolving an in-progress git merge or rebase conflict. Adapted from
mattpocock/skills (MIT).

## Procedure

1. **See the current state.** Check `git status`, the merge/rebase history, and the full
   content of every conflicting file before touching any hunk.

2. **Find the primary sources for each conflict.** Read the commit messages on both
   sides, check the associated pull requests, check the linked issues or tickets.
   Understand why each change was made and what its original intent was before deciding
   how to resolve it — do not resolve from the diff alone.

3. **Resolve each hunk.** Preserve both intents where they are compatible. Where they
   are genuinely incompatible, pick the version matching the merge's stated goal and
   record the trade-off in the commit message or a code comment. Never invent new
   behavior that neither side wrote.

4. **Run the project's automated checks** after resolving: linter, then tests, then
   formatter (or the project's `make lint` / `make test` targets). Fix anything the
   merge broke before proceeding.

5. **Finish the merge/rebase.** Stage the resolved files and commit. If rebasing,
   continue the rebase (`git rebase --continue`) until every commit in the sequence has
   been rebased.

## Git safety alignment

`git merge --abort` or `git rebase --abort` is a destructive operation under this
project's git safety rules and must not be used to escape a difficult conflict — always
resolve forward. If a conflict genuinely cannot be resolved without information only the
user has (ambiguous intent, conflicting business requirements), stop and ask rather than
guessing or aborting. Aborting the merge/rebase to discard resolution work in progress
requires explicit user permission, consistent with the project's rule that destructive
git operations (`reset --hard`, `push --force`, `clean -f`, `branch -D`, and by
extension `merge --abort` / `rebase --abort` mid-resolution) are never run without it.
