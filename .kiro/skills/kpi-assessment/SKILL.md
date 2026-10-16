---
name: kpi-assessment
description: >
  End-to-end KPI framework assessment. Use when defining, reviewing, or validating a set
  of KPIs for observability, SLA validation, or performance analysis. Produces a
  structured KPI catalog with formulas, measurement mappings, gap analysis, and
  prioritization. Not for implementing dashboards or collecting metrics — assessment and
  design only.
---

# KPI Assessment

## Workflow

1. **kpi-analyst — catalog and gaps.** Validate each KPI's formula and counters, then
   list the gaps. In a telecom domain, cross-check `references/telecom-kpi-catalog.md`
   for the standard counters and formulas before flagging a KPI as missing. The catalog
   entry and measurement-request templates, the percentile-direction convention, and the
   minimum-attempt thresholds are in `references/kpi-engineering-patterns.md`.
2. **telecom-engineer — domain review.** Check formulas against standards and vendor
   documentation (naming quirks, counters needing activation) and suggest missing KPIs.
   End the review with the literal line `NEEDS_CHANGES` only when the catalog needs
   revision; the native loop (target: kpi-analyst, max 2 iterations) re-runs step 1 with
   the feedback only when that token is present.
3. **kpi-analyst — final framework.** Merge the feedback, tier every KPI (must-have,
   nice-to-have, backup), and deliver: catalog table (formula, unit, counters), the
   measurement request list with counter names and source layers, and the gap summary.
