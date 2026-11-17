> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Share MCP servers

> Create one-click install links and an Add to Kiro badge for your MCP server, and share it with the Kiro registry.

Let people add your MCP server to Kiro in one click. Create an install link, put the Add to Kiro badge in your README, and share your server with the registry so Kiro users can find it. Browse curated servers in the [MCP server directory](https://kiro.dev/mcp).

## Install link schema

**URL Format:**
```
https://kiro.dev/launch/mcp/add?name=<server-name>&config=<url-encoded-config>
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | String | Yes | Display name for the MCP server |
| `config` | String | Yes | URL-encoded JSON configuration object (see [MCP Configuration](https://kiro.dev/docs/mcp/configuration.md#configuration-properties) for schema) |

## Generate an install link

Use these helper functions to programmatically create installation links for your MCP server. These links work universally across GitHub, web browsers, and documentation.

**JavaScript/TypeScript:**

```javascript
function createKiroInstallLink(name, config) {
  const encodedName = encodeURIComponent(name);
  const encodedConfig = encodeURIComponent(JSON.stringify(config));
  return `https://kiro.dev/launch/mcp/add?name=${encodedName}&config=${encodedConfig}`;
}

// Example 1: Local server with command execution
const localServerLink = createKiroInstallLink('aws-docs', {
  command: 'uvx',
  args: ['awslabs.aws-documentation-mcp-server@latest'],
  env: { FASTMCP_LOG_LEVEL: 'ERROR' },
  disabled: false,
  autoApprove: []
});

// Example 2: Remote server with URL endpoint
const remoteServerLink = createKiroInstallLink('aws-knowledge', {
  url: 'https://knowledge-mcp.global.api.aws',
  disabled: false,
  autoApprove: []
});

// Example 3: Server with environment variables
const dbServerLink = createKiroInstallLink('postgresql', {
  command: 'npx',
  args: ['-y', '@modelcontextprotocol/server-postgres'],
  env: { POSTGRES_CONNECTION_STRING: 'postgresql://localhost:5432/mydb' },
  disabled: false,
  autoApprove: []
});
```

**Python:**

```python
import json
from urllib.parse import urlencode, quote

def create_kiro_install_link(name: str, config: dict) -> str:
    """
    Creates a Kiro install link for one-click MCP server installation
    
    Args:
        name: Display name for the MCP server
        config: MCP server configuration dictionary
        
    Returns:
        Formatted HTTPS install link URL
    """
    encoded_name = quote(name)
    encoded_config = quote(json.dumps(config))
    return f"https://kiro.dev/launch/mcp/add?name={encoded_name}&config={encoded_config}"

# Example usage
link = create_kiro_install_link('my-server', {
    'command': 'npx',
    'args': ['-y', '@myorg/my-mcp-server'],
    'disabled': False,
    'autoApprove': []
})
```

**Command Line (Bash):**

```bash
#!/bin/bash

# Function to create Kiro install link
create_kiro_link() {
  local name="$1"
  local config="$2"
  
  # URL encode the parameters
  local encoded_name=$(printf %s "$name" | jq -sRr @uri)
  local encoded_config=$(printf %s "$config" | jq -sRr @uri)
  
  echo "https://kiro.dev/launch/mcp/add?name=${encoded_name}&config=${encoded_config}"
}

# Example usage
CONFIG='{"command":"npx","args":["-y","@modelcontextprotocol/server-git"],"disabled":false,"autoApprove":[]}'
create_kiro_link "git" "$CONFIG"
```

## Add the Kiro badge

Include the `Add to Kiro` badge in your project's README or documentation to let users install your MCP server with a single click:

```html
<a href="https://kiro.dev/launch/mcp/add?name=my-server&config=%7B%22command%22%3A%22npx%22...%7D">
  <img src="https://kiro.dev/images/add-to-kiro.svg" alt="Add to Kiro" />
</a>
```

**Markdown:**
```markdown
[![Add to Kiro](https://kiro.dev/images/add-to-kiro.svg)](https://kiro.dev/launch/mcp/add?name=my-server&config=%7B%22command%22%3A%22npx%22...%7D)
```

When clicked, users are prompted to open Kiro with the server configuration pre-filled. If the prompt doesn't work, the page displays the server name and a retry button.

## Get listed in the registry

Once your server has an install link, [share it with the registry](https://kiro.dev/registry/submit/?type=mcp). If it's a good fit, we'll list it in the [MCP server directory](https://kiro.dev/mcp).

## Discover more MCP servers

The [MCP server directory](https://kiro.dev/mcp) features curated servers, but hundreds more are available in the MCP ecosystem.

### Official resources

- **[MCP Registry](https://github.com/modelcontextprotocol/registry)** - Browse the official registry of community-contributed MCP servers with detailed documentation and installation instructions.

- **[Model Context Protocol Organization](https://github.com/modelcontextprotocol)** - Explore reference implementations and official servers maintained by the MCP team.

### Package registries

- **[npm (Node.js)](https://www.npmjs.com/search?q=mcp-server)** - Search for `mcp-server` or `@modelcontextprotocol/server-*` to find JavaScript/TypeScript implementations.

- **[PyPI (Python)](https://pypi.org/search/?q=mcp-server)** - Search for `mcp-server` or packages with MCP in the name to find Python implementations.
