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

Kiro IDE 1.3 and later use Tool Search automatically. Local V3 sessions in Kiro CLI 2.31 and later use it by default. Tool Search has no effect when you have no [MCP servers](https://kiro.dev/docs/mcp/configuration.md) configured.

## Enable Tool Search in V2 sessions

In V2 sessions, Tool Search remains opt-in. Enable it with:

```bash
kiro-cli settings toolSearch.enabled true
```

In V2, Tool Search activates when MCP tool definitions cross either configured threshold: 5% of the context window or 50,000 tokens by default. To activate it whenever any MCP tools are present, set both thresholds to `0`:

```bash
kiro-cli settings toolSearch.minPct 0
kiro-cli settings toolSearch.minTokens 0
```

### V2 settings

| Setting | Default | Description |
|---------|---------|-------------|
| `toolSearch.enabled` | `false` | Turn on Tool Search |
| `toolSearch.minPct` | `5` | Activate when MCP tool definitions exceed this context-window percentage |
| `toolSearch.minTokens` | `50000` | Activate when MCP tool definitions exceed this token count |

When both thresholds are set, either one can activate Tool Search. When both are `0`, any configured MCP tool activates it.

## V3 settings

V3 loads MCP tools on demand by default. Kiro CLI 2.31.1 and later applies saved `toolSearch.enabled`, `toolSearch.minPct`, and `toolSearch.minTokens` values to both interactive and non-interactive V3 runs. It applies saved thresholds only when `toolSearch.enabled` is also saved.

## Verify on-demand loading

When Tool Search is active:

- IDE and local V3 activity can show `tool_load` before `tool_call` for an MCP tool
- In V2, `/tools` shows lower MCP tool token use than preloading every definition

## How it works

1. **Indexing**: Kiro indexes the names and descriptions of tools from connected MCP servers.
2. **Deferred catalog**: The model receives a compact list instead of every full tool definition.
3. **Definition loading**: Kiro loads a needed tool's full description and input schema.
4. **Tool call**: Kiro calls the loaded tool through the normal permission and Hook checks.

In IDE and local V3 sessions, `tool_load` loads exact tool IDs and `tool_call` runs them. V2 uses the legacy `tool_search` path when you enable it.

## Next steps

- [Built-in tools](https://kiro.dev/docs/reference/built-in-tools.md): Tools included with Kiro
- [Settings reference](https://kiro.dev/docs/reference/settings.md): Tool Search settings
- [MCP configuration](https://kiro.dev/docs/mcp/configuration.md): Configure MCP servers
- [Terminal UI](https://kiro.dev/docs/cli/terminal-ui.md): View tool activity
