---
name: spec-to-dev
description: >
  Specification-driven development: plan-then-execute cycle for features from Jira
  tickets, specs, or feature descriptions. Triggers: 'implement this ticket', 'spec to
  code', 'build this feature', 'new feature', 'feature end-to-end'. Not for quick fixes
  (use reviewing-code), exploratory coding, or tasks without a clear goal.
---

# Specification-Driven Development

## Workflow

```
- [ ] Phase 1: Understanding (exploration + analysis + decomposition)
- [ ] Phase 2: Planning (design + user validation)
- [ ] Phase 3: Execution (coordinate + implement + review + fix)
- [ ] Phase 4: Closure (documentation)
```

### Phase 1 — Understanding

**Step 1** → `senior-developer`: If Jira URL/key provided, run jirafetcher. Inspect repo
structure, relevant modules, existing tests. Produce context summary.

**Step 2** → `software-architect`: Analyze context, define technical approach +
alternatives + risks, identify if an ADR is needed, produce the design document. For the
design-document template, design validation criteria, and the vertical-slicing rules
used when decomposing subtasks, load `references/spec-to-dev-playbook.md`. Decompose
into parallelizable subtasks:

```yaml
subtasks:
  - id: st-1
    title: "Brief description"
    boundary: "ComponentName"
    files_owned: [path/file1.py, path/file2.py]
    depends_on: []
    interfaces_exposed:
      - name: "InterfaceName"
        contract: "Signature or schema consumed by others"
    interfaces_consumed:
      - from: st-2
        name: "InterfaceName"
```

Decomposition rules: each subtask has EXCLUSIVE file ownership · non-overlapping
`boundary` = parallel-safe · empty `depends_on` = parallel · simple features (≤3 files)
use a single subtask.

### Phase 2 — Planning

**Step 3** → `orchestrator`: Build the plan per `Planning phases` in
`delegation-lifecycle.md`. **STOP for user approval before proceeding.**

### Phase 3 — Execution

**Step 4** → `orchestrator` (Coordination Protocol in `delegation-lifecycle.md`):

1. Group subtasks by `depends_on` into waves (wave 0 = parallel, wave N waits on N-1).
2. Build the Shared Context Contract per wave.
3. Delegate each subtask to `senior-developer` in **combined mode** by default; a
   separate preflight turn only for the reserved cases in `Delegation modes`, followed
   by execute mode once it clears.
4. **Interface gate**: before launching wave N+1, review the subtasks in wave N whose
   `interfaces_exposed` appear in any later wave's `interfaces_consumed`. Delegate one
   `code-reviewer` pass scoped to those interface contracts only — signatures, schemas,
   error contracts — not full implementation quality. Subtasks exposing nothing consumed
   downstream skip this gate and are reviewed once at Step 6.

**Step 5** → `senior-developer` (per subtask): Modify ONLY `files_owned` · implement
`interfaces_exposed` · consume `interfaces_consumed` · write tests. For implementation
order, load `references/spec-to-dev-playbook.md`; for function, error-handling, async,
and dataclass patterns, `references/senior-developer-patterns.md`. **GATE**:
`pytest --cov` passes at the coverage floor in `code-standards-summary.md`.

**Run artifact** — `notes/spec-to-dev_<feature>_<YYYY-MM-DD>.md`, written by the
orchestrator at Step 4 and appended to by each `senior-developer` dispatch:

```markdown
## Subtask status

| id   | phase                                                 | files touched |
| ---- | ----------------------------------------------------- | ------------- |
| st-1 | preflight-cleared \| implemented \| reviewed \| fixed | ...           |

## Implementation notes

- [st-1] One line per cross-cutting discovery that affects other subtasks.
```

Each dispatch reads `## Implementation notes` before starting and appends to it on
finishing — a single `[st-N]`-prefixed line, never a rewrite of the section, so
concurrent dispatches in the same wave cannot drop each other's entries. The
orchestrator re-reads `## Subtask status` at the start of every wave rather than
recalling it, and a resumed run continues from the first subtask not marked `reviewed`.

**Step 6** → `code-reviewer`: Review full implementation against plan and project
standards. Verify the diff touches only each subtask's declared `files_owned` — a file
modified outside its owner's boundary is a finding, not a style note. Produce structured
fix list if critical issues found.

**Step 7** → `senior-developer` (only if step 6 found problems): Apply fixes. **GATE**:
`pytest`, no regressions. Max 2 iterations of steps 6–7; remaining findings logged as
tech debt.

### Phase 4 — Closure

**Step 8** → `technical-writer`: Update README, API references, changelogs, usage
examples.

## Rules

- Orchestrator MUST pause for user validation after Phase 2.
- Gates are hard — no code moves forward with failing tests.
- For simple features without a Jira, skip step 1 jirafetcher and start from user
  description.

## Done when

- All gates pass (tests green, coverage at the floor) · code review complete with zero
  critical findings · documentation updated · user approved the plan before execution.
