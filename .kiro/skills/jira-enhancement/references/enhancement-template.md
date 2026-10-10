# Enhancement Documentation Template

Full 7-section markdown template for `jira-enhancement` Phase 1. Load this file when
drafting an enhancement markdown document.

## Output Format (7 sections)

Each enhancement markdown:

1. **Problem Description** — what is broken, missing, or suboptimal, and why it matters.
2. **Current Code / Current State** — relevant excerpts or behavior as-is, with file
   paths and line numbers.
3. **Proposed Solution** — the change being proposed, at a level a reviewer can evaluate
   without reading the full diff.
4. **Detailed Actions** — files affected, function names, line numbers; one bullet per
   discrete action.
5. **Verification** — how the proposed change will be validated (tests, manual steps,
   metrics to check).
6. **Estimated Effort** — rough sizing (hours/days) with the main cost driver named.
7. **Risks and Considerations** — backward compatibility, dependencies, rollback
   difficulty, known unknowns.

## Naming convention

`PROJECT-XXXXX_short_description.md`. Use a placeholder (`TBD_short_description.md`)
before a JIRA ID exists; rename once the ticket is created (Phase 2, step 7).

## Review checklist before finalizing

- Proposals match actual code (re-read the referenced lines, don't rely on memory).
- Estimates are realistic given the codebase's actual complexity, not a generic guess.
- Dependencies on other tickets/enhancements are identified and cross-referenced.
