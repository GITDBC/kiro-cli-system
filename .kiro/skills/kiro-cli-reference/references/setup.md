> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Setup & First Run

> Get up and running with Kiro CLI in minutes — from first install to productive coding

Kiro CLI is an AI coding agent that lives in your terminal — it reads your codebase, writes code, runs commands, and asks before doing anything destructive. This guide gets you from zero to productive in about five minutes.

## Prerequisites

If you haven't installed yet, run the install command from the [installation page](https://kiro.dev/docs/getting-started/installation.md) and complete browser authentication. Then come back here.

## Get to know the CLI

Kiro CLI has a built-in guide agent that knows everything about the CLI — commands, tools, settings, workflows, and best practices. Instead of reading docs, you can just ask it.

After launching a session, type:

```bash
> /guide
```

Then have a conversation:

```bash
[guide] > What can you help me with?

[guide] > How should I set up this project to work well with Kiro?

[guide] > What's the best way to do code reviews with Kiro?

[guide] > How do I connect my GitHub account?
```

The Guide agent draws from indexed documentation that matches your installed version. It can also create configuration files for you — agents, prompts, and steering files — right from the conversation.

**💡 Tip:** Think of `/guide` as your onboarding buddy. Ask it about your specific workflows and it'll tell you the best way to achieve them with Kiro CLI.

Press `Shift+Tab` to return to your main agent when you're ready to start working.

## Start your first session

Navigate to any project directory and launch Kiro:

```bash
cd my-project
kiro-cli
```

The terminal UI opens — a rich chat interface with syntax highlighting, interactive panels, and visual tool progress. You're now talking to an AI agent that can read, write, and run commands in your project.

## Have a conversation

Type naturally. Kiro understands your project context and can take action:

```bash
> Explain the architecture of this project

> Find all TODO comments and summarize them

> Write a unit test for the auth module

> Refactor the database connection to use connection pooling
```

Kiro reads your files, runs commands, and makes changes — asking for permission before anything destructive.

## Core interactions

### Reference files with @

Point Kiro at specific files using `@` with tab completion:

```bash
> Review @src/api/routes.ts for security issues
```

### Plan before acting

Press `Shift+Tab` to switch to Plan mode. Kiro outlines what it intends to do before making any changes — useful when you want to review the approach first.

```bash
[plan] > Migrate the Express routes to use async/await error handling
```

The agent produces a structured plan with steps. When you're satisfied, it switches to execution mode and carries out the work.

### Run shell commands directly

Prefix with `!` to run commands without going through the agent:

```bash
!npm run build
```

### Approve or reject changes

When Kiro wants to run a command or write a file, you'll see an approval prompt. Press `y` to approve, `n` to reject, or `Tab` to drill into options and provide feedback.

## Make Kiro understand your project

Out of the box, Kiro reads your files and infers context. But you can make it significantly smarter by telling it about your project's conventions. Create a steering file:

```bash
mkdir -p .kiro/steering
```

Add `.kiro/steering/project.md`:

```markdown
# Project Context

- This is a TypeScript project using Next.js 15
- Use pnpm for package management
- Follow the existing code style (Prettier + ESLint)
- Write tests with Vitest
- Prefer functional components with hooks
```

Kiro reads steering files automatically and follows your guidelines in every response. The difference is immediate — responses match your stack, your conventions, and your preferences.

