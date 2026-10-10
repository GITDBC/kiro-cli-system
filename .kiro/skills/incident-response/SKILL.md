---
name: incident-response
description: >
  Production incident response workflow with iterative diagnosis. Use when handling a
  production incident, outage, or degradation that needs diagnosis and remediation. The
  platform-engineer agent investigates in up to 3 rounds before handing off to
  remediation. Not for planned maintenance, post-mortems without active incidents, or
  security audits.
---

# Incident Response

## Workflow

1. **platform-engineer** — Diagnose (iterative, max 3 rounds):
   - **Round 1**: Analyze logs, metrics, traces. Form initial hypothesis. → Root cause
     identified? Proceed to step 2.
   - **Round 2**: Request broader data (time range, adjacent services, correlated
     events). Refine. → Root cause identified? Proceed to step 2.
   - **Round 3**: Escalate scope (infrastructure layer, recent deployments, external
     dependencies). Final hypothesis.
   - After 3 rounds, proceed with best-effort diagnosis and flag uncertainty.

2. **platform-engineer** — Implement fix: hotfix, rollback, scale infrastructure, or
   update configurations.

3. **platform-engineer** — Draft post-mortem with timeline, root cause, impact, and
   action items. If diagnosis was uncertain, mark as requiring follow-up investigation.

## Reference

For severity classification, communication templates, and post-mortem format, see
`references/incident-triage-and-postmortem.md`. For diagnosis heuristics (log
correlation, metric triage, rollback decision criteria) during Round 1-3 of the diagnose
step, load `references/sre-patterns.md`.

## Success Criteria

- Root cause identified (or explicitly flagged as uncertain with follow-up plan).
- Fix applied and verified (service restored or degradation mitigated).
- Post-mortem drafted with timeline, impact, and action items.
