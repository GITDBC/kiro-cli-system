> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# CLI commands

> Complete reference for all Kiro CLI commands

This page provides a comprehensive reference for all Kiro CLI commands and their arguments.

## Global arguments

These arguments work with any Kiro CLI command:

| Argument | Short | Description |
|----------|-------|-------------|
| `--verbose` | `-v` | Increase logging verbosity (can be repeated: `-v`, `-vv`, `-vvv`) |
| `--agent` | | Start a conversation using a specific custom agent configuration |
| `--v3` | | Start with the V3 agent harness for this invocation |
| `--help` | `-h` | Show help information |
| `--version` | `-V` | Show version information |
| `--help-all` | | Print help for all subcommands |

## Commands

### kiro-cli crew

Launch [Kiro Crew](https://github.com/kirodotdev/KiroCrew) or pass arguments to its command-line interface.

**Syntax:**
```bash
kiro-cli crew [--yes] [CREW_ARGUMENTS]...
```

On macOS and Linux, Kiro CLI prompts to install Crew when it isn't available. Kiro CLI consumes `--yes` or `-y` to install without the prompt. It forwards all other arguments after `crew` directly to Crew, without a `--` separator. On Windows, install Crew separately before using this command.

**Examples:**
```bash
# Start the Crew gateway to get started
kiro-cli crew gateway

# Install when needed, skip the prompt, and start the gateway
kiro-cli crew --yes gateway

# Forward a Crew option directly
kiro-cli crew --version
```

### kiro-cli agent

Manage agent configurations. Agent name is now a positional argument for create, edit, and other subcommands.

**Syntax:**
```bash
kiro-cli agent [SUBCOMMAND] [AGENT_NAME] [OPTIONS]
```

**Subcommands:**

| Subcommand | Description |
|------------|-------------|
| `list` | List the available agents |
| `create <name>` | Create an agent config (name is positional argument, v1.26.0+) |
| `edit [name]` | Edit an existing agent config (defaults to current agent if no name provided, v1.26.0+) |
| `validate` | Validate a config with the given path |
| `migrate` | Migrate profiles to agents (potentially destructive to existing agents) |
| `set-default` | Define a default agent to use when starting a session |

**Examples:**
```bash
kiro-cli agent list

# v1.26.0+: Agent name as positional argument
kiro-cli agent create my-agent
kiro-cli agent edit my-agent
kiro-cli agent edit  # Defaults to current agent

# Validate an agent config
kiro-cli agent validate --path ./my-agent.json
kiro-cli agent set-default my-agent
```

**New in v1.26.0:**
- Agent name is now a positional argument (e.g., `kiro-cli agent create my-agent` instead of `--name my-agent`)
- `edit` command defaults to editing the current agent when no argument is provided

### kiro-cli chat

Start an interactive chat session with Kiro. When no subcommand is specified, `kiro` defaults to `kiro-cli chat`.

**Syntax:**
```bash
kiro-cli chat [OPTIONS] [INPUT]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--no-interactive` | Print first response to STDOUT without interactive mode |
| `--resume` / `-r` | Resume the previous conversation from this directory |
| `--resume-picker` | Open interactive session picker to choose which session to resume |
| `--resume-id <ID>` | Resume a specific local or cloud session by its ID |
| `--cloud` | Run the V3 session in a managed cloud sandbox |
| `--repo <owner/repository>` | Add one or more comma-separated repositories to a V3 cloud session |
| `--list-sessions` | List all saved chat sessions for the current directory |
| `--list-models` | Display available models |
| `--delete-session <ID>` | Delete a saved chat session by ID |
| `--agent` | Specify which agent to use |
| `--v3` | Use the V3 agent harness for this session. Conflicts with `--agent-engine` |
| `--agent-engine <ENGINE>` | Agent harness for this session: `v3` or `v1`. Accepted on `kiro-cli chat` only, not at the root. In Kiro CLI 3.0.0 or later, `v1` selects the retired Classic interface and opens the Classic upgrade prompt |
| `--model <MODEL>` | Model for this session. Overrides the agent configuration's `model` value and `chat.defaultModel` |
| `--trust-all-tools` | Allow the model to use any tool without confirmation |
| `--trust-tools` | Pre-approve listed tools. Non-interactive V3 matches tool IDs and, in Kiro CLI 3.3.0 or later, `@server` references and `*`/`?` patterns; interactive V3 ignores the flag. See [Headless mode](https://kiro.dev/docs/cli/headless.md) |
| `--sandbox` | Require the local command sandbox for a V3 headless run. Use with `--no-interactive` or `--output-format stream-json` |
| `--require-mcp-startup` | Exit with code 3 if any MCP server fails to start |
| `--wrap` | Line wrapping mode: `always`, `never`, or `auto` (default) |
| `--effort <LEVEL>` | Set the initial reasoning effort level for the session: `low`, `medium`, `high`, `xhigh`, or `max` |
| `INPUT` | The first question to ask (positional argument) |

**Examples:**
```bash
# Start interactive chat
kiro-cli 

# Ask a question directly
kiro-cli chat "How do I list files in Linux?"

# Non-interactive mode with trusted tools
kiro-cli chat --no-interactive --trust-all-tools "Show me the current directory"

# Resume previous conversation
kiro-cli chat --resume

# Resume a specific session by ID
kiro-cli chat --resume-id abc123-def456

# Open session picker to choose which session to resume
kiro-cli chat --resume-picker

# List all saved sessions
kiro-cli chat --list-sessions

# List available models (plain text)
kiro-cli chat --list-models

# List available models (JSON output for scripting)
kiro-cli chat --list-models --format json

# Use specific agent
kiro-cli chat --agent my-agent "Help me with AWS CLI"

# Use the V3 harness for this session
kiro-cli chat --v3

# Set the initial reasoning effort level at launch
kiro-cli chat --effort high "Refactor this module for testability"
```

### kiro-cli acp

Start Kiro CLI as an [Agent Client Protocol](https://kiro.dev/docs/cli/acp.md) server for an editor or other ACP client. The client spawns this command and talks to it over standard input and output. `kiro-cli acp` is a hidden subcommand: it does not appear in `kiro-cli --help`.

**Syntax:**
```bash
kiro-cli acp [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--agent-engine <ENGINE>` | Agent harness for the server: `v3` or `v1`. Overrides the `acp.agentEngine` setting. In Kiro CLI 3.0.0 or later, when no harness is named the server starts V3 on a machine that can run it |
| `--auth-method <METHOD>` | Who answers access-token requests: `cli` (the default, your Kiro CLI login) or `client` (the client answers `_kiro/auth/getAccessToken`). Alias: `--authMethod`. V3 only; see [Start the CLI V3 server](https://kiro.dev/docs/cli/v3/acp-migration.md#1-start-the-cli-v3-server) |
| `--login` | Run the Kiro sign-in in the terminal, then exit without starting the server. Reconnect the ACP client after you sign in |
**Examples:**
```bash
# Serve an ACP client on the saved or default harness
kiro-cli acp

# Serve an ACP client on V3 and sign in through the client
kiro-cli acp --agent-engine v3 --auth-method client
```

### kiro-cli update

Update Kiro CLI to the latest version.

**Syntax:**
```bash
kiro-cli update [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--check` | Only check for updates without installing |
| `--force` | Install the advertised version even when the installed version is equal or newer (can reinstall or downgrade) |

If a package manager installed Kiro CLI, for example a deb or rpm package, `kiro-cli update` prints how to update with that package manager and installs nothing, even with `--force`.

On macOS and Linux, if you cannot write to the directory that holds Kiro CLI, `kiro-cli update` installs nothing and tells you to run `sudo kiro-cli update`.

**Examples:**
```bash
kiro-cli update
kiro-cli update --check
kiro-cli update --force
```

### kiro-cli integrations

Manage system integrations for Kiro. Available on macOS and Linux.

**Syntax:**
```bash
kiro-cli integrations <SUBCOMMAND> [OPTIONS] <INTEGRATION>
```

**Subcommands:**

| Subcommand | Description |
|------------|-------------|
| `install <integration>` | Install an integration (e.g., kiro-command-router) |
| `uninstall <integration>` | Uninstall an integration |
| `reinstall <integration>` | Reinstall an integration |
| `status <integration>` | Check integration status |

**Options:**
- `--silent` / `-s`: Suppress status messages (for `install`, `uninstall`, and `reinstall`)
- `--format` / `-f`: Output format (for status command)

Put options before the integration name.

**Examples:**
```bash
# Install kiro command router (v1.26.0+)
kiro-cli integrations install kiro-command-router

# Check integration status
kiro-cli integrations status kiro-command-router

# Uninstall silently
kiro-cli integrations uninstall --silent kiro-command-router
```

#### Kiro Command Router (v1.26.0+)

The kiro command router is a unified entry point that routes the `kiro` command between CLI and IDE based on your preference.

**Problem it solves:** By default, the `kiro` command launches Kiro IDE. Many users prefer it to launch the CLI since they use the app icon to open the IDE.

**Installation:**
```bash
# Install the router
kiro-cli integrations install kiro-command-router

# Set CLI as the default
kiro set-default cli

# Or set IDE as the default
kiro set-default ide
```

**After installation:**
- `kiro` - Launches your default (CLI or IDE)
- `kiro-cli` - Always launches CLI
- `kiro ide` - Always launches IDE

**Use cases:**
- CLI-focused workflows where you primarily use the terminal
- Quick access to CLI without typing `kiro-cli` every time
- Flexibility to switch defaults based on your current project or workflow

### kiro-cli login

Authenticate with Kiro CLI service using Builder ID, Identity Center, or social login (Google, GitHub).

**Syntax:**
```bash
kiro-cli login [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--license <TYPE>` | License type: `pro` (Identity Center) or `free` (Builder ID, Google, GitHub) |
| `--identity-provider <URL>` | Identity provider URL (for Identity Center) |
| `--region <REGION>` | AWS region (for Identity Center) |
| `--social <PROVIDER>` | Social provider: `google` or `github` |
| `--use-device-flow` | Force device flow (for remote/SSH environments) |
| `--verbose` | Increase logging verbosity (can be repeated) |
| `--help` | Print help information |

**Authentication Methods:**

**Local Environment:**
- Opens browser for unified auth portal
- Select authentication method interactively
- Login-selection flags (e.g., `--license`, `--social`) are generally ignored locally; the browser flow controls the method

**Remote Environment (SSH/Terminal):**
- Uses device flow automatically
- Shows device code and URL
- Complete authentication on another device
- CLI polls for completion
- In Kiro CLI 3.2.1 or later, `kiro-cli login` run at a terminal on a Linux host with no graphical session (neither `DISPLAY` nor `WAYLAND_DISPLAY` is set), such as a container, also uses the device flow. WSL keeps the browser flow

**Examples:**
```bash
# Basic login (opens browser locally, shows device code remotely)
kiro-cli login

# Identity Center login
kiro-cli login --license pro --identity-provider https://my-org.awsapps.com/start --region us-east-1

# Social login
kiro-cli login --social google

# Force device flow (useful for SSH sessions)
kiro-cli login --use-device-flow
```

**Troubleshooting:**

- **Already logged in error**: Logout first with `kiro-cli logout`
- **Browser doesn't open**: Use `--use-device-flow` flag
- **Authentication timeout**: Restart the login process
- **Identity Center fails**: Verify URL and region with your administrator

### kiro-cli logout

Sign out of Kiro CLI service and clear authentication credentials.

**Syntax:**
```bash
kiro-cli logout
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Increase logging verbosity (can be repeated) |
| `--help` | `-h` | Print help information |

**What Gets Cleared:**
- Authentication tokens
- Session credentials
- User profile information

**What's Preserved:**
- Agent configurations
- Saved conversations
- Settings
- MCP server configurations

**Example:**
```bash
kiro-cli logout
```

**Output:**
```
You are now logged out
Run kiro-cli login to log back in to Kiro CLI
```

**Note:** Logout is user-wide and affects all workspaces.

### kiro-cli whoami

Display information about the current user and authentication status, including your email address for Builder ID, IAM Identity Center, and Social login types.

**Syntax:**
```bash
kiro-cli whoami [OPTIONS]
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--format` | `-f` | Output format: `plain`, `json`, `json-pretty` |
| `--verbose` | `-v` | Increase logging verbosity (can be repeated) |
| `--help` | `-h` | Print help information |

**Output Information:**
- Username/user ID
- Authentication method (Builder ID, Identity Center, Social)
- Session status
- Profile information

**Examples:**
```bash
# Check current user
kiro-cli whoami
# Logged in with Builder ID
# Email: user@example.com

kiro-cli whoami --format json
kiro-cli whoami --format json-pretty
```

**Example Output (Identity Center):**
```
Logged in with IAM Identity Center (https://my-org.awsapps.com/start)

Profile:
Q-Dev-Amazon-Profile
arn:aws:codewhisperer:us-east-1:...:profile/...
```

**Example Output (Builder ID):**
```
Logged in with Builder ID

Profile:
builder-id-username
```

**Troubleshooting:**

- **Not logged in error**: Login with `kiro-cli login`

### kiro-cli settings

Manage kiro-cli configuration settings.

**Syntax:**
```bash
kiro-cli settings [SUBCOMMAND] [OPTIONS] [KEY] [VALUE]
```

**Arguments:**

| Argument | Short | Description |
|----------|-------|-------------|
| `--delete` | `-d` | Delete a setting |
| `--format` | `-f` | Output format: `plain`, `json`, `json-pretty` |
| `KEY` | | Setting key (positional) |
| `VALUE` | | Setting value (positional) |

**Subcommands:**

| Subcommand | Description |
|------------|-------------|
| `open` | Open settings file in default editor |
| `list` | List configured settings |
| `list --all` | List all available settings with descriptions |

**Examples:**
```bash
# View all settings
kiro-cli settings list

# View all available settings
kiro-cli settings list --all

# Get a specific setting
kiro-cli settings telemetry.enabled

# Set a setting
kiro-cli settings telemetry.enabled true

# Delete a setting
kiro-cli settings --delete chat.defaultModel

# Open settings file
kiro-cli settings open

# JSON output
kiro-cli settings list --format json-pretty
```

### kiro-cli diagnostic

Generate a system information report for troubleshooting.

**Syntax:**
```bash
kiro-cli diagnostic [OPTIONS]
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--format` | `-f` | Output format: `plain`, `json`, `json-pretty` (default: `plain`) |
| `--force` | | Accepted for compatibility. Has no effect |
| `--verbose` | `-v` | Increase logging verbosity (can be repeated) |
| `--help` | `-h` | Print help information |

The `plain` format outputs TOML.

**Output Information:**

The diagnostic report includes:
- Kiro CLI version, build hash, and build date
- System information (OS, chip, core count, memory)
- Environment (current directory, Kiro CLI path, install method, and the `in-ssh`, `in-ci`, `in-wsl`, and `in-codespaces` flags, each shown only when true)
- Cloud session settings
- Kiro CLI environment variables, plus shell and display variables such as `PATH`, `SHELL`, and `TERM`

The report replaces your username in paths with `USER`.

**Examples:**
```bash
# Generate a diagnostic report
kiro-cli diagnostic

# JSON output
kiro-cli diagnostic --format json-pretty
```

**Example Output (excerpt):**
```toml
[q-details]
version = "1.23.0"
hash = "97d58722cd90f6d3dda465f6462ee4c6dc104b22"
date = "2025-12-18T16:49:27.015389Z (4d ago)"

[system-info]
os = "macOS 15.7.1 (24G231)"
chip = "Apple M1 Pro"
total-cores = 10
memory = "32.00 GB"

[environment]
cwd = "/Users/USER/project"
cli-path = "/Users/USER/.local/bin/kiro-cli"
install-method = "unknown"

[env-vars]
PATH = "..."
SHELL = "/bin/zsh"
TERM = "xterm-256color"
```

**Troubleshooting:**

- **Permission errors**: Run with appropriate permissions or ignore errors

**Use Cases:**
- Troubleshooting installation issues
- Providing information to support
- Verifying environment configuration

### kiro-cli issue

Create a GitHub issue for feedback or bug reports.

**Syntax:**
```bash
kiro-cli issue [OPTIONS] [DESCRIPTION...]
```

**Arguments:**

| Argument | Short | Description |
|----------|-------|-------------|
| `--force` | `-f` | Force issue creation |
| `DESCRIPTION` | | Issue description (positional) |

**Examples:**
```bash
kiro-cli issue
kiro-cli issue "Chat session fails to resume after restart"
```

### kiro-cli version

Display version information and changelog.

**Syntax:**
```bash
kiro-cli version [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--changelog` | Show changelog for current version |
| `--changelog=all` | Show changelog for all versions |
| `--changelog=x.x.x` | Show changelog for specific version |

**Examples:**
```bash
kiro-cli version
kiro-cli version --changelog
kiro-cli version --changelog=all
kiro-cli version --changelog=1.5.0
```

### kiro-cli mcp

Manage Model Context Protocol (MCP) servers.

**Syntax:**
```bash
kiro-cli mcp [SUBCOMMAND] [OPTIONS]
```

**Subcommands:**

#### kiro-cli mcp add

Add or replace a configured MCP server.

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--name` | Server name (required) |
| `--command` | Launch command (required) |
| `--scope` | Scope: `workspace` or `global` |
| `--env` | Environment variables: `key1=value1,key2=value2` |
| `--timeout` | Launch timeout in milliseconds |
| `--force` | Overwrite existing server |

**Example:**
```bash
kiro-cli mcp add --name my-server --command "node server.js" --scope workspace
```

#### kiro-cli mcp remove

Remove an MCP server.

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--name` | Server name (required) |
| `--scope` | Scope: `workspace` or `global` |

**Example:**
```bash
kiro-cli mcp remove --name my-server --scope workspace
```

#### kiro-cli mcp list

List configured MCP servers.

**Syntax:**
```bash
kiro-cli mcp list [SCOPE]
```

**Example:**
```bash
kiro-cli mcp list
kiro-cli mcp list workspace
kiro-cli mcp list global
```

#### kiro-cli mcp import

Import server configuration from a file.

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--file` | Configuration file (required) |
| `--force` | Overwrite existing servers |
| `SCOPE` | Scope: `workspace` or `global` |

**Example:**
```bash
kiro-cli mcp import --file config.json workspace
```

#### kiro-cli mcp status

Get the status of an MCP server.

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--name` | Server name (required) |

**Example:**
```bash
kiro-cli mcp status --name my-server
```

## Session management

Kiro CLI automatically saves all chat sessions on every conversation turn. You can resume from any previous chat session at any time.

### From the command line

```bash
# Resume the most recent chat session
kiro-cli chat --resume

# Interactively pick a chat session to resume
kiro-cli chat --resume-picker

# List all saved chat sessions for the current directory
kiro-cli chat --list-sessions

# Delete a saved chat session
kiro-cli chat --delete-session <SESSION_ID>
```

### From within a chat session

Use the `/chat` command to manage sessions:

```bash
# Start a fresh conversation (saves current session automatically)
/chat new

# Start a fresh conversation with an initial prompt
/chat new <PROMPT>

# Resume a chat session (interactive selector)
/chat resume

# Save current V3 session to a zip archive
/chat save <FILE_PATH>.zip

# Load a V3 session archive
/chat load <FILE_PATH>.zip
```

In V3, `/chat save` writes a zip session archive and `/chat load` reads that archive.

### Custom session storage

You can use custom scripts to control where chat sessions are saved to and loaded from. This allows you to store sessions in version control systems, cloud storage, databases, or any custom location.

```bash
# Save session via custom script (receives JSON via stdin)
/chat save-via-script <SCRIPT_PATH>

# Load session via custom script (outputs JSON to stdout)
/chat load-via-script <SCRIPT_PATH>
```

**Tips:**
- Session IDs are UUIDs that uniquely identify each chat session
- Sessions are stored per directory, so each project has its own set of sessions
- The most recently updated sessions appear first in the list

## Log files

Kiro CLI maintains log files for troubleshooting:

**Locations:**
- **macOS**: `$TMPDIR/kiro-log/`
- **Linux**: `$XDG_RUNTIME_DIR` or `/tmp/kiro-log/`

**Environment Variables:**

Control logging, the Kiro home directory, and the runtime directory with these environment variables:

| Variable | Values | Description |
|----------|--------|-------------|
| `KIRO_HOME` | path | Override the global Kiro directory used for MCP configuration and sign-ins, permissions, sessions, Powers, settings, custom agents, Skills, Steering, Workflows, and other V3 agent state |
| `KIRO_RUNTIME_DIR` | absolute path | Extract the bundled runtime to this directory instead of the home directory. A relative value is ignored |
| `KIRO_LOG_LEVEL` | `error`, `warn`, `info`, `debug`, `trace` | Set logging verbosity (default: `error`) |
| `KIRO_LOG_NO_COLOR` | `1`, `true`, `yes` | Disable colored log output (v1.26.0+) |

**Log Levels:**

Set via `KIRO_LOG_LEVEL` environment variable:

- `error`: Only errors (default)
- `warn`: Warnings and errors
- `info`: Info, warnings, and errors
- `debug`: Debug info and above
- `trace`: All messages including detailed traces

**Examples:**
```bash
# Enable debug logging
export KIRO_LOG_LEVEL=debug
kiro-cli chat

# Disable colored output (useful for CI/CD, v1.26.0+)
export KIRO_LOG_NO_COLOR=1
kiro-cli chat

# Combined
export KIRO_LOG_LEVEL=debug
export KIRO_LOG_NO_COLOR=true
kiro-cli chat

# For fish shell
set -x KIRO_LOG_LEVEL debug
set -x KIRO_LOG_NO_COLOR 1
kiro-cli chat
```

**New in v1.26.0:** `KIRO_LOG_NO_COLOR` environment variable to disable colored log output, useful for CI/CD pipelines and log file processing.

**Warning:** Log files may contain sensitive information including file paths, code snippets, and command outputs. Be cautious when sharing logs.

## Next steps

- [Slash Commands Reference](https://kiro.dev/docs/reference/slash-commands.md)
- [Settings Configuration](https://kiro.dev/docs/reference/settings.md)
- [Setup and troubleshooting](https://kiro.dev/docs/cli/setup.md)
