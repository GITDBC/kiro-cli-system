> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Settings

> Configure Kiro CLI behavior through settings

Kiro CLI provides extensive customization through settings. You can configure everything from telemetry to chat behavior, key bindings, and feature toggles.

## Accessing settings

Manage settings directly from the command line:

```bash
# List all configured settings
kiro-cli settings list

# List all available settings with descriptions
kiro-cli settings list --all

# View a specific setting
kiro-cli settings telemetry.enabled

# Set a setting
kiro-cli settings telemetry.enabled true

# Delete a setting
kiro-cli settings --delete chat.defaultModel

# Open settings file in editor
kiro-cli settings open
```

### Output formats

```bash
# Plain text (default)
kiro-cli settings list

# JSON
kiro-cli settings list --format json

# Formatted JSON
kiro-cli settings list --format json-pretty
```

## Settings reference

### Telemetry and privacy

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `telemetry.enabled` | boolean | Enable/disable telemetry collection | `kiro-cli settings telemetry.enabled true` |
| `telemetryClientId` | string | Client identifier for telemetry | `kiro-cli settings telemetryClientId "client-123"` |

### Chat interface

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `chat.defaultModel` | string | Default AI model for conversations | `kiro-cli settings chat.defaultModel "claude-3-sonnet"` |
| `chat.defaultAgent` | string | Default agent configuration | `kiro-cli settings chat.defaultAgent "my-agent"` |
| `chat.diffTool` | string | External diff tool for viewing code changes (classic only) | `kiro-cli settings chat.diffTool "delta"` |
| `chat.greeting.enabled` | boolean | Show greeting message on chat start | `kiro-cli settings chat.greeting.enabled false` |
| `chat.editMode` | boolean | Enable Vi edit mode (classic only) | `kiro-cli settings chat.editMode true` |
| `chat.enableNotifications` | boolean | Enable desktop notifications | `kiro-cli settings chat.enableNotifications true` |
| `chat.notificationMethod` | string | Notification method: `auto`, `bel`, or `osc9` | `kiro-cli settings chat.notificationMethod "osc9"` |
| `chat.disableMarkdownRendering` | boolean | Disable markdown formatting (classic only) | `kiro-cli settings chat.disableMarkdownRendering false` |
| `chat.disableWrap` | boolean | Emit chat output without hard line breaks for clean copy-paste; terminal soft-wrap still applies. | `kiro-cli settings chat.disableWrap true` |
| `chat.disableAutoCompaction` | boolean | Disable automatic conversation summarization | `kiro-cli settings chat.disableAutoCompaction true` |
| `compaction.excludeMessages` | number | Minimum message pairs to retain during compaction | `kiro-cli settings compaction.excludeMessages 2` |
| `compaction.excludeContextWindowPercent` | number | Minimum % of context window to retain during compaction | `kiro-cli settings compaction.excludeContextWindowPercent 2` |
| `chat.enablePromptHints` | boolean | Show startup hints with tips and shortcuts (v1.26.0+, default: true) | `kiro-cli settings chat.enablePromptHints false` |
| `chat.enableHistoryHints` | boolean | Show conversation history hints (classic only) | `kiro-cli settings chat.enableHistoryHints true` |
| `chat.uiMode` | string | UI variant to use | `kiro-cli settings chat.uiMode "compact"` |
| `chat.historyMode` | string | Prompt history scope: `session` (per-session, default) or `global` (shared across sessions). Set via `/settings history`; applies on next session | `kiro-cli settings chat.historyMode global` |
| `chat.sessionDashboard.indexResponses` | boolean | `/sessions` search scope: `true` for **Prompts and agent responses**, `false` for **Prompts only** (default: `true`). Titles and your prompts are always indexed and tool output never is. Set via `/settings` → **Session search** | `kiro-cli settings chat.sessionDashboard.indexResponses false` |
| `chat.ui` | string | Terminal UI implementation: `tui` (default) or `classic` | `kiro-cli settings chat.ui "classic"` |
| `chat.disableGranularTrust` | boolean | Disable tiered trust options for tool approvals (terminal UI only) | `kiro-cli settings chat.disableGranularTrust true` |
| `chat.autoExpandToolOutput` | boolean | Auto-expand tool output instead of collapsing (terminal UI only) | `kiro-cli settings chat.autoExpandToolOutput true` |
| `chat.modelDefaults` | object | Per-model default settings (e.g., effort level) that apply across new sessions | See [Effort](https://kiro.dev/docs/models/effort.md) |
| `chat.enableContextUsageIndicator` | boolean | Show context usage percentage in prompt (classic only) | `kiro-cli settings chat.enableContextUsageIndicator true` |

### Display and accessibility (terminal UI)

These settings control how the terminal UI renders output. You can toggle animation, ASCII art, icons, and thinking display from within a session with `/settings display`.

| Setting | Type | Default | Description | Example |
|---------|------|---------|-------------|---------|
| `chat.allowAnimations` | boolean | `true` | Animated spinners and shimmers. When `false`, indicators show static frames | `kiro-cli settings chat.allowAnimations false` |
| `chat.allowAsciiArt` | boolean | `true` | Unicode/braille symbols and box-drawing. When `false`, falls back to plain ASCII | `kiro-cli settings chat.allowAsciiArt false` |
| `chat.allowIcons` | boolean | `true` | Status indicator icons (●, ○, ⚠). When `false`, uses text-only labels | `kiro-cli settings chat.allowIcons false` |
| `chat.showThinking` | boolean | `true` | Show the agent's reasoning (thinking) blocks in chat output (v2.5.0+). Startup-only | `kiro-cli settings chat.showThinking false` |
| `chat.preserveScrollback` | boolean | `true` | Preserve terminal history when the interface redraws. Set to `false` to restore clear-and-repaint behavior | `kiro-cli settings chat.preserveScrollback false` |

**ℹ️ Info:** Setting the `KIRO_ASCII_MODE=1` environment variable forces ASCII mode regardless of `chat.allowAsciiArt`. See [Thinking display](https://kiro.dev/docs/cli/chat/settings.md#thinking-display) for more on `chat.showThinking`. The terminal title feature is toggled from `/settings display` → **Terminal title** (not available as a CLI setting).

### Busy indicators

The terminal UI shows a busy indicator while Kiro works. Set `chat.enableCustomSpinnerVerbs` to `true` to use the verb pool in `chat.spinnerVerbs`.

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `chat.enableCustomSpinnerVerbs` | boolean | `false` | Apply the custom verb pool from `chat.spinnerVerbs` |
| `chat.spinnerVerbs` | object | Not set | A verb pool with `append` or `replace` mode |

Run `kiro-cli settings open`, then merge these properties into the top-level object in `~/.kiro/settings/cli.json`. Do not replace existing settings:

```json
{
  "chat.enableCustomSpinnerVerbs": true,
  "chat.spinnerVerbs": {
    "mode": "append",
    "verbs": [
      "Checking...",
      "Reading documentation <https://docs.example.com>"
    ]
  }
}
```

Use `append` to add your verbs to Kiro's built-in pool. Use `replace` to use only your verbs. An empty `replace` list falls back to the built-in busy indicator. A verb can end with a space and an `http` or `https` URL in angle brackets. Kiro shows the verb text and makes it a terminal hyperlink when the terminal supports hyperlinks.

### Knowledge base

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `chat.enableKnowledge` | boolean | Enable knowledge base functionality | `kiro-cli settings chat.enableKnowledge true` |
| `knowledge.defaultIncludePatterns` | array | Default file patterns to include | `kiro-cli settings knowledge.defaultIncludePatterns '["*.py", "*.js"]'` |
| `knowledge.defaultExcludePatterns` | array | Default file patterns to exclude | `kiro-cli settings knowledge.defaultExcludePatterns '["*.log", "node_modules"]'` |
| `knowledge.maxFiles` | number | Maximum files for indexing | `kiro-cli settings knowledge.maxFiles 1000` |
| `knowledge.chunkSize` | number | Text chunk size for processing | `kiro-cli settings knowledge.chunkSize 512` |
| `knowledge.chunkOverlap` | number | Overlap between text chunks | `kiro-cli settings knowledge.chunkOverlap 50` |
| `knowledge.indexType` | string | Type of knowledge index | `kiro-cli settings knowledge.indexType "fast"` |

### Key bindings (classic only)

These key bindings apply to the classic interface only and have no effect in the terminal UI.

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `chat.skimCommandKey` | char | Key for fuzzy search command | `kiro-cli settings chat.skimCommandKey "f"` |
| `chat.autocompletionKey` | char | Key for autocompletion hint acceptance | `kiro-cli settings chat.autocompletionKey "Tab"` |
| `chat.tangentModeKey` | char | Key for tangent mode toggle | `kiro-cli settings chat.tangentModeKey "t"` |
| `chat.delegateModeKey` | char | Key for delegate command | `kiro-cli settings chat.delegateModeKey "d"` |

### Key bindings (terminal UI)

Override the terminal UI shortcuts for cancelling a response, closing overlay menus, and quitting the session. Values use `ctrl+`, `shift+`, and `alt+`/`meta+` modifiers with a single key (for example `ctrl+shift+q`, `esc`). Invalid values fall back to the built-in default.

| Setting | Type | Default | Description | Example |
|---------|------|---------|-------------|---------|
| `chat.keybindings.cancelStream` | string | `esc` | Cancel the current agent response while it streams | `kiro-cli settings chat.keybindings.cancelStream "ctrl+x"` |
| `chat.keybindings.closeMenu` | string | `esc` | Close overlay panels and pickers | `kiro-cli settings chat.keybindings.closeMenu "ctrl+["` |
| `chat.keybindings.quit` | string | `ctrl+c` | Exit the chat session | `kiro-cli settings chat.keybindings.quit "ctrl+shift+q"` |

### Tool Search

Configure on-demand MCP tool discovery. See [Tool Search](https://kiro.dev/docs/mcp/tool-search.md) for details.

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `toolSearch.enabled` | boolean | Enable Tool Search for on-demand MCP tool discovery (default: false) | `kiro-cli settings toolSearch.enabled true` |
| `toolSearch.minPct` | number | Activate when MCP tool specs exceed this % of context window (default: 5) | `kiro-cli settings toolSearch.minPct 0` |
| `toolSearch.minTokens` | number | Activate when MCP tool specs exceed this token count (default: 50000) | `kiro-cli settings toolSearch.minTokens 0` |

### Feature toggles

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `chat.enableThinking` | boolean | Enable the thinking tool for complex reasoning (distinct from `chat.showThinking`, which displays the model's own reasoning blocks) | `kiro-cli settings chat.enableThinking true` |
| `chat.enableTangentMode` | boolean | Enable tangent mode feature (classic only) | `kiro-cli settings chat.enableTangentMode true` |
| `introspect.tangentMode` | boolean | Auto-enter tangent mode for introspect (classic only) | `kiro-cli settings introspect.tangentMode true` |
| `chat.enableTodoList` | boolean | Enable todo list feature (classic only) | `kiro-cli settings chat.enableTodoList true` |
| `chat.enableCheckpoint` | boolean | Enable checkpoint feature (classic only) | `kiro-cli settings chat.enableCheckpoint true` |
| `chat.enableDelegate` | boolean | Enable delegate tool (classic only) | `kiro-cli settings chat.enableDelegate true` |
| `app.disableAutoupdates` | boolean | Disable background auto-updates | `kiro-cli settings app.disableAutoupdates true` |

### API and service

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `api.timeout` | number | Overall timeout in seconds for a streaming response (default `3600`). Counts the full duration of the response, so the hour-long default gives long responses room to finish; set a lower value to enforce a shorter limit | `kiro-cli settings api.timeout 600` |
| `api.streamIdleSoftTimeout` | number | Seconds of response-stream silence before a stall warning is shown (default `60`) | `kiro-cli settings api.streamIdleSoftTimeout 120` |
| `api.streamIdleHardTimeout` | number | Seconds of response-stream silence before the stalled request is cancelled (default `300`) | `kiro-cli settings api.streamIdleHardTimeout 600` |
| `api.subagentTimeout` | number | Seconds a subagent can sit idle before it times out, instead of stalling the parent turn (default `3600`) | `kiro-cli settings api.subagentTimeout 1800` |

Transient request failures — throttling, 5xx errors, and connection drops (including mid-stream resets) — are retried automatically with backoff; no setting is required.

### Model context protocol (MCP)

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `mcp.initTimeout` | number | MCP server initialization timeout in milliseconds (default `5000`) | `kiro-cli settings mcp.initTimeout 10000` |
| `mcp.noInteractiveTimeout` | number | MCP initialization timeout in milliseconds for non-interactive runs (default `30000`) | `kiro-cli settings mcp.noInteractiveTimeout 60000` |
| `mcp.loadedBefore` | boolean | Track previously loaded MCP servers | `kiro-cli settings mcp.loadedBefore true` |

## Common configuration examples

### Basic setup

```bash
# Enable telemetry
kiro-cli settings telemetry.enabled true

# Set default chat model
kiro-cli settings chat.defaultModel "claude-3-sonnet"

# Disable greeting message
kiro-cli settings chat.greeting.enabled false
```

### Knowledge base configuration

```bash
# Enable knowledge base
kiro-cli settings chat.enableKnowledge true

# Set file patterns to include
kiro-cli settings knowledge.defaultIncludePatterns '["*.py", "*.js", "*.md", "*.txt"]'

# Set file patterns to exclude
kiro-cli settings knowledge.defaultExcludePatterns '["*.log", "node_modules", ".git", "*.pyc"]'

# Set maximum files to index
kiro-cli settings knowledge.maxFiles 2000
```

### Enable experimental features

```bash
# Enable thinking tool
kiro-cli settings chat.enableThinking true

# Enable tangent mode
kiro-cli settings chat.enableTangentMode true

# Enable todo lists
kiro-cli settings chat.enableTodoList true

# Enable checkpoints
kiro-cli settings chat.enableCheckpoint true

# Configure key bindings
kiro-cli settings chat.tangentModeKey "t"
kiro-cli settings chat.delegateModeKey "d"
```

### Performance tuning

```bash
# Cap streaming responses at 10 minutes instead of the 60-minute default
kiro-cli settings api.timeout 600

# Give slow connections more room before a stall warning
kiro-cli settings api.streamIdleSoftTimeout 120

# Adjust knowledge base chunk size
kiro-cli settings knowledge.chunkSize 1024

# Disable auto-compaction for long conversations
kiro-cli settings chat.disableAutoCompaction true
```

## Troubleshooting settings

### Invalid setting values

**Boolean values:** Use `true` or `false` (lowercase)
```bash
kiro-cli settings telemetry.enabled true  # ✓ Correct
kiro-cli settings telemetry.enabled True  # ✗ Wrong
```

**Array values:** Use JSON format with single quotes
```bash
kiro-cli settings knowledge.defaultIncludePatterns '["*.py", "*.js"]'  # ✓ Correct
```

**String values:** Use quotes for strings with spaces
```bash
kiro-cli settings chat.defaultModel "claude-3-sonnet"  # ✓ Correct
```

### Resetting settings

Delete individual settings:
```bash
kiro-cli settings --delete setting.name
```

Open settings file for manual editing:
```bash
kiro-cli settings open
```

View current settings to identify issues:
```bash
kiro-cli settings list --all
```

### Settings file issues

If the settings file becomes corrupted:

1. **Back up current settings:**
   ```bash
   kiro-cli settings list --format json > backup.json
   ```

2. **Open the settings file:**
   ```bash
   kiro-cli settings open
   ```

3. **Verify JSON syntax or restore from backup**

## Settings file location

Settings are stored in `~/.kiro/settings/cli.json`.

You can edit this file directly, but using `kiro-cli settings` commands is recommended for validation.

## Environment variables

| Variable | Description |
|----------|-------------|
| `KIRO_HOME` | Overrides the `~/.kiro` directory used for global agents, prompts, skills, steering, settings, and sessions. Useful for keeping multiple independent Kiro profiles on the same machine. |
| `KIRO_LOG_NO_COLOR` | Set to `1` to disable colored log output |
| `NO_COLOR` | Set to any value to disable all color output in the terminal UI |
| `KIRO_ACP_RECORD_PATH` | Path to a JSONL file for recording TUI ACP wire traffic. Useful for debugging agent communication protocol issues. |
| `KIRO_CLI_TOOL_SEARCH_MATCHING_THRESHOLD` | Minimum relevance score for Tool Search keyword results (default: `1.5`) |

## Next steps

- [Configure custom agents](https://kiro.dev/docs/custom-agents/configuration-reference.md)
- [Set up MCP servers](https://kiro.dev/docs/mcp.md)
- [Configure custom diff tools](https://kiro.dev/docs/cli/chat/diff-tools.md)
- [Enable experimental features](https://kiro.dev/docs/cli/experimental.md)
- [CLI Commands Reference](https://kiro.dev/docs/reference/cli-commands.md)
