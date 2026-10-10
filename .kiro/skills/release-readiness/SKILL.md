---
name: release-readiness
description: >
  Release readiness assessment workflow. Use when evaluating whether a release is ready
  to ship, checking test results, reliability, and security posture. Not for feature
  development, bug fixing, or post-release monitoring.
---

# Release Readiness

## Invocation

Use when: evaluating whether a release is ready to ship, gathering test/reliability/
security posture ahead of a go/no-go decision.

Do NOT use when: developing the feature itself (`spec-to-dev`), fixing bugs
(`debugging`), or monitoring after the release has already shipped.

## Workflow

Run these agents in **parallel** (independent assessments):

1. **qa-engineer** — Test coverage, failure patterns, flaky tests, quality metrics.
2. **platform-engineer** — SLOs, monitoring, rollback plan, capacity.
3. **security-engineer** — Open vulnerabilities, secrets scan, dependency audit.

Synthesize into a go/no-go recommendation with risk summary.

## Success Criteria

- All 3 reports received.
- Clear GO or NO-GO stated with justification.
- Every NO-GO blocker has a concrete remediation or mitigation path.
- Risk summary includes residual risks accepted for a GO decision.
- No critical test failures, open vulnerabilities, or missing rollback plans left
  unaddressed.
