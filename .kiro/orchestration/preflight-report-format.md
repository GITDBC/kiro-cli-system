# Preflight Report format

On-demand reference. Read it when a dispatch declares `mode: preflight` — a separate,
read-only preflight turn whose only deliverable is this report. Combined mode, the
default through Medium complexity, needs a 2-3 line preflight and does not consult this
file.

The rules that govern when each mode applies live in `.kiro/steering/COMMON.md`
(`## Preflight Protocol`) for the agent side and
`.kiro/orchestration/delegation-lifecycle.md` (`### Delegation modes`,
`### Depth calibration`) for the orchestrator side. This file carries the shape of the
artifact only.

## Template

```markdown
## Preflight Report

**Task understanding**: [1-2 sentences restating what you need to do] **Complexity
assessment**: trivial | low | medium | high **Feasibility**: ✅ fully feasible | ⚠️
feasible with risks | ❌ blocked

### Can do

- [Concrete items you can deliver]

### Risks (I can handle)

- [Problems you foresee but can resolve]

### Blockers (need help)

- [Items outside your scope]
- [Suggested agent: <agent-name> — reason: <why>]

### Ambiguities (need clarification)

- [Questions where the task is unclear]
- [Assumptions you would make if no clarification]

### Execution plan

- [Ordered list of steps]
- [Files you will read/modify]
```

## Why the template is not always-on

The template is consumed only in the rare separate-preflight dispatch, while
`.kiro/steering/COMMON.md` is auto-loaded into every session of every agent, so a
resident copy was paid on every request to serve a minority of turns. The mitigation for
moving it is that the `Preflight` row of the Delegation modes table names this path, so
the dispatch instruction itself carries the read; without that, an agent with no
template in context improvises a plausible-looking report and the orchestrator's
structural validation passes on the wrong shape.
