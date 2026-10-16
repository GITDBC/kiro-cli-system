> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Tools

> Learn how to use MCP tools, prompts, resource templates, and elicitation with Kiro for enhanced productivity and specialized capabilities.

MCP servers can expose tools, prompts, and resource templates to Kiro. This page covers how to interact with each of these capabilities across all surfaces.

## Interacting with MCP tools

Once you've [configured MCP servers](https://kiro.dev/docs/mcp/configuration.md), you can interact with their tools in several ways:

### Direct questions

The simplest way to use MCP tools is to ask questions related to the server's domain:

```
Tell me about Amazon Bedrock
```


```
How do I configure S3 bucket policies?
```

Kiro automatically selects the appropriate MCP tool based on your question.

### Specific tool requests

You can request specific MCP tools by describing what you want to do:

```
Search AWS documentation for information about ECS task definitions
```


```
Get recommendations for AWS CloudFormation best practices
```

### Explicit context (IDE)

In the IDE, you can provide explicit context to the tool picker:

```
#[aws-docs] search_documentation Tell me about AWS Lambda
```

This format specifies both the server (`aws-docs`) and the tool (`search_documentation`).

## Managing MCP tools

    IDE
    CLI
    Web

    ### MCP tools panel

    The Kiro panel includes an MCP servers tab that provides:

    - A list of all configured MCP servers
    - Connection status indicators
    - Individual tool management
    - Quick access to server tools

    To access the MCP panel:

    1. Select the Kiro icon in the activity bar
    2. Navigate to the MCP servers tab
    3. View all connected servers and their available tools

    ### Managing individual tools

    Each MCP server can expose multiple tools. You can enable or disable specific tools without affecting the entire server:

    **Via the Kiro Panel:**

    1. Open the Kiro panel and navigate to MCP servers
    2. Expand a server to see its available tools
    3. Click on a tool to see options:
       - **Enable** - Activate a disabled tool
       - **Disable** - Temporarily disable a tool without removing the server
    4. Disabled tools show a "Disabled" label and won't be available to Kiro

    **Via JSON Config:**

    Use the `disabledTools` array in your MCP configuration to permanently disable specific tools:

    ```json
    
      }
    }
    ```

    This is useful for:
    - **Blocking dangerous operations** (like delete or force push)
    - **Reducing tool clutter** by hiding tools you don't use
    - **Improving performance** by limiting the tools Kiro considers
    - **Enforcing team policies** when sharing workspace configurations

    ### Server-level actions

    Right-click on a server in the MCP panel to access additional options:

    - **Reconnect** - Restart the connection to the server
    - **Disable** - Temporarily disable the entire server
    - **Disable All Tools** - Disable all tools from this server at once
    - **Enable All Tools** - Re-enable all previously disabled tools
    - **Show MCP Logs** - View detailed logs for troubleshooting

    ### Viewing available tools

    Use the `/tools` command in an interactive session to see all available MCP tools and their token usage.

    ### Tool Search

    Kiro CLI 2.31 and later local V3 sessions load MCP tools on demand automatically. You do not need to enable a setting.

    In V2 sessions, Tool Search remains opt-in:

    ```bash
    kiro-cli settings toolSearch.enabled true
    ```

    See [Tool Search](https://kiro.dev/docs/mcp/tool-search.md) for V2 thresholds and how on-demand loading works.

In Kiro Web, MCP tools are managed from the sandbox settings panel. Go to [Settings > Agent](https://app.kiro.dev/settings/agent) to configure which MCP servers are loaded into your sessions.

Tools from configured servers are available automatically - the agent can invoke them without additional setup. See [Sandbox > Powers and MCP](https://kiro.dev/docs/web/sandbox/mcp.md) for configuration details.

**ℹ️ Info:** Remote HTTP/SSE MCP servers are not supported in Web. Only local stdio servers configured in the sandbox are available.

## Tool approval process

When Kiro wants to use an MCP tool, it requests your approval first:

1. You'll see a prompt describing the tool and its purpose
2. Review the tool details and parameters
3. Click "Approve" to allow the tool to run, or "Deny" to prevent it

### Auto-approving trusted tools

To avoid repeated approval prompts for tools you trust, add tool names to the `autoApprove` array in your MCP configuration:

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

**ℹ️ Info:** In an untrusted workspace, every MCP tool call asks for approval, including tools listed in `autoApprove`, and a call retried after the server asks you to sign in or open a URL asks again. Before any MCP tool runs, Kiro also checks that its approval is still current, so an approval withdrawn or changed while the call was waiting is not applied. See [Workspace trust](https://kiro.dev/docs/permissions.md#workspace-trust).

## Examples by server type

### AWS Documentation server

#### Searching documentation

```
Search AWS documentation for S3 bucket versioning
```

This uses the `mcp_aws_docs_search_documentation` tool to find relevant AWS documentation.

#### Reading documentation

```
Read the AWS Lambda function URLs documentation
```

This uses the `mcp_aws_docs_read_documentation` tool to retrieve and display documentation content.

#### Getting recommendations

```
Find related content to AWS ECS task definitions
```

This uses the `mcp_aws_docs_recommend` tool to suggest related documentation.

### GitHub MCP server

#### Repository information

```
Show me information about the tensorflow/tensorflow repository
```

This retrieves details about the specified GitHub repository.

#### Code search

```
Find examples of React hooks in facebook/react
```

This searches for code matching your query in the specified repository.

#### Issue management

```
Create an issue in my repository about the login bug
```

This helps you create a new GitHub issue with appropriate details.

## Advanced usage techniques

### Chaining MCP tools

You can use multiple MCP tools in sequence for complex tasks:

```
First search AWS documentation for ECS task definitions, then find related content about service discovery
```

### Combining with local context

MCP tools work best when combined with your local context:

```
Based on my Terraform code, help me optimize my AWS Lambda configuration using best practices from AWS documentation
```

## MCP prompts

MCP servers can expose reusable [prompt templates](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts) that provide pre-built instructions for common tasks. A prompt is a structured message template defined by the server, with an optional set of arguments you can fill in to customize it. Prompts appear alongside other context providers in the `#` mention list in chat.

### Accessing prompts

1. Type `#` in the chat input to open the context provider menu
2. MCP prompts from connected servers appear in the list with an MCP icon
3. Select a prompt to insert it into your message

If a prompt has no arguments, the resolved content is inserted directly into your chat context.

### Prompts with arguments

Some prompts accept arguments to customize their behavior. When you select a prompt that requires input, an inline form appears where you fill in the parameters before the prompt is added to your message.

For example, a server might expose a `code_review` prompt with a required `code` argument and an optional `language` argument. After you complete the form, the server resolves the prompt and the resulting content is inserted into the chat context.

Prompts are always user-initiated - Kiro never sends a prompt to a server without you selecting it. The list of available prompts updates automatically when servers add or remove them.

For the full protocol details, see the [MCP prompts specification](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts).

## MCP resource templates

MCP servers can also expose resource templates, which are parameterized URI templates that resolve to specific content. Like prompts, resource templates appear in the `#` mention list in chat.

### Accessing resource templates

1. Type `#` in the chat input to open the context provider menu
2. Resource templates from connected servers appear in the list with an MCP icon
3. Select a template to see its argument form

### Filling in template parameters

When you select a resource template, an inline form appears for you to provide the template parameters. After you submit the form, Kiro resolves the URI and includes the resulting resource content as context in your conversation.

For example, a documentation server might expose a template like `docs:///`. You would fill in the topic and version fields, and the resolved documentation content becomes available to Kiro.

## MCP elicitation

During tool execution, an MCP server may need additional information from you to complete its task. This is called [elicitation](https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation). Rather than failing or guessing, the server pauses and asks you directly.

### Form-based elicitation

When a tool needs more input, it sends an elicitation request with a message explaining what it needs. Kiro renders an inline form in the execution timeline with fields based on the type of data requested:

| Field type | Rendered as |
|------------|-------------|
| Text | Text input (may include format hints like email or date) |
| Number | Number input |
| Yes/No | Checkbox |
| Choice | Select dropdown |

Required fields are marked, and default values are pre-filled when provided by the server.

After reviewing the form, you can submit your responses, decline the request, or dismiss it. If you decline or dismiss, the server decides how to proceed - it might offer alternatives or skip the step entirely.

For the full schema details, see the [MCP elicitation specification](https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation).

### URL-based elicitation

Some servers request that you visit an external URL, for example to complete an OAuth authorization flow. In this case, Kiro displays the URL with an **Open** button in the execution timeline. After you complete the external action, the tool continues execution.

### Security considerations

Kiro always shows you which server is requesting information and what data it needs. You can decline any elicitation request at any time. Servers should not request sensitive information like passwords through elicitation - if you see such a request, consider whether you trust the server.

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

## Troubleshooting tool usage

If you encounter issues when using MCP tools:

### Tool not responding

1. Check the MCP server status in the Kiro panel (IDE) or use `/mcp` (CLI)
2. Review the MCP logs for error messages
3. Try reconnecting the server

### Incorrect results

1. Try rephrasing your request to be more specific
2. Check that you're using the appropriate tool for your task
3. Verify that the MCP server has the necessary permissions

### Tool not available

1. Ensure the MCP server is properly configured
2. Check that the server is running and connected
3. Verify that you have the necessary permissions to use the tool

## Best practices

- **Be specific** in your requests to get the most relevant results
- **Start with direct questions** before using explicit tool references
- **Auto-approve only tools** you trust and use frequently
- **Combine MCP tools** with local context for best results
- **Check tool parameters** before approval to ensure they're correct

---

*For information on available MCP servers, see the [Server directory](https://kiro.dev/docs/mcp/servers.md) page.*
