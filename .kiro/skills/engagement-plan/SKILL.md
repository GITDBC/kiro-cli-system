---
name: engagement-plan
description: >
  Client engagement planning workflow. Use when structuring a technical validation,
  prototype demonstration, or proof-of-concept delivery for a client. Produces a phased
  engagement plan with deliverables, data requirements, risk register, and communication
  strategy. Not for internal sprint planning, backlog grooming, or technical
  implementation.
---

# Engagement Plan

## Invocation

Use when: structuring a technical validation, prototype demonstration, or
proof-of-concept delivery for an external client.

Do NOT use when: planning internal sprints or backlog grooming (`spec-to-dev`), or
implementing the technical work itself (`senior-developer`).

## Workflow

1. **engagement-manager** — Engagement structure:
   - Receive context (client, solution to validate, timeline, constraints).
   - Define phases with entry/exit criteria and deliverables per phase. Use the phased
     deliverable template in `references/engagement-manager-patterns.md`.
   - Identify data governance constraints (access, retention, deletion). Run the data
     governance checklist in `references/engagement-manager-patterns.md`.
   - Map stakeholders and concerns. Use the stakeholder map template in
     `references/engagement-manager-patterns.md`.
   - Produce draft plan with scope boundaries (in/out/deferred).

2. **kpi-analyst** — Technical deliverable definition:
   - Define KPIs and analysis outputs needed per phase.
   - Classify deliverables: internal analysis, periodic client updates, final report.
   - Identify data dependencies (which measurements must be available by when).
   - Flag analysis that cannot be completed if data constraints are binding.

3. **engagement-manager** — Final plan and risk assessment:
   - Integrate technical deliverable plan into the engagement structure.
   - Build risk register: technical, commercial, and operational risks with mitigations.
     Use the risk register template (severity × likelihood scoring, mitigation vs.
     contingency) in `references/engagement-manager-patterns.md`.
   - Define communication cadence (what, when, and at what detail level).
   - Produce final engagement plan document ready for internal review and client
     presentation.

Size each phase's write-up to its actual scope; a low-risk phase states that briefly
rather than matching the length of a higher-risk one.

## Success Criteria

- Phased plan with entry/exit criteria and deliverables per phase.
- Risk register covering technical, commercial, and operational risks.
- Data dependencies and governance constraints documented.
- Communication cadence defined and ready for client presentation.
