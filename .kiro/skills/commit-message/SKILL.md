---
name: commit-message
description: >
  Generates structured commit messages following Conventional Commits with optional
  gitemojis and traceability metadata. Trigger phrases: 'commit message', 'write
  commit', 'git commit', 'prepare commit'. Not for writing code, changelogs, or release
  notes.
---

# Commit Message Generator

Messages follow
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/); only the
house additions are stated here.

## House Conventions

- Subject: `[optional gitmoji] <type>[(scope)][!]: <description>` — description ≤50
  chars, imperative, lowercase first letter, no trailing period. Use the
  [gitmoji](https://gitmoji.dev/) for the type only when the project already uses
  emojis.
- Body wrapped at 72 chars, explaining what and why.
- Traceability footer, when the project requires it:

  ```
  Tracking-Id: <GEN_TAG> JIRA-ID: <TICKET-ID>
  ```

  `GEN_TAG` is one of `GEN:NA` · `GEN:LOW` · `GEN:HIGH` · `GEN:AUTO`. Ask the user for
  the Jira ID and GEN tag; never guess them.

## Workflow

1. Infer type, scope, and description from `git diff --cached`, a supplied diff, or the
   user's description; one logical change per commit.
2. Present the full message for user approval before committing.
