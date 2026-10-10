> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# CLI 2.x reference

> Reference documentation for Kiro CLI 2.x hooks, agent config, and formats that changed in 3.0

This page documents CLI 2.x behavior for users who haven't yet migrated to 3.0. For the current format, see the [Features](https://kiro.dev/docs/hooks.md) documentation.

## Hooks

In CLI 2.x, hooks were embedded directly in the agent configuration file rather than in standalone files.

### Format

```json
{
  "hooks": {
    "agentSpawn": [{"command": "echo 'starting'", "matcher": ".*"}],
    "preToolUse": [{"command": "npm run lint", "matcher": "Write|Edit"}],
    "fileEdited": [{"command": "prettier --write", "matcher": "\\.ts$"}]
  }
}
```

Each trigger name maps to an array of hook definitions. Each definition has:

| Field | Description |
|-------|-------------|
| `command` | Shell command to execute |
| `matcher` | Regex pattern for filtering (what it matches depends on the trigger) |

### Available triggers

| Trigger | Fires when | `matcher` matches |
|---------|-----------|-------------------|
| `agentSpawn` | Agent is activated | Not evaluated |
| `userPromptSubmit` | User submits a prompt | Not evaluated |
| `preToolUse` | Before a tool executes | Tool name |
| `postToolUse` | After a tool executes | Tool name |
| `fileEdited` | After a file is written | File path |
| `fileCreated` | After a new file is created | File path |
| `agentStop` / `stop` | Session ends | Not evaluated |

### Hook communication

Hooks receive context as JSON via STDIN and communicate results through exit codes:

- **Exit code 0**: Hook succeeded. STDOUT is captured.
- **Exit code 2**: (preToolUse only) Block tool execution. STDERR is returned to the agent.
- **Other exit codes**: Hook failed. STDERR is shown as a warning.

### What changed in 3.0

- Hooks moved from embedded agent config to standalone `.kiro/hooks/*.json` files
- Trigger names changed to PascalCase (e.g., `agentSpawn` → `SessionStart`)
- New `version: "v1"` schema with `name`, `description`, `enabled`, and `timeout` fields
- New triggers added: `PreTaskExec`, `PostTaskExec`, `PostFileDelete`, `Manual`
- `}` template variable available for file-related triggers
- `stop` hook gained Block Decision support (return `` to continue the session)

For the full migration guide, see [Hooks migration](https://kiro.dev/docs/cli/v3/hooks-migration.md).

## Permissions and tool trust

In CLI 2.x, tool permissions were managed through CLI flags, slash commands, and per-tool settings in agent config. In 3.0, this is replaced by structured `permissions.yaml` files.

### CLI flags

```bash
kiro-cli --trust-all-tools
kiro-cli --trust-tools shell,write
```

### Slash commands

| Command | Description |
|---------|-------------|
| `/tools` | Show current permission status for all tools |
| `/tools trust <tool>` | Trust a specific tool for the session |
| `/tools untrust <tool>` | Revert a tool to per-request confirmation |
| `/tools trust-all` | Trust all tools (equivalent to `/acceptall`) |
| `/tools reset` | Reset all runtime permissions to defaults |

### Per-tool settings in agent config (`toolsSettings`)

```json
{
  "toolsSettings": {
    "shell": {
      "allowedCommands": ["git *", "npm *"],
      "deniedCommands": ["rm -rf *", "sudo *"]
    },
    "read": {
      "allowedPaths": ["src/**"],
      "deniedPaths": ["*.env"]
    }
  }
}
```

| Setting | Description |
|---------|-------------|
| `allowedCommands` | Regex patterns for auto-approved shell commands |
| `deniedCommands` | Regex patterns for blocked shell commands |
| `allowedPaths` | Regex patterns for auto-approved file paths |
| `deniedPaths` | Regex patterns for blocked file paths |
| `autoAllowReadonly` | Auto-approve read-only shell commands (e.g., `git status`) |
| `denyByDefault` | Block all tools unless explicitly allowed |

### Shell command trust levels (interactive)

When the agent requested a shell command, a tiered picker appeared:

```text
Press (↑↓) to navigate (⏎) to select scope
> Full command          → git pull --rebase
  Partial command       → git pull *
  Base command          → git *
  Entire Tool           → *
```

Trusted patterns persisted for the session and were stored as regex in `allowedCommands`.

### Read and write path trust levels (interactive)

When the agent needed to access a file outside the working directory:

```text
Press (↑↓) to navigate (⏎) to select scope
> Specific paths       → ~/.config/app/settings.json
  Complete directory   → ~/.config/app
  Entire Tool          → *
```

### What changed in 3.0

- `toolsSettings` replaced by `permissions.yaml` with `capability`/`match`/`effect` rules
- `--trust-all-tools` still works as a session-scope override but `permissions.yaml` is preferred
- Regex patterns replaced by glob patterns (`.*` → `*`, `\.ts$` → `*.ts`)
- Separate per-tool deny was independent; now deny-always-wins across all scopes
- `autoAllowReadonly` removed — explicitly list allowed commands
- `denyByDefault` removed — use `exclude` patterns instead
- Interactive trust levels and `/tools` commands still available for session-level management

For the full migration guide, see [Permissions migration](https://kiro.dev/docs/cli/v3/permissions.md).

## Compaction

In CLI 2.x, compaction behavior was the same as 3.0:

- `/compact` for manual trigger
- Automatic trigger when context window overflows
- Creates a new session with compacted context; resume original via `/chat resume`
- Configurable via `compaction.excludeMessages` and `compaction.excludeContextWindowPercent`

No changes in 3.0 for this feature.

## Custom agent config

In CLI 2.x, agent configs were JSON-only with embedded `toolsSettings` and `hooks`.

### Format

`.kiro/agents/my-agent.json`:

```json
{
  "name": "my-agent",
  "description": "A development agent",
  "prompt": "file://resources/MY_PROMPT.md",
  "model": "claude-sonnet-4",
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

### What changed in 3.0

- **Markdown format** added (`.md` files with YAML frontmatter + body as system prompt)
- **`toolsSettings` removed** — replaced by `permissions` field with capability-based rules
- **`hooks` moved** to standalone `.kiro/hooks/*.json` files
- **New fields**: `excludedTools`, `includeMcpJson`, `includePowers`, `permissions`, `welcomeMessage`
- **Tags system** — tool names simplified to short categories (`read`, `write`, `shell`, `web`, `@mcp`, `@builtin`, `*`)
- **`resources` field** now supports `skill://` URIs in addition to `file://`

For the current format reference, see [Custom agents](https://kiro.dev/docs/custom-agents.md).
