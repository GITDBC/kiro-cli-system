> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Hooks

> Automate repetitive tasks and enforce best practices with event-driven agent hooks

Hooks run shell commands or agent prompts automatically when specific events happen in your session - the agent modifies a file, invokes a tool, or completes a task. You define the trigger and the action; Kiro handles the execution.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Event-driven hooks | ✓ | ✓ | — | — |
| Shell command actions | ✓ | ✓ | — | — |
| Agent prompt actions | ✓ | ✓ | — | — |
| Create Hooks by asking the agent in chat | ✓ | ✓ | — | — |

## What you can do with hooks

- **Enforce standards** - run linters, formatters, or type checks automatically after agent file changes
- **Gate dangerous operations** - block tool execution unless preconditions are met (PreToolUse)
- **Generate companion files** - auto-create tests, docs, or translations when new source files appear
- **Validate before commit** - check code quality before the agent finalizes changes
- **Inject context** - feed the agent additional instructions based on what it's doing

## Quick example

A `PostFileSave` hook that runs ESLint whenever the agent saves or edits a TypeScript file:

```json
{
  "version": "v1",
  "hooks": [{
    "name": "Lint on save",
    "trigger": "PostFileSave",
    "matcher": "\\.(ts|tsx)$",
    "action": { "type": "command", "command": "npx eslint --fix" }
  }]
}
```

