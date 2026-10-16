---
name: security-audit
description: >
  Security audit in two parallel dispatches: security-engineer (threat model, code
  vulnerabilities, configuration/dependencies) plus code-reviewer. Triggers: 'security
  audit', 'check for vulnerabilities', 'pen test review'. Not for dependency scanning
  only (use deps-audit) or operational security (delegate to platform-engineer).
---

# Security Audit

## Workflow

### Step 1 — Parallel analysis (2 dispatches)

Run both in **parallel**:

1. **security-engineer** — the whole security surface in one pass, carrying the coverage
   instruction below verbatim.
2. **code-reviewer** — input validation, error handling, auth patterns, and other
   quality-adjacent findings with security consequences.

Why two dispatches rather than four: "Security audit" section of
`.kiro/orchestration/orchestration-rationale.md`.

#### Coverage instruction (paste verbatim into the security-engineer dispatch)

> Cover all three perspectives in this single pass, and structure the report under one
> heading per perspective so a gap is visible rather than implicit:
>
> - **A — Threat model (attacker view)**: attack surface enumeration, exploitability,
>   attack chains, OWASP Top 10, privilege boundaries, highest-impact attack paths.
> - **B — Code vulnerabilities**: injection, deserialization, authentication and
>   authorization logic, session handling, crypto use, error and log handling, CWE Top
>   25, secrets in source.
> - **C — Configuration and dependencies**: dependency CVEs and pinning, container and
>   runtime configuration, CI/CD pipeline exposure, network and permission
>   configuration, secret management, defense-in-depth gaps and missing controls.
>
> Report everything you find with a severity attached; do not withhold a finding because
> it looks minor, and do not filter at the finding stage. Filtering by severity happens
> in the synthesis step, downstream of the report.

The reporting rule is deliberate: a bar applied while findings are being produced
silently lowers recall, whereas a complete severity-tagged list can be filtered
afterwards without losing anything.

For the STRIDE threat-model template, a secure API endpoint pattern, and the CI/CD
security scan stages, load `references/security-engineer-patterns.md`; the
per-perspective checklists (OWASP Top 10, controls, configuration), the finding report
format, and severity scoring are in `references/three-perspective-audit-checklist.md`.
When the audit target is a skill, agent prompt, bundled script, or MCP configuration
rather than application code, the report contract is in
`references/skill-audit-report-format.md`.

#### When a third dispatch is justified

Add one further security-engineer dispatch scoped to perspective C **only** when the
configuration or dependency surface is genuinely a separate codebase — a standalone IaC
repository, a vendored dependency tree, an infrastructure monorepo audited alongside the
application. Configuration files living next to the code under audit are not a separate
codebase and stay inside the single dispatch.

### Step 2 — Synthesis

Consolidate the two reports into a unified security assessment:

- Merge duplicates: the same defect reported by both agents keeps the higher severity
  and cites both.
- Attach confidence per finding from the evidence, not from agreement counts: **HIGH**
  when the report cites the offending code, configuration, or dependency version
  directly; **MEDIUM** when the finding is inferred from surrounding behaviour and needs
  manual confirmation.
- Sort by severity (Critical → Low), then confidence.

## Success Criteria

- Both agent reports received and synthesized.
- The security-engineer report covers perspectives A, B, and C under explicit headings.
- Every finding carries a severity and a confidence level.
- Findings sorted by severity with concrete remediation per item.
- No Critical finding without a remediation recommendation.
- Final report includes a summary table with counts by severity and confidence.
