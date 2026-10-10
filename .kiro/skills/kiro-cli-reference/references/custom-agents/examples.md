> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Agent examples

> Real-world examples of custom agents for common development workflows

This page provides practical examples of custom agents you can use as starting points for your own workflows.

**ℹ️ Info:** Some examples below show both the current (v3) format and the older (v2) format for comparison. Use the [`/upgrade-agent`](https://kiro.dev/docs/custom-agents/configuration-reference.md#upgrading-from-older-configs) command to convert older configs automatically.

## AWS specialist agent

This custom agent is optimized for AWS infrastructure management. It pre-approves safe operations while restricting destructive commands.

IDE 1.0 / CLI 3.0
IDE 0.x / CLI 2.x (legacy)

```json
{
  "name": "aws-specialist-agent",
  "description": "Specialized agent for AWS infrastructure and development tasks",
  "prompt": "You are an expert AWS infrastructure specialist with deep knowledge of cloud architecture and best practices",
  "tools": ["read", "write", "shell", "@git"],
  "permissions": {
    "rules": [
      { "capability": "shell", "match": ["aws *", "terraform *", "git *"], "effect": "allow" },
      { "capability": "fs_write", "match": ["infrastructure/**", "scripts/**", "*.yaml", "*.yml"], "effect": "allow" },
      { "capability": "shell", "match": ["rm -rf *", "sudo *"], "effect": "deny" }
    ]
  },
  "resources": [
    "file://README.md",
    "file://infrastructure/**/*.yaml",
    "file://docs/aws-setup.md"
  ],
  "hooks": [
    {
      "name": "check-aws-identity",
      "trigger": "SessionStart",
      "action": { "type": "command", "command": "aws sts get-caller-identity" }
    }
  ],
  "model": "claude-sonnet-4"
}
```


```json
{
  "name": "aws-specialist-agent",
  "description": "Specialized custom agent for AWS infrastructure and development tasks",
  "prompt": "You are an expert AWS infrastructure specialist with deep knowledge of cloud architecture and best practices",
  "tools": ["read", "write", "shell", "aws"],
  "allowedTools": ["read", "aws"],
  "toolsSettings": {
    "aws": { "allowedServices": ["s3", "lambda", "cloudformation", "ec2", "iam", "logs"] },
    "write": { "allowedPaths": ["infrastructure/**", "scripts/**", "*.yaml", "*.yml", "*.json"] }
  },
  "resources": ["file://README.md", "file://infrastructure/**/*.yaml", "file://docs/aws-setup.md"],
  "hooks": {
    "agentSpawn": [{ "command": "aws sts get-caller-identity" }]
  },
  "model": "claude-sonnet-4"
}
```

**Use cases:**
- Deploying CloudFormation stacks
- Managing S3 buckets and Lambda functions
- Troubleshooting AWS service issues
- Reviewing and updating infrastructure as code

## Development workflow agent

This custom agent is designed for general software development tasks, including code review, testing, and Git operations.

IDE 1.0 / CLI 3.0
IDE 0.x / CLI 2.x (legacy)

```json
{
  "name": "development-workflow-agent",
  "description": "General development workflow agent with Git integration",
  "prompt": "You are a software development assistant with expertise in Git workflows and code management",
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${GITHUB_PAT}" },
      "disabledTools": ["create_issue", "update_issue", "create_pull_request", "merge_pull_request", "push_files", "delete_file"]
    }
  },
  "tools": ["read", "write", "shell", "@github/issue_read", "@github/search_issues"],
  "allowedTools": ["read", "@github/issue_read", "@github/search_issues"],
  "toolAliases": {
    "@github/issue_read": "issue",
    "@github/search_issues": "issues"
  },
  "permissions": {
    "rules": [
      { "capability": "fs_write", "match": ["src/**", "tests/**", "docs/**", "*.md", "*.json"], "effect": "allow" },
      { "capability": "shell", "match": ["git *", "npm *"], "effect": "allow" },
      { "capability": "mcp", "match": ["@github/issue_read", "@github/search_issues"], "effect": "allow" }
    ]
  },
  "resources": [
    "file://README.md",
    "file://CONTRIBUTING.md",
    "file://docs/**/*.md"
  ],
  "hooks": [
    {
      "name": "git-status",
      "trigger": "SessionStart",
      "action": { "type": "command", "command": "git status --porcelain" }
    },
    {
      "name": "current-branch",
      "trigger": "SessionStart",
      "action": { "type": "command", "command": "git branch --show-current" }
    }
  ]
}
```


```json
{
  "name": "development-workflow-agent",
  "description": "General development workflow agent with Git integration",
  "prompt": "You are a software development assistant with expertise in Git workflows and code management",
  "mcpServers": {
    "git": { "command": "git-mcp-server", "args": [], "timeout": 30000 }
  },
  "tools": ["read", "write", "shell", "@git"],
  "allowedTools": ["read", "@git/git_status", "@git/git_log", "@git/git_diff"],
  "toolAliases": { "@git/git_status": "status", "@git/git_log": "log", "@git/git_diff": "diff" },
  "toolsSettings": {
    "write": { "allowedPaths": ["src/**", "tests/**", "docs/**", "*.md", "*.json"] }
  },
  "resources": ["file://README.md", "file://CONTRIBUTING.md", "file://docs/**/*.md"],
  "hooks": {
    "agentSpawn": [{ "command": "git status --porcelain" }, { "command": "git branch --show-current" }]
  }
}
```

**Use cases:**
- Code review and analysis
- Writing and updating tests
- Git workflow management
- Documentation updates

## Code review agent

This custom agent focuses specifically on code review tasks, with tools and context optimized for analyzing code quality, security, and best practices.

IDE 1.0 / CLI 3.0
IDE 0.x / CLI 2.x (legacy)

```json
{
  "name": "code-review-agent",
  "description": "Specialized agent for code review and quality analysis",
  "prompt": "You are a code review specialist focused on quality, security, and best practices",
  "tools": ["read", "shell"],
  "allowedTools": ["read"],
  "permissions": {
    "rules": [
      { "capability": "shell", "match": ["grep *", "find *", "git diff *", "git log *", "eslint *", "pylint *"], "effect": "allow" },
      { "capability": "shell", "match": ["rm *", "sudo *"], "effect": "deny" }
    ]
  },
  "resources": [
    "file://CONTRIBUTING.md",
    "file://docs/coding-standards.md",
    "file://.eslintrc.json",
    "file://pyproject.toml"
  ],
  "hooks": [
    {
      "name": "changed-files",
      "trigger": "SessionStart",
      "action": { "type": "command", "command": "git diff --name-only HEAD~1" }
    }
  ]
}
```


```json
{
  "name": "code-review-agent",
  "description": "Specialized agent for code review and quality analysis",
  "prompt": "You are a code review specialist focused on quality, security, and best practices",
  "tools": ["read", "shell"],
  "allowedTools": ["read", "shell"],
  "toolsSettings": {
    "shell": {
      "allowedCommands": ["grep", "find", "wc", "head", "tail", "diff", "git diff", "git log", "eslint", "pylint"]
    }
  },
  "resources": ["file://CONTRIBUTING.md", "file://docs/coding-standards.md", "file://.eslintrc.json", "file://pyproject.toml"],
  "hooks": {
    "agentSpawn": [{ "command": "git diff --name-only HEAD~1" }]
  }
}
```

**Use cases:**
- Reviewing pull requests for code quality
- Identifying security vulnerabilities
- Checking adherence to coding standards
- Suggesting improvements and refactoring

## Project-specific agent

This example shows how to create a custom agent tailored to a specific project, including project-specific MCP servers, documentation, and build processes.

IDE 1.0 / CLI 3.0
IDE 0.x / CLI 2.x (legacy)

```json
{
  "name": "mobile-app-agent",
  "description": "Agent for the mobile app backend project",
  "prompt": "You are a backend development specialist for mobile applications with expertise in Docker and database management",
  "mcpServers": {
    "docker": {
      "command": "docker-mcp-server",
      "args": ["--socket", "/var/run/docker.sock"]
    },
    "database": {
      "command": "postgres-mcp-server",
      "args": ["--connection", "postgresql://localhost:5432/myapp"],
      "env": { "PGPASSWORD": "${DATABASE_PASSWORD}" }
    }
  },
  "tools": ["read", "write", "shell", "@docker", "@database"],
  "allowedTools": ["read", "@docker/docker_ps", "@docker/docker_logs", "@database/query_read_only"],
  "toolAliases": {
    "@docker/docker_ps": "containers",
    "@docker/docker_logs": "logs",
    "@database/query_read_only": "query"
  },
  "permissions": {
    "rules": [
      { "capability": "fs_write", "match": ["src/**", "tests/**", "migrations/**", "docker-compose.yml", "Dockerfile"], "effect": "allow" },
      { "capability": "shell", "match": ["npm test", "npm run build", "docker-compose *"], "effect": "allow" },
      { "capability": "shell", "match": ["rm -rf *", "sudo *"], "effect": "deny" }
    ]
  },
  "resources": [
    "file://README.md",
    "file://docs/api-documentation.md",
    "file://docs/database-schema.md",
    "file://docker-compose.yml"
  ],
  "hooks": [
    {
      "name": "compose-status",
      "trigger": "SessionStart",
      "action": { "type": "command", "command": "docker-compose ps" }
    },
    {
      "name": "git-status",
      "trigger": "SessionStart",
      "action": { "type": "command", "command": "git status --porcelain" }
    }
  ]
}
```


```json
{
  "name": "mobile-app-agent",
  "description": "Agent for the mobile app backend project",
  "prompt": "You are a backend development specialist for mobile applications with expertise in Docker and database management",
  "mcpServers": {
    "docker": { "command": "docker-mcp-server", "args": ["--socket", "/var/run/docker.sock"] },
    "database": { "command": "postgres-mcp-server", "args": ["--connection", "postgresql://localhost:5432/myapp"], "env": { "PGPASSWORD": "$DATABASE_PASSWORD" } }
  },
  "tools": ["read", "write", "shell", "@docker", "@database"],
  "allowedTools": ["read", "@docker/docker_ps", "@docker/docker_logs", "@database/query_read_only"],
  "toolAliases": { "@docker/docker_ps": "containers", "@docker/docker_logs": "logs", "@database/query_read_only": "query" },
  "toolsSettings": {
    "write": { "allowedPaths": ["src/**", "tests/**", "migrations/**", "docker-compose.yml", "Dockerfile"] },
    "shell": { "allowedCommands": ["npm test", "npm run build", "docker-compose up", "docker-compose down"] }
  },
  "resources": ["file://README.md", "file://docs/api-documentation.md", "file://docs/database-schema.md", "file://docker-compose.yml"],
  "hooks": {
    "agentSpawn": [{ "command": "docker-compose ps" }, { "command": "git status --porcelain" }]
  }
}
```

**Use cases:**
- Managing Docker containers and services
- Running database queries and migrations
- Building and testing the application
- Debugging production issues

## Remote MCP server integration

This example shows an agent configured to use a remote MCP server:

```json
{
  "name": "domain-finder",
  "description": "Agent with access to domain search capabilities",
  "prompt": "You help users find and research domain names using the find-a-domain service.",
  "mcpServers": {
    "find-a-domain": {
      "type": "http",
      "url": "https://api.findadomain.dev/mcp"
    }
  },
  "tools": ["@find-a-domain"],
  "allowedTools": ["@find-a-domain"]
}
```

This agent provides access to domain search tools through a remote MCP server. If the server requires OAuth authentication, use the `/mcp` command to authenticate when prompted.

### With OAuth configuration

For servers requiring OAuth with specific scopes:

```json
{
  "name": "github-agent",
  "description": "Agent with GitHub API access",
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.github.com/mcp",
      "oauthScopes": ["repo", "user", "read:org"]
    }
  },
  "tools": ["@github"],
  "allowedTools": ["@github"]
}
```

If you encounter OAuth scope errors, you can use an empty array to bypass scope requirements:

```json
{
  "name": "github-agent",
  "description": "Agent with GitHub API access",
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.github.com/mcp",
      "oauthScopes": []
    }
  },
  "tools": ["@github"],
  "allowedTools": ["@github"]
}
```

## Tips for creating effective custom agents

- **Start simple** - Begin with basic tool configurations and add complexity as needed
- **Use descriptive names** - Choose custom agent names that clearly indicate their purpose
- **Include relevant context** - Add project documentation and configuration files to resources
- **Pre-approve safe tools** - Include frequently used, low-risk tools in allowedTools
- **Use hooks for dynamic context** - Include current system state through command hooks
- **Limit tool scope** - Use toolsSettings to restrict tool access to relevant paths and services
- **Test thoroughly** - Verify that your custom agent configuration works as expected
- **Document your custom agents** - Use clear descriptions to help team members understand custom agent purposes

## Next steps

- [Creating custom agents](https://kiro.dev/docs/custom-agents/creating.md)
- [Configuration reference](https://kiro.dev/docs/custom-agents/configuration-reference.md) - full details on all fields
- [Upgrading older configs](https://kiro.dev/docs/custom-agents/configuration-reference.md#upgrading-from-older-configs) - use `/upgrade-agent` to migrate v2 configs
- [Troubleshooting](https://kiro.dev/docs/custom-agents/troubleshooting.md) - resolve common issues
