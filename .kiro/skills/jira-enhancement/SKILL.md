---
name: jira-enhancement
description: >
  Full lifecycle management of enhancement JIRAs for prototypes. Phase 1: creates
  detailed markdown documentation (problem, solution, affected files, verification,
  effort, risks). Phase 2: synchronizes with JIRA (create subtasks, update descriptions,
  attach files, manage priority tables). Phase 3: audits alignment between local
  markdowns and JIRA tickets. Triggers: 'document enhancement', 'jira enhancement',
  'sync with jira', 'audit jira'. Not for simple ticket reads (use jira-fetcher).
---

# JIRA Enhancement Documentation

## Workflow

```
- [ ] Phase 1: Document the enhancement (create/update markdown)
- [ ] Phase 2: Synchronize with JIRA (create/update tickets)
- [ ] Phase 3: Audit existing JIRAs (verify alignment)
```

## Context Setup (mandatory before any phase)

Ask the user for all 7 before proceeding:

1. Prototype name/acronym
2. Path to context document (architecture summary markdown)
3. Path to source code (main package)
4. Path to tests
5. Path to enhancement markdowns destination folder
6. Path to potential improvements summary file (if exists)
7. Path to figures folder

## Phase 1 — Document the enhancement → `senior-developer`

1. **Gather context** — Read architecture, source, tests. Ask user which workflow to
   follow (existing JIRA / user idea / AI analysis). Present steps and wait for
   confirmation.
2. **Analyze code** — Read relevant source files. Identify affected files: paths,
   function names, line numbers.
3. **Write the markdown** — 7-section structure (see
   `references/enhancement-template.md`). Naming: `PROJECT-XXXXX_short_description.md`.
4. **Review against checklist** — Proposals match actual code · estimates are realistic
   · dependencies identified.

## Phase 2 — Synchronize with JIRA → `senior-developer`

5. **Connect to JIRA** — Use `JIRA_URL`, `JIRA_TOKEN`, `JIRA_EMAIL` env vars. Use
   `jira-fetcher` skill. Never display tokens.
6. **Create or update JIRA** — New subtasks: identify parent, copy fields from siblings,
   create ticket, upload attachments. Existing JIRAs: update description (wiki format),
   update time tracking.
7. **Update local markdown** — Rename placeholder files with real JIRA ID, add JIRA
   link.
8. **Attach and reference** — Attach markdown to JIRA, append reference in description.
9. **Priority table (optional)** — Read parent JIRA, check for existing table, inform
   user, update only after confirmation.

## Phase 3 — Audit existing JIRAs → `senior-developer`

10. **List and compare** — Query parent JIRA subtasks, compare with local markdowns.
    Identify: JIRAs without markdown · markdowns without JIRA · mismatches.
11. **Sequential review** — For each item: download JIRA description, read local
    markdown, compare, report discrepancies, propose actions, wait for user decision.
12. **Summary** — Brief summary of findings and changes applied.

## Output Format

For the full 7-section markdown template and naming convention, load
`references/enhancement-template.md`.

## Interaction Rules

- Present steps before starting; wait for confirmation after workflow selection.
- Never auto-analyze — only identify improvements when explicitly requested.
- Always validate proposal summary with user before documenting.
- Sequential processing: one item at a time with user conversation.
- Confirm before each JIRA action (create, update, attach, transition).

## Rules

- Markdown is source of truth — be specific: file paths, function names, line numbers.
- Always check backward compatibility.
- Use `jira-fetcher` skill for all JIRA API interactions.
- Never display tokens in commands or responses.

## Done when

- Markdown follows the 7-section structure (`references/enhancement-template.md`) ·
  proposals verified against actual code · dependencies identified.
- (Phase 2) JIRA created/updated and markdown attached.
- (Phase 3) All items reviewed and discrepancies resolved.
