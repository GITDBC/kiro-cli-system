> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# MCP registry

> Centrally managed MCP server access for enterprise teams using IAM Identity Center

**ℹ️ For administrators:** If you're an administrator setting up the MCP registry, see [MCP Governance](https://kiro.dev/docs/enterprise/governance/mcp.md) for configuration instructions.

Pro-tier customers using IAM Identity Center can have MCP server access controlled through an MCP registry. When configured by administrators, users can only use MCP servers explicitly allowed in the registry.

**Without Registry** (default):
- Users can add any MCP server
- Servers configured in agent files or via CLI
- No central control

**With Registry** (enterprise):
- Administrator configures allowed servers
- Users select from registry list
- Cannot add custom servers - servers not in the registry are hidden, including ones you define yourself in `mcp.json`
- Centralized governance and security

## Adding registry servers

    IDE
    CLI
    Web

    In registry mode, available servers appear in the MCP panel. Select a server to add it to your configuration.

    ```bash
    # Interactive selection from registry
    kiro-cli mcp add

    # Add specific server from registry
    kiro-cli mcp add --name myserver

    # In chat session
    /mcp add
    ```

    
**ℹ️ Registry mode:** The `/mcp add` picker only lists servers from your organization's registry. Servers you define directly in `mcp.json` are also restricted to the registry - see [Servers not in the registry](#servers-not-in-the-registry).

    MCP registry is managed by your organization's administrator. Available servers are automatically configured for Web sessions when registry mode is enabled.

## Servers not in the registry

When a registry is active, it is the only source of servers that can run. A server you define in `mcp.json` (global `~/.kiro/mcp.json` or workspace `.kiro/mcp.json`) loads only if its name matches an entry in the registry. Anything else is hidden and never started, including servers that were working before the registry was turned on.

In the IDE, hidden servers appear as an "N servers hidden" notice in the MCP panel rather than as individual entries. To run a server that isn't in the registry, ask your administrator to add it.

A `mcp.json` entry whose name *is* in the registry is still useful: it's how you supply values specific to your setup, such as API keys or local paths. See [Registry server overrides](#registry-server-overrides).

## Registry server overrides

Even with registry mode enabled, you can customize servers using registry overrides in your agent configuration or in an `mcp.json` file (global `~/.kiro/mcp.json` or workspace `.kiro/mcp.json`). Your values are merged on top of registry defaults - for example, if the registry sets `NODE_ENV=development` and your override sets `NODE_ENV=production`, the server runs with `NODE_ENV=production`. The `env` and `headers` objects merge per-key, so registry defaults you don't override are preserved.

```json
{
  "mcpServers": {
    "github": {
      "type": "registry",
      "env": {
        "GITHUB_TOKEN": "$GITHUB_TOKEN",
        "GITHUB_ORG": "my-org"
      },
      "timeout": 60000
    }
  }
}
```

Override fields:
- **Local (stdio) servers** - `env` (environment variables), `timeout` (request timeout in ms)
- **Remote (HTTP) servers** - `headers` (HTTP headers), `timeout` (request timeout in ms)

The `env`, `headers`, and `timeout` overrides you define for a registry-type entry flow through to the launched server, so the running process uses your customized values.
