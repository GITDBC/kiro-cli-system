# Agent & Skill Patterns Reference

Concrete conventions and templates for creating agents and skills in this project.
Complements the workflow in `SKILL.md` with structural patterns.

## Project Structure

```
.kiro/
├── agents/           # Agent JSON configs (one per agent)
│   └── <name>.json
├── prompts/          # Agent prompt files (one per agent)
│   └── <name>.md
├── skills/           # Skills (one directory per skill)
│   └── <name>/
│       ├── SKILL.md
│       └── references/   # Optional supporting docs
├── steering/         # Always-on context (loaded by all agents or orchestrator)
└── .cli_bash_history # Kiro internal (gitignored)
```

## Agent Prompt Template

```markdown
---
name: Agent Name
description: One-sentence description of what this agent does and its specialization.
color: "<hex or named color>"
vibe: Short phrase capturing the agent's working style.
---

# Agent Name Agent

All [relevant] rules from COMMON.md apply.

## Critical Rules

1. **Rule one** — concise imperative statement
2. **Rule two** — concise imperative statement

## Workflow

1. **Step name** — one-line description of what to do
2. **Step name** — one-line description
3. **Verify** — what to check before declaring done

## Technical Deliverables

Load `references/<name>-patterns.md` for concrete templates:

- **Pattern A** — brief description
- **Pattern B** — brief description

## Boundaries

Do NOT use this agent when:

- Condition → use `<other-agent>` instead
- Condition → use `<other-agent>` instead

## Safety

- Safety rule 1
- Safety rule 2
```

### Required Sections

| Section                                      | Required | Purpose                                       |
| -------------------------------------------- | :------: | --------------------------------------------- |
| Frontmatter (name, description, color, vibe) |    ✅    | Identity and display                          |
| Critical Rules                               |    ✅    | Hard constraints the agent must never violate |
| Workflow                                     |    ✅    | How the agent approaches tasks                |
| Technical Deliverables                       | Optional | Reference to detailed patterns file           |
| Boundaries                                   |    ✅    | When NOT to use (prevents mis-routing)        |
| Safety                                       |    ✅    | Security and destructive-action guardrails    |

### What NOT to include

- "Your Identity & Memory" / personality prose — behavior comes from rules, not
  self-description
- "Success Metrics" — agents don't self-measure
- "Communication Style" — obvious professional norms don't need restating
- Verbose motivation or context-setting paragraphs

## Agent JSON Config Template

```json
{
  "name": "<kebab-case-name>",
  "description": "One sentence matching the prompt's description.",
  "prompt": "file://../prompts/<name>.md",
  "tools": ["read", "write", "shell"],
  "includeMcpJson": false,
  "includePowers": false,
  "permissions": {
    "rules": [
      { "capability": "fs_read", "match": ["./**"], "effect": "allow" },
      { "capability": "fs_write", "match": ["./**"], "effect": "allow" },
      {
        "capability": "fs_write",
        "match": ["config.toml", "**/config.toml", ".env", "**/.env"],
        "effect": "deny"
      },
      { "capability": "shell", "match": ["uv *", "make *"], "effect": "allow" },
      { "capability": "skill", "match": ["*"], "effect": "allow" },
      { "capability": "diagnostics", "match": ["*"], "effect": "allow" }
    ]
  },
  "resources": [
    "file://../steering/COMMON.md",
    "file://../steering/code-standards-summary.md",
    "file://../steering/python-environment.md",
    "skill://.kiro/skills/<relevant-skill>/SKILL.md"
  ],
  "welcomeMessage": "One line stating what the agent is ready to do.",
  "model": "claude-sonnet-5"
}
```

### Config Field Conventions

The v3 agent engine is the only supported target, so the template above carries v3
fields exclusively. The distinctions that matter when writing a new config:

- `tools` takes **capability tags** (`read`, `write`, `shell`, `web`, `subagent`,
  `knowledge`), not individual tool ids. The `read` tag covers `read`, `glob`, `grep`
  and `code` together, so none of those is listed separately.
- `permissions.rules` is the only authorization mechanism. Each rule names a
  `capability`, a `match` list of **glob** patterns, and an `effect` of `allow`, `deny`
  or `ask`.
- Deny wins across every scope, with no precedence, and an operation matching no rule
  **asks** rather than being denied. An `ask` reaching a non-interactive subagent fails
  fast, so every capability an agent needs must carry an explicit allow rule.
- Omitting a capability is how access is withheld: an agent that must not write files
  carries no `fs_write` allow rule, and a `deny` rule is added only where a narrower
  exception inside an allowed scope is required (credential files inside an allowed
  `./**` write scope, for example).

Three field shapes are **removed** in v3 and must never appear in a new config:
`allowedTools`, per-tool `toolsSettings` blocks (`shell`, `fs_read`, `fs_write`, and
settings such as `allowedCommands`, `deniedPaths`, `autoAllowReadonly`,
`denyByDefault`), and an embedded `hooks` key — hooks live in standalone
`.kiro/hooks/*.json` files using the v1 schema. The `Legacy v2 agent config fields`
drift check fails the build when any of them reappears under `.kiro/agents/`.

The single surviving `toolsSettings` sub-block is `toolsSettings.subagent`, which is
added only on an agent that dispatches subagents:

```json
{
  "toolsSettings": {
    "subagent": {
      "availableAgents": ["<agent-slug>", "<agent-slug>"],
      "trustedAgents": ["*"]
    }
  }
}
```

`availableAgents` lists the agents this agent may spawn and `trustedAgents` those that
run without an approval prompt. Both matter for non-interactive dispatch, since a
subagent that cannot prompt fails fast when an approval is required.

### Resource Conventions

