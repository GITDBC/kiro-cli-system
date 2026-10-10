---
name: software-design-review
description: >
  Software design review applying principles from 'A Philosophy of Software Design'
  (Ousterhout). Use when evaluating module depth, information hiding, interface design,
  or naming quality. Triggers: 'design review', 'is this well designed', 'evaluate
  architecture'. Scope boundary: this skill judges design quality only — it never finds
  bugs, enforces coding conventions, or applies fixes. Not for security review (use
  security-audit), code style/linting, bug-finding, convention enforcement, or applying
  fixes (use reviewing-code — that skill owns all code-level red-flag scanning and
  remediation, plus code style and lint enforcement, this skill owns structural design
  judgment only), or debt inventory/scoring (use tech-debt-tracking — this skill's
  structural findings overlap its code-debt criteria but do not score or prioritize).
---

# Software Design Review

## Workflow

Execute two agents in **parallel**. For the full Ousterhout red-flag checklists used by
both tracks, load `references/ousterhout-principles.md`.

### Track 1 — Structural design → `software-architect`

Evaluate module depth, information hiding, and abstraction quality (full checklist in
`references/ousterhout-principles.md`).

Output: findings table `| Location | Principle violated | Severity | Suggestion |`

### Track 2 — Code-level red flags → `code-reviewer`

Scan for the Ousterhout-specific red flags catalogued in
`references/ousterhout-principles.md` (Information Leakage, Pass-Through Method,
Repetition, Vague Name, etc.). This track exists to check design-quality red flags
specifically; general bug-finding and convention enforcement stay with the
`reviewing-code` skill and are out of scope here.

Output: findings table `| Location | Red flag | Severity | Suggestion |`

## Synthesis

Combine both tracks into a single report:

1. **Design Health Summary** — Overall rating:
   - 🟢 Clean: few or no design issues
   - 🟡 Moderate: some improvements would reduce complexity
   - 🔴 Concerning: significant issues that will compound over time

2. **Consolidated Findings** — All items from both tracks, single table sorted by
   severity (critical → low), noting which track flagged each.

3. **Design Principles Scorecard:**

| Principle          | Score (1-5) | Notes |
| ------------------ | ----------- | ----- |
| Module depth       |             |       |
| Information hiding |             |       |
| Error design       |             |       |
| Naming quality     |             |       |
| Abstraction level  |             |       |
| Code obviousness   |             |       |

4. **Recommended Refactoring** — Top 3 highest-impact improvements with concrete steps.

## Success Criteria

- Both agent reports received and synthesized · every finding has a concrete actionable
  suggestion · findings sorted by severity · scorecard completed.
