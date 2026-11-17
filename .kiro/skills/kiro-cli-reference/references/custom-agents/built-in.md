> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Built-in agents

> Pre-configured agents that ship with Kiro for common workflows - planning, specs, debugging, and documentation help

Kiro ships with built-in agents for common development workflows. These use the same agent framework as custom agents but are pre-configured and maintained by Kiro. You can switch between the primary agents during a session or invoke them with dedicated UI controls and slash commands. Kiro also has built-in sub-agents it invokes on its own. In Kiro CLI V3, the Introspect sub-agent answers questions about Kiro. In Kiro CLI V3 and the Kiro IDE, the [validation sub-agent](#validation-sub-agent) checks a larger change after it is finished.

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

## Introspect sub-agent

In a Kiro CLI V3 session, ask Kiro about its own features, such as which Hook trigger fires when or what a setting does, and Kiro may invoke the built-in Introspect sub-agent, which answers from the official Kiro documentation. Kiro decides whether to delegate the question; you do not switch to it, so it does not appear in the table above. It reads documentation pages with the `web_fetch` and `read_file` tools and is told which Kiro client you are using, so its answers match the CLI. It does not change your configuration: to create or edit agents, Hooks, or Steering files, ask the default agent.

## Validation sub-agent

The validation sub-agent checks a change the default agent has finished against what you asked for. It runs in its own context, separate from the default agent's conversation, and reports any requirement the change missed before the work is called done. Not every account has it yet; see [Availability](#availability).

After the default agent finishes a change, it decides whether the change needs validation. It is designed to run the check only when the change is substantial and not yet verified. Substantial means it spans three or more files, adds a new module, or covers several distinct requirements. Not yet verified means the agent has not already checked each requirement. Read-only answers, cosmetic edits, and small single-purpose changes skip it. The Plan, Spec, Quick Spec, and Bug Fix agents do not use it.

To run it on demand, ask for it in your prompt:

```text
Add retries to the upload client and a flag to turn them off, then invoke the validation sub-agent
```

The validation sub-agent starts from your original request, a short summary of what changed, and the tests the default agent already ran. It is built to:

- Break your request into a few concrete claims, up to five.
- Check each claim with focused evidence from the workspace or a targeted test. When no test fits, it may write a short check, run it, and delete it. For a qualitative claim, it uses its own judgment as a last resort.
- Reuse the test results the default agent already has, and avoid running your full build or test suite.
- Note failures that look pre-existing or environmental without reporting them as problems with the change.

It then reports a pass, or a fail with a one-line reason for each unmet requirement. On a fail, the default agent makes one limited correction pass, then stops. It does not run the validation sub-agent again on the same change. The default agent reports any requirement it could not fix in the sub-agent's own words, so the final call is yours. The validation sub-agent does not replace your own tests or code review. A pass means the checks it chose found no gap, not that the change is correct.

The label differs by client. In the IDE, it appears as a sub-agent step titled **Sub-agent: validation**. In the CLI, the step is labeled **Subagent** with `validation` as its target.

Starting the validation sub-agent does not prompt you. Its own file edits and shell commands follow the same approvals as the default agent. It has no permissions of its own and inherits the session's policy, so it cannot do anything the default agent could not. For how Kiro approves sub-agent tool calls, see [Sub-agent permissions](https://kiro.dev/docs/custom-agents/subagents.md#sub-agent-permissions).

### Availability

Kiro is rolling the validation sub-agent out gradually to Kiro CLI V3 and the Kiro IDE. You do not need to change any setting. When the rollout reaches your account, the default agent can start using it. Until then, Kiro does not offer it, and asking for it has no effect. Kiro CLI 2.x sessions and Kiro Web are not part of this rollout.

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

Agent switching is not available in Kiro Web or Mobile, so the default agent remains the primary session agent. On Web, custom agents committed to your repository (`.kiro/agents/`) and personal agents uploaded to [cloud configuration](https://kiro.dev/docs/web/cloud-configuration.md) are available for sub-agent delegation. The same applies to sessions you start from Mobile.

## Creating your own agents

Built-in agents demonstrate how Kiro uses agent configurations for specialized workflows. You can create your own agents with the same capabilities - tailored tools, permissions, prompts, and models for your specific workflows.

See [Creating custom agents](https://kiro.dev/docs/custom-agents/creating.md) to get started.

If you're using CLI 2.x, see [built-in names in the CLI 2.x reference](https://kiro.dev/docs/cli/2x-reference.md#built-in-names).
