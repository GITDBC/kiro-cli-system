> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Built-in tools

> The tools available to Kiro's agent - file operations, shell commands, web access, code intelligence, and more

Kiro's agent includes built-in tools for development tasks. These are provided by the unified agent harness and shared across surfaces. The default agent has access to all built-in tools - custom agents can restrict this.

**At a glance:**

| | |
|---|---|
| **Cross-surface** | File read/write, shell, web search/fetch, sub-agents, context, task tracking, introspect |
| **IDE and CLI** | Hook creation |
| **IDE and Web** | Powers (`kiro_powers`) |
| **IDE only** | Background processes (dev servers), editor code analysis (`read_code`, semantic rename) |
| **CLI only** | Code intelligence (`code`), goal, session settings, MCP tool search (`tool_search`), knowledge (experimental), thinking (experimental) |
| **Deprecated** | `aws`, `delegate` - being replaced |
| **Configuration** | Use [custom agents](https://kiro.dev/docs/custom-agents.md) `tools` field + [permissions](https://kiro.dev/docs/permissions.md) |

## Tool catalog

All tools below are available across IDE, CLI, Web, and Mobile.

| Tool | Category | Description |
|------|----------|-------------|
| `read_file` / `read_files` | File | Read single or multiple files |
| `list_directory` | File | List directory contents |
| `file_search` | File | Fuzzy file path search (glob) |
| `grep_search` | File | Regex content search |
| `fs_write` | File | Create or overwrite a file |
| `fs_append` | File | Append to an existing file |
| `str_replace` | File | Targeted text replacement |
| `delete_file` | File | Delete a file |
| `execute_bash` | Shell | Run a shell command |
| `web_search` | Web | Search the web |
| `web_fetch` | Web | Fetch content from a URL |
| `invoke_subagent` | Agent | Delegate tasks in parallel |
| `disclose_context` | Context | Activate skills or steering |
| `introspect` | Context | Answer questions about Kiro's own features from official docs |
| `todo_list` | Session | Track tasks within a session |

### Surface availability

Some tools aren't available on every surface yet:

| Tool | IDE | CLI | Web | Mobile | Status |
|------|:---:|:---:|:---:|:------:|--------|
| `control_bash_process` | ✓ | — | — | — | GA |
| `get_process_output` | ✓ | — | — | — | GA |
| `list_processes` | ✓ | — | — | — | GA |
| `kiro_powers` | ✓ | — | ✓ | — | GA |
| `create_hook` | ✓ | ✓ | — | — | GA |
| `code` | — | ✓ | — | — | GA |
| `goal` | — | ✓ | — | — | GA |
| `session_settings` | — | ✓ | — | — | GA |
| `tool_search` | — | ✓ | — | — | GA |
| `knowledge` | — | ✓ | — | — | Experimental |
| `thinking` | — | ✓ | — | — | Experimental |
| `aws` | — | ✓ | — | — | Deprecated |
| `delegate` | — | ✓ | — | — | Deprecated → use sub-agents |

The background-process tools (`control_bash_process`, `get_process_output`, `list_processes`) power the IDE's [dev servers](https://kiro.dev/docs/ide/chat/dev-servers.md) workflow. The `code` tool (tree-sitter and LSP-based [code intelligence](https://kiro.dev/docs/tools/code-intelligence.md)) is provided to non-IDE clients; in the IDE, equivalent capabilities are built in as editor-native tools - `read_code` for AST analysis and semantic rename - riding the language servers the editor already runs.

## Configuring tool access

Use the `tools` field of a [custom agent](https://kiro.dev/docs/custom-agents.md) to control which tool categories are available:

```json
{
  "tools": ["read", "write", "shell", "web"]
}
```

Each category maps to a set of tools:

| Category | Includes |
|----------|----------|
| `read` | read_file, read_files, list_directory, file_search, grep_search, code |
| `write` | fs_write, fs_append, str_replace, delete_file |
| `shell` | execute_bash, control_bash_process, get_process_output, list_processes |
| `web` | web_fetch, web_search |
| `subagent` | invoke_subagent |
| `spec` | Spec workflow tools |
| `context` | disclose_context, introspect, knowledge |

Special values:

| Value | Effect |
|-------|--------|
| `@builtin` | All built-in tools |
| `@mcp` | All MCP server tools |
| `*` | Everything (built-in + MCP) |

Exclude specific categories: `"excludedTools": ["web"]`

Control what tools can *do* (not just which are visible) with [permissions](https://kiro.dev/docs/permissions.md).

**💡 Tip:** Need tools beyond the built-in set? Add custom tools via [MCP servers](https://kiro.dev/docs/mcp.md) - databases, APIs, cloud services, and any tool that speaks the Model Context Protocol.

## File tools (read)

| Tool | Description |
|------|-------------|
| `read_file` | Read a single file (text or image). Aliases: `fs_read` |
| `read_files` | Read multiple files with optional line ranges |
| `list_directory` | List directory contents in long format |
| `file_search` | Fuzzy file path search (glob patterns). Aliases: `glob` |
| `grep_search` | Regex content search across files. Aliases: `grep` |
| `code` | AST-based code analysis - signatures, symbols, fuzzy search |

All read tools apply [permissions](https://kiro.dev/docs/permissions.md) `fs_read` capability rules. `.kiroignore` support [varies by surface](https://kiro.dev/docs/kiroignore.md); in CLI V3, `file_search` and `grep_search` filter ignored paths from results.

## File tools (write)

| Tool | Description |
|------|-------------|
| `fs_write` | Create or overwrite a file. Aliases: `write` |
| `fs_append` | Append content to the end of an existing file |
| `str_replace` | Replace exact text in a file (targeted edits) |
| `delete_file` | Delete a file |

Write tools respect [permissions](https://kiro.dev/docs/permissions.md) `fs_write` capability rules.

## Shell tools

| Tool | Description | Surfaces |
|------|-------------|----------|
| `execute_bash` | Run a shell command. Aliases: `shell`, `execute_cmd` | IDE · CLI · Web |
| `control_bash_process` | Start/stop long-running background processes | IDE · CLI |
| `get_process_output` | Read output from a background process | IDE · CLI |
| `list_processes` | List running background processes | IDE · CLI |

Shell tools respect [permissions](https://kiro.dev/docs/permissions.md) `shell` capability rules. Use `match` patterns to pre-approve common commands:

```yaml
rules:
  - capability: shell
    match: ["git *", "npm *", "cargo *"]
    effect: allow
  - capability: shell
    match: ["rm -rf *", "sudo *"]
    effect: deny
```

## Web tools

[Detailed guide →](https://kiro.dev/docs/tools/web.md)

| Tool | Description |
|------|-------------|
| `web_search` | Search the web for current information |
| `web_fetch` | Fetch and extract text content from a URL |

**Limitations:** 10 MB max per fetch, 30s timeout, text/HTML only, 3 retries.

Enterprise administrators can disable web tools from **Settings > Shared settings**. See [Enterprise governance - Web tools](https://kiro.dev/docs/enterprise/governance/web-tools.md).

## Code intelligence

[Detailed guide →](https://kiro.dev/docs/tools/code-intelligence.md)

Tree-sitter based code understanding for 18 languages - symbol search, document symbols, pattern search, and AST-based rewriting. Optional LSP integration for find references, go-to-definition, rename, and diagnostics.

**Supported languages:** Bash, C, C++, C#, Elixir, Go, Java, JavaScript, Kotlin, Lua, PHP, Python, Ruby, Rust, Scala, Swift, TSX, TypeScript

## Sub-agent delegation

| Tool | Description |
|------|-------------|
| `invoke_subagent` | Delegate a task to an agent running in isolated context |

See [Invoking as sub-agents](https://kiro.dev/docs/custom-agents/subagents.md) for the full guide.

## Context tools

| Tool | Description |
|------|-------------|
| `disclose_context` | Activate skills or steering files into context |
| `introspect` | Search indexed Kiro documentation (semantic + BM25) |
| `knowledge` | Search indexed knowledge bases (experimental) |

## Tool search (CLI)

[Detailed guide →](https://kiro.dev/docs/mcp/tool-search.md)

Loads MCP tools on demand instead of including every tool definition in every request. Keeps context efficient with many MCP servers. Available in the CLI.

**How it works:** Index → deferred compact list → on-demand `tool_search` call → activate matched tool.

| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_id` | string | Exact `server_name::tool_name` identifier |
| `query` | string | Keywords for BM25 search |
| `max_results` | integer | Max results (default: 5) |

Enable in CLI: `kiro-cli settings toolSearch.enabled true`

| Setting | Default | Description |
|---------|---------|-------------|
| `toolSearch.enabled` | `false` | Master toggle |
| `toolSearch.minPct` | `5` | Activate when tool specs exceed this % of context |
| `toolSearch.minTokens` | `50000` | Activate when tool specs exceed this token count |

## Session tools

| Tool | Description | Status |
|------|-------------|--------|
| `todo_list` | Track tasks within a session (create, complete, list) | GA |
| `create_hook` | Create agent hooks from chat | GA |
| `kiro_powers` | List, activate, and use installed powers | GA |

## Next steps

- [Web tools - detailed guide](https://kiro.dev/docs/tools/web.md)
- [Code intelligence - detailed guide](https://kiro.dev/docs/tools/code-intelligence.md)
- [Custom agents](https://kiro.dev/docs/custom-agents.md) - configure which tools agents can access
- [Permissions](https://kiro.dev/docs/permissions.md) - control what tools can do
- [MCP](https://kiro.dev/docs/mcp.md) - extend with external tools
- [Configuration scopes](https://kiro.dev/docs/configuration.md) - where tool settings are stored
