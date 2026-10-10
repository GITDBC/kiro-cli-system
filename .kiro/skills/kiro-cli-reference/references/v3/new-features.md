> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# New features in 3.0

> New capabilities in Kiro CLI 3.0 — plan mode, permissions, hooks, built-in tools, and more

These features are available in 3.0 without migration — none require changes to existing configs. Adopt them incrementally.

### Try these first

## Plan mode

Press **Shift+Tab** to toggle Plan mode. The Plan agent analyzes your request, creates a step-by-step plan, and executes it with checkpoints between steps.

## Trusted workspaces

On first open, CLI prompts you to trust the workspace. In untrusted workspaces, the agent restricts capabilities (no shell, limited writes) until you explicitly trust it.

## Manual compaction

Use `/compact` to manually trigger context compaction when your session gets long. The engine generates a structured summary (preserving task status, file paths, key decisions, and next steps) and persists it as a checkpoint marker. On session reload, only the summary loads rather than replaying full history.

### Available when you need it

## Powers auto-pickup

Powers installed via the IDE are automatically detected by CLI sessions. Install a power once in the IDE, and it's available everywhere.

## Skills system

Create reusable agent capabilities in `.kiro/skills/<name>/SKILL.md`. Skills are automatically discovered and available to all agents in the workspace.

## Steering front matter

Steering documents now support front matter with inclusion modes:

```markdown
---
inclusion: fileMatch
fileMatchPattern: "**/*.tsx"
---

# React Guidelines
...
```

Modes: `always`, `fileMatch`, `manual`, `auto`. (The `auto` mode is determined by the engine based on context — not directly configurable in file front matter.)

## Session export/import

Save and restore sessions for portability across machines or for sharing context. Session data is stored in `~/.kiro/sessions/`.

## Sub-agents

Sub-agents run complex tasks in parallel with isolated contexts. You interact with the primary agent; sub-agents execute behind the scenes. In the IDE, a visual tree shows progress across all branches.

### Default agent permissions

Out of the box, without any `permissions.yaml`, the agent has these defaults:

- **Allowed:** Read any file in the workspace (`fs_read ./**`), common git read-only commands (`git status`, `git log`, `git diff`, etc.), system info commands (`pwd`, `whoami`, `uname`)
- **Denied:** Writes to `~/.kiro/settings/` or `.kiro/settings/` (prevents the agent from modifying its own trust boundaries)
- **Everything else:** Prompts for approval (`ask`)

Add a `permissions.yaml` to pre-approve or block specific operations.

## Expanded agent profiles

Markdown format with embedded MCP servers, permissions, resources, and a full system prompt as the document body.

## Built-in tools

CLI 3.0 includes these built-in tools (use short aliases in agent profiles and permissions):

| Tool | Description |
|------|-------------|
| `read` / `read_file` | Read file contents |
| `write` / `fs_write` | Create or edit files |
| `glob` / `list_directory` | Find files by pattern |
| `grep` / `grep_search` | Search file contents |
| `shell` | Execute terminal commands |
| `web_fetch` | Fetch URL content |
| `web_search` | Web search |
| `code` | Code Intelligence — LSP-powered go-to-definition, find references, symbol search |
| `knowledge` | Semantic indexing and search across sessions |
| `todo` | In-session task tracking (gated — IDE visualization coming) |

> **Note:** Checkpoints are not available in CLI 3.0. They remain an IDE-only feature. Use session export for state preservation.

## Known gaps in 3.0

| Gap | Detail |
|-----|--------|
| **AL2 not supported** | Kiro CLI 3.0 does not run on Amazon Linux 2. Use CLI 2.x if your environment requires AL2. |
| **Classic mode not supported** | The legacy non-TUI mode (`kiro-cli chat` without the TUI) does not support the v3 engine. Use the TUI. |
| **Session resume** | V3 sessions cannot be resumed in V2. If you switch back to the V2 engine, previously created V3 sessions will not be available. |
