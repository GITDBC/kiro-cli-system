> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Agent config changes

> New optional fields and Markdown format for agent profiles in CLI V3

CLI V3 loads JSON and Markdown agent profiles that use the current schema. CLI 2.x profiles that still use `allowedTools` or `toolsSettings` without a `permissions` block are skipped until `/upgrade-agent` converts them; other supported fields carry over unchanged.

## Old format

`.kiro/agents/my-agent.json`:

```json
{
  "name": "my-agent",
  "description": "A development agent",
  "prompt": "file://resources/MY_PROMPT.md",
  "model": "claude-sonnet-4.6",
  "tools": ["fs_read", "fs_write", "execute_bash", "grep", "glob", "code"],
  "toolsSettings": {
    "execute_bash": {
      "allowedCommands": ["^git status$", "^cargo build[^&;]*$"],
      "deniedCommands": ["^rm -rf"],
      "denyByDefault": false
    },
    "fs_read": {
      "allowedPaths": ["src/**", "docs/**"],
      "deniedPaths": [".env", "secrets/**"]
    },
    "fs_write": {
      "allowedPaths": ["src/**"],
      "deniedPaths": ["*.lock"]
    }
  },
  "resources": ["file://AGENTS.md"],
  "hooks": {
    "agentSpawn": [{ "command": "git status", "description": "Add git context" }]
  },
  "welcomeMessage": "Hello! How can I help?"
}
```

## New Markdown format

`.kiro/agents/backend-dev.md`:

```markdown
---
name: backend-dev
description: Backend development agent
model: claude-sonnet-4.6
tools: ["read", "write", "shell", "web"]
excludedTools: ["knowledge"]
includeMcpJson: true
includePowers: false
mcpServers:
  postgres:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-postgres"]
    env:
      DATABASE_URL: "${DATABASE_URL}"
resources:
  - file://./ARCHITECTURE.md
  - skill://backend-patterns
permissions:
  rules:
    - capability: shell
      match: ["npm *", "node *"]
      effect: allow
welcomeMessage: "Ready to work on backend code."
---

You are a backend developer focused on Node.js and TypeScript.
Always use async/await. All database queries must be parameterized.
```

CLI V3 supports both formats once a profile uses the current fields. Use Markdown when your system prompt is long or benefits from human readability; JSON works well for programmatically generated configs. The same fields are available in both formats.

## Tags vs Capabilities

V3 separates tool *visibility* from tool *authorization* into two distinct systems.

**Selectors** (in the `tools` field) control which tools the agent can see and invoke. Category tags include `read`, `write`, `shell`, `web`, and `subagent`; `knowledge` is a direct tool ID. Selectors such as `@mcp`, `@builtin`, and `*` include broader sets.

**Capabilities** (in the `permissions` field) control what those tools can do at invocation time — auto-approved, blocked, or requiring confirmation. They use capability names (`fs_read`, `fs_write`, `shell`, etc.) which don't map 1:1 to tags.

See [Built-in tools](https://kiro.dev/docs/tools.md#configuring-tool-access) for the authoritative category membership and selector behavior.

> **Example:** `tools: ["web"]` gives the agent `web_fetch` and the web-search tool (`remote_web_search`, displayed as `web_search`). In permissions, these use separate `web_fetch` and `web_search` capabilities.

## New fields reference

| Field | Type | Description |
|-------|------|-------------|
| `excludedTools` | string[] | Tools to exclude even if `tools` allows them |
| `includeMcpJson` | boolean | Include workspace `.kiro/settings/mcp.json` servers |
| `includePowers` | boolean | Include IDE-installed powers |
| `resources` | string[] | URIs to load into context: `file://./path`, `skill://name` |
| `permissions` | object | Inline policy rules (agent scope, supports all effects) |
| `welcomeMessage` | string | Custom greeting on session start |
| `hooks` | array | Profile-scoped Hook definitions using the current PascalCase trigger schema |

> **Note:** Once the model list is available, Kiro checks whether an agent's `model:` value is available when a V3 terminal UI session starts. If that model is unavailable, Kiro keeps it selected and reports that requests will fail. Choose an available model with `/model`, or update the agent configuration. An explicit `--model` overrides the agent value. Without an explicit `--model`, Kiro uses `chat.defaultModel` only when the agent configuration has no model.

> **Note:** `toolsSettings` is removed in V3 — migrate per-tool rules to the unified `permissions` block. See [Permissions migration →](https://kiro.dev/docs/cli/v3/permissions.md).

## MCP server config

Supports stdio and HTTP transports. Both transports accept a `timeout` field in milliseconds. HTTP servers also accept `headers`. Both expand environment variables at runtime using `$` syntax.

Agent config migration is complete. If your agents used embedded hooks, continue to [hooks migration →](https://kiro.dev/docs/cli/v3/hooks-migration.md).
