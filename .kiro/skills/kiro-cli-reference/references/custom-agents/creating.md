> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Creating custom agents

> Learn how to create and configure custom agents for specialized workflows

Custom agents allow you to tailor Kiro behavior for specific tasks by defining which tools are available, what permissions are granted, and what context is automatically included.

## Quick start

IDE
CLI

Create an agent file directly in your project:

1. Create a `.kiro/agents/` directory in your workspace (or `~/.kiro/agents/` for global agents)
2. Add a Markdown or JSON file - the filename becomes the agent name

For example, create `.kiro/agents/backend-dev.md`:

```markdown
---
name: backend-dev
description: Backend development specialist
model: claude-sonnet-4.6
tools: ["read", "write", "shell"]
permissions:
  rules:
    - capability: shell
      match: ["npm *", "git *"]
      effect: allow
---

You are a backend engineer focused on Node.js and TypeScript.
Always use async/await. All database queries must be parameterized.
```

Then switch to it using the agent picker in the chat pane header.

You can create an agent using the `/agent create` slash command from within a Kiro CLI chat session. By default, it uses AI-assisted mode to generate a full agent configuration based on your description:

```text
> /agent create

✔ Enter agent name:  · backend-specialist
✔ Enter agent description:  · You are a specialist in backend coding practices
✔ Agent scope · Local (current workspace)
Select MCP servers (use Space to toggle, Enter to confirm): markdown-downloader (node), code-analysis (uv)

✓ Agent 'backend-specialist' has been created and saved successfully!
```

You can also provide a name and options inline:

```text
> /agent create backend-specialist -D "Backend coding specialist" -m code-analysis
```

**ℹ️ Info:** `/agent generate` is an alias for `/agent create`. Both commands behave identically.

Alternatively, use the CLI command directly from your terminal:

```bash
kiro-cli agent create backend-specialist
```

### Options

The `/agent create` slash command and the `kiro-cli agent create` CLI command share some flags, while others are exclusive to the slash command:

| Flag | Description | Availability |
|------|-------------|--------------|
| `--directory` | Where to save the agent (see [directory values](#directory-values)) | Both |
| `--from` | Template agent to base the new agent on (implies `--manual`) | Both |
| `--description` | Description of the agent | Slash command |
| `--mcp-server` | MCP server to include (repeatable) | Slash command |
| `--manual` | Use editor-based creation instead of AI generation | Slash command |

**⚠️ Warning:** The `--description` and `--mcp-server` flags are only available in AI-assisted mode. They cannot be combined with `--manual` or `--from`.

### Directory values

The `--directory` flag accepts two special values in addition to custom paths:

| Value | Description |
|-------|-------------|
| `workspace` | Creates the agent in `.kiro/agents/` in your current working directory |
| `global` | Creates the agent in `~/.kiro/agents/` (the default) |
| `./path` or `/path` | Creates the agent in the specified custom path |

When no `--directory` is specified, agents are saved to the global directory (`~/.kiro/agents/`).

### Manual creation mode

If you prefer to define the agent configuration yourself in an editor rather than using AI generation, pass the `--manual` flag:

```text
> /agent create my-agent --manual
```

This opens your default editor with a basic agent configuration file. You can also base a new agent on an existing one using `--from`:

```text
> /agent create my-agent --from backend-specialist
```

## Agent configuration file

Custom agents are defined using JSON or Markdown configuration files. Here's a basic JSON example:

```json
{
  "name": "my-agent",
  "description": "A custom agent for my workflow",
  "tools": ["read", "write"],
  "permissions": {
    "rules": [{ "capability": "fs_read", "effect": "allow" }]
  },
  "resources": [
    "file://README.md",
    "file://.kiro/steering/**/*.md",
    "skill://.kiro/skills/**/SKILL.md"
  ],
  "prompt": "You are a helpful coding assistant",
  "model": "claude-sonnet-4.6"
}
```

See the [Configuration reference](https://kiro.dev/docs/custom-agents/configuration-reference.md) for full details on all available fields.

## File locations

You can define local agents and global agents.

### Local agents (project-specific)

```text
.kiro/agents/
```

Local agents are specific to the current workspace and only available when running Kiro from that directory or its subdirectories.

**Example:**
```text
my-project/
├── .kiro/
│   └── agents/
│       ├── dev-agent.json
│       └── aws-specialist.json
└── src/
    └── main.py
```

### Global agents (user-wide)

```text
~/.kiro/agents/
```

Global agents are available from any directory.

**Example:**
```text
~/.kiro/agents/
├── general-assistant.json
├── code-reviewer.json
└── documentation-writer.json
```

### Agent precedence

When Kiro looks for an agent:

1. **Local first**: Checks `.kiro/agents/` in the current directory
2. **Global fallback**: Checks `~/.kiro/agents/` in the HOME directory

If both locations have agents with the same name, the local agent takes precedence with a warning message.

## Using your custom agent

    IDE
    CLI

    Click the agent name (e.g., "Default") in the bottom bar of the chat input to open the agent picker, then select your custom agent from the list. The switch applies to the current session, and your agent's tools, permissions, and prompt take effect from the next message.

    You can also choose a custom agent from the workflow options when starting a new session.

    Start a new chat session - which uses the default agent ("kiro_default") - and swap to an agent using the agent slash command:

    ```bash
    > /agent swap

     Choose one of the following agents
    ❯ rust-developer-agent
      kiro_default
      backend-specialist
    ```

    After selecting an agent, you will see the following:

    ```bash
    ✔ Choose one of the following agents · backend-specialist

    [backend-specialist] >
    ```

    Alternatively, start a chat session with your custom agent:

    ```bash
    kiro-cli --agent my-agent
    ```

## Next steps

- [Configuration reference](https://kiro.dev/docs/custom-agents/configuration-reference.md) - explore all available configuration options
- [Built-in agents](https://kiro.dev/docs/custom-agents/built-in.md) - see how Kiro's pre-configured agents are set up
- [Examples](https://kiro.dev/docs/custom-agents/examples.md) - real-world agent configurations
- [Troubleshooting](https://kiro.dev/docs/custom-agents/troubleshooting.md) - resolve common issues
