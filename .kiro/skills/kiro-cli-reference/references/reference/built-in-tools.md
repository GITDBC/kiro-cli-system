> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Built-in tools

> Explore Kiro CLI's built-in tools for enhanced terminal productivity

Kiro CLI includes a collection of built-in tools that enhance your terminal experience with AI-powered assistance for common development tasks.

**ℹ️ Info:** This page documents the CLI 2.x tool identifiers and `toolsSettings` configuration. For the CLI V3 tool catalog and tag-based configuration, see [Tools](https://kiro.dev/docs/tools.md). The CLI 2.x structured AWS tool used the internal name `use_aws` and preferred alias `aws`; it is not a V3 built-in. Connect an AWS MCP server instead.

## File read
**Tool name**: `read`

**Aliases**: `fs_read`, `fsRead`

**Description**: Reads files, folders and images

```bash
> what dependencies does my application have

Reading file: src/snake/package.json, all lines (using tool: read)
 ✓ Successfully read 1417 bytes from src/snake/package.json
 - Completed in 0.86s

> Your application has:

Runtime Dependencies:
- typescript (^3.5.1) - TypeScript compiler
- gh-pages (^2.0.1) - GitHub Pages deployment

Dev Dependencies:
- sass (^1.20.3) - CSS preprocessing
- eslint (^5.16.0) + TypeScript plugins - Code linting
- jest (^29.5.0) + ts-jest - Testing framework

No external game libraries or frameworks.
```

You can also configure the `read` tool in the agent configuration to have specific access to the files and folders in your project, giving you granular control over what the Kiro can read. 

```json
{
  "toolsSettings": {
    "read": {
      "allowedPaths": ["~/projects", "./src/**"],
      "deniedPaths": ["d1/denied/path/", "d2/denied/path/**/file.txt"]
    }
  }
}
```

### Configuration options

| Option | Type | Required | Description |
|--------|------|---------|-------------|
| `allowedPaths` | array of paths | No | Paths that can read without prompting. |
| `deniedPaths` | array of paths | No | Paths that are denied. |

Path values can be glob patterns similar to the behavior as gitignore. For example, `~/temp` would match `~/temp/child` and `~/temp/child/grandchild` 

## Glob

**Tool name**: `glob`

**Description**: Fast file discovery using glob patterns. Respects `.gitignore`. Prefer this over `find` command in bash.

```bash
> find all TypeScript test files in my project

Finding files matching pattern: **/*.test.ts (using tool: glob)

 ✓ Found 8 files
 - Completed in 0.12s

> Here are the TypeScript test files:

src/utils/helpers.test.ts
src/utils/validators.test.ts
src/components/button.test.ts
src/components/header.test.ts
src/services/auth.test.ts
src/services/api.test.ts
src/hooks/useAuth.test.ts
src/hooks/useForm.test.ts
```

You can configure the `glob` tool in the agent configuration to control which paths can be searched.

```json
{
  "toolsSettings": {
    "glob": {
      "allowedPaths": ["~/projects", "./src/**"],
      "deniedPaths": ["/etc", "/var"],
      "allowReadOnly": true
    }
  }
}
```

### Configuration options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `allowedPaths` | array of strings | `[]` | List of paths that can be searched without prompting. Supports glob patterns |
| `deniedPaths` | array of strings | `[]` | List of paths that are denied. Deny rules are evaluated before allow rules |
| `allowReadOnly` | boolean | `false` | Whether to allow searches anywhere without prompting |

## Grep

**Tool name**: `grep`

**Description**: Fast content search using regex. Respects `.gitignore`. Use this instead of `grep`, `rg`, or `ag` commands in bash.

```bash
> find all TODO comments in my project

Searching for pattern: TODO (using tool: grep)

 ✓ Found 12 matches across 5 files
 - Completed in 0.34s

> Here are the TODO comments I found:

src/utils/helpers.ts:23
  // TODO: Add error handling for edge cases

src/components/header.tsx:45
  {/* TODO: Implement mobile navigation */}

src/api/routes.ts:12
  // TODO: Add rate limiting
  // TODO: Implement caching

src/services/auth.ts:78
  // TODO: Add refresh token logic

...
```

You can configure the `grep` tool in the agent configuration to control which paths can be searched.

```json
{
  "toolsSettings": {
    "grep": {
      "allowedPaths": ["~/projects", "./src/**"],
      "deniedPaths": ["/etc", "/var"],
      "allowReadOnly": true
    }
  }
}
```

### Configuration options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `allowedPaths` | array of strings | `[]` | List of paths that can be searched without prompting. Supports glob patterns |
| `deniedPaths` | array of strings | `[]` | List of paths that are denied. Deny rules are evaluated before allow rules |
| `allowReadOnly` | boolean | `false` | Whether to allow searches anywhere without prompting |

## File write

**Tool name**: `write`

**Aliases**: `fs_write`, `fsWrite`

**Description**: Tool for creating and editing files

``` bash
> collect best practices for writing typescript code and save it to the kiro steering folder as codingpractices.md

I'll create the following file: src/snake/.kiro/steering/codingpractices.md (using tool: write)
Purpose: Create TypeScript coding best practices document

+     1: # TypeScript Coding Best Practices
+     2: 
+     3: ## Type Safety
+     4: - Enable strict mode in `tsconfig.json` (`strict: true`)
+     5: - Avoid `any` type - use `unknown` for truly dynamic types
+     6: - Use explicit return types for functions
+     7: - Leverage type inference where it improves readability
+     8: - Use union types instead of enums when possible
+     9: - Prefer `interface` for object shapes, `type` for unions/intersections
+    10: 
+    11: ## Code Organization
+    12: - One class/interface per file (exceptions for small related types)
+    13: - Group related functionality into modules
+    14: - Use barrel exports (`index.ts`) for clean imports
+    15: - Keep functions small and focused (single responsibility)
+    16: - Separate business logic from presentation logic
```

You can also configure the `write` tool in the agent configuration to have specific access to the files and folders in your project, giving you granular control over what the Kiro can write to. 

```json
{
  "toolsSettings": {
    "write": {
      "allowedPaths": ["~/projects/output.txt", "./src/**"],
      "deniedPaths": ["/d1/denied/path/", "/d2/denied/path/**/file.txt"]
    }
  }
}
```

### Custom diff tools

By default, the write tool displays code changes using a built-in inline diff. You can configure an external diff tool to view changes instead. See [Custom diff tools](https://kiro.dev/docs/cli/chat/diff-tools.md) for setup instructions and supported tools.

### Configuration options

| Option | Type | Required | Description |
|--------|------|---------|-------------|
| `allowedPaths` | array of paths | No | Paths that can be written to without prompting. |
| `deniedPaths` | array of paths | No | Paths that are denied. |

Path values can be glob patterns similar to the behavior as gitignore. For example, `~/temp` would match `~/temp/child` and `~/temp/child/grandchild` 

## Execute shell commands

**Tool name**: `shell`

**Aliases**: `execute_bash`, `execute_cmd`

**Description**: Tool for executing a specified bash command.

You can also configure the `shell` tool in the agent configuration to control what commands Kiro can execute. 

``` json
{
  "toolsSettings": {
    "shell": {
      "allowedCommands": ["git status", "git fetch"],
      "deniedCommands": ["git commit .*", "git push .*"],
      "autoAllowReadonly": true
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| allowedCommands | 	array of strings | [] | List of commands that are allowed without prompting  |
| deniedCommands |	array of strings | [] |	 List of commands that are denied. Deny rules are evaluated before allow rules |
| autoAllowReadonly |	boolean | 	false | When enabled, read-only commands are allowed without prompting. This parameter does not restrict write actions. |
| denyByDefault |	boolean | 	false |	When true, deny any command outside allowedCommands and not auto-approved by `autoAllowReadonly`, instead of prompting for approval |

**Note**: `allowedCommands` and `deniedCommands` support regex formatting. regex entered are anchored with \A and \z, and does NOT support look-around, including look-ahead and look-behind.

**⚠️ Environment variables can change what a command runs:** Kiro CLI does not control the environment variables that a command sets. A variable assignment in front of a command can make a read-only program run another program.

Kiro CLI asks for approval when a command sets a variable from its list of known dangerous variables. That list cannot include every variable that every tool reads. An `allowedCommands` pattern that matches text before the program name, such as `.*git diff`, also matches commands with variable assignments.

You are responsible for the commands that you let Kiro CLI run without approval. If the agent works in a repository that you do not trust, keep `autoAllowReadonly` off and review each command before you approve it.

This note applies to the `shell` settings on this page. It does not apply to V3 (`kiro-cli --v3`), which uses permission rules instead of `toolsSettings`. For details, see [Permissions migration](https://kiro.dev/docs/cli/v3/permissions.md).

### Side channels for wrapper scripts

When the agent runs a shell command, Kiro CLI exports two environment variables that point to per-invocation FIFOs. Wrapper scripts can write to them to route output independently of stdout:

| Variable | Captured in tool result? | Streamed to the TUI? | Use for |
|----------|-------------------------|----------------------|---------|
| `AGENT_DISPLAY_OUT` | No | Yes | User-facing output that shouldn't bloat the agent's context, like a verbose build log whose summary is already on stdout |
| `AGENT_CONTEXT_OUT` | Yes (as `agent_notes`) | Yes | Messages the agent needs to see but that wouldn't reliably reach it through stdout, such as when the user pipes stdout through `grep` or `tail` |

Lines written to `$AGENT_CONTEXT_OUT` surface in the tool result's `agent_notes` field, so the agent can read them alongside stdout and stderr. Lines written to `$AGENT_DISPLAY_OUT` only reach the TUI.

Example wrapper:

```bash
#!/usr/bin/env bash
# Run a verbose build, show the log to the user, and tell the agent where it ended up.
./gradlew build 2>&1 | tee "$AGENT_DISPLAY_OUT"
echo "Build finished. Full log at ./build/reports/build.log" > "$AGENT_CONTEXT_OUT"
echo "ok"  # plain stdout — captured normally
```

Both variables are only set when the agent is driving the command; wrappers should fall back gracefully if the variable is empty (for example, test with `[ -n "$" ]`).

## Execute AWS commands (CLI 2.x legacy)

**Internal tool name**: `use_aws`

**Preferred alias**: `aws`

**Description**: Tool for making AWS CLI calls with the specified service, operation, and parameters

``` bash
 list my s3 buckets

Running aws cli command (using tool: aws):

Service name: s3api
Operation name: list-buckets
Parameters: 
Region: us-east-1
Label: List all S3 buckets
```

You can also configure the `aws` tool in the agent configuration to only perform specific AWS operations.  

```json
{
  "toolsSettings": {
    "aws": {
      "allowedServices": ["s3", "lambda", "ec2"],
      "deniedServices": ["eks", "rds"],
      "autoAllowReadonly": true
    }
  }
}
```

## Web search and fetch

Web access capabilities enable Kiro agent to access current information from the internet in real-time. This feature enables you to get up-to-date answers about topics that may have changed since the model's training data was created. These tools have been designed to not reproduce meaningful chunks of text and work with publicly accessible webpages. Search results may vary over time as internet content changes.

| Tool | Description | 
| --- | --- | 
| `web_search` | Tool for searching the web | 
| `web_fetch` | Tool for fetching content from a URL |

**⚠️ Important:** You are responsible for your use of output that incorporates web search or grounded information. You will know when your output includes grounded information from citations or links to the source material. You must retain and display these citations and links in the output if you display the grounded output to a downstream user. If you don't want Kiro to use these tools, create a custom agent that [excludes](https://kiro.dev/docs/custom-agents/configuration-reference.md#tools-field) these tools. Citations are provided for output that incorporates web search or grounded information. You can follow a provided citation to the source page.


```bash

# Example 1
> What is the latest on EC2 instances?

> I'll search for the latest information on EC2 instances.
Searching the web for: AWS EC2 instances latest 2025 (using tool: web_search)

 ✓ Found 10 search results
 - Completed in 2.12s

> Here's what I found:

Recent EC2 Instance Launches (2025):

New Instance Families:
- **M8a instances** - General-purpose instances with 5th Gen AMD EPYC (Turin) processors running at 4.5GHz. They deliver up to 30% higher performance and 19% better price-performance versus M7a instances.

- **C8gd, M8gd, R8gd instances** - Graviton-based instances with up to 11.4 TB of local NVMe SSD storage, now generally available.

- **X8g instances** - Powered by AWS Graviton4 processors, delivering up to 60% better performance than X2gd instances. Available in US East (Ohio).

- **R8i and R8i-flex instances** - Intel-based memory-optimized instances offering up to 15% better price-performance and 2.5x more memory bandwidth compared to previous Intel generations. They deliver 20% better performance than R7i 
instances.

- **I7i instances** - Storage-optimized instances with 5th Gen Intel Xeon processors, delivering up to 23% better compute performance and 10% better price-performance over I4i instances.

Expanded Availability:
- C7i-flex and M7i-flex now available in 12xlarge and 16xlarge sizes
- Various instances expanding to additional regions including Europe (Milan) and US West (N. California)

Key Trend: AWS continues focusing on performance improvements (20-30% gains), better price-performance (10-19% improvements), and expanding processor options across Intel, AMD, and Graviton architectures.

References:
[1] Document history for the Amazon EC2 Instance Types Guide - https://docs.aws.amazon.com/ec2/latest/instancetypes/doc-history.html
... 
[10] Amazon EC2 C7i-flex and C7i instances are now available in 2 additional regions - https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-ec2-c7i-flex-c7i-instances-additional-...
 ▸ Time: 19s


# Example 2
> What is the latest on t3 medium instance pricing.

Searching the web for: AWS EC2 t3.medium instance pricing 2025 (using tool: web_search)

 ✓ Found 10 search results
 - Completed in 1.596s

Fetching content from: https://aws.amazon.com/ec2/pricing/on-demand/ (searching for: t3.medium price cost) [mode: selective] (using tool: web_fetch)

 ✓ Fetched 11395 bytes (selective) from URL
 - Completed in 0.718s

> The page doesn't show specific pricing in the excerpt. Let me get the actual pricing information:
Fetching content from: https://instances.vantage.sh/aws/ec2/t3.medium (searching for: t3.medium $0.04) [mode: selective] (using tool: web_fetch)

 ✓ Fetched 3971 bytes (selective) from URL
 - Completed in 0.780s

> Here's what I found:

AWS EC2 t3.medium Instance Pricing (2025):

...
```

To optimize retrieving content from a URL and better manage your context window, `web_fetch` tool has "Selective" and "Truncated" modes. 

```bash
# Example - using truncated
>  https://kiro.dev/blog/introducing-kiro-cli/ --> Can you get some of this page for me?

Fetching content from: https://kiro.dev/blog/introducing-kiro-cli/ [mode: truncated] (using tool: web_fetch)

 ✓ Fetched 8051 bytes (truncated content) from URL
 - Completed in 0.521s

> I've fetched the beginning portion of the page. It's a blog post announcing Kiro CLI. Here's what this section covers:

Title: "Bring Kiro agents to your terminal with Kiro CLI" (November 17, 2025)

Main Points:
- Kiro CLI brings AI agents into your terminal so you don't lose context when debugging production servers or working in SSH sessions
- Built on Q Developer CLI technology with additions like social login, Haiku 4.5, and the Auto agent
- Supports custom agents tailored to specific workflows (backend, frontend, DevOps)
- Your .kiro folder configs work in both IDE and CLI

Installation:
bash
curl -fsSL https://cli.kiro.dev/install | bash


Key Features covered in this section:
1. Custom agents with pre-approved tools, persistent context, and controlled access
2. Smart context management (Agent Resources, Session Context, Knowledge Bases)
3. Multiple authentication options (GitHub, Google, AWS Builder ID, IAM Identity Center)
4. Full IDE integration - MCP servers and steering rules transfer seamlessly
5. Interactive chat, multimodal input, and MCP support

The page continues beyond what was fetched. Would you like me to get a specific section or search for particular information?

```

In this case, since no specific pointers on the type of content to retrieve was provided, the tool automatically only retrieves part of the page (up to 8KB) to manage the context window.

```bash
# Example - using selective 

> https://kiro.dev/blog/introducing-kiro-cli/ --> Can you get installation information from this page for me.

Fetching content from: https://kiro.dev/blog/introducing-kiro-cli/ (searching for: installation install getting started) [mode: selective] (using tool: web_fetch)

 ✓ Fetched 7909 bytes (selective) from URL
 - Completed in 0.434s

> Here's the installation information from the page:

## Installation

Kiro CLI is available for macOS and Linux. Installation is straightforward:

bash
curl -fsSL https://cli.kiro.dev/install | bash


## First Steps

1. Authenticate and start chatting: Sign in with your credentials

2. Explore commands: Get help anytime

The page also mentions at the end:

bash
curl -fsSL https://cli.kiro.dev/install | bash


That's the single command you need to install Kiro CLI on macOS or Linux systems.
```

In this case, since the prompt was specific, the tool only retrieves selected content from the page. 

### Fetch modes

| Mode | Behavior | Use case |
|------|----------|----------|
| `selective` (default) | Returns 10 sentences before/after search term matches; 20 sentences if no matches | Targeted extraction |
| `truncated` | First 8000 characters | Quick preview |
| `full` | Complete content (up to 10MB) | Comprehensive analysis |

### Configuration

Configure URL-based permissions using `toolsSettings`:

```json
{
  "toolsSettings": {
    "web_fetch": {
      "trusted": [".*docs\\.aws\\.amazon\\.com.*", ".*github\\.com.*"],
      "blocked": [".*pastebin\\.com.*"]
    }
  }
}
```

| Option | Type | Description |
|--------|------|-------------|
| `trusted` | array of regex | URL patterns to auto-allow without prompting |
| `blocked` | array of regex | URL patterns to deny (takes precedence over trusted) |

**Pattern behavior:**
- Patterns are regex, automatically anchored with `^` and `$`
- `blocked` takes precedence over `trusted`
- Invalid regex in `blocked` denies all URLs (fail-safe)
- Invalid regex in `trusted` are skipped

**ℹ️ Info:** `trusted` and `blocked` patterns are enforced in the terminal UI (the default) as well as the classic interface. A blocked URL is denied and a trusted URL is auto-allowed regardless of which interface you run.

### Limitations

- **Size**: 10MB maximum per page fetch
- **Timeout**: 30 seconds per request
- **Redirects**: Maximum 10 redirects followed
- **Content type**: Only text/html pages supported
- **Retries**: 3 automatic retry attempts on failure

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Fetch failed | Page >10MB, timeout, too many redirects, or binary content | Try different URL or check page accessibility |
| Empty content | Search terms don't match page content | Use different search terms or `truncated`/`full` mode |
| URL blocked | URL matches `blocked` pattern | Remove pattern from `toolsSettings` |
| Tool requires approval | URL not in `trusted` patterns and `web_fetch` not in `allowedTools` | Add URL pattern to `trusted` or add `web_fetch` to `allowedTools` |
| `web_search` and `web_fetch` not available | Web tools disabled by enterprise administrator | Contact your administrator to enable web tools |

## Introspect Kiro CLI capabilities

**Tool name**: `introspect`

**Description**: Provides self-awareness for Kiro CLI by answering questions about its features, commands, and functionality using official documentation.

The introspect tool activates automatically when you ask Kiro CLI questions about itself. It searches built-in documentation to provide accurate answers about commands, settings, tools, and features.

```bash
> How do I save conversations?

Introspecting to get you the right information (using tool: introspect) - Completed in 0.68s

> You can save conversations using `/chat save <PATH>`:

- `/chat save ~/conversation.json` - Save to a specific path

Load saved conversations later with `/chat load <PATH>`.
```

### How it works

By default, introspect uses semantic search:

1. Downloads embedding models
2. Uses semantic search to find relevant documentation
3. Returns matched docs directly

For enterprise environments where model downloads may be blocked, enable progressive mode:

```bash
kiro-cli settings set introspect.progressiveMode true
```

Progressive mode skips the model download and returns the documentation index instead. The LLM then fetches specific docs as needed.

**ℹ️ Info:** Progressive mode may require multiple introspect calls to retrieve all relevant information, which can be slower than semantic search.

### What it provides

- **Command help**: Real-time documentation for all slash commands (`/chat`, `/context`, `/agent`, etc.)
- **Feature guides**: Information about capabilities like MCP, hooks, steering, and custom agents
- **Settings reference**: All configuration options and how to change them
- **Tool documentation**: Details about built-in tools and their configuration

### Example questions

```bash
> What experimental features does Kiro CLI have?
> Can Kiro CLI read and write files?
> How do I configure MCP servers?
> What settings are available?
```

### Configuration

Enable automatic [tangent mode](https://kiro.dev/docs/cli/experimental/tangent-mode.md) for introspect questions to keep help conversations separate from your main work:

```bash
kiro-cli settings set introspect.tangentMode true
```

**ℹ️ Info:** Be explicit when asking about Kiro CLI — ask "How does Kiro CLI handle files?" rather than "How do you handle files?" for more accurate responses. Despite safeguards, the AI may occasionally provide inaccurate information, so always verify important details using the documentation links provided in responses.

## Code intelligence

**Tool name**: `code`

**Description**: Provides code intelligence capabilities including symbol search, LSP integration, and pattern-based code search and rewriting.

```bash
> Find the UserRepository class

Searching for symbols matching: "UserRepository" (using tool: code)

 ✓ Found 1 match
 - Completed in 0.45s

> Found:
  Class UserRepository at src/repositories/user.repository.ts:15:1
```

For comprehensive documentation on code intelligence features, see [Code Intelligence](https://kiro.dev/docs/tools/code-intelligence.md).

This tool has no configuration options.

### Permissions

Symbol lookups and code edits inside your current workspace run without prompting. Anything targeting files **outside the workspace** requires your approval first, which prevents accidental reads or writes against credentials, system configs, or other projects on disk.

## Tool Search (V2)

**Tool name**: `tool_search`

**Description**: Find and load MCP tools on demand instead of sending every tool definition with each request.

This legacy tool is available in V2 sessions when Tool Search is enabled. Kiro CLI 2.31 and later local V3 sessions load MCP tools automatically through `tool_load` and `tool_call`. See [Tool Search](https://kiro.dev/docs/mcp/tool-search.md) for availability and settings.

### Parameters

The V2 `tool_search` tool accepts these parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tool_id` | string | One of `tool_id` or `query` | Exact tool identifier in `server_name::tool_name` format |
| `query` | string | One of `tool_id` or `query` | Keywords to search for matching tools |
| `max_results` | integer | No | Maximum results to return (default: 5) |

Provide exactly one of `tool_id` or `query`, not both. Matched tools become available to the agent.

## Delegate tasks

**Tool name**: `delegate`

**Description**: Delegate tasks to background agents that run asynchronously. Useful for long-running tasks that don't need immediate results.

```bash
> Analyze all TypeScript files for potential bugs and create a report

Delegating task to background agent (using tool: delegate)

 ✓ Task delegated successfully
 - Agent ID: agent-abc123
 - Check status with /delegate status

> I've started analyzing your TypeScript files in the background. 
  Use /delegate status to check progress.
```

This tool has no configuration options.

## Submit an issue or feature request

**Tool name**: `report`

**Description**: Opens the browser to a pre-filled GitHub issue template to report chat issues, bugs, or feature requests.

This tool has no configuration options.

## Knowledge tool (experimental)

**Tool name**: `knowledge`

**Description**: Store and retrieve information in a knowledge base across chat sessions. Provides semantic search capabilities for files, directories, and text content.

This tool has no configuration options.

## Thinking tool (experimental)

**Tool name**: `thinking`

**Description**: An internal reasoning mechanism that improves the quality of complex tasks by breaking them down into atomic actions.

This tool has no configuration options.

## ToDo list tool (experimental)

**Tool name**: `todo`

**Description**: 

Create and manage ToDo lists for tracking multi-step tasks. 

This tool has no configuration options.

## Goal tool

**Tool name**: `goal`

**Description**: Lets the agent report that the goal you set with `/goal` is complete. Only you create or clear a goal: `/goal <description> [--max <N>]` starts the loop (default 5 iterations, ceiling 50) and `/goal clear` cancels it. The agent cannot set a goal with this tool.

The tool has one command, `complete`, which takes a `summary` of what was accomplished and how it was verified. Until the agent calls it, the goal loop re-prompts the agent at the start of each iteration. See [Goal](https://kiro.dev/docs/cli/chat/goal.md) for usage documentation.

```bash
> /goal refactor the auth module to use JWT tokens and ensure all tests pass
goal set: "refactor the auth module to use JWT tokens and ensure all tests pass" (max 5)

[Agent implements changes, runs the tests, then calls goal complete with a summary]

 ✓ Goal complete
```

In CLI V3, `/goal` is a command behind the Workflows opt-in and does not use this tool.

This tool has no configuration options.

## Session settings tool

**Tool name**: `session`

**Description**: Temporarily override CLI settings for the current session without modifying your config files. All session overrides are stored in memory and reset when the session ends.

You can ask the agent to adjust settings conversationally:

- "Disable markdown rendering for this session"
- "Switch to compact UI mode"
- "Turn on the thinking tool"

The agent can perform four operations:

| Operation | Description |
|-----------|-------------|
| `list` | Show all settings with non-default values |
| `get` | Read the current value of a specific setting |
| `set` | Override a setting for the current session |
| `reset` | Reset a single setting or all session overrides |

Only settings marked as session-safe can be modified through this tool. The `set` and `reset` operations always require your confirmation before applying.

This tool has no configuration options.

## Subagent tool

**Tool name**: `subagent`

**Aliases**: `use_subagent`

**Description**: Delegate complex tasks to specialized subagents that run in parallel with isolated context. Useful for breaking down multi-step tasks into parallel subtasks, preventing context window bloat, running independent research simultaneously, or delegating to different agent configurations.

**ℹ️ Custom agent configuration:** This tool is included in the default agent. For custom agents, you need to explicitly add `subagent` to your `tools` array or include it via the `@builtin` sigil.

**Features:**
- Spawn multiple subagents simultaneously for parallel task execution
- Each subagent operates with its own isolated context to prevent main conversation bloat
- Real-time visual indicator showing status of all running subagents
- Support for different agent configurations per subagent
- Automatic execution summary with tool usage and duration metrics

### Configuration

The `subagent` tool supports the following `toolsSettings`:

| Setting | Type | Description |
|---------|------|-------------|
| `availableAgents` | `string[]` | Restrict which agents can be spawned as subagents. Supports glob patterns (e.g., `docs-*`). |
| `trustedAgents` | `string[]` | Allow specific agents to run without permission prompts. Supports glob patterns. |

```json
{
  "toolsSettings": {
    "subagent": {
      "availableAgents": ["reviewer", "tester", "analyzer", "docs-*"],
      "trustedAgents": ["reviewer", "tester"]
    }
  }
}
```

Subagents can also use different agent configurations:

- **Default subagent**: Uses the built-in default agent configuration
- **Custom subagents**: Can reference custom agent configurations by name when delegating tasks

The subagent inherits its tool access, permissions, and behavior from whichever agent configuration it's assigned to use.

### Example workflow

```bash
> Research the top 3 JavaScript frameworks and compare their performance

# Main agent spawns 3 subagents:
# - Subagent 1: Research React performance metrics
# - Subagent 2: Research Vue.js performance metrics
# - Subagent 3: Research Angular performance metrics

# Each subagent:
# - Conducts independent research
# - Gathers relevant data
# - Calls summary tool with findings

# Main agent receives all summaries and synthesizes comparison
```

For details on how subagents work and best practices, see [Subagents](https://kiro.dev/docs/custom-agents/subagents.md).

## Using tool settings in agent configuration

Tool settings are specified in the `toolsSettings` section of the agent configuration file. Each tool's settings are specified using the tool's name as the key.

For MCP server tools, use the format `@server_name/tool_name` as the key:

```json
{
  "toolsSettings": {
    "write": {
      "allowedPaths": ["~/projects"]
    },
    "@git/git_status": {
      "git_user": "$GIT_USER"
    }
  }
}
```

## Tool permissions

Tools can be explicitly allowed in the `allowedTools` section of the agent configuration:

```json
{
  "allowedTools": [
    "read",
    "knowledge",
    "@git/git_status"
  ]
}
```

If a tool is not in the `allowedTools` list, the user will be prompted for permission when the tool is used unless an allowed `toolsSettings` configuration is set.

Some tools have default permission behaviors:
- `report` is trusted by default
- `read`, `grep`, and `glob` are trusted in the current working directory
- `shell`, `write`, and `aws` prompt for permission by default, but can be configured to allow specific commands/paths/services

## Next steps

- **[Custom Agents](https://kiro.dev/docs/custom-agents.md)** - Use tools with custom agents
- **[MCP Integration](https://kiro.dev/docs/mcp.md)** - Connect external tools via MCP
- **[Settings](https://kiro.dev/docs/reference/settings.md)** - Configure tool preferences
- **[Troubleshooting](https://kiro.dev/docs/custom-agents/troubleshooting.md)** - Common tool issues
