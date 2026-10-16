> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Custom agents

> Create and deploy specialized AI agents for your workflows

Custom agents provide a way to customize Kiro behavior by defining specific configurations for different use cases. Each custom agent is defined by a configuration file that specifies which tools the agent can access, what permissions it has, and what context it should include.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Project-level agents (`.kiro/agents/`) | ✓ | ✓ | ✓ | — |
| Global agents (`~/.kiro/agents/`) | ✓ | ✓ | — | — |
| Agent switching via UI | ✓ | ✓ | — | — |
| Modify agent settings | ✓ | ✓ | — | — |

By default, Kiro provides access to all available tools but requires user confirmation for most operations. This approach prioritizes security but can interrupt your workflow with frequent permission prompts.

Custom agents solve this by allowing you to:

- **Pre-approve trusted operations** - Define which operations can run without prompting
- **Limit tool access** - Restrict which tools are available to reduce complexity
- **Include relevant context** - Automatically load project files, documentation, or system information
- **Configure tool behavior** - Set specific parameters for how tools should operate

## Benefits of using custom agents

1. **Workflow optimization** - Create custom agents tailored to specific tasks like AWS infrastructure management, code reviews, or debugging sessions.
2. **Reduced interruptions** - Pre-approve trusted operations to eliminate permission prompts during focused work sessions.
3. **Enhanced context** - Automatically include relevant project documentation, configuration files, or system information.
4. **Team collaboration** - Share custom agent configurations with team members to ensure consistent development environments.
5. **Security control** - Limit tool access to only what's needed for specific workflows, reducing potential security risks.

## Relationship to MCP and built-in tools

Custom agents work with both [built-in tools](https://kiro.dev/docs/tools.md) and external tools from [MCP servers](https://kiro.dev/docs/mcp.md). Use the `tools` field to specify exactly which tools from each source are available. In CLI V3, keep full MCP selectors instead of relying on the CLI 2.x `toolAliases` field.

## Configuration file formats

Agent configurations support two formats - JSON and Markdown. Both support identical fields. Use Markdown when your system prompt is long or benefits from human readability; JSON works well for programmatically generated configs.

    JSON
    Markdown

`.kiro/agents/my-agent.json`:

```json
{
  "name": "my-agent",
  "description": "A custom agent for my workflow",
  "tools": ["read", "write", "shell"],
  "excludedTools": ["knowledge"],
  "includeMcpJson": true,
  "includePowers": false,
  "resources": [
    "file://./ARCHITECTURE.md",
    "skill://backend-patterns"
  ],
  "permissions": {
    "rules": [
      { "capability": "shell", "match": ["npm *", "git *"], "effect": "allow" }
    ]
  },
  "prompt": "You are a helpful coding assistant",
  "model": "claude-sonnet-4.6",
  "welcomeMessage": "Ready to help. What are you working on?"
}
```

`.kiro/agents/my-agent.md` - front matter for config, body for system prompt:

```markdown
---
name: my-agent
description: A custom agent for my workflow
model: claude-sonnet-4.6
tools: ["read", "write", "shell"]
excludedTools: ["knowledge"]
includeMcpJson: true
includePowers: false
resources:
  - file://./ARCHITECTURE.md
  - skill://backend-patterns
permissions:
  rules:
    - capability: shell
      match: ["npm *", "git *"]
      effect: allow
welcomeMessage: "Ready to help. What are you working on?"
---

You are a helpful coding assistant focused on clean, well-tested code.

## Guidelines
- Use async/await, never callbacks
- All database queries must be parameterized
- Write tests for every new function
```

### Storage locations

- **Workspace agents (project-specific):** `.kiro/agents/[name].json` or `.kiro/agents/[name].md` — shared via version control, loaded only if the workspace is trusted
- **Global agents (user-wide):** `~/.kiro/agents/[name].json` or `~/.kiro/agents/[name].md` — available across all projects

When both locations have agents with the same name, workspace agents take precedence.

Nested directories are supported. The agent name is the path relative to the agents directory without the extension: `~/.kiro/agents/team/planner.md` becomes `team/planner`.

#### Surface behavior

The IDE and CLI can select a custom agent as the primary session agent. Kiro Web loads project-level custom agents committed to `.kiro/agents/` and can invoke them for sub-agent delegation, but you cannot select one as the primary Web session agent. Mobile uses Kiro's [built-in agents](https://kiro.dev/docs/custom-agents/built-in.md) only.

To use personal custom agents in cloud sessions, upload them from **Settings > Sync** in [Kiro Web](https://app.kiro.dev/settings/cloud-config), then manage them under **Settings > Agents**.

**💡 Tip:** Custom agents control **what tools are available and what they can do**. If you want to influence how the agent thinks and responds without changing tool access, use [Steering files](https://kiro.dev/docs/steering.md) instead. You can combine both - a custom agent that includes steering via the `resources` field.

## Previous versions

If you're upgrading from IDE 0.x, existing JSON profiles continue to work. For CLI 2.x, profiles that still use `allowedTools` or `toolsSettings` without a `permissions` block must be converted with `/upgrade-agent` before CLI V3 can load them; other supported fields carry over. Current optional fields include `permissions`, `excludedTools`, `includeMcpJson`, `resources` with `skill://`, and Markdown format.

- [IDE 0.x reference - Custom agent config](https://kiro.dev/docs/ide/0x-reference.md#custom-agent-config)
- [CLI 2.x reference - Custom agent config](https://kiro.dev/docs/cli/2x-reference.md#custom-agent-config)
- [What's new in CLI V3 - Agent config changes](https://kiro.dev/docs/cli/v3/agent-config.md)
- [What's new in IDE 1.0 - Agent config changes](https://kiro.dev/docs/ide/whats-new-v1/agent-config.md)

## Next steps

- [Built-in agents](https://kiro.dev/docs/custom-agents/built-in.md) - pre-configured agents that ship with Kiro
- [Create a custom agent](https://kiro.dev/docs/custom-agents/creating.md)
- [Configuration reference](https://kiro.dev/docs/custom-agents/configuration-reference.md) - full reference for all configuration fields
- [Invoking as sub-agents](https://kiro.dev/docs/custom-agents/subagents.md) - delegate tasks to agents in parallel
- [Permissions](https://kiro.dev/docs/permissions.md) - configure capability-based access control
- [Examples](https://kiro.dev/docs/custom-agents/examples.md) - real-world agent configurations
- [Troubleshooting](https://kiro.dev/docs/custom-agents/troubleshooting.md) - common issues and solutions
