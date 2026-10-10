# Spec-to-Dev Playbook

## Phase 1: Discovery (senior-developer — read-only)

### Slicing Discipline

Subtasks and tickets are **vertical slices** ("tracer bullets"): each cuts a narrow but
complete path through every layer a feature touches (schema, API, business logic,
tests), so a single slice is independently demoable or verifiable. Adapted from
mattpocock/skills (MIT).

**Horizontal decomposition anti-pattern.** Slicing by architectural layer — one subtask
for "the schema changes," another for "the API layer," another for "the UI" — looks tidy
on a dependency diagram but produces subtasks that are individually unverifiable: none
of them delivers observable behavior on its own, so integration risk piles up at the end
instead of being retired slice by slice. A 26-ticket horizontal-slice run
(mattpocock/skills' measured baseline) produced roughly 20 runs per ticket and about 75%
rework, because each layer-ticket had to be revisited once the layers above and below it
were actually wired together. Prefer cutting by capability or user-visible behavior;
each subtask should own its own thin slice of schema, logic, and interface rather than
owning one layer across many behaviors.

**Expand–migrate–contract escape hatch.** Wide refactors — a mechanical change whose
blast radius fans across the whole codebase (rename a shared column, retype a
widely-used symbol) so that a single edit breaks many call sites at once — cannot be cut
into a vertical slice; no slice can land green while the rename is half-applied.
Sequence these instead:

1. **Expand** — add the new form beside the old so nothing breaks yet.
2. **Migrate** — move call sites over in batches sized by blast radius (per package, per
   directory); each batch is its own subtask blocked by the expand step, and CI stays
   green batch to batch because the old form still exists throughout.
3. **Contract** — delete the old form once no caller remains, in a final subtask blocked
   by every migration batch.

If even individual batches cannot stay green alone, keep the three-phase sequence but
let the migration batches share an integration branch that all block a final
integrate-and-verify subtask; green is promised only there, not at every intermediate
batch.

### Codebase Exploration Checklist

1. **Identify entry points** — Where does the feature connect to existing code?
   - Routes/endpoints that will be modified or added
   - Database models/schemas affected
   - Shared utilities or services involved

2. **Map dependencies** — What does this feature depend on?
   - External services or APIs
   - Internal modules that must be stable
   - Configuration or environment variables needed

3. **Assess test coverage** — What's the current state?
   - Existing tests for affected modules
   - Test patterns used (unit, integration, e2e)
   - Coverage gaps that need filling

4. **Check constraints** — What limits the implementation?
   - Performance requirements (latency, throughput)
   - Backward compatibility requirements
   - Deployment constraints (feature flags, migrations)

### Discovery Output

```markdown
## Codebase Discovery Report

**Feature**: [name] **Affected files**: [list with brief role of each] **Dependencies**:
[internal and external] **Current test coverage**: [% or qualitative assessment]
**Constraints identified**: [list] **Recommended approach**: [brief — 2-3 sentences]
**Open questions for architect**: [list]
```

## Phase 2: Design (software-architect)

### Design Document Structure

```markdown
## Design: [Feature Name]

### Problem Statement

[What we're solving and why — 2-3 sentences]

### Proposed Solution

[High-level approach — what changes, what stays the same]

### Interface Design

[API contracts, function signatures, data models]

### Data Flow

[How data moves through the system for this feature]

### Error Handling

[What can go wrong and how we handle each case]

### Migration Strategy

[If schema changes: how to migrate without downtime]

### Alternatives Considered

| Option | Pros | Cons | Why rejected |
| ------ | ---- | ---- | ------------ |

### Risks

- [Risk 1]: [mitigation]
- [Risk 2]: [mitigation]
```

### Design Validation Criteria

Before approving the design, verify:

- [ ] Interfaces are minimal and well-defined
- [ ] Error cases are explicitly handled
- [ ] No unnecessary coupling introduced
- [ ] Migration path is safe (reversible if possible)
- [ ] Performance impact is acceptable

## Phase 3: Implementation (senior-developer)

### Implementation Order

1. **Database/schema changes** — Migrations first, backward-compatible
2. **Domain logic** — Core business rules, well-tested
3. **API/interface layer** — Endpoints, validation, serialization
4. **Integration** — Wire everything together
5. **Tests** — Unit → integration → e2e (if not TDD)

### Commit Strategy

- One logical change per commit
- Commit message format: `type(scope): description`
- Types: feat, fix, refactor, test, docs, chore
- Each commit should leave the codebase in a working state

### Quality Gates During Implementation

After each major component:

- [ ] Tests pass
- [ ] Linter clean
- [ ] No type errors
- [ ] Feature works as designed (manual smoke test)

## Phase 4: Verification (code-reviewer + senior-developer)

### Review Focus Areas

- Does the implementation match the approved design?
- Are edge cases handled?
- Is error handling consistent with project patterns?
- Are tests meaningful (not just coverage padding)?
- Is the code readable without the design doc?

## Phase 5: Documentation (technical-writer)

### What to Document

- [ ] API reference (if new endpoints)
- [ ] Configuration changes (new env vars, feature flags)
- [ ] Migration guide (if breaking changes)
- [ ] README updates (if user-facing)
- [ ] Changelog entry
