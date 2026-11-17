> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Manage prompts

> Create, organize, and reuse custom prompts for efficient CLI interactions

The Kiro CLI provides comprehensive prompt management capabilities for both local prompts and Model Context Protocol (MCP) prompts. This system allows you to create, edit, organize, and use reusable prompts across your development workflow.

## About prompt types

The prompt system supports three types of prompts:

* **Local prompts**: Project-specific prompts stored in your workspace
* **Global prompts**: User-wide prompts available across all projects
* **MCP prompts**: Prompts provided by MCP servers with enhanced functionality

## Commands

All prompt management is accessed through the `/prompts` command with various subcommands.

### List prompts

```
/prompts list
```

Displays all available prompts in a three-column layout showing names, descriptions, and sources. Shows prompt counts and indicates which prompts come from local storage, global storage, or MCP servers.

### Create prompts

```
/prompts create --name name [--content content]
```

Creates a new local prompt in the current workspace.

###### Parameters

`name` (required)
:   Prompt name (maximum 50 characters)

`--content content` (optional)
:   Direct content specification

**Behavior:**

* If `--content` is provided, creates prompt with specified content
* If no content provided, opens your default editor for content creation
* Prompts are saved to `.kiro/prompts/` in the current workspace

### Edit prompts

```
/prompts edit name
```

Opens an existing prompt in your default editor for modification.

**Supported prompts:**

* Local workspace prompts
* Global user prompts
* MCP prompts (where supported by the server)

### View prompt details

```
/prompts details name
```

Shows comprehensive information about a prompt including:

* Metadata and argument details
* Complete prompt content before AI processing
* Parameter requirements and examples
* Source information (local, global, or MCP server)

## Using prompts

In V3, workspace, global, and MCP prompts appear in slash-command completion. Type `/` and select a prompt, or invoke it directly:

```
/prompt-name [arguments]
```

Completion shows the prompt's argument hints. Kiro resolves the file template or requests the MCP prompt content before sending the expanded text to the model. Other CLI engines continue to support the `@prompt-name` form.

### File and directory references (v1.26.0+)

In addition to prompts, you can use the `@` syntax to reference files and directories directly in your messages. Kiro will automatically expand these references to include the content or structure in your conversation.

**Basic Syntax:**

```bash
# Include file contents
> Review @src/auth.rs for security issues

# Include directory tree
> What's the structure of @crates/agent/?

# Quoted paths for spaces
> Check @"my file.txt" for errors

# Relative paths
> Compare @./v1/api.rs with @./v2/api.rs
```

**Features:**
- **Tab completion** - Press Tab after `@` to auto-complete file and directory paths
- **Syntax highlighting** - References highlighted in purple for visibility
- **Automatic formatting** - Files displayed as code blocks, directories as tree listings
- **Smart prioritization** - Known prompts take precedence over file paths

**Size Limits:**
- Files: 250KB maximum (larger files truncated with warning)
- Directories: 3 levels deep, 10 items per level maximum
- Binary files not supported (shows error message)

**Priority Rules:**

When you use `@name`, Kiro checks in this order:
1. **Known prompts** - If `@name` matches a prompt (local, global, or MCP), it's treated as a prompt
2. **Files** - Otherwise checked as a file path
3. **Directories** - If not a file, checked as a directory

This means your prompts always take precedence over files with the same name.

**Limitations:**
- No glob patterns (`@*.rs` won't work)
- No line range syntax (`@file.rs:10-20` won't work)
- No home directory expansion (`@~` won't work)
- Binary files not supported
- Files without read permission show errors

### Examples

```
/code-review
# Uses your local code-review prompt in V3

@src/auth.rs
# Includes the contents of src/auth.rs file

@crates/agent/
# Shows the directory structure of crates/agent/
```

## Passing arguments to prompts

MCP prompts can declare required and optional arguments. V3 file prompts can interpolate positional arguments with `$` through `$`, all arguments with `$ARGUMENTS`, or the same full argument string with `$`.

### Prompt argument syntax

```
/prompt-name <required-arg> [optional-arg]
```

Use `/prompts details prompt-name` to inspect an MCP prompt's declared arguments. Slash-command completion shows the same hints.

```
# Examples: V3 prompts with arguments
/analyze "performance issue" "detailed"
/scan "web-app" "high-severity"
```

## Storage locations

### Local prompts (workspace-specific)

* **Location**: `project/.kiro/prompts/`
* **Scope**: Available only within the current project
* **Priority**: Highest (overrides global and MCP prompts with same name)

### Global prompts (user-wide)

* **Location**: `~/.kiro/prompts/`
* **Scope**: Available across all projects
* **Priority**: Medium (overrides MCP prompts with same name)

### MCP prompts

* **Source**: Provided by configured MCP servers
* **Scope**: Depends on server configuration
* **Priority**: Lowest (overridden by local and global prompts)

## Priority system

When multiple prompts have the same name, the system uses this priority order:

1. **Local prompts** (highest priority)
2. **Global prompts**
3. **MCP prompts** (lowest priority)

This allows you to override MCP or global prompts with project-specific versions when needed.

## Enhanced features

### Content preview

The system displays the complete prompt content before sending it to the AI model, eliminating confusion about what information was actually processed.

### Improved error handling

* MCP server errors are converted to user-friendly messages
* Helpful usage examples are generated from prompt metadata
* Clear guidance for invalid parameters or missing requirements

### Visual formatting

* Consistent terminal styling across all prompt operations
* Proper content display for all prompt message types
* Three-column layout for improved readability in listings

## MCP integration

The prompt system seamlessly integrates with MCP servers:

* **Automatic discovery**: MCP prompts are automatically discovered from configured servers
* **Enhanced UX**: Improved user experience for MCP prompt management
* **Error translation**: Raw JSON errors are converted to actionable messages
* **Content preview**: Full content preview for MCP prompts before execution

## Examples

These examples demonstrate file-based prompt creation and MCP prompt usage.

### Basic file-based prompt creation and usage

```
# Create a simple prompt without arguments
/prompts create --name code-review --content "Please review this code for best practices, security issues, and potential improvements:"

# Use the prompt in V3
/code-review
```

### MCP prompt usage with arguments

```
# Using MCP prompts with arguments
/analyze "performance bottleneck" "cpu usage"
/scan "web-app" "high-severity"
/deploy "my-service" "production" "us-west-2"
```
