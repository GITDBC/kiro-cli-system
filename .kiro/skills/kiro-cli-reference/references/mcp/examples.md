> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Examples

> Practical examples of using MCP servers with Kiro CLI

This guide provides information about a few sample Model Context Protocol (MCP) servers, their capabilities, and how to set them up with Kiro.

**⚠️ Warning:** Only add MCP servers from trusted sources, and review all applicable server licensing information and documentation. Kiro is not responsible for any third-party MCP servers or other packages.

## AWS Documentation server

The AWS Documentation server provides access to AWS documentation, search capabilities, and content recommendations.
Capabilities

- Search AWS documentation across all services
- Read documentation pages in markdown format
- Get content recommendations related to specific documentation pages

### Setup instructions
#### Prerequisites

1. Install uv from Astral:
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex
```

2. Install Python 3.10 or newer:

```bash
    uv python install 3.10
```

#### Configuration

For macOS/Linux:
```json
{
  "mcpServers": {
    "aws-docs": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

For Windows:
```json
{
  "mcpServers": {
    "aws-docs": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "awslabs.aws-documentation-mcp-server@latest",
        "awslabs.aws-documentation-mcp-server.exe"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

### Available tools
| Tool Name | Description |
|-----------|-------------|
|mcp_aws_docs_search_documentation |Search AWS documentation for specific topics|
|mcp_aws_docs_read_documentation	|Read AWS documentation pages in markdown format|
|mcp_aws_docs_recommend	|Get content recommendations related to a documentation page|

### Usage examples
```
# Search for information about S3 bucket policies
Search AWS documentation for S3 bucket policies

# Read specific documentation
Read the AWS Lambda function URLs documentation

# Get recommendations
Find related content to AWS ECS task definitions
```

## GitHub MCP server

The GitHub MCP server allows Kiro to interact with GitHub repositories, issues, and pull requests.

### Capabilities

- Access repository information including files, commits, and branches
- Create and manage issues and pull requests
- Search repositories for specific content

### Setup instructions

**⚠️ Warning:** The previously recommended @modelcontextprotocol/server-github package has been archived. GitHub now recommends using their official Docker-based MCP server.

### Prerequisites
1. Install Docker if not already installed:
    - Docker Desktop for macOS and Windows
    - Docker Engine for Linux

2. Create a GitHub Personal Access Token:
    - Go to GitHub Settings > Developer settings > Personal access tokens (fine-grained)
    - Generate a new token with permissions that fit the tools you need

### Configuration

Follow these steps from the official GitHub documentation:

1. Create a `.kiro/settings/mcp.json` file in your workspace directory (or edit if it already exists)
2. Add this configuration:

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", 
        "-i", 
        "--rm", 
        "-e", 
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token-here"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

For more detailed installation instructions, refer to the official GitHub MCP Server documentation.

### Common tools

The GitHub MCP server provides a comprehensive set of tools for interacting with GitHub. Here are some of the most commonly used tools organized by category:
|Category|Tool Name|Description|
|--------|---------|-----------|
|Repository Tools| search_repositories| Search for GitHub repositories|
|Repository Tools| list_branches| List branches in a repository|
|Issue Tools|list_issues|List issues in a repository|
|Issue Tools|update_issue|Update an existing issue|
|Issue Tools|add_issue_comment|Add a comment to an issue|
|Pull Request Tools|create_pull_request|	Create a new pull request|
	
### Available toolsets

The GitHub MCP server organizes its functionality into toolsets that can be enabled or disabled as needed. By default, all toolsets are enabled. You can specify which toolsets you want to enable when configuring the GitHub MCP server. This allows you to control which GitHub API capabilities are available to your AI tools.

You can specify which toolsets you want to enable when configuring the GitHub MCP server. This allows you to control which GitHub API capabilities are available to your AI tools.
Using Toolsets With Docker

When using Docker, you can pass the toolsets as environment variables:
```bash
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=<your-token> \
  -e GITHUB_TOOLSETS="repos,issues,pull_requests,actions,code_security,experiments" \
  ghcr.io/github/github-mcp-server
```

### Usage examples
```
# Get repository information
Show me information about the tensorflow/tensorflow repository

# Search for code
Find examples of React hooks in facebook/react

# Create an issue
Create an issue in my repository about the login bug
```

## Custom MCP servers

You can create your own MCP servers to extend Kiro's capabilities for your specific needs.

### Creating a custom server

1. Choose a programming language (Python, Node.js, etc.)
2. Implement the MCP protocol using available libraries
3. Define your tools and their capabilities
4. Package and distribute your server

#### Resources for custom server development

- [MCP Protocol Specification](https://modelcontextprotocol.io/specification/2025-06-18)
- [MCP Server Template (Python)]()
- [MCP Server Template (Node.js)]()

### Additional MCP servers
#### Database servers
- **PostgreSQL MCP Server**: Query and manage PostgreSQL databases
- **MongoDB MCP Server**: Interact with MongoDB databases

#### Development tools
- **Docker MCP Server**: Manage Docker containers and images
- **Kubernetes MCP Server**: Interact with Kubernetes clusters

### Finding more MCP servers

To discover additional MCP servers:
- Visit the [MCP Registry](https://github.com/modelcontextprotocol/registry)
- Check the [GitHub MCP Organization](https://github.com/modelcontextprotocol)
- Search for **mcp-server** on npm or PyPI

## In the meantime

While we prepare comprehensive examples, you can:

- Review [Security Best Practices](https://kiro.dev/docs/mcp/security.md) for secure integration
- Visit the [official MCP documentation](https://modelcontextprotocol.io/introduction)
- Return to [MCP Overview](https://kiro.dev/docs/mcp.md)

## Next steps

- Review [Security Best Practices](https://kiro.dev/docs/mcp/security.md)
- Return to [MCP Overview](https://kiro.dev/docs/mcp.md)
