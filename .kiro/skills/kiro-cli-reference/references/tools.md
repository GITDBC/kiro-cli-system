> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Built-in tools

> The tools available to Kiro's agent - file operations, shell commands, web access, code intelligence, and more

Kiro's agent includes built-in tools for development tasks. These are provided by the unified agent harness and shared across surfaces. The default agent has access to all built-in tools - custom agents can restrict this.

**At a glance:**

| | |
|---|---|
| **Cross-surface** | File read/write, shell, web search/fetch, sub-agents, context, introspect |
| **IDE and CLI** | Hook creation and on-demand MCP tool loading |
| **IDE only** | Background process control and output, dev-server orchestration, and editor code analysis (`read_code`, semantic rename) |
| **IDE and Web** | Powers (`kiro_powers`) |
| **CLI only** | Code intelligence (`code`) and knowledge (experimental) |
| **CLI 2.x legacy** | `session`, `tool_search` (V2), `thinking` (experimental), `use_aws` (preferred alias `aws`), `delegate`, `task` (aliases `todo`, `todo_list`), `goal`; not V3 built-ins |
| **Configuration** | Use [custom agents](https://kiro.dev/docs/custom-agents.md) `tools` field + [permissions](https://kiro.dev/docs/permissions.md) |

## Tool catalog

The catalog below covers built-in tools across Kiro surfaces. Availability can vary by surface and agent engine.

| Tool | Category | Description |
|------|----------|-------------|
| `read_file` | File | Read a single file |
| `list_directory` | File | List directory contents |
| `file_search` | File | Fuzzy file path search (glob) |
| `grep_search` | File | Regex content search |
| `fs_write` | File | Create or overwrite a file |
| `fs_append` | File | Append to an existing file |
| `str_replace` | File | Targeted text replacement |
| `delete_file` | File | Delete a file |
| `execute_bash` | Shell | Run a shell command |
| `remote_web_search` | Web | Search the web (displayed as `web_search`) |
| `web_fetch` | Web | Fetch content from a URL |
| `invoke_sub_agent` | Agent | Delegate tasks in parallel |
| `disclose_context` | Context | Activate skills or steering |
| `introspect` | Context | Answer questions about Kiro's own features from official docs |

### Surface availability

Some tools aren't available on every surface or agent engine yet. CLI V3 has no task-list tool, so the `chat.enableTodoList` setting has no effect there:

| Tool | IDE | CLI | Web | Mobile | Status |
|------|:---:|:---:|:---:|:------:|--------|
| `control_bash_process` / `control_pwsh_process` | ✓ | — | — | — | GA |
| `get_process_output` | ✓ | — | — | — | GA |
| `list_processes` | ✓ | — | — | — | GA |
| `kiro_powers` | ✓ | — | ✓ | — | GA |
| `createHook` | ✓ | ✓ | — | — | GA |
| `code` | — | ✓ | — | — | GA |
| `session` | — | 2.x | — | — | CLI 2.x only |
| `tool_search` | — | V2 | — | — | CLI V2 only |
| `knowledge` | — | ✓ | — | — | Experimental |
| `thinking` | — | 2.x | — | — | CLI 2.x only |
| `use_aws` / `aws` | — | 2.x | — | — | CLI 2.x only → use MCP servers |
| `delegate` | — | 2.x | — | — | CLI 2.x only → use sub-agents |
| `task` (aliases `todo`, `todo_list`) | — | 2.x | — | — | CLI 2.x only |
| `goal` | — | 2.x | — | — | CLI 2.x only; reports verified completion of a `/goal` you set |

The background-process tools (`control_bash_process` or `control_pwsh_process`, `get_process_output`, and `list_processes`) are available in the IDE, where they support [dev servers](https://kiro.dev/docs/ide/chat/dev-servers.md). CLI V3 can start a command in the background through `execute_bash` (`execute_pwsh` on Windows) with `run_in_background`, but it does not register these process-control tools. The `code` tool (tree-sitter and LSP-based [code intelligence](https://kiro.dev/docs/tools/code-intelligence.md)) is provided to non-IDE clients; in the IDE, equivalent capabilities are built in as editor-native tools - `read_code` for AST analysis and semantic rename - riding the language servers the editor already runs.

## Configuring tool access

Use the `tools` field of a [custom agent](https://kiro.dev/docs/custom-agents.md) to control which category tags and direct tool selectors are available:

```json
{
  "tools": ["read", "write", "shell", "web"]
}
```

Common category mappings include:

| Category | Commonly includes |
|----------|-------------------|
| `read` | read_file, list_directory, file_search, grep_search, code, `tool_search` (V2), introspect |
| `write` | fs_write, fs_append, str_replace, delete_file, code |
| `shell` | execute_bash or execute_pwsh; IDE clients may also expose control_bash_process or control_pwsh_process, get_process_output, and list_processes |
| `web` | web_fetch, remote_web_search |
| `subagent` | Per-agent dispatch tools (displayed as `subagent/<agent>`) |

Some built-ins are selected directly by tool ID rather than a category tag, including `knowledge` and `invoke_sub_agent`.

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
| `read_file` | Read a single file (text or image). Call it once per file to read several files. The CLI 2.x alias `fs_read` maps to the `read` tag during migration; it is not a Hook or runtime ID |
| `list_directory` | List directory contents in long format |
| `file_search` | Fuzzy file path search (glob patterns). CLI 2.x name: `glob` |
| `grep_search` | Regex content search across files. CLI 2.x name: `grep` |
| `code` | AST-based code analysis - signatures, symbols, fuzzy search |

All read tools apply [permissions](https://kiro.dev/docs/permissions.md) `fs_read` capability rules. `.kiroignore` support [varies by surface](https://kiro.dev/docs/kiroignore.md); in CLI V3, matching direct reads are blocked, while `file_search` and `grep_search` filter ignored paths from results.

## File tools (write)

| Tool | Description |
|------|-------------|
| `fs_write` | Create or overwrite a file. CLI 2.x name: `write` |
| `fs_append` | Append content to the end of an existing file |
| `str_replace` | Replace exact text in a file (targeted edits) |
| `delete_file` | Delete a file |

Write tools respect [permissions](https://kiro.dev/docs/permissions.md) `fs_write` capability rules.

## Shell tools

| Tool | Description | Surfaces |
|------|-------------|----------|
| `execute_bash` | Run a shell command. CLI 2.x names: `shell`, `execute_cmd` | IDE · CLI · Web |
| `control_bash_process` / `control_pwsh_process` | Start/stop long-running background processes | IDE |
| `get_process_output` | Read output from a background process | IDE |
| `list_processes` | List running background processes | IDE |

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
| `remote_web_search` | Search the web for current information. Displayed as `web_search` |
| `web_fetch` | Fetch and extract text content from a URL |

**Limitations:** 10 MB max per fetch, 30s timeout, text/HTML only. Retry behavior varies by surface; CLI V3 retries transient failures once.

Enterprise administrators can disable web tools from **Settings > Shared settings**. See [Enterprise governance - Web tools](https://kiro.dev/docs/enterprise/governance/web-tools.md).

## Code intelligence

[Detailed guide →](https://kiro.dev/docs/tools/code-intelligence.md)

Tree-sitter based code understanding for 18 languages - symbol search, document symbols, pattern search, and AST-based rewriting. Optional LSP integration for find references, go-to-definition, rename, and diagnostics.

**Supported languages:** Bash, C, C++, C#, Elixir, Go, Java, JavaScript, Kotlin, Lua, PHP, Python, Ruby, Rust, Scala, Swift, TSX, TypeScript

## Sub-agent delegation

| Tool | Description |
|------|-------------|
| `invoke_sub_agent` | Delegate a task to an agent running in isolated context |

See [Invoking as sub-agents](https://kiro.dev/docs/custom-agents/subagents.md) for the full guide.

## Context tools

| Tool | Description |
|------|-------------|
| `disclose_context` | Activate skills or steering files into context |
| `introspect` | Search indexed Kiro documentation (semantic + BM25) |
| `knowledge` | Search indexed knowledge bases (experimental) |

## Tool search

[Detailed guide →](https://kiro.dev/docs/mcp/tool-search.md)

Kiro IDE 1.3 and later load MCP tools on demand. Local V3 sessions in Kiro CLI 2.31 and later do too. Kiro receives a compact tool list, loads the definitions it needs, then calls those tools through normal permission and Hook checks.

V3 activity can show `tool_load` before `tool_call`. V2 sessions can enable the legacy `tool_search` path. See the [Tool Search guide](https://kiro.dev/docs/mcp/tool-search.md#enable-tool-search-in-v2-sessions).

## Session tools

| Tool | Description | Status |
|------|-------------|--------|
| `createHook` | Create agent hooks from chat | GA |
| `kiro_powers` | List, activate, and use installed powers | GA |

## Next steps

- [Web tools - detailed guide](https://kiro.dev/docs/tools/web.md)
- [Code intelligence - detailed guide](https://kiro.dev/docs/tools/code-intelligence.md)
- [Custom agents](https://kiro.dev/docs/custom-agents.md) - configure which tools agents can access
- [Permissions](https://kiro.dev/docs/permissions.md) - control what tools can do
- [MCP](https://kiro.dev/docs/mcp.md) - extend with external tools
- [Configuration scopes](https://kiro.dev/docs/configuration.md) - where tool settings are stored
