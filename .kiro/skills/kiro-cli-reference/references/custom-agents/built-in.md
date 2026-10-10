> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Built-in agents

> Pre-configured agents that ship with Kiro for common workflows - planning, specs, debugging, and documentation help

Kiro ships with built-in agents for common development workflows. These use the same agent framework as custom agents but are pre-configured and maintained by Kiro. You can switch between them during a session or invoke them with dedicated UI controls and slash commands.

| Agent | IDE | CLI | Purpose |
|-------|:---:|:---:|---------|
| **Default** | ✓ | ✓ | General-purpose coding assistant |
| **Spec** | ✓ | ✓ | Structured feature development (requirements, design, tasks) |
| **Quick Spec** | ✓ | ✓ | Fast spec workflow - auto-generates all phases without approval gates |
| **Bug Fix** | ✓ | ✓ | Structured bug investigation and resolution |
| **Plan** | ✓ | ✓ | Read-only planning before execution |
| **Guide** | — | ✓ | Documentation-grounded CLI help (terminal UI) |
| **Help** | — | ✓ | Documentation-grounded CLI help (classic interface) |

## Default agent

The default agent is the general-purpose assistant that starts with every session. It has access to all built-in tools, MCP servers, and your workspace context. Most development tasks - writing code, debugging, refactoring, answering questions - happen here.

You don't need to invoke it explicitly; it's the starting point for all sessions.

## Spec agents

The Spec, Quick Spec, and Bug Fix agents produce formal requirements, design, and task documents stored in `.kiro/specs/`. They guide you through structured phases with approval gates between each one.

    IDE
    CLI

When starting a new session, the **"Let's build"** screen shows workflow options under "Start with a workflow":

| Workflow | What it produces |
|----------|-----------------|
| **Spec** | Requirements → design → tasks with approval gates between phases |
| **Quick Spec** | All three phases auto-generated without gates - fastest path to implementation |
| **Bug Fix** | Root cause analysis → fix design → implementation tasks |

Select a workflow to start a session with that agent. You can also invoke specs mid-session by clicking **Build with spec** in the chat input area.

Use the `/spec` slash command:

```bash
> /spec new my-feature    # starts a new spec - prompts for type
> /spec run my-feature    # executes all tasks autonomously
> /spec my-feature        # resumes an existing spec
```

Spec types in CLI:

- **Build a Feature** - structured feature development
- **Fix a Bug** - structured bug investigation
- **Quick Spec** - auto-generate all phases without approval gates

For the full guide on structured development workflows, see [Specs](https://kiro.dev/docs/specs.md).

## Plan agent

Plan mode helps you think before you act. It operates in **read-only mode** - exploring your codebase, gathering requirements, and producing implementation plans without making any changes. Once you approve, it hands off to the default agent for execution.

    IDE
    CLI

Select **Plan** from the workflow selector when starting a new session, or switch to it mid-session using the agent picker in the chat input bar (click the agent name, e.g., "Default", and select Plan).

Press `Shift+Tab` or run:

```bash
> /plan
> /plan Build a REST API for user authentication
```

When active, you'll see `[plan]` in your prompt.

### What Plan mode can access

| Operation | Available |
|-----------|:---------:|
| File reading, code intelligence, search | ✓ |
| Web search | ✓ |
| File writing, command execution, MCP tools | — |

For the full Plan mode workflow and best practices, see [Plan mode](https://kiro.dev/docs/specs/plan.md).

## Guide agent (CLI only)

The Guide agent provides documentation-grounded answers about Kiro. Unlike the default agent's general knowledge, the Guide agent searches indexed documentation that matches your installed version.

```bash
> /guide
```

Press `Shift+Tab` to return to your previous agent.

### What you can ask

- **Commands** - slash commands, CLI commands, their options and behavior
- **Settings** - available configuration options
- **Features** - MCP, hooks, steering, custom agents, sub-agents, code intelligence
- **Create files** - generate agent configs, prompts, and steering files in `.kiro/`

The Guide agent uses the **introspect** tool - hybrid search (semantic + BM25) over indexed documentation embedded at compile time.

## Help agent (CLI only)

**ℹ️ Info:** In the terminal UI, the Help Agent has been replaced by the Guide agent. Use `/guide` instead.

The Help agent provides the same documentation-grounded assistance as the Guide agent but in the classic (non-TUI) interface. Invoke with `/help` or `/help <question>`.

## Switching between agents

    IDE
    CLI
    Web

When you open a new session, the **"Let's build"** screen offers workflow options:

- **Spec** - Structured feature development
- **Plan** - Plan-only mode (read-only, no changes)
- **Bug Fix** - Structured bug investigation
- **Quick Spec** - Fast spec workflow without approval gates

Selecting a workflow automatically switches the active agent for that session. You can also switch agents mid-session by clicking the agent name (e.g., "Default") in the bottom bar of the chat pane to open the agent picker.

Use the `/agent` slash command:

```bash
> /agent swap           # opens interactive picker
> /agent swap my-agent  # switch directly by name
```

Or start a session with a specific agent:

```bash
kiro-cli --agent my-agent
```

Agent switching is not available in Kiro Web or Mobile, so the default agent remains the primary session agent. On Web, custom agents committed to your repository (`.kiro/agents/`) are available for sub-agent delegation. Mobile uses built-in sub-agents only.

## Creating your own agents

Built-in agents demonstrate how Kiro uses agent configurations for specialized workflows. You can create your own agents with the same capabilities - tailored tools, permissions, prompts, and models for your specific workflows.

See [Creating custom agents](https://kiro.dev/docs/custom-agents/creating.md) to get started.
