> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Tool Search

> Reduce context window usage by loading MCP tools on demand

Tool Search keeps unused MCP tool definitions out of each request. This leaves more model context for your work while Kiro loads the tools it needs.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Tool Search | ✓ | ✓ | — | — |

## Availability

Kiro IDE 1.3 and later use Tool Search automatically. Local V3 sessions in Kiro CLI use it by default. Tool Search has no effect when you have no [MCP servers](https://kiro.dev/docs/mcp/configuration.md) configured.

## V3 settings

V3 loads MCP tools on demand by default. Saved `toolSearch.enabled`, `toolSearch.minPct`, and `toolSearch.minTokens` values apply to both interactive and non-interactive V3 runs. They apply saved thresholds only when `toolSearch.enabled` is also saved.

## Verify on-demand loading

When Tool Search is active:

- IDE and local V3 activity can show `tool_load` before `tool_call` for an MCP tool

## How it works

1. **Indexing**: Kiro indexes the names and descriptions of tools from connected MCP servers.
2. **Deferred catalog**: The model receives a compact list instead of every full tool definition.
3. **Definition loading**: Kiro loads a needed tool's full description and input schema.
4. **Tool call**: Kiro calls the loaded tool through the normal permission and Hook checks.

In IDE and local V3 sessions, `tool_load` loads exact tool IDs and `tool_call` runs them.

## Next steps

- [Built-in tools](https://kiro.dev/docs/reference/built-in-tools.md): Tools included with Kiro
- [Settings reference](https://kiro.dev/docs/reference/settings.md): Tool Search settings
- [MCP configuration](https://kiro.dev/docs/mcp/configuration.md): Configure MCP servers
- [Terminal UI](https://kiro.dev/docs/cli/terminal-ui.md): View tool activity
