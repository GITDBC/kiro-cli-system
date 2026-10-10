> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Migration guide

> Step-by-step guide to migrate from Kiro CLI 2.x to 3.0

Follow these steps in order to upgrade from CLI 2.x to 3.0.

## 1. Export sessions before upgrading

Session data format has changed and existing sessions are **not** automatically migrated. Back up your session data before upgrading:

```bash
# Back up your session directory
cp -r ~/.kiro/sessions ~/.kiro/sessions-v2-backup
```

After upgrading, session import capabilities will be available to restore key sessions. Complex sessions with extensive tool result history may lose some historical tool outputs — the conversation flow and decisions are preserved.

## 2. Migrate hooks to .kiro/hooks/*.json

Hooks have moved from embedded agent config to standalone files.

**Old format — do not use in 3.0** (shown for migration reference only):

```json
{
  "hooks": {
    "agentSpawn": [{"command": "echo 'starting'", "matcher": ".*"}],
    "preToolUse": [{"command": "npm run lint", "matcher": "Write|Edit"}],
    "fileEdited": [{"command": "prettier --write", "matcher": "\\.ts$"}]
  }
}
```

**New format** (`.kiro/hooks/my-hooks.json`):

```json
{
  "version": "v1",
  "hooks": [
    {
      "name": "lint-on-save",
      "trigger": "PostFileSave",
      "matcher": "\\.ts$",
      "action": { "type": "command", "command": "npm run lint" },
      "timeout": 30,
      "enabled": true
    },
    {
      "name": "format-on-save",
      "trigger": "PostFileSave",
      "matcher": "\\.ts$",
      "action": { "type": "command", "command": "prettier --write {{filePath}}" },
      "timeout": 10,
      "enabled": true
    }
  ]
}
```

**Trigger name mapping:**

| Old Trigger | New Trigger | Notes |
|-------------|-------------|-------|
| `agentSpawn` | `SessionStart` | Fires when a new session begins |
| `userPromptSubmit` | `UserPromptSubmit` | Fires before the agent processes a prompt |
| `preToolUse` | `PreToolUse` | Fires before a tool executes |
| `postToolUse` | `PostToolUse` | Fires after a tool completes |
| `fileEdited` | `PostFileSave` | Fires after a file is written |
| `fileCreated` | `PostFileCreate` | Fires after a new file is created (IDE legacy alias, now unified) |
| `agentStop` / `stop` | `Stop` | Fires when the session ends — `agentStop` is IDE legacy; CLI used `stop` |

**New triggers in 3.0:**

| Trigger | Description |
|---------|-------------|
| `PreTaskExec` | Before a task/plan step executes |
| `PostTaskExec` | After a task/plan step completes |
| `PostFileDelete` | After a file is deleted |
| `Manual` | Triggered only by explicit user invocation |

## 3. Migrate trust config to permissions.yaml

Before migrating manually, run `kiro-cli agent migrate` — it auto-converts compatible rules and reports what needs manual attention. Review the output, then apply the remaining changes below.

For CI pipelines, `--trust-all-tools` still works as a session-scope override. Alternatively, create `~/.kiro/settings/permissions.yaml` with `capability: all, effect: allow` in your CI environment.

**Old approach:**

```bash
kiro-cli --trust-all-tools
kiro-cli --trust-tools shell,write

/tools trust write
/tools trust-all
```

**New approach** (`~/.kiro/settings/permissions.yaml` for user scope):

```yaml
rules:
  - capability: shell
    match: ["git *", "npm *", "npx *"]
    effect: allow

  - capability: fs_write
    match: ["src/**", "tests/**"]
    effect: allow

  - capability: fs_read
    effect: allow

  - capability: mcp
    match: ["my-server/*"]
    effect: allow
```

