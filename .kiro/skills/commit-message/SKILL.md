---
name: commit-message
description: >
  Generates structured commit messages following Conventional Commits with optional
  gitemojis and traceability metadata. Trigger phrases: 'commit message', 'write
  commit', 'git commit', 'prepare commit'. Not for writing code, changelogs, or release
  notes.
---

# Commit Message Generator

[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) with
traceability metadata.

## Format

```
[optional emoji] <type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Type

`feat` (MINOR in SemVer) · `fix` (PATCH) · `docs` · `style` · `refactor` · `test` ·
`chore` · `perf` · `ci` · `build` · `revert`

The gitemoji for each type, and three worked end-to-end messages, are in
`references/commit-conventions.md` — load it when the project uses emojis, or when the
type choice for a change is not obvious.

## Scope, Description, Body

- **Scope**: noun in parentheses — `feat(etl):`, `fix(kpi):`
- **Description**: ≤50 chars · imperative mood · no trailing period · lowercase first
  letter.
- **Body**: blank line separator · wrap at 72 chars · explain _what_ and _why_, not
  _how_.

## Footer

**Tracking-Id** (when project requires traceability):

```
Tracking-Id: <GEN_TAG> JIRA-ID: <TICKET-ID>
```

GEN tags: `GEN:NA` · `GEN:LOW` · `GEN:HIGH` · `GEN:AUTO`

**Breaking Changes** — append `!` after type/scope, or use footer:

```
feat(api)!: change authentication response format

BREAKING CHANGE: token field renamed from `access_token` to `token`.
```

## Workflow

**Step 1** → `code-reviewer`: Analyze staged changes (`git diff --cached` or user
description). Determine type and scope.

**Step 2** → `code-reviewer`: Compose message. If project uses Tracking-Id, ask for Jira
ID and GEN tag.

**Step 3** → `code-reviewer`: Present full message for user approval before committing.

## Rules

1. Imperative mood in subject ("add", not "added" or "adds").
2. No trailing period in subject.
3. Body explains _why_, not _how_.
4. One logical change per commit.
5. If user provides a diff, infer type, scope, and description automatically.
6. Present full message for user approval before committing.
7. Reference issues/tickets in footer when applicable.

## Done when

- Message follows Conventional Commits format · user has approved.
