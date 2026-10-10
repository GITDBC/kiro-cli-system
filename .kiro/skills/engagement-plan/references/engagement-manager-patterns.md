# Engagement Manager Patterns

Concrete templates for structuring client engagements. Load this file when drafting the
engagement structure (Step 1) or the risk register and communication plan (Step 3) of
the `engagement-plan` skill.

## Risk Register Template

| ID   | Risk description | Category                             | Likelihood (1-5) | Severity (1-5) | Score (L×S) | Mitigation                                                                 | Contingency                                               | Owner | Status                               |
| ---- | ---------------- | ------------------------------------ | ---------------- | -------------- | ----------- | -------------------------------------------------------------------------- | --------------------------------------------------------- | ----- | ------------------------------------ |
| R-01 |                  | Technical / Commercial / Operational |                  |                |             | Action taken to reduce likelihood or severity BEFORE the risk materializes | Action taken AFTER the risk materializes, to limit impact |       | Open / Mitigated / Accepted / Closed |

Scoring guide:

- **Likelihood** (1 = rare, unlikely this engagement · 5 = near-certain, already
  observed in similar engagements).
- **Severity** (1 = cosmetic delay · 5 = engagement-ending: client withdraws, data
  breach, contractual breach).
- **Score** = Likelihood × Severity. Escalate to sponsor/steering committee when Score
  ≥ 15. Review weekly when Score ≥ 9.
- Mitigation reduces the _probability_; contingency reduces the _impact_. Every risk
  with Score ≥ 9 must have both, not just one.

## Phased Deliverable Template

| Phase          | Objective                                                    | Entry criteria                           | Exit criteria                                                                       | Deliverables                                 | Owner | Duration |
| -------------- | ------------------------------------------------------------ | ---------------------------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------- | ----- | -------- |
| 0 — Discovery  | Confirm scope, access, and success metrics                   | Signed engagement letter / NDA           | Data access confirmed; success metrics agreed in writing                            | Scope document, data access checklist        |       |          |
| 1 — Validation | Prove technical feasibility on a representative sample       | Entry criteria of Phase 0 met            | Feasibility demonstrated against agreed threshold, or explicit no-go with rationale | Feasibility memo, go/no-go recommendation    |       |          |
| 2 — Prototype  | Build a demonstrable prototype on the full available dataset | Go decision from Phase 1                 | Prototype meets acceptance criteria in a live or staged demo                        | Working prototype, demo script, results deck |       |          |
| 3 — Handover   | Transfer knowledge and artifacts to the client team          | Prototype accepted by client stakeholder | Client team can operate/extend the artifact without the engagement team             | Runbook, source code, final report           |       |          |

Rules:

- Do not start a phase before its entry criteria are met and signed off — this is the
  most common source of scope disputes.
- Exit criteria must be measurable (a threshold, a signed acceptance, a passing demo) —
  never "client is satisfied" without a concrete proxy.
- Keep phases short enough that a no-go decision at Phase 1 wastes at most one phase of
  effort.

## Stakeholder Map Template

| Stakeholder | Role | Influence (H/M/L) | Interest (H/M/L) | Quadrant             | Communication cadence            | Preferred channel |
| ----------- | ---- | ----------------- | ---------------- | -------------------- | -------------------------------- | ----------------- |
|             |      |                   |                  | Manage closely (H/H) | Weekly 1:1 or steering committee |                   |
|             |      |                   |                  | Keep satisfied (H/L) | Milestone summary only           |                   |
|             |      |                   |                  | Keep informed (L/H)  | Bi-weekly digest                 |                   |
|             |      |                   |                  | Monitor (L/L)        | Ad hoc / on request              |                   |

Quadrant guidance:

- **Manage closely (High influence, High interest)**: sponsors, primary technical
  counterpart. Weekly touchpoints minimum; involve in go/no-go decisions.
- **Keep satisfied (High influence, Low interest)**: executives, budget holders.
  Milestone-level updates; avoid technical detail unless requested.
- **Keep informed (Low influence, High interest)**: end users, adjacent teams. Regular
  but lightweight updates; no decision authority to manage.
- **Monitor (Low influence, Low interest)**: peripheral stakeholders. Minimal proactive
  contact; respond if they reach out.

## Data Governance Constraint Checklist

Complete before any data leaves the client environment or before any analysis begins:

- [ ] **Data residency**: confirmed whether data (or derivatives) may leave the client's
      environment/cloud tenant at all, or must be processed in place.
- [ ] **Anonymization/pseudonymization**: identify direct identifiers (names, IDs,
      contact info) and quasi-identifiers (combinations that re-identify); confirm the
      required transformation (hashing, tokenization, aggregation) before export.
- [ ] **Purpose limitation**: confirm data is used only for the scope defined in the
      engagement letter — not for building a reusable internal benchmark without
      separate consent.
- [ ] **Retention period**: confirm how long data/derivatives may be retained after
      engagement close, and the deletion mechanism (who deletes, how it is verified).
- [ ] **Access control**: confirm which named individuals on the engagement team may
      access raw data vs. derived/aggregated data only.
- [ ] **Third-party subprocessors**: confirm whether any tool used (cloud LLM API, SaaS
      analytics platform) constitutes a subprocessor requiring client sign-off.
- [ ] **Breach notification**: confirm the agreed notification window and contact if a
      data incident occurs during the engagement.
- [ ] **Audit trail**: confirm whether the client requires logging of who accessed what
      data and when.

Any unchecked item is a blocker for Phase 0 exit, not a "note for later."
