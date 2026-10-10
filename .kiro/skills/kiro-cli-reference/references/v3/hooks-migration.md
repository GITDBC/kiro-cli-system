> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Hooks migration

> Migrating from CLI 2.x embedded hooks to the new standalone .kiro/hooks/*.json format

> **New to Kiro CLI 3.0?** This page covers migration from CLI 2.x hooks. For the current hooks format reference, see [Hooks →](https://kiro.dev/docs/hooks.md).

> **Tip:** Run `kiro-cli agent migrate` first — it auto-converts hooks to the new format and reports any triggers it couldn't convert.

Hooks have moved from embedded fields in agent config to standalone `.kiro/hooks/*.json` files with a versioned JSON schema. Rename your trigger keys using the table below, then move the definitions to a new file.

## Old format — do not use in 3.0 (shown for migration reference only)

Hooks were embedded directly in agent config:

```json
{
  "hooks": {
    "agentSpawn": [{"command": "echo 'starting'", "matcher": ".*"}],
    "preToolUse": [{"command": "npm run lint", "matcher": "Write|Edit"}],
    "fileEdited": [{"command": "prettier --write", "matcher": "\\.ts$"}]
  }
}
```

## New format

Each hooks file is a standalone `.kiro/hooks/*.json` file:

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

Matcher syntax is unchanged — regex patterns from 2.x transfer directly. The `}` template variable is new in 3.0 and only available in the new format.

## Trigger reference

| Trigger | Fires when | Matcher matches | Can block? |
|---------|-----------|-----------------|:----------:|
| `SessionStart` | Session begins | — | No |
| `Stop` | Session ends | — | No |
| `PreToolUse` | Before tool executes | Tool name (regex) | **Yes** |
| `PostToolUse` | After tool executes | Tool name (regex) | No |
| `PreTaskExec` | Before a spec task starts | — | **Yes** |
| `PostTaskExec` | After a spec task finishes | — | No |
| `UserPromptSubmit` | User submits a prompt | — | **Yes** |
| `PostFileCreate` | After a file is created by the agent | File path (regex) | No |
| `PostFileSave` | After a file is saved/edited by the agent | File path (regex) | No |
| `PostFileDelete` | After a file is deleted by the agent | File path (regex) | No |
| `Manual` | User-triggered on demand | — | No |

**Old trigger names** (2.x → 3.0 mapping):

| Old Trigger | New Trigger | Notes |
|-------------|-------------|-------|
| `agentSpawn` | `SessionStart` | Fires when a new session begins |
| `userPromptSubmit` | `UserPromptSubmit` | Fires before the agent processes a prompt |
| `preToolUse` | `PreToolUse` | Fires before a tool executes |
| `postToolUse` | `PostToolUse` | Fires after a tool completes |
| `fileEdited` | `PostFileSave` | Fires after a file is written |
| `fileCreated` | `PostFileCreate` | Fires after a new file is created (IDE legacy alias, now unified) |
| `agentStop` / `stop` | `Stop` | Fires when the session ends — `agentStop` is IDE legacy; CLI used `stop` |

### Matcher semantics by trigger

The `matcher` field is a regex pattern, but what it matches against depends on the trigger:

| Trigger | `matcher` matches against |
|---------|--------------------------|
| `PostFileSave`, `PostFileCreate`, `PostFileDelete` | File path (e.g., `\\.ts$`, `src/.*`) |
| `PreToolUse`, `PostToolUse` | Tool name (e.g., `write`, `shell`, `write\|read`) |
| `UserPromptSubmit` | Prompt text content |
| `SessionStart`, `Stop`, `PreTaskExec`, `PostTaskExec`, `Manual` | Not evaluated — hook always fires |

Regex patterns from CLI 2.x transfer directly. The `}` template variable is available only in the new format for file-related triggers.

Once your files are in `.kiro/hooks/`, Kiro picks them up automatically. See the [full hooks reference →](https://kiro.dev/docs/hooks.md) for schema details and advanced action types.
