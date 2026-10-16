> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# New features in V3

> New capabilities in Kiro CLI V3 — plan mode, permissions, hooks, built-in tools, and more

V3 combines new capabilities with changes to agent profiles, permissions, and Hooks. You can use most additions immediately; migrate older custom configuration where the sections below link to a migration guide.

## Try these first

### Plan mode

Press **Shift+Tab** to toggle Plan mode. The Plan agent explores your codebase and creates a step-by-step implementation plan without making changes. After you approve the plan, Kiro hands it to the default agent for execution.

### Interactive Specs

Run `/spec new` to describe what you want to build before Kiro drafts the requirements. At each phase checkpoint, press `Ctrl+X` to read the document and stage line comments. When implementation starts, the full-screen task view lets you choose the task scope and follow progress. See [Specs](https://kiro.dev/docs/specs.md) for the complete workflow.

### Session dashboard

Run `/sessions`, or launch with `kiro-cli chat --sessions`, to browse, search, filter, resume, and clean up local and cloud sessions across workspaces. Content search can include both your prompts and agent responses. See [Session management](https://kiro.dev/docs/cli/chat/session-management.md).

### Cloud sessions

Run `kiro-cli --cloud` to work in a managed sandbox that keeps running after you disconnect. Attach a repository at launch or later with `/repo`, then resume the session from another machine or Kiro surface. See [Cloud sessions](https://kiro.dev/docs/cloud-sessions.md).
### Trusted workspaces

On first open, CLI prompts you to trust the workspace. Until you trust it, the agent does not load the workspace's custom agents, Steering files, MCP servers, Skills, or Workflow files; it asks before every shell command and every MCP tool call, even when a rule allows them; and it asks before writing to Kiro configuration directories. See [Workspace trust](https://kiro.dev/docs/permissions.md#workspace-trust) for the full list.

### Manual compaction

Use `/compact` to manually trigger context compaction when your session gets long. The harness generates a structured summary (preserving task status, file paths, key decisions, and next steps) and persists it as a checkpoint marker. On session reload, only the summary loads rather than replaying full history.

## Available when you need it

### Introspect subagent

Ask Kiro about its features to get documentation-grounded guidance inline. The introspect subagent can explain capabilities, help with custom agents, Hooks, and Steering, and suggest configuration for your workflow.

### Configuration panel and sync

Run `/config` to inspect agents, MCP servers, Powers, Steering, Skills, and Hooks in one place, with their local or cloud source when known. [Configuration Sync](https://kiro.dev/docs/web/cloud-configuration.md) can also make uploaded personal configuration available to new local CLI sessions without writing it into the local `.kiro` directory. See [CLI configuration](https://kiro.dev/docs/configuration.md) for scope and precedence details.

### Global Hooks

Place a Hook in `~/.kiro/hooks/` to run it in every workspace alongside project Hooks under `.kiro/hooks/`. Hooks also support dynamic confirmation through `confirmCommand`. See [Hooks](https://kiro.dev/docs/hooks.md).

### Model and reasoning controls

Open `/model` to select a model for the current session and configure the Thinking and Effort controls that model supports. Kiro saves Thinking and Effort defaults for future sessions. To save the active model as your default, run `/model set-current-as-default`. See [Models](https://kiro.dev/docs/models.md) and [Reasoning effort](https://kiro.dev/docs/models/effort.md).

### Voice and fullscreen

Use `/voice` for locally transcribed speech input. Use `/fullscreen` to move an interactive session into a dedicated terminal screen with its own scrolling, then run it again to return inline. See [Voice mode](https://kiro.dev/docs/cli/voice.md) and [Fullscreen mode](https://kiro.dev/docs/cli/fullscreen.md).

### MCP and headless automation

MCP configuration hot-reloads while a session is running, and the CLI provides explicit authentication controls plus pre-registered OAuth client support. V3 also connects to servers using the current MCP protocol revision. For automation, `--output-format stream-json` emits JSON Lines events and `--require-mcp-startup` stops a run when required servers fail to start. See [MCP configuration](https://kiro.dev/docs/mcp/configuration.md) and [Headless mode](https://kiro.dev/docs/cli/headless.md).
### Powers auto-pickup

Powers installed via the IDE are automatically detected by CLI sessions. Install a power once in the IDE, and it's available everywhere.

### Skills system

Create reusable agent capabilities in `.kiro/skills/<name>/SKILL.md`. Skills are automatically discovered and available to all agents in the workspace.

### Steering front matter

Steering documents now support front matter with inclusion modes:

```markdown
---
inclusion: fileMatch
fileMatchPattern: "**/*.tsx"
---

# React Guidelines
...
```

Modes: `always`, `fileMatch`, `manual`, `auto`. (The `auto` mode is determined by the harness based on context — not directly configurable in file front matter.)

### Session export/import

Use `/chat save <path>` to export a local conversation and `/chat load <path>` to restore an exported file. For normal resumption, use the session dashboard; cloud sessions remain in your account-backed session store. See [Session management](https://kiro.dev/docs/cli/chat/session-management.md).

### Sub-agents

Sub-agents run complex tasks in parallel with isolated contexts. Their cards show a one-line prompt preview; press `Ctrl+O` to expand the full prompt and `Ctrl+G` to monitor every running sub-agent without interrupting the main chat.

## Default agent permissions

CLI V3 uses Kiro's shared built-in permission defaults, then layers user, workspace, agent, and session rules on top. See [Default behavior](https://kiro.dev/docs/permissions.md#default-behavior) for the authoritative defaults and [Permissions migration](https://kiro.dev/docs/cli/v3/permissions.md) for CLI 2.x conversion. To approve all tool calls only for the rest of the current session, run `/tools trust-all`.

### Expanded agent profiles

Markdown format with embedded MCP servers, permissions, resources, and a full system prompt as the document body. See [Agent config changes](https://kiro.dev/docs/cli/v3/agent-config.md) for migration guidance and current fields.

### Built-in tools

CLI V3 includes file, shell, web, Code Intelligence, documentation-help, and knowledge tools. Use [Built-in tools](https://kiro.dev/docs/tools.md) for the authoritative catalog, surface availability, category membership, and permission guidance.

> **Note:** The experimental `/checkpoint` feature remains classic-only and is not available on the V3 harness. Use `/rewind` to branch from an earlier turn and version control to restore files.

## Remaining differences

See [Feature parity today and remaining differences from V2](https://kiro.dev/docs/cli/v3.md#feature-parity-today) for the current support matrix and the legacy workflows that still require V2.
