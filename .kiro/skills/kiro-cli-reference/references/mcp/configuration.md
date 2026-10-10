> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Configuration

> Configure Model Context Protocol (MCP) servers across IDE, CLI, and Web including configuration file structure, server setup, and management.

This guide provides detailed information on configuring Model Context Protocol (MCP) servers with Kiro, including configuration file structure, server setup, and management across all surfaces.

## Configuration file structure

MCP configuration files use JSON format with the following structure:

```json
{
  "mcpServers": {
    "local-server-name": {
      "command": "command-to-run-server",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR1": "hard-coded-variable",
        "ENV_VAR2": "${EXPANDED_VARIABLE}"
      },
      "disabled": false,
      "autoApprove": ["tool_name1", "tool_name2"],
      "disabledTools": ["tool_name3"]
    },
    "remote-server-name": {
      "url": "https://endpoint.to.connect.to",
      "headers": {
        "HEADER1": "value1",
        "HEADER2": "value2"
      },
      "disabled": false,
      "autoApprove": ["tool_name1", "tool_name2"],
      "disabledTools": ["tool_name3"]
    }
  }
}
```

### Configuration properties

#### Local server

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `command` | String | Yes | The command to run the MCP server |
| `args` | Array | No | Arguments to pass to the command |
| `env` | Object | No | Environment variables for the server process |
| `disabled` | Boolean | No | Whether the server is disabled (default: false) |
| `autoApprove` | Array | No | Tool names to auto-approve without prompting (use `"*"` to auto-approve all tools) |
| `disabledTools` | Array | No | Tool names to omit when calling the Agent |