This file lives at `.kiro/hooks/lint-on-save.json` and activates automatically - no manual prompting needed. The hook receives the saved file path and session context via STDIN. See [Hook Actions](https://kiro.dev/docs/hooks/actions.md) for details on how commands receive event data.

## How hooks work

Project Hook configurations are JSON files stored in `.kiro/hooks/`. Kiro CLI V3 also loads global Hooks from `~/.kiro/hooks/`, so one Hook can run across every workspace. Global and workspace Hooks run alongside each other. Each file defines one or more Hooks with a trigger event, an optional matcher pattern, and an action.

When the trigger event fires, Kiro checks the matcher. If it matches (or no matcher is specified), the action executes:

- **Command actions** run a shell command in your project root. The command receives session context as JSON on STDIN.
- **Agent actions** inject a prompt into the current conversation, steering the agent's behavior.

### Choose a trigger

Use [Hook types](https://kiro.dev/docs/hooks/types.md) to choose the trigger for your task. It is the authoritative trigger list and documents surface availability and trigger-specific behavior.

## Hook file schema

Each hook file is a standalone JSON file at `.kiro/hooks/<id>.json`. The full schema:

```json
{
  "version": "v1",
  "hooks": [
    {
      "name": "example-hook",
      "trigger": "PostFileSave",
      "matcher": "\\.(ts|tsx)$",
      "action": { "type": "command", "command": "npx eslint --fix" }
    }
  ]
}
```

### Field reference

| Field | Required | Description |
|-------|:--------:|-------------|
| `version` | Yes | Schema version - currently `"v1"` |
| `hooks` | Yes | Array of hook definitions |
| `hooks[].name` | Yes | Human-readable identifier for the hook |
| `hooks[].description` | No | Documentation only |
| `hooks[].trigger` | Yes | Event that fires the hook (PascalCase - see [Hook types](https://kiro.dev/docs/hooks/types.md)) |
| `hooks[].matcher` | No | Filters which events fire this hook. For `PreToolUse`/`PostToolUse`, a tool selector (tool ID, category tag, `@mcp`, `@<server>`, or wildcard) or a regex against the tool ID; see [Hook types](https://kiro.dev/docs/hooks/types.md#pre-tool-use). For file events, a regex against the file path. Defaults to always-match. |
| `hooks[].action.type` | Yes | `"command"` (shell command) or `"agent"` (inject prompt) |
| `hooks[].action.command` | Cond. | Shell command to run (required when `type` is `"command"`) |
| `hooks[].action.prompt` | Cond. | Prompt text to inject (required when `type` is `"agent"`) |
| `hooks[].timeout` | No | Timeout in seconds for command actions (default: 60). `0` disables the timeout. Ignored for agent actions. |
| `hooks[].enabled` | No | Set `false` to skip the hook without deleting it (default: `true`) |
| `hooks[].confirm` | No | Ask for confirmation before a `Stop` command hook runs. See [Confirmation prompts](#confirmation-prompts). |

### Confirmation prompts

A command hook on the `Stop` trigger can ask before it runs. Add a `confirm` block with the question to ask and the options to present:

```json
{
  "version": "v1",
  "hooks": [
    {
      "name": "Submit session results",
      "trigger": "Stop",
      "action": { "type": "command", "command": "./submit.sh" },
      "confirm": {
        "question": "Submit this session's results?",
        "options": [
          { "id": "submit", "label": "Yes, submit", "run": true },
          { "id": "dismiss", "label": "Not this time", "run": false }
        ]
      }
    }
  ]
}
```

Each option has an `id`, a `label` shown on the button, and a `run` flag that controls whether the hook's command executes when that option is chosen.

#### Dynamic confirm options with `confirmCommand`

To decide at run time whether and what to ask, add an optional `confirmCommand` to the `confirm` block. The command runs before the prompt appears, and its stdout controls the prompt as JSON:

- `` suppresses the prompt and skips the hook for this turn
- `` replaces the static question and options

```json
{
  "confirm": {
    "question": "Submit this session's results?",
    "confirmCommand": "./confirm-options.sh",
    "options": [
      { "id": "submit", "label": "Yes, submit", "run": true },
      { "id": "dismiss", "label": "Not this time", "run": false }
    ]
  }
}
```

If `confirmCommand` exits non-zero, times out, or prints invalid JSON, the static `question` and `options` are used as a fallback. This makes it useful for prompts that should only appear under certain conditions - for example, a "don't ask again this session" option that writes a marker file and returns `` on later turns.

### File naming and location

- **Workspace location**: `.kiro/hooks/` in your project root
- **Global location (CLI V3)**: `~/.kiro/hooks/` for Hooks that run in every workspace
- **Naming**: Any `.json` filename works - use descriptive kebab-case names (e.g., `lint-on-save.json`, `guard-writes.json`)
- **Multiple Hooks per file**: A single file can define multiple Hooks in the `hooks` array
- **Activation**: Hooks activate automatically when a session starts - no manual registration needed

## Setting up hooks

    IDE
    CLI
    Web

    Click the **+** button in the Agent Hooks section of the Kiro panel and select **Ask Kiro to create a hook**. Describe what you want in natural language - for example, "run tests after every file save" - and Kiro generates the hook configuration through conversation.

    The resulting hook is saved as a JSON file in `.kiro/hooks/`.

    [Video](https://kiro.dev/videos/hooks-ide.mp4)

    Create hook files directly in `.kiro/hooks/`. Hooks activate automatically when you start a session.

    ```json
    
      }]
    }
    ```

    See [Hook Actions](https://kiro.dev/docs/hooks/actions.md) for exit code behavior and the [Configuration Reference](https://kiro.dev/docs/custom-agents/configuration-reference.md#hooks-field) for the complete schema.

    Kiro Web can store personal Hook configuration through **Settings > Sync** and show uploaded configuration under **Settings > Hooks**. Apply that cloud configuration to new local IDE or CLI sessions to use the Hooks without copying files into your local `.kiro` directory.

    Kiro Web sessions do not run the event-driven triggers or command and agent actions documented on this page, and Web chat does not create Hooks.

## Previous versions

The `.kiro/hooks/*.json` format was introduced in **IDE 1.0** and **CLI V3**. If you're upgrading from an earlier version:

- **From IDE 0.x** - Hooks moved from the previous format to standalone JSON files with PascalCase trigger names. See [What's new in IDE 1.0: Hooks](https://kiro.dev/docs/ide/whats-new-v1/hooks.md) for the trigger mapping.
- **From CLI 2.x** - Run `/upgrade-agent` to convert object-form Hooks into a profile-scoped array. Move definitions that should run independently of a profile or across surfaces into standalone `.kiro/hooks/*.json` files. See [CLI V3 Hooks migration](https://kiro.dev/docs/cli/v3/hooks-migration.md) for both current placements and the trigger mapping.

## Next steps

- **[Hook Triggers](https://kiro.dev/docs/hooks/types.md)** - Trigger types and their use cases
- **[Hook Actions](https://kiro.dev/docs/hooks/actions.md)** - Command and agent action details
- **[Management](https://kiro.dev/docs/hooks/management.md)** - Organize, edit, and maintain hooks
- **[Best Practices](https://kiro.dev/docs/hooks/best-practices.md)** - Patterns for effective hook design
- **[Examples](https://kiro.dev/docs/hooks/examples.md)** - Templates you can use
- **[Troubleshooting](https://kiro.dev/docs/hooks/troubleshooting.md)** - Common issues and solutions
