> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Model Context Protocol (MCP)

> Model Context Protocol (MCP) extends Kiro's capabilities by connecting to specialized servers that provide additional tools and context. This guide helps you set up, configure, and use MCP servers with Kiro.

Model Context Protocol (MCP) extends Kiro's capabilities by connecting to specialized servers that provide additional tools and context. This guide helps you set up, configure, and use MCP servers with Kiro across all surfaces.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Local (stdio) MCP servers | ✓ | ✓ | ✓ | — |
| Remote (HTTP/SSE) MCP servers | ✓ | ✓ | ✓ | — |
| MCP config file (JSON) | ✓ | ✓ | ✓ | — |
| Server-provided prompts and resources | ✓ | ✓ | ✓ | — |

## What is MCP?

MCP is a protocol that allows Kiro to communicate with external servers to access specialized tools, prompts, and resources. For example, the AWS Documentation MCP server provides tools to search, read, and get recommendations from AWS documentation directly within Kiro.

With MCP, you can:

- Access specialized knowledge bases and documentation
- Integrate with external services and APIs
- Extend Kiro's capabilities with domain-specific tools
- Use server-provided prompt templates and resource templates via the `#` mention system in chat
- Respond to server elicitation requests when tools need additional input during execution
- Create custom tools for your specific workflows

## Setting up MCP

### Prerequisites

Before using MCP, make sure you have:

1. The latest version of Kiro installed
2. Any specific prerequisites for the MCP servers you want to use (listed in each server's documentation)

### Adding an MCP server

    IDE
    CLI
    Web

### Open the MCP configuration

Open the command palette (`Cmd + Shift + P` on Mac, `Ctrl + Shift + P` on Windows/Linux) and search for **Kiro: Open workspace MCP config (JSON)** or **Kiro: Open user MCP config (JSON)**.

        Alternatively, open the Kiro panel and select the **Open MCP Config** icon.

      
### Add your server configuration

```json
        
          }
        }
        ```

      
### Save and verify

Save the config file (`Cmd+S`). Servers reconnect automatically. Check the MCP servers tab in the Kiro panel to confirm the server is connected.

### Add a server via the command line

```bash
        kiro-cli mcp add \
          --name "fetch" \
          --scope global \
          --command "uvx" \
          --args "mcp-server-fetch"
        ```

      
### Or edit the config file directly

Edit `~/.kiro/settings/mcp.json` (global) or `.kiro/settings/mcp.json` (workspace):

        ```json
        
          }
        }
        ```

      
### Verify the server is loaded

In an interactive session, use the `/mcp` slash command to see loaded servers:

        ```bash
        /mcp
        ```

    Kiro Web loads local MCP servers from `.kiro/settings/mcp.json` in your repository. Use the same JSON structure shown in the IDE and CLI examples, or configure servers from the sandbox settings panel. See [Powers and MCP](https://kiro.dev/docs/web/sandbox/mcp.md) for detailed Web instructions.

    
      
### Open Settings

Go to [Settings](https://app.kiro.dev/settings/agent) and select the **Agent** tab.

      
### Add a server

Under **MCP server settings**, click **Add server**. Enter the server name, type (HTTP or local), and command or URL.

### Installing from an install link

Some server directories and websites offer one-click install links that use the `kiro://` URL scheme. Opening one of these links doesn't change your setup immediately: Kiro shows a confirmation dialog before anything is written to your configuration. The dialog lists the command that will run and its arguments, along with the names of any environment variables or headers - their values stay hidden. Review the details and confirm to add the server, or cancel to leave your configuration unchanged.

**⚠️ Warning:** Only install MCP servers from sources you trust. See [Security best practices](https://kiro.dev/docs/mcp/security.md) for guidance on evaluating servers before installing them.

### Agent configuration

You can also define MCP servers directly in an agent's configuration file. The `mcpServers` field specifies which MCP servers the agent has access to:

```json
{
  "name": "myagent",
  "description": "My special agent",
  "mcpServers": {
    "fetch": {
      "command": "fetch3.1",
      "args": []
    }
  },
  "includeMcpJson": false
}
```

The `includeMcpJson` field determines whether to include MCP servers defined in workspace and user-level configuration files. When set to `true`, the agent has access to all MCP servers defined in user and workspace-level configurations in addition to those defined in the agent's `mcpServers` field.

## Troubleshooting

### Checking MCP logs

    IDE
    CLI

    1. Open the Kiro panel
    2. Select the Output tab
    3. Choose "Kiro - MCP Logs" from the dropdown

    Use the `/mcp` slash command to check server status. Review terminal output for connection errors when starting a session.

### Common issues and solutions

| Issue | Solution |
|-------|----------|
| Connection failures | Verify prerequisites are installed correctly |
| Permission errors | Check that tokens and API keys are valid |
| Tool not responding | Review MCP logs for specific error messages |
| Configuration not loading | Validate JSON syntax and save the config file |

### Tool validation errors

If you see "The following tools have been excluded due to validation errors", the tool fails one of these requirements:
- Tool name exceeds 64 characters (including server prefix)
- Tool name contains invalid characters (must match `^[a-zA-Z][a-zA-Z0-9_]*$`)
- Tool description is empty

Contact the MCP server maintainer to fix the tool specification.

### Large description warnings

If you see "The following tools have large descriptions which may impact agent performance", a tool description exceeds 10,000 characters. The tool still works but may slow down responses. Consider asking the server maintainer to shorten the description.

## Additional resources

- [Official MCP Documentation](https://modelcontextprotocol.io/introduction)

## Next steps

- **[Configuration](https://kiro.dev/docs/mcp/configuration.md)** - Detailed configuration options and file structure
- **[Server directory](https://kiro.dev/docs/mcp/servers.md)** - Browse available MCP servers
- **[Tools](https://kiro.dev/docs/mcp/usage.md)** - Learn how to use MCP tools effectively
- **[Best practices](https://kiro.dev/docs/mcp/security.md)** - Security best practices for MCP usage
