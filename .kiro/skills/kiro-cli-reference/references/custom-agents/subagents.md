> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Invoking as sub-agents

> Delegate focused tasks to agents that run in parallel with isolated context

Sub-agents let you hand off focused tasks to agents that run in their own isolated context. The main agent spawns sub-agents when a task benefits from parallelism, specialized tools, or context isolation - then aggregates the results when they finish.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Automatic sub-agent invocation | ✓ | ✓ | ✓ | ✓ |
| Explicit sub-agent invocation | ✓ | ✓ | ✓ | ✓ |
| Custom agents as sub-agents | ✓ | ✓ | ✓ | ✓ |
| Parallel execution | ✓ | ✓ | ✓ | ✓ |

On Web, custom agents committed to `.kiro/agents/` can be invoked as sub-agents, along with Kiro's [built-in sub-agents](#built-in-sub-agents). Sessions you start from Mobile can use the same custom agents as Kiro Web.

## How sub-agents work

1. **Task assignment** - You describe a task (or the main agent identifies one that benefits from delegation)
2. **Agent selection** - Kiro selects the appropriate agent configuration based on the task and available agents
3. **Isolated execution** - The sub-agent runs with its own context window, tools, and permissions
4. **Result return** - When finished, the sub-agent returns findings to the main agent

