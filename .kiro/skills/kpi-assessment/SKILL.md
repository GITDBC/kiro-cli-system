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

1. **kpi-analyst** — KPI inventory and gap analysis:
   - Receive scope (use case, technology domain, available data sources).
   - Categorize existing KPIs by domain.
   - For each KPI: validate formula, identify required measurements, flag missing
     denominators/normalizations, check distribution availability. For counter-formula
     validation patterns and common normalization pitfalls, load
     `references/kpi-engineering-patterns.md`.
   - Identify gaps: uncovered categories, average-only KPIs without distribution
     support, missing cross-layer correlations. If the domain is telecom, cross-check
     against `references/telecom-kpi-catalog.md` for standard counters and formulas
     before flagging a KPI as missing.
   - Produce a structured KPI catalog as a Markdown table.

2. **telecom-engineer** — Domain validation:
   - Review catalog against relevant standards and vendor documentation.
   - Validate formulas are physically meaningful and correctly normalized.
   - Flag vendor-specific quirks (naming inconsistencies, counters requiring special
     activation).
   - Suggest additional KPIs from domain engineering perspective.

3. **kpi-analyst** — Consolidation and prioritization:
   - Merge domain expert feedback into the catalog.
   - Classify each KPI: must-have, nice-to-have, backup.
   - Recommend percentile-based analysis over threshold-based where applicable.
   - Produce final KPI framework document: catalog, measurement request list, gap
     summary, analysis recommendations.

Size each catalog entry and gap note to what the KPI needs; do not add filler rows to
match the length of other entries.

## Success Criteria

- KPI catalog produced as Markdown table with formula, unit, and counters per KPI.
- Every KPI formula validated for dimensional consistency (no missing denominators).
- Gap analysis identifies domains with no coverage.
- KPIs classified into tiers (must-have, nice-to-have, backup).
- Measurement request list produced with counter names and source layers.