- `file://` paths resolve relative to the JSON file's directory (`.kiro/agents/`).
- `skill://` paths resolve from the project root.
- Knowledge bases use object syntax with `type: "knowledgeBase"`.
- Order resources by priority (first = loaded first, last to be evicted on compaction).

## Skill SKILL.md Template

```markdown
---
name: skill-name
description: >
  What the skill enables (1-2 sentences). Include trigger phrases and negative scope.
  Under 1024 characters.
---

# Skill Title

## Workflow

1. **agent-name** — What this agent does in this skill:
   - Sub-steps or details
   - Expected output

2. **agent-name** — Next step:
   - Sub-steps
   - Gate: what must pass before proceeding

## Rules

- Rule 1
- Rule 2

## Success Criteria

- Criterion 1
- Criterion 2
```

### Required Sections

| Section                         | Required | Purpose                           |
| ------------------------------- | :------: | --------------------------------- |
| Frontmatter (name, description) |    ✅    | Triggering and routing            |
| Workflow                        |    ✅    | Step-by-step agent sequence       |
| Rules                           | Optional | Constraints beyond workflow logic |
| Success Criteria                |    ✅    | When the skill is "done"          |

### Frontmatter Description Guidelines

The `description` field is how Kiro matches user intent to skills. It must:

- State what the skill does and when to use it.
- Include 3-5 trigger phrases (natural language the user would say).
- Include negative scope ("Not for X, Y, Z").
- Stay under 1024 characters.

Example:

```yaml
description: >
  Full specification-driven development workflow. Use when implementing features from
  Jira tickets, specs, or feature descriptions. Triggers: 'implement this ticket', 'spec
  to code', 'build this feature'. Not for quick fixes, exploratory coding, or tasks
  without a clear goal.
```

### Skill Authoring Principles

1. **Add what the agent lacks** — don't repeat what's in the agent's prompt.
2. **Provide defaults, not menus** — pick the right approach, don't list options.
3. **Include gotchas** — highest-value content is non-obvious constraints.
4. **Output format > prose** — show the expected output structure.
5. **Procedures > declarations** — "do X then Y" beats "X should be Y".
6. **Validation loops** — include do → validate → fix → repeat cycles.
7. **Progressive disclosure** — inline what every branch needs, move branch-specific
   detail to `references/`. See the authoring rules in `SKILL.md`.

## Instruction File Conventions

Files under `.kiro/steering/` are always-on: Kiro CLI loads every one of them into every
session, subagent sessions included, regardless of an agent's `resources` list. Only
material every agent needs belongs there. Orchestrator-only instruction files live in
`.kiro/orchestration/` and reach the session solely through the orchestrator's
`resources`, so a specialist never pays for them.

| File                                    | Purpose                                  | Who loads it             |
| --------------------------------------- | ---------------------------------------- | ------------------------ |
| `steering/COMMON.md`                    | Behavioral rules for all agents          | All agents               |
| `steering/code-standards-summary.md`    | Compact coding essentials                | All agents (lightweight) |
| `steering/python-environment.md`        | uv and env rules                         | All agents               |
| `orchestration/routing.md`              | Routing rules and collaboration patterns | Orchestrator             |
| `orchestration/delegation-lifecycle.md` | Delegation, planning and harness gates   | Orchestrator             |

Adding a file to `.kiro/steering/` taxes every turn of every agent, so the bar is that
all thirteen agents act on it. Anything narrower goes to `.kiro/orchestration/` with an
explicit `resources` entry, or into a skill loaded on demand.

Full coding conventions and JIRA interaction rules are deliberately NOT steering files.
They live in the `code-standards` and `jira-fetcher` skills and load on demand via
`skill://`, because always-on duplication of detail that most invocations never need is
paid for on every turn.

### When to create a new steering file vs. a skill

- **Steering**: Rules that apply always-on to multiple agents (conventions, safety,
  environment).
- **Skill**: Workflow triggered on-demand for specific task types.

## Integration Checklist

After creating an agent or skill:

- [ ] Agent added to `orchestrator.json` → `availableAgents`
- [ ] Agent added to `routing.md` → Quick Lookup table (with Fallback)
- [ ] Agent added to `routing.md` → Routing Rules (`trigger_when` / `never_when`)
- [ ] Agent added to `routing.md` → Capabilities Matrix
- [ ] Agent added to `routing.md` → Routing shortcut line + Fallback chain
- [ ] Skill added to `routing.md` → Collaboration Patterns table (if multi-agent)
- [ ] Run `make drift-check` to validate references

## Skill Authoring Rules — detail

Rationale behind the four rules stated in `SKILL.md`. Adapted from
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT). Reach for this while
drafting in Phase 2 when a rule's application to a specific draft is unclear.

- **Pointer rule** — a pointer states what the material is and names the branches that
  should reach it. Front-load the leading word and give one trigger per branch, so that
  a reader on a branch recognises its own case in the first few words.
- **No-op hunt** — read the draft sentence by sentence and delete every instruction the
  model already follows by default. A sentence that changes no behaviour still costs
  context on each load. When a sentence fails the test, delete the whole sentence rather
  than shortening it.
- **Positive instruction** — state the target behaviour. Naming the unwanted behaviour
  puts it into context and makes it more available, so "return early to keep the happy
  path unindented" outperforms the prohibition it replaces. This governs skill
  **bodies**. Skill **descriptions** keep their explicit `Not for ...` boundaries:
  routing here costs a whole delegation round when a skill mis-fires, so the precision a
  stated negative scope buys outweighs the cost of naming the excluded case.
- **Progressive-disclosure test** — inline what every branch needs; move behind a
  pointer what only some branches reach. Line count is a symptom rather than the
  criterion: a long body every branch reads in full is correct, while a short body whose
  bulk serves one rare branch belongs in `references/`.
