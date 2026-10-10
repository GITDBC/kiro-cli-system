---
name: deps-audit
description: >
  Dependency audit using depschecker. Use when checking dependency freshness,
  vulnerabilities, or planning upgrades. Triggers: 'check dependencies', 'audit deps',
  'outdated packages', 'vulnerability scan'. Not for general code review or security
  audits beyond dependencies.
---

# Dependency Audit

## Invocation

Use when: checking dependency freshness, scanning for vulnerabilities, or planning
upgrades ahead of a migration.

Do NOT use when: general code review without a dependency focus (`reviewing-code`) or a
full security audit beyond dependencies (`security-audit`).

## Workflow

1. **senior-developer** — Freshness check:
   - Run
     `cd tools/depschecker && uv run depschecker --freshness-only <path-to-pyproject.toml>`.
   - Highlight packages with major/minor updates requiring migration effort.
   - Produce summary with upgrade recommendations and risk assessment.

2. **security-engineer** — Vulnerability scan:
   - Run
     `cd tools/depschecker && uv run depschecker --vulns-only <path-to-pyproject.toml>`.
   - Cross-reference with freshness report: flag whether upgrading resolves each
     vulnerability.
   - Produce prioritized report: Package | Current | CVE/Advisory | Severity | Fixed in
     | Upgrade resolves?
   - State "uncertain" rather than asserting a fix when the advisory data does not
     clearly confirm the upgrade resolves the CVE. A false "resolves" claim leaves the
     team exposed.

Pass the full senior-developer report as context to the security-engineer step.

## Success Criteria

- Freshness report produced with upgrade recommendations.
- Vulnerability report produced with severity and fix-version mapping.
- Clear prioritization: which upgrades resolve security issues vs. are optional
  freshness bumps.