See [Steering](https://kiro.dev/docs/steering.md) for the full guide on writing effective steering files.

## Essential slash commands

Slash commands control your session. Type `/` and the TUI shows autocomplete suggestions. Here are the ones you'll use most:

| Command | What it does |
|---------|-------------|
| `/help` | Opens a searchable panel of all commands |
| `/guide` | Switches to the Guide agent for help with Kiro itself |
| `/context` | Shows what files are in context and token usage |
| `/model` | Switch between AI models |
| `/agent` | Switch between agents |
| `/chat new` | Start a fresh conversation |

## Work with multiple agents

Kiro ships with built-in agents for different tasks, and you can create your own:

- **Default agent** — general-purpose coding assistant
- **Plan agent** — breaks down complex tasks into structured plans (`Shift+Tab`)
- **Guide agent** — answers questions about Kiro CLI itself (`/guide`)

Create custom agents for recurring workflows — code review, test writing, deployment, or anything specific to your team:

```bash
> /guide Create an agent for code review
```

The Guide agent generates a `.kiro/agents/code-review.yaml` file. Switch to it anytime with `/agent swap code-review`.

### Parallel work with subagents

For larger tasks, Kiro can spawn subagents that work in parallel with isolated context. Press `Ctrl+G` to open the crew monitor and watch them work in real time.

See [Subagents](https://kiro.dev/docs/custom-agents/subagents.md) and [Custom agents](https://kiro.dev/docs/custom-agents.md) for the full guide.

## Stay in control

Beyond the per-action approval flow, you have fine-grained control over what Kiro can do:

- **Trust patterns** — approve a command once, or trust a pattern (e.g., all `npm run` commands) so you're not interrupted for routine operations
- **Tool permissions** — use `/tools trust <name>` to pre-approve specific tools, or `/tools untrust <name>` to require explicit permission
- **Reset anytime** — `/tools reset` clears all runtime permissions

See [Permissions](https://kiro.dev/docs/permissions.md) for the full trust model.

## Extend with external tools

Kiro supports the Model Context Protocol (MCP), which lets it interact with databases, APIs, GitHub, and other services directly. Once you configure an MCP server, you can ask things like "list my open pull requests" or "query the staging database."

See [MCP integration](https://kiro.dev/docs/mcp.md) to connect your first server.

## Tips for your first session

- Press `Shift+Enter` to type multi-line prompts
- Press `Shift+Tab` to switch to Plan mode (agent plans before acting)
- Press `Esc` to cancel the agent or close any panel
- Type `/help` to see all available commands

The full keyboard reference is in [Terminal UI](https://kiro.dev/docs/cli/terminal-ui.md#keyboard-shortcuts).

## Proxy configuration

Kiro CLI (v1.8.0+) respects standard proxy environment variables. Set these in your shell:

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1,.company.com
```

For proxies that require authentication:

```bash
export HTTPS_PROXY=http://username:password@proxy.company.com:8080
```

## Debugging and troubleshooting

If you're having a problem with Kiro CLI, run `kiro-cli doctor` to identify and fix common issues.

### Expected output

```bash
$ kiro-cli doctor

✔ Everything looks good!

Kiro CLI still not working? Run kiro-cli issue to let us know!
```

If your output doesn't look like the expected output, follow the prompts to resolve your issue.

### Log file locations

Kiro CLI writes logs to platform-specific locations:

| Platform | Path |
|----------|------|
| macOS | `$TMPDIR/kiro-log/kiro-chat.log` |
| Linux | `$XDG_RUNTIME_DIR/kiro-log/kiro-chat.log` |
| Windows | `%TEMP%\kiro-log\logs\kiro-chat.log` |

Override the log path with the `KIRO_CHAT_LOG_FILE` environment variable:

```bash
KIRO_CHAT_LOG_FILE=/tmp/my-debug.log kiro-cli chat
```

On Windows (PowerShell):

```powershell
$env:KIRO_CHAT_LOG_FILE = "C:\temp\my-debug.log"
kiro-cli chat
```

### Common issues

- **Home directory fills during startup:** In storage-constrained environments such as CloudShell, set `KIRO_SKIP_BINARY_PINNING=1` only when the installed Kiro binary remains at a fixed, stable path. This avoids creating a session-specific binary copy. Do not use it if an installer can replace or delete the binary during the session.
- **Authentication failures** — Run `kiro-cli login` to re-authenticate.
- **Autocomplete not working** — Run `kiro-cli doctor` to verify shell integration.
- **SSH integration issues** — Verify your SSH server accepts the required environment variables.

### Troubleshooting steps

1. Run `kiro-cli doctor` to identify and fix common issues.
2. Check your internet connection.
3. Verify that you're using a supported environment. See [CLI commands](https://kiro.dev/docs/reference/cli-commands.md) for supported shells.
4. Try reinstalling Kiro CLI from the [installation page](https://kiro.dev/docs/getting-started/installation.md).
5. If the issue persists, report it using `kiro-cli issue`.

## What to explore next

Now that you're up and running, here's where to go deeper:

- [Terminal UI](https://kiro.dev/docs/cli/terminal-ui.md) — Full reference for the chat interface, themes, and panels
- [Steering](https://kiro.dev/docs/steering.md) — Guide Kiro with project-specific context and conventions
- [Custom agents](https://kiro.dev/docs/custom-agents.md) — Build specialized agents for your workflows
- [MCP](https://kiro.dev/docs/mcp.md) — Connect external tools and data sources
- [Hooks](https://kiro.dev/docs/hooks.md) — Automate actions before and after commands
- [Headless mode](https://kiro.dev/docs/cli/headless.md) — Run Kiro non-interactively in CI/CD pipelines
- [Guide agent](https://kiro.dev/docs/custom-agents/built-in.md) — Ask Kiro about its own features anytime with `/guide`