#### Remote server

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `url` | String | Yes | HTTPS endpoint for the remote MCP server (or HTTP endpoint for localhost) |
| `headers` | Object | No | Headers to pass to the MCP server during connection |
| `env` | Object | No | Environment variables for the server process |
| `oauth` | Object | No | OAuth configuration for servers that require authentication (see [OAuth configuration](#oauth-configuration)) |
| `oauthScopes` | Array | No | OAuth scopes to request (fallback; overridden by `oauth.oauthScopes` if both are set) |
| `disabled` | Boolean | No | Whether the server is disabled (default: false) |
| `autoApprove` | Array | No | Tool names to auto-approve without prompting (use `"*"` to auto-approve all tools) |
| `disabledTools` | Array | No | Tool names to omit when calling the Agent |

## Configuration locations

    IDE
    CLI
    Web

    You can configure MCP servers at two levels:

    1. **Workspace Level**: `.kiro/settings/mcp.json`
       - Applies only to the current workspace
       - Ideal for project-specific MCP servers

    2. **User Level**: `~/.kiro/settings/mcp.json`
       - Applies globally across all workspaces
       - Best for MCP servers you use frequently

    If both files exist, configurations are merged with workspace settings taking precedence.

    ### Creating configuration files

    **Using the command palette:**

    1. Open the command palette (`Cmd + Shift + P` on Mac, `Ctrl + Shift + P` on Windows/Linux)
    2. Search for "MCP" and select one of these options:
       - **Kiro: Open workspace MCP config (JSON)** - For workspace-level configuration
       - **Kiro: Open user MCP config (JSON)** - For user-level configuration

    **Using the Kiro panel:**

    1. Open the Kiro panel
    2. Select the **Open MCP Config** icon

    ### Enabling MCP support

    1. Open Settings with `Cmd + ,` (Mac) or `Ctrl + ,` (Windows/Linux)
    2. Search for "MCP"
    3. Enable the MCP support setting

    ### Applying changes

    Changes to MCP configuration apply automatically when you save the file. Save the config file (`Cmd+S`) and servers will reconnect.

    You can configure MCP servers at two levels:

    1. **Workspace Level**: `.kiro/settings/mcp.json`
       - Applies only to the current workspace
       - Ideal for project-specific MCP servers

    2. **User Level**: `~/.kiro/settings/mcp.json`
       - Applies globally across all workspaces
       - Best for MCP servers you use frequently

    ### Adding servers via command line

    ```bash
    # Add a new MCP server
    kiro-cli mcp add \
      --name "awslabs.aws-documentation-mcp-server" \
      --scope global \
      --command "uvx" \
      --args "awslabs.aws-documentation-mcp-server@latest" \
      --env "FASTMCP_LOG_LEVEL=ERROR"
    ```

    ### Adding servers to a specific agent

    ```bash
    kiro-cli mcp add --name git-server --agent rust-dev
    ```

    ### Viewing loaded servers

    To verify your configuration, check which MCP servers are currently loaded in an interactive chat session:

    ```bash
    /mcp
    ```

    This displays all active MCP servers, their connection status, and available tools. If a server you configured doesn't appear in the list, check the troubleshooting section below - the most common causes are JSON syntax errors and missing environment variables.

    Kiro Web loads local MCP servers from `.kiro/settings/mcp.json` in your repository. You can edit that JSON file in your repository or configure servers from the Kiro Web settings panel. See [Powers and MCP](https://kiro.dev/docs/web/sandbox/mcp.md) for complete Web-specific configuration details.

    1. Add local server definitions to `.kiro/settings/mcp.json` in your repository, or open the sandbox MCP server settings in Kiro Web (**Settings > Profile > Sandbox > MCP server settings**)
    2. In the settings panel, click **Add server**
    3. Enter the server name, type, and command

    The sandbox MCP settings panel is not shown for every account type (for example, some organization-managed sign-ins hide it). Editing `.kiro/settings/mcp.json` in your repository works on every account.

    MCP servers are loaded when the sandbox starts and remain available throughout task execution.

    ### Using environment variables and secrets

    You can reference [environment variables and secrets](https://kiro.dev/docs/web/sandbox/environment-variables.md) in your MCP configuration using the `$` syntax:

    ```json
    ",
            "SECRET_KEY": "$"
          }
        }
      }
    }
    ```

    Both environment variables and secrets use the same syntax. The values are resolved when the sandbox starts.

## MCP server loading priority

When multiple configurations define the same MCP server, they are loaded based on this hierarchy (highest to lowest priority):

1. **Agent Config** - `mcpServers` field in agent JSON
2. **Workspace MCP JSON** - `.kiro/settings/mcp.json`
3. **Global MCP JSON** - `~/.kiro/settings/mcp.json`

### Example scenarios

**Complete override:**
```
Agent config:     { "fetch": { command: "fetch-v2" } }
Workspace config: { "fetch": { command: "fetch-v1" } }
Global config:    { "fetch": { command: "fetch-old" } }

Result: Only "fetch-v2" from agent config is used
```

**Additive (different names):**
```
Agent config:     { "fetch": {...} }
Workspace config: { "git": {...} }
Global config:    { "aws": {...} }

Result: All three servers are used (fetch, git, aws)
```

**Disable via override:**
```
Agent config:     { "fetch": { command: "...", disabled: true } }
Workspace config: { "fetch": { command: "..." } }

Result: No fetch server is launched
```

## Example configurations

### Local server with environment variables

```json
{
  "mcpServers": {
    "web-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-bravesearch"
      ],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

### Remote server with headers

```json
{
  "mcpServers": {
    "api-server": {
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}",
        "X-Custom-Header": "value"
      }
    }
  }
}
```

### Multiple servers

```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"],
      "env": {
        "GIT_CONFIG_GLOBAL": "/dev/null"
      }
    },
    "aws-docs": {
      "command": "npx",
      "args": ["-y", "@aws/aws-documentation-mcp-server"]
    }
  }
}
```

## Environment variables

Many MCP servers require environment variables for authentication or configuration. Use the `$` syntax to reference environment variables:

```json
{
  "mcpServers": {
    "server-name": {
      "env": {
        "API_KEY": "${YOUR_API_KEY}",
        "DEBUG": "true",
        "TIMEOUT": "30000"
      }
    }
  }
}
```

IDE
    CLI
    Web

    For security, Kiro only expands environment variables that are explicitly approved. When you add or modify an MCP server configuration that includes unapproved environment variables, Kiro displays a security warning popup listing the variables that need approval.

    To manage approved environment variables:

    1. Open Kiro settings
    2. Search for "**Mcp Approved Env Vars**"
    3. Add the environment variables you want to allow for expansion

    Make sure to set environment variables in your shell before running Kiro CLI:

    ```bash
    export YOUR_API_KEY="your-actual-key"
    ```

    Environment variables for MCP servers in Web are configured through the sandbox settings. See [Environment variables](https://kiro.dev/docs/web/sandbox/environment-variables.md) for how to set them.

## OAuth authentication

Remote MCP servers that require OAuth authentication are supported. Kiro handles the browser-based OAuth flow automatically when connecting to an OAuth-protected server.

```json
{
  "mcpServers": {
    "remote-server-with-oauth": {
      "url": "https://api.example.com/mcp",
      "oauth": {
        "clientId": "your-client-id",
        "redirectUri": "http://127.0.0.1:8080/oauth/callback",
        "oauthScopes": ["read", "write"]
      }
    }
  }
}
```

If you encounter OAuth scope errors, use an empty array: `"oauthScopes": []`

Most servers use [Dynamic Client Registration](https://datatracker.ietf.org/doc/html/rfc7591) (DCR) and need no extra configuration - just connect, and Kiro opens the authorization page.

### OAuth configuration

For servers that don't support Dynamic Client Registration (DCR) - like Figma, Slack, or GitHub - you can provide your own OAuth credentials in the `oauth` object. This works with auth servers like **Cognito**, **Auth0**, and **Okta**.

**⚠️ Warning:** Client secret support differs by surface. The CLI supports confidential clients (`clientId` + `clientSecret`), which servers like Figma require. The IDE supports public OAuth clients only (PKCE without a client secret) - services that require a `client_secret` won't work from the IDE with this configuration.

**⚠️ Warning:** **Exact issuer matching required (RFC 8414).** When your MCP server uses a custom identity provider, Kiro validates the authorization server by comparing the URL advertised in the protected-resource metadata against the `issuer` field in the authorization-server metadata document. Every character must match exactly: scheme, host, port, path, and trailing slash. For example, `https://auth.example.com` and `https://auth.example.com/` are treated as different issuers. Kiro does not normalize either value, and a mismatch aborts discovery.

