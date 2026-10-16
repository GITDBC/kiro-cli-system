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
convention adherence · `name` matches the directory (kebab-case, 1–64 chars) ·
description answers "what?" and "when?" and keeps the `Not for ...` boundary · body
passes the progressive-disclosure test · every `references/` file is reachable from the
body (`make drift-check` reports unreachable ones).

### Phase 4 — Security audit → `security-engineer`

Audit for: command injection · data exfiltration · prompt injection · overly broad
`allowedCommands`.

All CRITICAL/HIGH items must be resolved before integration.

### Phase 5 — Integration → `orchestrator`

**For agents:** add to routing table in `routing.md`, add to `availableAgents` in
`orchestrator.json`, add collaboration patterns.

**For skills:** add a `skill://.kiro/skills/<name>/SKILL.md` entry to the `resources` of
every agent that declares the skill (including the orchestrator when it runs the
workflow); add or update the skill's Collaboration Patterns row in `routing.md` (every
non-direct-invoke skill needs one); verify it triggers correctly on 2+ realistic
prompts; run `make drift-check`. The integration checklist in
`references/patterns-reference.md` lists the remaining wiring.

## Skill Authoring Rules

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). Apply all
four to every draft; the rationale for each is in `references/patterns-reference.md` (§
"Skill Authoring Rules — detail"), which is the file to load when a rule's application
to a specific draft is unclear.

- **Pointer rule** — state what the material is and name the branches that should reach
  it, front-loading the leading word and giving one trigger per branch.
- **No-op hunt** — delete every instruction the model already follows by default, whole
  sentence at a time. Generic engineering method (how to debug, design a pipeline,
  structure a report) is a no-op too: a skill earns its place only with facts the model
  cannot derive — repository paths and conventions, `tools/` invocations, safety rules,
  orchestration contracts, frozen output formats, or domain data. A workflow with none
  of those becomes a "pattern only" row in `routing.md`, not a skill.
- **Positive instruction** — state the target behaviour rather than the prohibition it
  replaces. This governs skill **bodies**; skill **descriptions** keep their explicit
  `Not for ...` boundaries.
- **Progressive-disclosure test** — inline what every branch needs; move behind a
  pointer what only some branches reach. Line count is a symptom, not the criterion.

## Reference Material

`references/patterns-reference.md` — this repository's templates and conventions (prompt
skeleton, agent JSON shape, resource conventions, steering-file table, integration
checklist). Load it in Phase 2 before writing any file and in Phase 5. Where it and the
upstream standard disagree, this repository's conventions win.

`references/agentskills/` — vendored mirror of the official Agent Skills documentation
(CC-BY-4.0; provenance in `PROVENANCE.md`; refreshed by `make sync-agentskills`, which
overwrites local edits):

| File                         | Load when                                                      |
| ---------------------------- | -------------------------------------------------------------- |
| `specification.md`           | a frontmatter limit, directory layout, or name is in question  |
| `optimizing-descriptions.md` | a skill misfires or a new description is being written         |
| `best-practices.md`          | a draft reads generic or the level of prescription is unclear  |
| `evaluating-skills.md`       | output quality is disputed or a change needs evidence          |
| `using-scripts.md`           | a skill must execute code (inline command vs `scripts/` entry) |
| `quickstart.md`              | a minimal worked example settles a structural question         |

## Done when

- Artifact files created following conventions.
- Review passes with no critical issues.
- Security audit clean (no CRITICAL/HIGH open).
- Integration complete (routing row, `skill://` entries or `availableAgents`).
- Tested with realistic prompts.