For the full reference — behavioral changes, scope definitions, and pattern conversion table — see [Permissions migration →](https://kiro.dev/docs/cli/v3/permissions.md).

## 4. Update agent configs

Agent profiles are backward-compatible — existing configs continue to work. The unified agent harness adds new optional fields and a Markdown format option.

**Old format** (`.kiro/agents/my-agent.json`):

```json
{
  "name": "backend-dev",
  "description": "Backend development agent",
  "prompt": "You are a backend developer.",
  "model": "claude-sonnet-4",
  "tools": ["fs_read", "fs_write", "execute_bash", "grep", "glob"],
  "toolsSettings": {
    "execute_bash": {
      "allowedCommands": ["^git status$", "^npm test"],
      "deniedCommands": ["^rm -rf"],
      "denyByDefault": false
    },
    "fs_read": { "allowedPaths": ["src/**"], "deniedPaths": [".env"] },
    "fs_write": { "allowedPaths": ["src/**"] }
  }
}
```

**New format** (`.kiro/agents/backend-dev.json`):

```json
{
  "name": "backend-dev",
  "description": "Backend development agent",
  "prompt": "file://resources/PROMPT.md",
  "model": "claude-sonnet-4",
  "tools": ["read", "write", "shell"],
  "permissions": {
    "rules": [
      { "capability": "shell", "match": ["git status", "git diff", "npm test*"], "effect": "allow" },
      { "capability": "shell", "match": ["rm -rf*"], "effect": "deny" },
      { "capability": "fs_read", "match": [".env", "secrets/**"], "effect": "deny" },
      { "capability": "fs_write", "match": ["*.lock"], "effect": "deny" }
    ]
  }
}
```

The `tools` field now uses **tags** (category names like `read`, `write`, `shell`) instead of individual tool IDs. The `toolsSettings` block is replaced by the `permissions.rules` array.

**Migrating `toolsSettings` to `permissions`:**

| V2 `toolsSettings` | V3 `permissions` rule |
|--------------------|----------------------|
| `execute_bash.allowedCommands: ["^git status$"]` | `` |
| `execute_bash.deniedCommands: ["^rm -rf"]` | `` |
| `execute_bash.denyByDefault: true` | `` |
| `fs_read.allowedPaths: ["src/**"]` | `` |
| `fs_read.deniedPaths: [".env"]` | `` |
| `fs_write.allowedPaths: ["src/**"]` | `` |

> **Note:** V2 `allowedCommands`/`deniedCommands` used regex patterns. V3 uses glob — simple patterns translate directly (remove anchors `^`/`$`, replace `.*` with `*`). Complex regex must be rewritten as multiple glob rules.

**New format — Markdown** (`.kiro/agents/backend-dev.md`):

```markdown
---
name: backend-dev
description: Backend development agent
model: claude-sonnet-4-20250514
tools: ["read", "write", "shell", "grep"]
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

**New fields reference:**

| Field | Type | Description |
|-------|------|-------------|
| `excludedTools` | string[] | Tools to exclude even if `tools` allows them |
| `includeMcpJson` | boolean | Include workspace `.kiro/settings/mcp.json` servers |
| `includePowers` | boolean | Include IDE-installed powers |
| `resources` | string[] | URIs to load into context: `file://./path`, `skill://name` |
| `permissions` | object | Inline policy rules (agent scope, supports all effects) |
| `welcomeMessage` | string | Custom greeting on session start |

**MCP servers in agent profiles** — supports stdio and HTTP:

```json
{
  "mcpServers": {
    "local": { "command": "npx", "args": ["-y", "@org/server"], "env": {} },
    "remote": { "url": "https://api.example.com/mcp", "headers": { "Authorization": "Bearer ${TOKEN}" } }
  }
}
```

Environment variables use `$` syntax and are expanded at runtime.

## 5. Replace aws_tool with MCP server

The built-in `aws_tool` has been removed. Configure an AWS MCP server instead. Check the [MCP server registry](https://kiro.dev/docs/mcp/servers.md) for available AWS servers, or use a community server:

**`.kiro/settings/mcp.json`:**

```json
{
  "mcpServers": {
    "aws": {
      "command": "npx",
      "args": ["-y", "@aws/aws-mcp-server"],
      "env": { "AWS_PROFILE": "${AWS_PROFILE}", "AWS_REGION": "${AWS_REGION}" }
    }
  }
}
```

> For example, `@aws/aws-mcp-server` is the official package. See the [MCP registry →](https://kiro.dev/docs/mcp/servers.md) for other options.

## 6. Update scripts referencing old tool IDs

If you have hooks, permissions, or scripts that reference tool IDs, update them:

| Old Tool ID (2.x) | New Tool ID | Capability |
|-------------------|-------------|------------|
| `readFile` | `read` | `fs_read` |
| `writeFile` / `fsWrite` | `write` | `fs_write` |
| `listDirectory` | `glob` | `fs_read` |
| `grepSearch` | `grep` / `grep_search` | `fs_read` |
| `fileSearch` | `file_search` | `fs_read` |
| `webFetch` | `web_fetch` | `web_fetch` |
| `webSearch` | `web_search` | `web_search` |

Both old camelCase IDs and new IDs are accepted in agent profiles and permissions. Use the new IDs going forward.

## Next steps

- [Permissions migration](https://kiro.dev/docs/cli/v3/permissions.md) — detailed guidance on migrating trust flags to `permissions.yaml`
- [Hooks migration](https://kiro.dev/docs/cli/v3/hooks-migration.md) — full trigger mapping and new format reference

## 7. Validate your migration

```bash
kiro-cli diagnostic
```

This checks for: invalid hook schemas, agent configs referencing removed tools (including `aws_tool`), and permissions file syntax errors. Fix any reported warnings before deploying to CI.