If your server fails to connect with an OAuth error, see [OAuth issuer mismatch](#oauth-issuer-mismatch) in the troubleshooting section.


```json
{
  "mcpServers": {
    "figma": {
      "url": "https://mcp.figma.com/mcp",
      "oauth": {
        "clientId": "my-figma-client-id",
        "clientSecret": "my-figma-client-secret",
        "redirectUri": "http://localhost:7778/oauth/callback",
        "oauthScopes": ["files:read"]
      }
    }
  }
}
```

To use this configuration, register an OAuth app in the Figma Developer Console. Set the redirect URI in your app settings to `http://localhost:7778/oauth/callback` - the port and path must match exactly. Figma requires a confidential client, so both `clientId` and `clientSecret` are needed.

#### OAuth properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `oauth.clientId` | String | No | Pre-registered OAuth client ID. When set, Dynamic Client Registration is skipped entirely. |
| `oauth.clientSecret` | String | No | Client secret for servers that require one. Only meaningful alongside `clientId`. |
| `oauth.redirectUri` | String | No | Custom loopback redirect URI for the OAuth callback. See [redirect URI formats](#redirect-uri-formats) below. |
| `oauth.clientMetadataUrl` | String | No | HTTPS URL of a hosted Client ID Metadata Document. When set, Kiro authenticates as that URL instead of registering a client. See [Client ID Metadata Documents](#client-id-metadata-documents-cimd) below. |
| `oauth.oauthScopes` | Array | No | OAuth scopes to request from the authorization server. Takes priority over top-level `oauthScopes`. |

#### How it works

- **No `clientId` or `clientMetadataUrl` set** - Kiro attempts Dynamic Client Registration with the server. If DCR fails, it falls back to a default client configuration.
- **`clientId` set (without `clientSecret`)** - Kiro skips DCR and authenticates as a public OAuth client using your registered client ID.
- **`clientId` and `clientSecret` both set (CLI only)** - Kiro skips DCR and authenticates as a confidential client, sending the secret to the token endpoint. This is required for servers like Figma that issue tokens only to confidential clients.
- **`clientMetadataUrl` set (without `clientId`)** - Kiro skips DCR and presents the metadata document URL as its client identity, when the authorization server supports it. See [Client ID Metadata Documents](#client-id-metadata-documents-cimd) below.

If you bring your own identity provider, your MCP server must serve authorization-server metadata at the RFC 8414 well-known URL and validate Bearer tokens against the provider's JWKS. For an issuer without a path such as `https://auth.example.com`, metadata lives at `https://auth.example.com/.well-known/oauth-authorization-server`. For a path-bearing issuer such as `https://auth.example.com/tenant1`, the well-known suffix is inserted before the path, giving `https://auth.example.com/.well-known/oauth-authorization-server/tenant1`.

#### Redirect URI formats

The `redirectUri` field accepts several formats. The host must be `127.0.0.1` or `localhost`, and the scheme must be `http` (the callback is served by a local loopback server).

| Format | Example | Description |
|--------|---------|-------------|
| Full URL | `http://localhost:7778/oauth/callback` | Pin the port and path to match a pre-registered app |
| Host and port | `127.0.0.1:7778` | Pin the port; path defaults to `/` |
| Port only | `:7778` | Pin the port on `127.0.0.1` |
| Omitted | *(not set)* | OS assigns a random available port |

Use a full URL with a custom path when your OAuth app has a pre-registered redirect URI that includes a specific callback path.

#### Client ID Metadata Documents (CIMD)

If you host a [Client ID Metadata Document](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document), set `oauth.clientMetadataUrl` to its HTTPS URL. Instead of registering a client through DCR, Kiro presents that URL as its client identity, and the authorization server fetches your document to learn the client's metadata. This works only when the authorization server advertises `client_id_metadata_document_supported`; otherwise Kiro falls back to DCR.

```json
{
  "mcpServers": {
    "enterprise-server": {
      "url": "https://mcp.example.com/mcp",
      "oauth": {
        "clientMetadataUrl": "https://apps.example.com/kiro-client.json",
        "redirectUri": "http://127.0.0.1:8080/oauth/callback"
      }
    }
  }
}
```

**⚠️ Warning:** Pair `clientMetadataUrl` with a pinned `oauth.redirectUri`. Under CIMD, the authorization server validates the callback against the `redirect_uris` listed in your hosted document, not against the request. Because Kiro assigns a random loopback port by default, an unpinned callback is rejected on every connect. Pin the port (and path) to a value your document lists - see [redirect URI formats](#redirect-uri-formats) above.

Do not set both `clientMetadataUrl` and `clientId`. When a `clientId` is present, Kiro uses it and never consults `clientMetadataUrl`.

#### Scopes

You can specify OAuth scopes in two places:

```json
{
  "mcpServers": {
    "server": {
      "url": "https://mcp.example.com",
      "oauthScopes": ["openid", "email"],
      "oauth": {
        "clientId": "my-id",
        "oauthScopes": ["read:data", "write:data"]
      }
    }
  }
}
```

When both are set, `oauth.oauthScopes` takes priority. When neither is specified, Kiro requests a default set of scopes (`openid`, `email`, `profile`, `offline_access`).

### Mid-session token refresh

When an OAuth token expires during a session and no refresh token is available, Kiro automatically triggers a new browser-based authentication flow. You don't need to restart your session - the re-authentication happens transparently and the MCP server reconnects with the new token. In the IDE, a warning indicator and **Re-authenticate** button appear in the MCP panel when a token expires.

This is particularly useful for identity providers that issue short-lived tokens without refresh tokens.

### Managing credentials (CLI)

When automatic refresh isn't sufficient - for example, if a token was revoked or you need to switch accounts - you can manage OAuth credentials manually in the CLI:

| Command | Keyboard shortcut | Description |
|---------|-------------------|-------------|
| `/mcp auth` | `^A` | Force re-authentication when a token is expired or invalid |
| `/mcp cancel-auth` | `^X` | Abort a pending auth flow stuck waiting for browser confirmation |
| `/mcp logout` | `^R` | Remove stored credentials for a server |

Keyboard shortcuts are available in the MCP panel status view. See [Slash Commands](https://kiro.dev/docs/reference/slash-commands.md#mcp-auth) for full usage details.

## Hot-reload

Agent and MCP configurations hot-reload when you save changes on disk. A file watcher monitors `.kiro/agents` directories and `mcp.json` files, reconciling the running servers and agent state without restarting your session or losing conversation context.

This applies to:

- Editing an existing agent config or `mcp.json`
- Adding or removing an agent file
- Adding, removing, or editing MCP server entries

How reconciliation works:

- **Only changed servers restart** - if you add, remove, or edit a server entry, only the affected servers are stopped or started. Unchanged servers continue running.
- **Order-independent config diff** - reordering environment variables or JSON keys does not count as a change and won't trigger a restart.
- **Session-injected servers preserved** - servers added mid-session via `/mcp add` are re-merged during reconciliation.

No command is required to trigger a reload. Save the file and the change takes effect at the next idle boundary (between turns).

## Disabling servers and tools

To temporarily disable an MCP server without removing its configuration, set `disabled` to `true`:

```json
{
  "mcpServers": {
    "server-name": {
      "disabled": true
    }
  }
}
```

To keep a server active but prevent an agent from using specific tools, use `disabledTools`:

```json
{
  "mcpServers": {
    "server-name": {
      "disabledTools": ["delete_file", "execute_command"]
    }
  }
}
```

## MCP registry (enterprise)

For enterprise teams using IAM Identity Center, MCP server access can be centrally controlled through an MCP registry. See the [MCP Registry](https://kiro.dev/docs/mcp/registry.md) page for details.

## Troubleshooting configuration

1. **Validate JSON syntax**
   - Ensure your JSON is valid with no syntax errors
   - Check for missing commas, quotes, or brackets
   - Use a JSON validator or linter

2. **Verify command paths**
   - Make sure the command specified exists in your PATH
   - Try running the command directly in your terminal

3. **Check environment variables**
   - Verify that all required environment variables are set
   - Check for typos in environment variable names

4. **OAuth issuer mismatch**
   - If an OAuth-protected server fails to connect, the authorization server URL your MCP server advertises may not exactly match the `issuer` value in the authorization-server metadata.
   - Fetch `/.well-known/oauth-protected-resource` from your MCP server. Note the URL in `authorization_servers[0]`.
   - Fetch the authorization-server metadata for that issuer URL. Per RFC 8414, for an issuer without a path (e.g. `https://auth.example.com`) the metadata endpoint is `https://auth.example.com/.well-known/oauth-authorization-server`; for a path-bearing issuer (e.g. `https://auth.example.com/tenant1`) it is `https://auth.example.com/.well-known/oauth-authorization-server/tenant1`. Compare the returned `issuer` field against `authorization_servers[0]` character-for-character: scheme, host, port, path, and trailing slash must be identical. For example, `https://auth.example.com` and `https://auth.example.com/` are treated as different issuers.
   - Correct whichever metadata source has the wrong value. Do not add client-side normalization or bypasses.

5. **Review configuration loading**
   - Check which configuration files are being loaded and their priority:

    ```bash
    # Check workspace config
    cat .kiro/settings/mcp.json

    # Check user config
    cat ~/.kiro/settings/mcp.json
    ```

## Security considerations

When configuring MCP servers, follow these security best practices:

- Use environment variable references (e.g., `$`) instead of hardcoding sensitive values
- Never commit configuration files with credentials to version control
- Only connect to trusted remote servers
- Review tool permissions before adding them to `autoApprove`
- Use `disabledTools` to restrict access to dangerous operations

For comprehensive security guidance, see the [MCP Security Best Practices](https://kiro.dev/docs/mcp/security.md) page.
