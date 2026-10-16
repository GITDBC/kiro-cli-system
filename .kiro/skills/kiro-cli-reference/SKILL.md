---
name: kiro-cli-reference
description: >
  Kiro CLI official documentation reference. Use when answering questions about Kiro CLI
  features, configuration, commands, agents, skills, steering, specs, MCP, hooks,
  permissions, or any Kiro CLI capability. Triggers: 'kiro', 'kiro-cli', 'agent config',
  'steering files', 'skills spec', 'slash commands', 'MCP servers', 'knowledge base',
  'subagents', 'headless mode'. Not for general coding tasks unrelated to Kiro CLI
  itself.
---

# Kiro CLI Reference

Official Kiro CLI documentation, mirrored verbatim from <https://kiro.dev/docs/> under
`references/`. Each directory holds one topic; a file named after a directory (for
example `hooks.md` beside `hooks/`) is that topic's overview. Grep the relevant
directory for the exact term rather than reading pages end to end. Mirror scope, sync
commands and editing rules: [PROVENANCE.md](PROVENANCE.md).

## Topic Index

| Topic                       | Location                                            | Read when                                                                                     |
| --------------------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Setup and first steps       | `setup.md`, `getting-started/`                      | Orienting in the CLI or walking through steering, specs, hooks and MCP on a sample project    |
| Architecture and config     | `how-kiro-works.md`, `configuration.md`             | Resolving which global, project or agent scope a setting comes from                           |
| Steering                    | `steering.md`                                       | Writing steering files, inclusion modes, always-on versus on-demand context                   |
| Skills                      | `skills.md`                                         | Authoring or loading `SKILL.md` packages and their resources                                  |
| Permissions                 | `permissions.md`, `v3/permissions.md`               | Capability-based permissions, trust rules, and migrating 2.x trust flags                      |
| Custom agents and subagents | `custom-agents.md`, `custom-agents/`                | Agent JSON fields (`configuration-reference.md`), built-in agents, `subagents.md` delegation  |
| Hooks                       | `hooks.md`, `hooks/`                                | Trigger types, actions, examples, debugging hook failures                                     |
| MCP                         | `mcp.md`, `mcp/`                                    | Server configuration, tool search, MCP security, usage of tools, prompts and resources        |
| Chat                        | `chat.md`, `chat/`                                  | Context management, `@path` references, sessions, prompts, `/goal`, queued steering, settings |
| Built-in tools              | `tools.md`, `tools/`, `reference/built-in-tools.md` | What each agent tool does, code intelligence, web search and fetch                            |
| CLI reference               | `reference/`                                        | Commands and flags, slash commands, settings keys, exit codes for scripting                   |
| Headless and CI             | `headless.md`, `reference/exit-codes.md`            | Running the CLI non-interactively in pipelines and scripts                                    |
| Models and effort           | `models.md`, `models/`                              | Model selection, availability and lifecycle, the effort setting                               |
| Context handling            | `compaction.md`, `checkpoints.md`, `kiroignore.md`  | Automatic summarisation, undo and conversation forks, excluding files from search             |
| Specs                       | `specs.md`, `specs/`                                | Feature and bugfix specs, requirements-first versus design-first, quick specs, correctness    |
| CLI 3.0                     | `v3.md`, `v3/`                                      | 3.0 changes: Markdown agent profiles (`agent-config.md`), new features, tangent conversations |
| Experimental                | `experimental.md`, `experimental/`                  | Knowledge bases, delegate, tangent mode, thinking, TODO lists                                 |
| Privacy and security        | `privacy-and-security.md`, `privacy-and-security/`  | Data protection, firewall and VPC endpoint requirements, compliance, IAM permissions          |

## Reading Guidance

- Prefer the 3.0 pages. Where a top-level page and a `v3/` page disagree, the `v3/` page
  describes the current harness; the mirror no longer carries the 2.x reference or the
  2.x-to-3.0 migration guides.
- Some pages cover several Kiro surfaces (IDE, CLI, Web). Answer from the CLI-specific
  passages and say so when a feature is documented for another surface only.
- Cite the page path when quoting configuration fields, so the claim can be checked
  against the mirror.
