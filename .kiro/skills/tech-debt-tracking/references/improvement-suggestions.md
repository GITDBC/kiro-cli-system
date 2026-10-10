# Improvement Suggestions Workflow

Full detail for Workflow 2 of `tech-debt-tracking`. Load this file when the user asks
for improvement suggestions rather than a debt assessment (triggers: 'suggest
improvements', 'what can be improved', 'optimization opportunities').

## Workflow 2: Improvement Suggestions

Execute three agents **in parallel**:

1. **code-reviewer** — repetitive patterns, automation candidates, code duplication
2. **software-architect** — missing abstractions, workflow bottlenecks, reuse
   opportunities
3. **platform-engineer** — observability gaps, toil reduction, missing monitoring

### Phase 2: System Self-Analysis

After parallel analysis, **orchestrator** performs:

- **Agent configuration audit** — overlapping triggers, dead agents, consolidation
  candidates
- **Tool gap analysis** — missing integrations, feature opportunities
- **Instruction freshness** — stale rules, redundant instructions, deprecated patterns

### Output

Save to `suggestions/improvements_<YYYY-MM-DD>.md`:

- **Quick wins**: low effort, high impact
- **New tools/skills proposed**: what they'd do, which agents use them
- **Workflow optimizations**: steps to remove, parallelize, or automate
- **Deferred ideas**: high effort, worth considering later
- **System health**: agent utilization, overlap, coverage gaps
- **Instruction freshness**: stale or redundant agent instructions

## Rules

- Run periodically (suggested: monthly).
- Assessment only — do not apply fixes directly; hand off to `senior-developer` or
  `code-reviewer` for execution.
