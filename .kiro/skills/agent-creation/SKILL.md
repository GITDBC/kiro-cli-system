---
name: agent-creation
description: >
  Sequential workflow for creating new agents or skills within the work-agents system.
  Use when asked to create a new agent, add a new skill, write a SKILL.md, improve
  existing agent/skill definitions, or evaluate whether a skill triggers correctly. Not
  for general coding tasks, refactoring, or documentation outside the agent system.
---

# Agent / Skill Creation Workflow

## Workflow

```
- [ ] Phase 1: Discovery (define spec)
- [ ] Phase 2: Drafting (write files)
- [ ] Phase 3: Review (quality check)
- [ ] Phase 4: Security audit
- [ ] Phase 5: Integration
```

### Phase 1 — Discovery → `software-architect`

**For agents**, produce a spec with: name (kebab-case), description, `trigger_when` /
`never_when`, tools needed, collaboration patterns. Evaluate whether an existing agent
could absorb the capability.

**For skills**, clarify: what it enables, when it triggers, expected output format,
grounding in project artifacts.

### Phase 2 — Drafting → `senior-developer`

**For agents:**

1. `.kiro/prompts/<name>.md` — Identity, Core Mission, Critical Rules, Boundaries.
2. `.kiro/agents/<name>.json` — prompt reference, tools, resources.

**For skills:**

1. `.kiro/skills/<name>/SKILL.md` with:
   - Frontmatter: `name` (kebab-case, matches directory), `description` (max 1024 chars,
     includes trigger contexts and the `Not for ...` boundary).
   - Body: workflow steps referencing agents, rules, done-when criteria.

Apply the skill authoring rules below to every draft, and keep the highest-value content
in view while writing: provide defaults rather than menus, state the gotchas, and give a
validation loop (do → validate → fix → repeat).

### Phase 3 — Review → `code-reviewer`

Check: clarity (another LLM can follow unambiguously) · no routing overlap · project
convention adherence · body passes the progressive-disclosure test · description answers
"what?" and "when?".

### Phase 4 — Security audit → `security-engineer`

Audit for: command injection · data exfiltration · prompt injection · overly broad
`allowedCommands`.

All CRITICAL/HIGH items must be resolved before integration.

### Phase 5 — Integration → `orchestrator`

**For agents:** add to routing table in `routing.md`, add to `availableAgents` in
`orchestrator.json`, add collaboration patterns.

**For skills:** verify triggers correctly on 2+ realistic prompts; add collaboration
pattern to `routing.md` if multi-agent.

## Skill Authoring Rules

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). Apply all
four to every draft; the rationale for each is in `references/patterns-reference.md` (§
"Skill Authoring Rules — detail"), which is the file to load when a rule's application
to a specific draft is unclear.

- **Pointer rule** — state what the material is and name the branches that should reach
  it, front-loading the leading word and giving one trigger per branch.
- **No-op hunt** — delete every instruction the model already follows by default, whole
  sentence at a time.
- **Positive instruction** — state the target behaviour rather than the prohibition it
  replaces. This governs skill **bodies**; skill **descriptions** keep their explicit
  `Not for ...` boundaries.
- **Progressive-disclosure test** — inline what every branch needs; move behind a
  pointer what only some branches reach. Line count is a symptom, not the criterion.

## Reference Material

`references/patterns-reference.md` — templates and structural conventions of this
repository: prompt skeleton, agent JSON shape, resource conventions, steering-file
table, integration checklist. Reach for it in Phase 2 before writing any file, and in
Phase 5 when wiring the artifact into routing. Where it and the upstream standard
disagree, this repository's conventions win.

`references/agentskills/` holds a vendored mirror of the official Agent Skills standard
documentation (CC-BY-4.0). `references/agentskills/PROVENANCE.md` records the upstream
paths, the fetch date and the attribution; corrections go upstream and arrive through
`make sync-agentskills`, which overwrites local edits.

- **Format specification** — `agentskills/specification.md` carries the normative
  frontmatter fields and their limits, the directory layout, and file-reference
  semantics. Reach for it when a frontmatter constraint is in question, when placing
  content between `scripts/`, `references/` and `assets/`, or when validating a name.
- **Description tuning** — `agentskills/optimizing-descriptions.md` explains how a
  description drives triggering, how to design should-trigger and should-not-trigger
  queries, and how to run the optimisation loop. Reach for it when a skill fails to
  fire, when it fires on unrelated prompts, or when writing a new description.
- **Authoring practice** — `agentskills/best-practices.md` covers scoping and
  calibration: starting from real expertise, gotchas sections, defaults over menus,
  procedures over declarations, output templates. Reach for it when a draft reads
  generic or when the level of prescription for a step is unclear.
- **Output evaluation** — `agentskills/evaluating-skills.md` describes eval-driven
  iteration: test cases, assertions, grading, aggregation. Reach for it when a skill
  triggers correctly but its output quality is disputed, or when a proposed change needs
  evidence that it helps.
- **Script bundling** — `agentskills/using-scripts.md` compares one-off commands with
  bundled scripts and covers self-contained dependencies and script interfaces. Reach
  for it when a skill has to execute code, or when choosing between an inline command
  and a `scripts/` entry.
- **First-skill walkthrough** — `agentskills/quickstart.md` builds one minimal skill end
  to end. Reach for it when onboarding someone to the format, or when a worked minimal
  example settles a structural question faster than the specification.

## Skill Quality Checklist

- [ ] `name` matches directory, kebab-case, 1–64 chars
- [ ] `description` states what and when, includes the `Not for ...` boundary, under
      1024 chars
- [ ] Body passes the progressive-disclosure test; branch-specific detail sits in
      `references/`
- [ ] Every file in `references/` is reachable from the body (`make drift-check` reports
      unreachable ones)
- [ ] Instructions explain _why_, not just _what_
- [ ] Examples included where usage is not obvious
- [ ] Tested with at least 2 realistic prompts

## Done when

- Artifact files created following conventions.
- Review passes with no critical issues.
- Security audit clean (no CRITICAL/HIGH open).
- Integration complete (routing table, orchestrator config).
- Tested with realistic prompts.
