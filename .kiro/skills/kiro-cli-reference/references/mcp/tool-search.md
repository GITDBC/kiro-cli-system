> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Tool Search

> Reduce context window usage by loading MCP tools on demand

Tool Search loads MCP tools on demand instead of sending every tool definition with each request. This keeps your context window clear when you have many MCP servers configured, and lets the agent discover the right tools automatically.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Tool Search | — | ✓ | — | — |

## When to enable Tool Search

Enable Tool Search if:
- You have 5+ MCP servers configured
- You see context window overflow errors during long conversations
- The `/tools` command shows MCP tools consuming more than 50,000 tokens total

If you only use a few MCP tools, the overhead of Tool Search may not be worth it.

**ℹ️ Info:** Tool Search requires at least one [MCP server](https://kiro.dev/docs/mcp/configuration.md) to be configured. It has no effect if you only use built-in tools.

## Enabling Tool Search

Tool Search is disabled by default. Enable it via settings:

```bash
kiro-cli settings toolSearch.enabled true
```

Once enabled, Tool Search activates automatically when MCP tool specs are large enough to benefit from deferral. The default thresholds (5% of context window or 50,000 tokens) cover most cases. To force activation whenever any MCP tools are present, set the thresholds to `0`:

```bash
kiro-cli settings toolSearch.minPct 0
kiro-cli settings toolSearch.minTokens 0
```

### Settings

Configure Tool Search behavior with these settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `toolSearch.enabled` | `false` | Master toggle for Tool Search |
| `toolSearch.minPct` | `5` | Activate when MCP tool specs exceed this % of the context window |
| `toolSearch.minTokens` | `50000` | Activate when MCP tool specs exceed this token count |

When both thresholds are set, Tool Search activates if either is exceeded (OR logic). When both thresholds are set to `0`, Tool Search is always active regardless of MCP tool count.

## Verifying Tool Search is active

When Tool Search is active:
- The `/tools` command shows reduced token counts for MCP tools compared to when it's disabled
- You'll see `tool_search` calls in the agent's tool usage when it discovers tools on demand

## How it works

1. **Indexing**: When MCP servers connect, all tool specs are indexed for keyword search. Each tool's name, server name, description, and parameter descriptions are tokenized.

2. **Deferred tool list**: Instead of full JSON schemas, the model receives a compact list of `server_name::tool_name: description` entries. Descriptions are truncated to 1KB.

3. **On-demand loading**: When the model needs a tool, it calls `tool_search` with either an exact `tool_id` (e.g., `builder-mcp::InternalSearch`) or a keyword `query` (e.g., `"search documents"`).

4. **Activation**: Matched tools are loaded and their full schemas are included in subsequent requests.

## The tool_search built-in tool

**Tool name**: `tool_search`

Finds and loads MCP tools on demand. Automatically allowed without user permission prompts (read-only).

### Parameters

The `tool_search` tool accepts the following parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tool_id` | string | One of `tool_id` or `query` | Exact tool identifier in `server_name::tool_name` format |
| `query` | string | One of `tool_id` or `query` | Keywords to search for matching tools |
| `max_results` | integer | No | Maximum results to return (default: 5) |

Provide exactly one of `tool_id` or `query`, not both. Matched tools are immediately activated and available for invocation.

### Keyword matching

Keyword search uses BM25 relevance scoring. Tool names are split on casing boundaries (e.g., `ReadFile` → `read file`, `read_file` → `read file`) to improve matching. Only results above the matching threshold are returned.

The default threshold is `1.5`, configurable via the `KIRO_CLI_TOOL_SEARCH_MATCHING_THRESHOLD` environment variable.

## Next steps

- [Built-in tools](https://kiro.dev/docs/reference/built-in-tools.md): All built-in tools including `tool_search`
- [Settings reference](https://kiro.dev/docs/reference/settings.md): `toolSearch.*` settings
- [MCP configuration](https://kiro.dev/docs/mcp/configuration.md): Configuring MCP servers
- [Terminal UI](https://kiro.dev/docs/cli/terminal-ui.md): Real-time shell output and tool display