Any [custom agent](https://kiro.dev/docs/custom-agents.md) can be invoked as a sub-agent. The main agent automatically selects agents based on their `description` field, or you can request one explicitly:

```text
Use the code-reviewer agent to analyze src/auth/ for security issues
```

## What sub-agents inherit

Sub-agents share the workspace environment but run with isolated conversation context:

| Shared with main agent | Isolated per sub-agent |
|------------------------|----------------------|
| [Steering files](https://kiro.dev/docs/steering.md) | Conversation history |
| [MCP servers](https://kiro.dev/docs/mcp.md) | Context window |
| Workspace file access | [Spec](https://kiro.dev/docs/specs.md) state |
| [Permissions](https://kiro.dev/docs/permissions.md) configuration | [Hook](https://kiro.dev/docs/hooks.md) triggers |

## Built-in sub-agents

Kiro includes internal sub-agents used automatically when appropriate:

- **Context gathering** - Explores your project structure and gathers relevant files and context
- **General purpose** - Handles parallelized tasks of any kind using the default agent configuration
- **Validation** - Checks a finished change against your request (rolling out gradually). See [Validation sub-agent](https://kiro.dev/docs/custom-agents/built-in.md#validation-sub-agent)
- **Introspect** - Answers questions about Kiro from its documentation (CLI V3). See [Introspect sub-agent](https://kiro.dev/docs/custom-agents/built-in.md#introspect-sub-agent)

You don't need to configure these - the main agent uses them as needed.

## Parallel execution

Sub-agents run in parallel, each working independently. This is useful for:

- Refactoring multiple files simultaneously
- Researching several topics in parallel
- Running independent analysis tracks

```text
Refactor these three services to use the new auth middleware - do them in parallel
```

## Task dependencies

Sub-agents support directed acyclic graphs (DAGs) where tasks depend on each other. The main agent plans the full task graph upfront, then executes in the right order - running independent tasks in parallel and waiting for dependencies before starting dependent ones.

```text
  ┌─────────────┐
  │  1. Analyze  │
  │ dependencies │
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │ 2. Refactor  │
  │   modules    │
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │  3. Run and  │
  │  fix tests   │
  └──────────────┘
```

**ℹ️ Info:** Task graphs are planned upfront and cannot be modified during execution. The agent determines the full DAG before any sub-agent starts running.

## Review loops

A stage can loop back to an earlier stage when its output signals that more work is needed - for example, a reviewer sends work back to an implementer for revisions.

```text
Implement the feature, then have a reviewer check it and send it back for fixes until it passes
```

The agent builds a looping pipeline with:

- **target** - the stage to re-run when the loop triggers
- **trigger** - text in the stage output that fires the loop (e.g., `NEEDS_CHANGES`)
- **max_iterations** - safety cap (between 1 and 10)

Constraints:
- A stage cannot loop back to itself
- Mutual loops (A → B → A) are rejected
- The trigger must be at least four characters

## Tool availability

The default sub-agent has the same built-in tools as the main agent - `read`, `write`, `shell`, `web_search`, `web_fetch`, and any configured MCP tools.

When you delegate to a custom agent, the sub-agent uses that agent's `tools` and `permissions` configuration. Tools not listed in the custom agent's config won't be available to the sub-agent. In CLI V3 and the IDE, the parent session's permissions also apply to the sub-agent's tool calls. See [Sub-agent permissions](#sub-agent-permissions).

**ℹ️ Custom orchestrator agents need the subagent tool:** If you're building a custom agent that will spawn sub-agents, include `subagent` in its `tools` array (or use `@builtin`). Without it, the agent can't delegate.

## Configuring sub-agent access

To limit which agents an agent can spawn, list `subagent/<name>` entries in its `tools` instead of `subagent`. Don't add `@builtin` or `*` to that agent's `tools`, since both include `invoke_sub_agent`, which can start any agent. To start a sub-agent without a prompt, add a `subagent` rule to its `permissions`:

```json
{
  "tools": ["read", "write", "shell", "web", "subagent/reviewer", "subagent/tester"],
  "permissions": {
    "rules": [
      { "capability": "subagent", "match": ["reviewer", "tester"], "effect": "allow" }
    ]
  }
}
```

To restrict the tools a sub-agent can use, configure `tools` in the **sub-agent's own config file** rather than in the parent.

## Sub-agent permissions

In CLI V3 and the IDE, Kiro checks every sub-agent tool call against two policies:

- The parent session's policy. This is your user and workspace `permissions.yaml`, the parent agent's `permissions`, and the approvals you gave earlier in the session.
- The sub-agent's own `permissions`.

The stricter result wins:

- A `deny` from either policy denies the call.
- An `ask` rule in either policy prompts you.
- If the parent session's policy has no rule for the call, Kiro prompts you, even when the sub-agent's own rules allow it.

A sub-agent's `allow` rules take effect only when that agent runs as the top-level agent, for example with `kiro-cli chat --agent <name>`. A call that the sub-agent's rules don't mention follows the parent session's policy. A sub-agent with no `permissions` block runs under the parent session's policy.

To let a sub-agent's tool calls run without prompts in CLI V3, add the sub-agent's `allow` rules to one of these:

- The parent agent's `permissions.rules`. The parent agent doesn't need the MCP server or tool itself.
- Your user-scope `~/.kiro/settings/permissions.yaml`. These rules apply to every agent.
- Your workspace-scope `permissions.yaml`. These rules apply to every agent in that workspace.

For example, a sub-agent named `data-analyst` that allows every tool from the `analytics` MCP server needs the same rule in the parent agent:

```json
{
  "tools": ["read", "write", "shell", "subagent/data-analyst"],
  "permissions": {
    "rules": [
      { "capability": "subagent", "match": ["data-analyst"], "effect": "allow" },
      { "capability": "mcp", "match": ["analytics/*"], "effect": "allow" }
    ]
  }
}
```

In a session where you trust every tool, `--trust-all-tools` approves sub-agent tool calls that would otherwise prompt. `deny` rules still apply.

## Surface-specific behavior

    IDE
    CLI
    Web

When workflows are disabled, sub-agents run in parallel and the main agent waits until all complete before proceeding. When workflows are enabled, the main agent instead launches custom-agent delegation as a background workflow run, so you can continue the parent conversation and monitor the run under **Workflows**. Each delegated agent has its own context window.

You can speed up development by leveraging sub-agents to perform multiple tasks simultaneously - for example, fetching and analyzing several tickets in parallel.

[Video](https://kiro.dev/videos/subagents.mp4)

In the CLI, you get live progress tracking as sub-agents work. Press **Ctrl+G** to open the execution monitor to inspect each sub-agent's activity - including current tool calls and output - without interrupting your main chat.

Inside the monitor, use **Ctrl+D** and **Ctrl+U** to navigate between sub-agents, and press **q** to return to the main chat.

**ℹ️ Delegation in V3 sessions with Workflows enabled:** **Workflow use** under `/settings features` controls how often the main chat starts Workflows. Choose **Only when asked**, **Only for large tasks**, or **As much as possible**. Custom agents inside a workflow can still invoke sub-agents when their tool configuration permits it. See [Background delegation and sub-agents](https://kiro.dev/docs/workflows.md#background-delegation-and-sub-agents).

### Runtime behavior

- **Working directory reads are auto-approved.** `fs_read` within the current working directory doesn't prompt. Reads outside still prompt.
- **In CLI V3, sub-agent approval prompts go to your session.** A headless run denies them. See [Sub-agent permissions](#sub-agent-permissions).
- **Sub-agent sessions record their parent.** Each persisted session includes the spawning session's ID for traceability.

Sub-agents run automatically in the background. The agent delegates tasks and aggregates results without additional user interaction.

## Best practices

1. **Use for complex tasks** - Most valuable for multi-step operations that benefit from isolation or parallelism
2. **Provide clear instructions** - Specific task descriptions lead to better agent selection and results
3. **Monitor progress** - In CLI, use Ctrl+G to check on long-running sub-agents
4. **Configure access** - Limit which agents an orchestrator agent can spawn, and decide which ones start without a prompt. See [Configuring sub-agent access](#configuring-sub-agent-access)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Sub-agent not starting | Verify the task description is clear and actionable |
| Unknown agent | Check the agent name with `kiro-cli agent list`; a request naming an unknown agent fails instead of falling back to the default agent |
| Missing tool access | Check the agent configuration's `tools` field |
| Approval prompts blocking | Add a `subagent` allow rule to skip the start prompt, and add the sub-agent's `allow` rules to the parent session's policy. See [Sub-agent permissions](#sub-agent-permissions) |
| Main agent can't spawn sub-agents | Add `subagent` to the orchestrator agent's `tools` array |
| Incomplete results | Provide more specific instructions or break into smaller tasks |
