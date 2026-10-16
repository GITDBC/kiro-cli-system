> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Best practices

> Security best practices for configuring and using Model Context Protocol (MCP) servers with Kiro, protecting sensitive information and maintaining system security.

Use these practices to limit MCP server access, protect credentials, and verify the code you run.

## Understanding MCP security

MCP servers extend Kiro's capabilities by connecting to external services and APIs. Since MCP servers are third-party code, this introduces security considerations:

- **Access to sensitive information**: MCP servers may require API keys or tokens
- **External code execution**: By default, MCP servers run code outside Kiro's local command sandbox. You can opt stdio servers into it; see [Sandboxing stdio servers](#sandboxing-stdio-servers)
- **Data transmission**: Information flows between Kiro and external services
- **Source verification**: Review the source code and verify the server comes from a trusted source before using
- **Isolation**: Run servers in isolated environments when possible and limit the permissions granted

**⚠️ Security warning:** A stdio MCP server runs code on your machine. Without local command sandbox wrapping, it can access the files, environment variables, credentials, and network resources available to your user account. Its own actions do not require a separate approval each time, so malicious server code could read or send data after it starts.

Treat the `command` and `args` like any other executable you install. Review the source and grant only the access it needs.

When you enable `mcpSandboxing`, the local command sandbox applies its file and network limits to stdio server processes. It does not affect remote HTTP or SSE servers. Kiro does not vet third-party MCP servers. The sandbox limits what a stdio server can reach, but it does not make an untrusted server safe.

## Security principles

The MCP security model is designed with these principles:

1. **Permission Checks**: Kiro's permissions system evaluates each MCP tool call. Depending on workspace trust and active rules, Kiro denies the call, asks for approval, or runs it without a per-call prompt.
2. **Local Execution**: Stdio MCP servers run locally on your machine. Remote HTTP and SSE servers run on the provider's infrastructure, and Kiro connects to them over the network
3. **Isolation**: Each stdio MCP server runs as a separate local process
4. **Transparency**: Users can see what tools are available and what they do

## Secure configuration

### Protecting API keys and tokens

1. **Never commit configuration files** with sensitive tokens to version control
2. **Create tokens with minimal permissions** necessary for the MCP server to function (for example, use fine-grained personal access tokens for GitHub instead of classic tokens)
3. **Limit access scope** to only the repositories or resources needed
4. **Regularly rotate API keys and tokens** used in configurations
5. **Use environment variables** when possible instead of hardcoding values

### Using environment variables

Instead of hardcoding tokens in your configuration:

```json
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

Set the environment variable in your shell:

```bash
export GITHUB_TOKEN=your-token-value
```

### Approved environment variables (IDE)

For security, Kiro IDE only expands environment variables that are explicitly approved. Only variables in the approved list will be expanded when found in MCP config files.

When you add or modify an MCP server configuration that includes unapproved environment variables, Kiro displays a security warning popup listing the variables that need approval. You can approve them directly from the popup or manage them in settings.

To manage approved environment variables:

1. Open Kiro settings
2. Search for "**Mcp Approved Env Vars**"
3. Add the environment variables you want to allow for expansion

This prevents MCP servers from accessing arbitrary environment variables on your system.

### Configuration file permissions

Restrict access to your MCP configuration files:

```bash
# Set restrictive permissions on user-level config
chmod 600 ~/.kiro/settings/mcp.json

# Set restrictive permissions on workspace-level config
chmod 600 .kiro/settings/mcp.json
```

## Safe tool usage

### Tool approval process

1. **Review each tool request** carefully before approval
2. **Check the parameters** being passed to the tool
3. **Understand what the tool will do** before approving it
4. **Deny any suspicious requests** that don't match your current task

### Auto-approval guidelines

Only auto-approve tools that:

1. **Don't have write access** to sensitive systems
2. **Come from trusted sources** with verified code
3. **Are used frequently** in your workflow
4. **Have limited scope** of what they can access

```json
{
  "mcpServers": {
    "aws-docs": {
      "autoApprove": [
        "mcp_aws_docs_search_documentation",
        "mcp_aws_docs_read_documentation"
      ]
    }
  }
}
```

## Access control

- Use least-privilege principles for server permissions
- Limit file system access to necessary directories only
- Restrict network access where possible
- Use `disabledTools` to restrict access to dangerous operations:

```json
{
  "mcpServers": {
    "github": {
      "disabledTools": ["delete_repository", "force_push"]
    }
  }
}
```

### Sandboxing stdio servers

On your own machine, the local command sandbox can start stdio MCP server processes inside the same OS-level sandbox it uses for the agent's shell commands. Set `mcpSandboxing` to `true` in your sandbox configuration; the server then runs under the same network mode and `sandbox_network` host rules as sandboxed commands. Remote HTTP and SSE servers are not affected, and their network access does not follow sandbox rules.

See [Local command sandbox](https://kiro.dev/docs/sandbox.md#wrap-stdio-mcp-servers) for setup, platform requirements, and what happens when wrapping fails.

## Workspace-specific configuration

Use workspace-level configuration to keep each project's MCP server list separate:

```
project-a/
├── .kiro/
│   └── settings/
│       └── mcp.json  # Project A specific servers
project-b/
├── .kiro/
│   └── settings/
│       └── mcp.json  # Project B specific servers
```

Kiro starts a project's workspace servers only when that project is open. Workspace configuration separates server lists; it does not isolate server access. Without the [local command sandbox](#sandboxing-stdio-servers) or other OS restrictions, a workspace server can still access the files, credentials, environment variables, and network resources available to your user account.

## Credential management

- Never hardcode API keys or tokens in configuration files
- Use environment variables for sensitive data
- Rotate credentials regularly
- Store credentials securely using system keychains

## Network security

1. **Use HTTPS** for remote MCP servers
2. **Verify SSL/TLS certificates**
3. **Use firewalls** to restrict outbound connections from MCP servers
4. **Monitor network traffic** for unusual activity
5. **Be cautious** with servers that require broad network access

## Monitoring and auditing

### Checking MCP logs

    IDE
    CLI
    Web

    1. Open the Kiro panel
    2. Select the Output tab
    3. Choose "Kiro - MCP Logs" from the dropdown

    Review terminal output for server activity. Use the `/mcp` command to check server status.

    MCP server logs are not directly accessible in Web. Monitor tool usage through the session activity feed.

### Auditing tool usage

Periodically review which tools you've approved:

1. Check your MCP configuration for auto-approved tools
2. Review the MCP logs for tool usage patterns
3. Monitor server activity for unexpected behavior
4. Remove auto-approval for tools you no longer use frequently

## Responding to security incidents

If you suspect a security issue with an MCP server:

1. **Disable the server** immediately in your configuration
2. **Revoke any tokens or API keys** associated with the server
3. **Check for unauthorized activity** in the connected services
4. **Report the issue** to the MCP server maintainer

## System security

1. **Keep your system updated** with security patches
2. **Run MCP servers with minimal privileges**
3. **Use separate user accounts** for running sensitive MCP servers
4. **Only install MCP servers from trusted sources**
5. **Review tool descriptions** and documentation before installation
6. **Check for security advisories** and updates regularly
