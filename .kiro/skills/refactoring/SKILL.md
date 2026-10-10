---
name: refactoring
description: >
  Proactive code refactoring workflow. Use when improving code quality without changing
  behavior: reducing complexity, improving naming, extracting abstractions, eliminating
  duplication. Different from reviewing-code (reactive to findings) and
  tech-debt-tracking (assessment without fixes).
---

# Refactoring Workflow

## Invocation

Use when: code works but is hard to understand/maintain, complexity >10, duplication
exists, modules >300 lines, naming is unclear, or preparing for a new feature.

Do NOT use when: code has bugs (`debugging`), adding new behavior (`spec-to-dev`),
reactive review (`reviewing-code`), or API contracts would change without user approval.

## Workflow

Delegate to **senior-developer**:

### Phase 1: Identify Targets

Scan for: long methods (>50 lines), god classes (>500 lines/>20 methods), deep nesting
(>3 levels), duplicated logic (3+ occurrences), primitive obsession, feature envy.
Prioritize most-changed files.

### Phase 2: Plan Refactoring

| Smell        | Refactoring                        | Technique                    |
| ------------ | ---------------------------------- | ---------------------------- |
| Long method  | Extract Method                     | Break into named steps       |
| God class    | Extract Class                      | Group related fields/methods |
| Deep nesting | Guard Clauses / Early Return       | Flatten conditionals         |
| Duplication  | Extract Function / Template Method | Single source of truth       |
| Bad naming   | Rename                             | Make intent explicit         |
| Data clump   | Introduce Parameter Object         | Group related params         |

### Phase 3: Execute Safely

1. Ensure test coverage exists before refactoring.
2. One refactoring at a time — commit after each atomic change.
3. Run tests after each step.
4. No functional changes mixed with refactoring.
5. If a refactor arrives via an in-progress merge or rebase conflict rather than a clean
   working tree, follow `references/resolving-merge-conflicts.md` before resuming the
   refactoring steps above.

### Phase 4: Validate

- All existing tests pass, no new linter warnings, complexity metrics improved, code is
  more readable.

## Output Format

```
## Refactoring Summary

**Scope**: [files/modules touched]
**Techniques applied**: [list]
**Metrics before/after**:
  - Avg method length: X → Y
  - Max complexity: X → Y
  - Duplication: X instances → Y
**Tests**: all passing (X total)
```

## Safety

- Never refactor and add features in the same change.
- Never refactor without test coverage (add tests first).
- Never change public API signatures without user confirmation.
