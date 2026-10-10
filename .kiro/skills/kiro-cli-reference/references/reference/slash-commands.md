> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Slash commands

> Quick reference for in-chat slash commands in Kiro CLI

## Overview

Slash commands are special commands you can use within an interactive chat session to quickly perform actions without leaving the conversation. They start with a forward slash (`/`) and provide shortcuts for common tasks.

## Using slash commands

Slash commands are only available in interactive chat mode:

```bash
kiro chat
> /help
```

## Available commands

### `/help`

Switch to the Help Agent to ask questions about Kiro CLI features, or display classic help text.

```bash
# Switch to Help Agent
> /help

# Ask a question directly
> /help How do I configure MCP servers?

# Show classic help text
> /help --legacy

# Show help for a specific command
> /help --legacy /context
```

See [Help Agent](https://kiro.dev/docs/custom-agents/built-in.md) for more details.

### `/quit`

Exit the interactive chat session.
```bash
> /quit
```

Aliases: /exit, /q

### `/clear`

Clear the current conversation history.

```bash
> /clear
```

Note: This only clears the display, not the saved conversation.

### `/context`

Manage context files and view context window usage. Context rules determine which files are included in your Kiro session and are derived from the current active agent.

```bash
# Display context rule configuration and matched files
> /context show

# Add context rules (filenames or glob patterns)
> /context add src/app.js
> /context add "*.py"
> /context add "src/**/*.js"

# Remove specified rules
> /context remove src/app.js

# Remove all rules
> /context clear
```

**Available subcommands:**
- `show` - Display the context rule configuration and matched files
- `add` - Add context rules (filenames or glob patterns)
- `remove` - Remove specified rules

**Notes:**
- You can add specific files or use glob patterns (e.g., `*.py`, `src/**/*.js`)
- Agent rules apply only to the current agent
- Context changes are NOT preserved between chat sessions. To make changes permanent, edit the agent config file.
- The files matched by these rules provide Kiro with additional information about your project or environment

See [Context Management](https://kiro.dev/docs/cli/chat/context.md) for detailed documentation.

### `/model`

Select an AI model for the current session. Use the interactive picker or specify a model name directly.

```bash
# Open interactive model picker
> /model

# Select a model directly by name
> /model claude-opus-4.6

# Tab completion for model names
> /model clau<Tab>

# Explicitly write the current model as the default
> /model set-current-as-default
```

**Available subcommands:**
- `set-current-as-default` - Explicitly persist your current model selection as the default for all future sessions

**Features:**
- Tab completion shows available models from the API as you type
- Ghost text hints appear showing matching model names
- Fuzzy matching suggests similar models if exact name not found
- Case-insensitive matching against model names and IDs

**Note:** Your `/model` selection persists automatically. Switch models once and Kiro saves the choice to `~/.kiro/settings/cli.json`, carrying it into future sessions. The `set-current-as-default` subcommand is no longer required to make a selection stick; it remains available to explicitly write your current model as the default. See [Persistence](https://kiro.dev/docs/cli/chat/settings.md#persistence) for details.

### `/agent`

Manage agents and switch between different agent configurations.

```bash
# List all available agents
> /agent list

# Create a new agent (AI-assisted by default)
> /agent create my-agent

# Create with description and MCP servers
> /agent create my-agent -D "Code reviewer" -m code-analysis

# Create using editor-based mode instead of AI generation
> /agent create my-agent --manual

# Create in a specific directory
> /agent create my-agent --directory workspace

# Generate is an alias for create
> /agent generate my-agent

# Edit the current agent
> /agent edit

# Edit a specific agent by name (interactive picker when no name given)
> /agent edit my-agent

# Edit an agent by file path
> /agent edit --path /absolute/path/to/my-agent.json

# Show agent config schema
> /agent schema

# Set default agent (interactive picker when no name given)
> /agent set-default my-agent

# Swap to a different agent at runtime
> /agent swap code-reviewer
```

**Available subcommands:**
- `list` - List all available agents with their descriptions
- `create` - Create a new agent using AI-assisted generation by default. Pass `--manual` for editor-based creation. Supports `-D` (description), `-m` (MCP server), `-d` (directory), and `-f` (template agent) flags.
- `edit` - Edit an existing agent configuration. Shows an interactive picker when no agent name is provided. Supports `--path` for direct file access.
- `generate` - Alias for `create`
- `schema` - Show agent config schema
- `set-default` - Define a default agent for new chat sessions. Shows an interactive picker when no agent name is provided.
- `swap` - Swap to a new agent at runtime (shows agent descriptions for selection)

**Notes:**
- Agent creation and editing are available in a local V3 session started with `kiro-cli --v3`. Cloud sessions don't support these operations.
- `/agent create` uses AI-assisted generation by default. Pass `--manual` to create the profile in your configured editor.
- `/agent edit` opens the selected profile in your configured editor.
- Agents can be stored globally in `~/.kiro/agents/` or per-workspace in `.kiro/agents/`
- The `--directory` flag accepts `workspace`, `global`, or a custom path
- Launch kiro-cli chat with a specific agent using `kiro-cli chat --agent agent_name`
- Built-in agents (`kiro_default`, `kiro_help`, `kiro_planner`) cannot be edited
- Type `/agent ` or `/agent swap ` and press Tab to autocomplete agent names. Ghost text hints appear inline as you type, matching the behavior in `/model`.
- Switching agents preserves your current `/model` selection unless the target agent's configuration specifies a model of its own — then it switches to that one.

When you edit an agent, changes are made in a **temporary file** first. If validation fails (for example, invalid JSON or missing required fields), you're prompted to continue editing or cancel. The original configuration file is never overwritten by a failed edit.

See [Custom Agents](https://kiro.dev/docs/custom-agents.md) for detailed documentation.

### `/upgrade-agent`

Migrate older agent configurations to the [v3 format](https://kiro.dev/docs/cli/v3/agent-config.md).

```bash
# Scan agents and open the selection menu
> /upgrade-agent

# Review upgraded agents and conversion warnings
> /upgrade-agent diagnostics
```

**Available subcommands:**
- `run` - Scan agents and open the selection menu (default)
- `diagnostics` - Review upgraded agents and their conversion warnings

**Notes:**
- Scans both `.kiro/agents/` (workspace) and `~/.kiro/agents/` (global)
- Original files are backed up to `.json.bak` before any changes
- Only agents that need upgrading appear in the selection menu

See [Upgrading agent configs](https://kiro.dev/docs/cli/v3/upgrade-agent.md) for detailed documentation.

### `/spawn`

Spawn a new agent session that runs a task in parallel with your current conversation.

```bash
# Spawn an agent with a task
> /spawn Analyze the test coverage in src/utils and suggest improvements

# Give the spawned session a name
> /spawn --name test-analysis Review all failing tests and categorize the failures
```

Spawned sessions run alongside your main conversation without blocking it. Monitor them in real time with `Ctrl+G` to open the crew monitor, which shows status for every spawned session.

Unlike [subagents](https://kiro.dev/docs/custom-agents/subagents.md), which are spawned by the main agent to delegate focused work within a task graph, `/spawn` is a user-driven command that starts a fresh long-running session you can return to later.

**Notes:**
- A task description is required — `/spawn` with no arguments fails.
- Use `--name` to label a session for easier identification in the crew monitor.

### `/chat`

Manage chat sessions, including saving, loading, and switching between sessions. Kiro CLI automatically saves all chat sessions on every conversation turn.

```bash
# Start a fresh conversation without restarting the CLI
> /chat new

# Start a fresh conversation with an initial prompt
> /chat new how do I set up a React project

# Open interactive session picker to resume a previous session
> /chat resume

# Save current session to a file
> /chat save /myproject/codereview.json

# Load a session from a file
> /chat load /myproject/codereview.json
```

**Available subcommands:**
- `new` - Start a fresh conversation without restarting the CLI. Optionally pass an initial prompt (e.g., `/chat new how do I set up a React project`). Use `/chat resume` to return to previous sessions.
- `resume` - Open interactive session picker to choose a session to resume
- `save` - Save current session to a file
- `load` - Load a session from a file (`.json` extension is optional)
- `save-via-script` - Save session using a custom script (receives JSON via stdin)
- `load-via-script` - Load session using a custom script (outputs JSON to stdout)

**Notes:**
- Sessions are automatically saved on every conversation turn
- Sessions are stored per directory, so each project has its own set of sessions
- The session picker shows session name, last activity, and message preview
- Use keyboard shortcuts in the picker: `↑`/`↓` to navigate, `Enter` to select, `/` to filter

### `/fullscreen`

Toggle the current interactive session between inline and fullscreen mode.

```
> /fullscreen
```

Fullscreen gives the conversation a dedicated terminal screen with mouse, touchpad, and keyboard scrolling. Run `/fullscreen` again to return inline. The command works with V2 and V3 and is available in both TUI and Lite; it is not available in non-interactive sessions.

To start future interactive TUI sessions in fullscreen, open `/settings`, choose **Display**, and turn on **Start fullscreen**. See [Fullscreen mode](https://kiro.dev/docs/cli/fullscreen.md) for navigation, selection, and troubleshooting details.

### `/sessions`

Open the V3 session dashboard to browse, search, resume, and clean up local and cloud sessions.

```bash
# Open the dashboard
> /sessions

# Preview cleanup of empty local sessions
> /sessions clean

# Confirm permanent cleanup
> /sessions clean --yes
```

The dashboard is available only in V3. To open it before starting a chat, run `kiro-cli chat --sessions`. See [Session management](https://kiro.dev/docs/cli/chat/session-management.md) for search coverage, cleanup safeguards, and engine-selection behavior.

### `/session-id`

Print the current chat session ID. Useful when you want to resume this exact session later with `kiro-cli chat --resume-id <ID>` or share the ID with support.

```bash
> /session-id
```

On exit, Kiro CLI also shows a resume hint with the ID so you can jump back into the same session from your next terminal.

#### Custom session storage

You can use custom scripts to control where chat sessions are saved to and loaded from. This allows you to store sessions in version control systems, cloud storage, databases, or any custom location.

**Save via script:**
```bash
> /chat save-via-script ./scripts/save-to-git.sh
```

Your script receives the chat session JSON via stdin. Example script to save to Git notes:

```bash
#!/bin/bash
set -ex
COMMIT=$(git rev-parse HEAD)
TEMP=$(mktemp)
cat > "$TEMP"
git notes --ref=kiro/notes add -F "$TEMP" "$COMMIT" --force
rm "$TEMP"
echo "Saved to commit ${COMMIT:0:8}" >&2
```

**Load via script:**
```bash
> /chat load-via-script ./scripts/load-from-git.sh
```

Your script should output the chat session JSON to stdout. Example script to load from Git notes:

```bash
#!/bin/bash
set -ex
COMMIT=$(git rev-parse HEAD)
git notes --ref=kiro/notes show "$COMMIT"
```

### `/save`

Save the current conversation to a file.

```bash
# Save <PATH>
> /chat save /myproject/codereview.json
```

### `/load`

Load a previously saved conversation.

```bash
# List available conversations
> /chat load /myproject/codereview.json
```

### `/editor`

Open your default editor to compose a longer prompt.

```bash
> /editor
```

Opens `$EDITOR` (defaults to vi if not set) to compose a multi-line message. Useful for crafting detailed prompts, pasting code snippets, or writing longer instructions. Save and exit the editor to send the message.

### `/reply`

Open your editor with the most recent assistant message quoted for reply.

```bash
> /reply
```

Opens `$EDITOR` with the AI's last response quoted, allowing you to reference and respond to specific parts of the message. Useful for providing feedback on specific sections or asking follow-up questions about particular details.

### `/checkpoint`

Manage workspace checkpoints to track and restore file changes.

```bash
# Initialize a new checkpoint
> /checkpoint init

# List all checkpoints
> /checkpoint list

# Restore to a checkpoint (interactive picker)
> /checkpoint restore

# Restore to specific checkpoint
> /checkpoint restore 2

# Restore with exact state match (removes newer files)
> /checkpoint restore 2 --hard

# View checkpoint details
> /checkpoint expand 1

# View differences between checkpoints
> /checkpoint diff 1 2

# Clean up checkpoint data
> /checkpoint clean
```

**Available subcommands:**
- `init` - Create a snapshot of current workspace state
- `list` - Show available checkpoints with timestamps and file stats
- `restore` - Restore workspace to a previous checkpoint state
- `expand` - Show detailed checkpoint information
- `diff` - View differences between checkpoints
- `clean` - Clean up checkpoint shadow repository

**How it works:**
- Creates a shadow bare git repository to track file changes
- Checkpoints created per conversation turn
- Sub-checkpoints for each tool use
- Conversation history reverts when restoring to a checkpoint
- Auto-enabled in git repositories (ephemeral mode)
- Can be manually initialized in non-git directories

**Restore modes:**
- **Default**: Reverts tracked changes and deletions, keeps files created after checkpoint
- **Hard mode** (`--hard`): Exactly matches checkpoint state, deletes files created after checkpoint

**Note:** This is an experimental feature. Enable with `kiro-cli settings chat.enableCheckpoint true`.

### `/plan`

Switch to the Plan agent for breaking down complex ideas into implementation plans.

```bash
# Switch to Plan agent
> /plan

# Switch with immediate prompt
> /plan Build a REST API for user management
```

The Plan agent specializes in breaking down complex ideas into actionable implementation plans. Use `Shift+Tab` to return to your previous agent.

### `/spec`

List specs, switch to spec mode, run spec tasks, or analyze requirements.

```bash
# List specs and switch to spec mode
> /spec

# Start a new spec
> /spec new my-feature

# Execute the spec's tasks
> /spec run my-feature

# Open a spec document
> /spec view my-feature requirements

# Analyze requirements for ambiguities and gaps
> /spec analyze_requirements my-feature
```

**Available subcommands:**

- `new <feature-name>` - Start a new spec and switch to spec mode
- `run <feature-name>` - Execute the spec's tasks
- `view <feature-name> [requirements|design|tasks]` - Open one of the spec's documents
- `analyze_requirements [feature-name]` - Analyze a spec's requirements for ambiguities, inconsistencies, and missing acceptance criteria. With no feature name, a searchable picker lists the specs that have a `requirements.md`

**Notes:**

- `/spec` is not available while a cloud session is active

See [Specs](https://kiro.dev/docs/specs.md) and [Analyze Requirements](https://kiro.dev/docs/specs/analyze-requirements.md) for detailed documentation.

### `/guide`

Switch to the Guide agent for documentation-grounded help and onboarding.

```bash
# Switch to Guide agent
> /guide
```

The Guide agent answers questions about Kiro CLI features, commands, tools, and settings using indexed documentation. It can also create configuration files in your `.kiro/` directory (agents, prompts, steering files).

Use `Shift+Tab` or `/agent swap` to return to your previous agent.

**ℹ️ Info:** The `/guide` command is only available in the terminal UI. In the classic interface, use `/help` for the same interactive agent experience.

See [Guide agent](https://kiro.dev/docs/custom-agents/built-in.md) for detailed documentation.

### `/knowledge`

Manage your knowledge base for semantic search across files and directories.

```bash
# Show all knowledge base entries
> /knowledge show

# Add a file or directory
> /knowledge add --name my-docs --path ./docs

# Add with include/exclude patterns
> /knowledge add --name src --path ./src --include "*.ts" --exclude "*.test.ts"

# Add with indexing type
> /knowledge add --name api --path ./api --index-type Best

# Search the knowledge base
> /knowledge search "authentication flow"

# Remove an entry
> /knowledge remove ./docs

# Update (re-index) an entry
> /knowledge update ./docs

# Re-index every knowledge base at once
> /knowledge update

# Clear entire knowledge base
> /knowledge clear

# Cancel background indexing operation
> /knowledge cancel
```

**Available subcommands:**
- `show` - List all knowledge base entries with status
- `add` - Add files or directories to knowledge base
- `search` - Semantically search indexed content
- `remove` (alias: `rm`) - Remove entry by path
- `update` - Re-index an existing entry. Run with no arguments to re-index every knowledge base at once.
- `clear` - Clear entire knowledge base (requires confirmation)
- `cancel` - Cancel background indexing operation

**Add options:**
- `--name, -n` - Entry name (required)
- `--path, -p` - File or directory path (required)
- `--include` - Include patterns (can specify multiple)
- `--exclude` - Exclude patterns (can specify multiple)
- `--index-type` - Fast or Best (default from settings)

**Note:** This is an experimental feature. Enable with `kiro-cli settings chat.enableKnowledge true`.

See [Knowledge Management](https://kiro.dev/docs/cli/experimental/knowledge-management.md) for detailed documentation.

### `/compact`

Summarize the conversation to free up context space.

```bash
> /compact
```

Condenses the conversation history while preserving key information, useful when approaching context limits. The AI creates a summary of the conversation so far and replaces the message history with this summary, freeing up tokens in your context window.

### `/paste`

Paste an image from your clipboard into the conversation.

```bash
> /paste
```

Adds an image from your system clipboard to the conversation, allowing the AI to analyze screenshots, diagrams, error messages, or any visual content. Supports common image formats (PNG, JPEG, etc.).

### `/tools`

View tools and permissions. By default, Kiro will ask for your permission to use certain tools. You can control which tools you trust so that no confirmation is required.

```bash
# View all tools, estimated token counts, and permissions
> /tools

# Show the input schema for all available tools
> /tools schema

# Trust a specific tool for the session
> /tools trust write

# Revert a tool to per-request confirmation
> /tools untrust write

# Trust all tools (equivalent to deprecated /acceptall)
> /tools trust-all

# Reset all tools to default permission levels
> /tools reset
```

**Available subcommands:**
- `schema` - Show the input schema for all available tools
- `trust` - Trust a specific tool or tools for the session
- `untrust` - Revert a tool or tools to per-request confirmation
- `trust-all` - Trust all tools (equivalent to deprecated /acceptall)
- `reset` - Reset all runtime permissions to defaults, including shell trust patterns, filesystem path permissions, and denied tools

**Output columns:**
- `~Tokens` - Estimated token count for each tool's schema (values 1000+ shown as `k`)
- `Permission` - Current permission status (Trusted, Ask, or Allowed)
- `Total` - Combined token count per origin (Native tools, each MCP server)

**Note:** For permanent tool configuration, see [Agent Configuration Reference](https://kiro.dev/docs/custom-agents/configuration-reference.md#tools-field).

### `/prompts`

View and retrieve prompts. Prompts are reusable templates that help you quickly access common workflows and tasks. These templates are provided by the MCP servers you have installed and configured.

```bash
# List available prompts from a tool or show all available prompts
> /prompts list

# Show detailed information about a specific prompt
> /prompts details code-review

# Get a specific prompt by name
> /prompts get code-review [arg]

# Quick retrieval (without /prompts prefix)
> @code-review [arg]

# Create a new local prompt
> /prompts create my-prompt

# Edit an existing local prompt
> /prompts edit my-prompt

# Remove an existing local prompt
> /prompts remove my-prompt
```

**Available subcommands:**
- `list` - List available prompts from a tool or show all available prompts
- `details` - Show detailed information about a specific prompt
- `get` - Get a specific prompt by name
- `create` - Create a new local prompt
- `edit` - Edit an existing local prompt
- `remove` - Remove an existing local prompt

**Quick tip:** To retrieve a prompt directly, use `@<prompt name> [arg]` without the `/prompts get` prefix.

See [Manage Prompts](https://kiro.dev/docs/cli/chat/manage-prompts.md) for detailed documentation.

### `/hooks`

View context hooks.

```bash
> /hooks
```

Display active context hooks for the current session.

### `/usage`

Show billing and credits information.

```bash
> /usage
```

View your current usage statistics and remaining credits. In non-interactive runs, `/usage` prints the full usage breakdown instead of a one-line summary.

{/*
### `/stats`

Inspect request IDs, timings, and token counts for recent turns. Reach for this when a response feels slow or when support asks for a specific request ID.

`/stats` is intentionally hidden from tab-completion, but works when typed directly.

```bash
# View all recorded requests
> /stats

# View only the last 5 requests
> /stats 5

# Export to JSON (defaults to stats.json)
> /stats save debug-session.json
```

Displays an in-memory log of recent API requests with their request IDs, total duration, time-to-first-chunk (TTFC), input and output token counts, and error status. The footer shows aggregate metrics (`avg`, `p90`, `max`, and `errors` count).

`/stats save` writes the records to a JSON file you can attach when filing a bug or sharing with support.

**Notes:**
- Stats are kept in an in-memory ring buffer of the last 100 requests and reset when the session ends.
- Durations over 5 seconds are highlighted in the panel.
*/}

### `/mcp`

View MCP servers and registry status.

```bash
> /mcp
```

Display Model Context Protocol servers currently active, their available tools, and registry status for managed servers.

When your organization has a registry configured, `/mcp add` and `/mcp remove` persist changes to your agent's configuration file, so additions and removals survive restarts.

**MCP disabled by your administrator**

If your organization's administrator has disabled MCP in the Kiro console, `/mcp` shows one of two messages:

- **`MCP has been disabled by your administrator`** — MCP is turned off for your organization. All servers (user-configured, legacy, registry, and session-injected) are suppressed and no MCP tools are available to the agent.
- **`Failed to retrieve MCP settings — MCP disabled`** — the Kiro client couldn't reach the governance API. MCP fails closed for security. This is usually transient; retry, check connectivity, or contact your administrator if it persists.

MCP governance applies to IAM Identity Center and API key users. Builder ID and social auth users are not affected.

See [MCP governance](https://kiro.dev/docs/enterprise/governance/mcp.md) for the administrator setup.

**Related commands:**
- `/mcp auth` — Force re-authentication for a remote server
- `/mcp cancel-auth` — Cancel a stuck authentication flow
- `/mcp logout` — Remove stored credentials for a server

### `/mcp auth`

Force re-authentication for a remote MCP server whose OAuth token has expired or become invalid.

```bash
# Re-authenticate with a specific server
> /mcp auth my-server
```

Use this when a remote MCP server stops responding due to an expired or revoked token. Kiro opens a browser-based OAuth flow to obtain a fresh token without requiring you to restart your session.

You can also press `^A` in the MCP panel status view to trigger the same action.

### `/mcp cancel-auth`

Abort a pending OAuth authentication flow that is stuck waiting for browser confirmation.

```bash
# Cancel a stuck auth flow
> /mcp cancel-auth my-server
```

If you triggered an OAuth flow (either automatically or via `/mcp auth`) and the server stays in a "waiting for authentication" state — for example, because the browser tab was closed or a popup was blocked — this command cancels the pending request so you can retry authentication or continue without that server.

You can also press `^X` in the MCP panel status view to abort.

### `/mcp logout`

Remove stored OAuth credentials for a remote MCP server.

```bash
# Remove credentials for a specific server
> /mcp logout my-server
```

This clears the locally cached token for the specified server. The next time the server requires authentication, a fresh OAuth flow is triggered. Use this when you need to switch accounts or fully revoke access.

You can also press `^R` in the MCP panel status view to remove credentials.

### `/config`

Review the agents, MCP servers, Powers, Steering, Skills, and Hooks configured for the current V3 session.

```bash
# Open the configuration summary
> /config

# Open a category directly
> /config skills
```

Available in local and cloud V3 sessions. When source information is available, the panel identifies configuration as local or cloud. See [Configuration scopes](https://kiro.dev/docs/configuration.md) for source-label behavior and category details.

### `/powers`

List the installed Powers.

```bash
> /powers
```

Powers are packaged bundles of MCP servers and documentation that extend the agent. See [Powers](https://kiro.dev/docs/powers.md) to learn what each one provides and how to install more.

Type `/` at the prompt to find installed Powers alongside built-in commands.

Available in a local V3 session started with `kiro-cli --v3`.

### `/theme`

Override theme colors for prompt and response text.

```bash
> /theme
```

Customize the colors used for your prompt input and agent response text. Falls back to ANSI colors when terminal color detection has low confidence.

### `/title`

Set, clear, or show the terminal window title for the current session. This helps you keep track of which session is running in which terminal window. The title displays as `kiro: <text>`.

```bash
# Show the current title
> /title

# Set a sticky custom title
> /title weekly standup notes

# Clear the custom title
> /title --clear
```

A title you set manually is sticky — it persists through session updates until you clear it with `--clear`.

Requires the terminal title feature to be enabled. Turn it on from `/settings display` → **Terminal title**; when it's off, `/title` tells you how to enable it.

**ℹ️ Info:** Titles are truncated to 60 characters. Some terminals ignore the OSC 0 escape sequence used to set the title, and under tmux you need `set-titles on` for the outer terminal to update. The title resets on exit, with exact behavior varying by terminal.

See [In-session settings](https://kiro.dev/docs/cli/chat/settings.md) for the `/settings display` toggle.

### `/copy`

Copy the last assistant response to your clipboard.

```bash
> /copy
```

Copies the full content of the most recent assistant response, including all segments across tool calls. Works over SSH and through terminal multiplexers (tmux, Zellij) via OSC 52 clipboard escape sequences. Payloads over 100KB are skipped to avoid silent truncation on terminals with size limits.

### `/transcript`

Open the conversation transcript in your pager, or save it to a file.

```bash
# Open the transcript in your pager
> /transcript

# Render the transcript as plaintext or JSON
> /transcript --plain
> /transcript --json

# Export the conversation to a file (markdown by default)
> /transcript save conversation.md

# Export as plaintext or JSON
> /transcript save conversation.txt --plain
> /transcript save conversation.json --json
```

Opens the full conversation history in `$PAGER` (defaults to `less`, or `notepad` on Windows). Press `q` to exit and return to the chat. Also available via `Ctrl+T`.

**Available subcommands:**
- `save` - Export the conversation to a file as markdown (default), plaintext, or JSON

**Format flags:**
- `--plain` - Render the transcript as plaintext instead of formatted markdown
- `--json` - Render the transcript as JSON

The `--plain` and `--json` flags switch the rendered transcript format inline, so you can read the conversation the way you want without leaving the pager. Combine them with `save` to control the exported format — `save` writes markdown by default, and the flag (not the file extension) determines the format.

### `/code`
Manage code intelligence configuration and get feedback.

```bash
# Initialize LSP-powered code intelligence in the current directory
> /code init

# Force reinitialization in the current directory - restarts LSP servers
> /code init -f

# Get a complete overview of the workspace
> /code overview

# Get overview with cleaner output
> /code overview --silent

# Get workspace status and LSP server statuses
> /code status

# View LSP logs for troubleshooting
> /code logs # Show last 20 ERROR logs

> /code logs -l INFO            # Show INFO level and above

> /code logs -n 50              # Show last 50 entries

> /code logs -l DEBUG -n 100    # Show last 100 DEBUG+ logs

> /code logs -p ./lsp-logs.json # Export logs to JSON file

```

**Available subcommands:**
- `init` - Initialize LSP servers for enhanced code intelligence
- `overview` - Get a complete overview of the workspace structure
- `status` - Show the detailed status of the LSP servers and workspace status
- `logs` - View logs

### `/experiment`

Toggle experimental features.

```bash
> /experiment
```

Enable or disable experimental CLI features.

### `/tangent`

Create conversation checkpoints to explore side topics.

```bash
> /tangent
```

Enter or exit [tangent mode](https://kiro.dev/docs/cli/experimental/tangent-mode.md) to explore tangential topics without disrupting your main conversation. Use `Ctrl+T` as a keyboard shortcut (when tangent mode is enabled).

### `/todos`

View, manage, and resume to-do lists.

```bash
# View todo
> /todo

# Add todo
> /todo add "Fix authentication bug"

# Complete todo
> /todo complete 1
```

### `/issue`

Create a new GitHub issue or make a feature request.

```bash
> /issue
```

Opens a workflow to submit issues or feature requests to the Kiro team.

### `/logdump`

Create a zip file with logs for support investigation and troubleshooting.

```bash
# Create log archive with chat logs
> /logdump

# Include MCP server logs
> /logdump --mcp
```

**Available options:**
- `--mcp` - Include MCP server logs in addition to chat logs

**Output:**

Creates a timestamped zip file in the current directory with the format `q-logs-YYYY-MM-DDTHH-MM-SSZ.zip`.

**What's included:**
- `logs/kiro-chat.log` - Main chat logs (always included)
- `logs/mcp.log` - MCP server logs (only with `--mcp` flag)

**When to use:**
- Reporting bugs or unexpected errors
- Sharing diagnostic information with AWS support
- Investigating agent or MCP server issues
- Troubleshooting tool execution problems

**Example output:**
```
Collecting logs...
✓ Successfully created q-logs-2025-01-22T14-30-52Z.zip with 1 log file
```

**Note:** Review the log contents before sharing publicly, as logs may contain file paths and conversation history from your session.

**Related:** See also [kiro-cli diagnostic](https://kiro.dev/docs/reference/cli-commands.md#kiro-cli-diagnostic) for system diagnostics and `/code logs` for LSP server logs.

### `/settings`

Configure theme, keybindings, terminal input, display preferences, and prompt history scope through an interactive menu.

```bash
# Open the settings menu
> /settings

# Customize theme colors
> /settings theme

# View keyboard shortcuts
> /settings keybindings

# Configure multi-line input for your terminal
> /settings terminal

# Toggle animations, ASCII art, icons, thinking display, and status-line segments
> /settings display

# Choose per-session or global prompt history
> /settings history
```

**Available subcommands:**
- `theme` — Customize prompt and response colors with a live preview
- `keybindings` — View configurable keyboard shortcuts (read-only reference)
- `terminal` — Enable `Shift+Enter` / `Option+Enter` for multi-line input. Auto-configures supported terminal apps (VS Code, Alacritty, Zed, Apple Terminal, and others) or shows manual workarounds for unsupported terminals
- `display` — Toggle animations, ASCII art, icon rendering, the thinking display (`Show thinking`), and status-line segments for date, time, current usage percentage, and remaining credits. Status-line segments are hidden by default; changes apply immediately and persist across sessions.
- `history` — Switch prompt history between `session` (default) and `global` modes

**Notes:**
- The `terminal` subcommand creates a `.bak` backup before modifying any terminal configuration files.
- tmux users need `set -s extended-keys on` in their `tmux.conf` for `Shift+Enter` to work.
- Animation, ASCII art, and icon changes apply immediately. Status-line changes apply immediately and persist across sessions. The `Show thinking` toggle and `history` mode apply to your next session.

See [In-session settings](https://kiro.dev/docs/cli/chat/settings.md) for the full subcommand reference.

### `/effort`

Set the model's reasoning effort level for the current session.

```bash
# Open interactive effort picker
> /effort

# Set a specific level
> /effort high
> /effort max
```

**Available levels:** `low`, `medium`, `high`, `xhigh`, `max`

Which levels are available depends on the active model. Higher effort levels use more tokens but produce more thorough responses for complex tasks.

Your `/effort` choice persists automatically. Change the level once and Kiro remembers it for future sessions. You can also set persistent per-model defaults in `~/.kiro/settings/cli.json` under `chat.modelDefaults`:

```json
{
  "chat": {
    "modelDefaults": {
      "claude-sonnet-4": {
        "effort": "high"
      },
      "claude-opus-4": {
        "effort": "max"
      }
    }
  }
}
```

**Precedence order:** loaded session effort > user defaults in cli.json > built-in defaults.

Workspace-level overrides are also supported via `.kiro/settings/cli.json` in your project root.

See [Effort](https://kiro.dev/docs/models/effort.md) for detailed documentation.

### `/goal`

Start a goal-driven iterative loop where the agent works autonomously toward an objective and verifies completion before stopping.

```bash
# Set a goal (default: 5 iterations)
> /goal refactor the auth module to use JWT tokens and ensure all tests pass

# Allow more iterations for complex tasks
> /goal --max 10 migrate the entire test suite from Jest to Vitest

# Cancel an active goal
> /goal clear
```

Unlike a regular prompt, `/goal` keeps the agent running through multiple cycles of implementation and self-check until the acceptance criteria in your goal statement are met. Be explicit about what "done" looks like — "all tests pass" or "no TypeScript errors" gives the agent a concrete verification target.

**Available subcommands:**
- `clear` — Cancel the active goal loop and return to standard interactive mode

**Options:**
- `--max <number>` — Maximum number of iterations (default: 5)

**Notes:**
- The agent runs up to 5 iterations by default. Use `--max` to increase for complex tasks.
- You can interrupt the agent at any point during a goal to give additional instructions.
- File changes made during the loop remain on disk even after clearing.
- Use [queue steering](https://kiro.dev/docs/cli/chat/queue-steering.md) (Ctrl+S) to nudge the agent mid-loop without cancelling.

See [Goal](https://kiro.dev/docs/cli/chat/goal.md) for detailed documentation.

### `/rewind`

Fork the conversation at an earlier turn to explore a different path.

```bash
# Open interactive turn picker
> /rewind

# Jump to a specific turn by index
> /rewind 4
```

Creates a new session starting from the selected turn. The original session is preserved and you can switch back with `/chat load` or `/chat resume`.

The interactive picker shows prompt previews, tool call details, and context usage percentage at each turn, listed newest-first.

**Notes:**
- The new session is a fork, not a destructive rewrite. Your original conversation remains intact.
- Useful for backtracking when a conversation went in the wrong direction, or for exploring alternative approaches from the same starting point.

See [Rewind](https://kiro.dev/docs/checkpoints.md) for detailed documentation.

### `/changelog`

View recent release notes inline in the CLI.

```bash
> /changelog
```

Displays the latest Kiro CLI release notes directly in your terminal, so you can see what changed without leaving your session.

### Skill-based slash commands

In addition to the built-in commands above, skills defined in `.kiro/skills/` and `~/.kiro/skills/` are automatically available as slash commands. Type `/` followed by the skill name to invoke it directly.

```bash
# Invoke a skill named "pr-review"
> /pr-review

# Invoke a skill named "cdk-deploy"
> /cdk-deploy
```

The available skill commands depend on which skills are present in your workspace and global skill directories. See [Agent Skills](https://kiro.dev/docs/skills.md) for details on creating and managing skills.

### Keyboard shortcuts

In interactive mode, you can also use:
- `Ctrl+C` - Cancel current input / exit session
- `Ctrl+D` - Exit session
- `Ctrl+D/U` - Navigate between subagents in the monitor
- `Ctrl+G` - Open subagent execution monitor
- `Ctrl+J` - Insert newline (all terminals including tmux)
- `Ctrl+O` - Expand collapsed shell output
- `Ctrl+R` - Reverse incremental history search
- `Ctrl+S` - Fuzzy search commands and context files, use tab to select multiple items
- `Ctrl+T` - Toggle tangent mode for isolated conversations (if enabled)
- `Alt+Enter` - Insert newline (Terminal.app, Ghostty)
- `Alt+Backspace` - Delete previous word
- `Shift+Enter` - Insert newline (iTerm2, Ghostty, Kitty, Warp, Zed)
- `Shift+Tab` - Enter plan mode
- `Up/Down arrows` - Navigate prompt history (per-session by default; configure with `/settings history`)
- `Tab` - Drill into approval options / autocomplete file references
- `Esc` - Close panels, cancel agent execution, clear prompt queue

## Next steps

- Learn about [CLI Commands](https://kiro.dev/docs/reference/cli-commands.md) for terminal usage
- Explore [Chat](https://kiro.dev/docs/cli/chat.md) for interactive chat features
- Check [Context Management](https://kiro.dev/docs/cli/chat/context.md) for advanced context handling
