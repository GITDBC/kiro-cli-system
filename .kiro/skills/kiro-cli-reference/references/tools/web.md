> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Web tools

> Search the web and fetch page content - real-time internet access for the Kiro agent

Web tools let Kiro access current information from the internet in real-time, grounding responses with up-to-date search results and page content. These tools are designed not to reproduce meaningful chunks of text, and they work with publicly accessible webpages.

Web tools are available across all surfaces (IDE, CLI, Web, and Mobile).

| Tool | Description |
|------|-------------|
| `web_search` | Search the web for current information |
| `web_fetch` | Fetch and extract text from a URL |

**ℹ️ Network and proxy behavior:** Request origin depends on the session. In local IDE and CLI sessions, `web_fetch` runs from your machine and honors standard proxy environment variables (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`). In Kiro Web, Mobile, and IDE or CLI cloud sessions, it runs in the managed sandbox and follows the sandbox's [internet access settings](https://kiro.dev/docs/web/sandbox/internet-access.md). For local firewall configuration, see [Firewalls](https://kiro.dev/docs/privacy-and-security/firewalls.md).

In the following demo, the agent automatically uses `web_search` to return up-to-date results for a query, then uses `web_fetch` to retrieve the latest contents at a specific URL:

[Video](https://kiro.dev/videos/web-fetch-ide.mp4)

## web_search

Searches the web and returns relevant results. The agent uses this automatically when you ask about current events, recent changes, or topics beyond the model's training data.

```text
> What is the latest on EC2 instances?

Searching the web for: AWS EC2 instances latest 2025 (using tool: web_search)
✓ Found 10 search results
```

## web_fetch

Fetches and extracts text content from a specific URL. Supports three modes for managing context efficiently.

### Fetch modes

| Mode | Behavior | Use case |
|------|----------|----------|
| `selective` (default) | Returns up to 8,000 characters around search term matches | Targeted extraction with bounded output |
| `truncated` | First 8,000 characters | Quick preview |
| `full` | Complete content (up to 10 MB) | Comprehensive analysis |

```text
> Get installation info from https://kiro.dev/blog/introducing-kiro-cli/

Fetching content from: https://kiro.dev/blog/introducing-kiro-cli/
(searching for: installation install getting started) [mode: selective]
✓ Fetched 7909 bytes (selective) from URL
```

When no specific content is requested, the tool defaults to `truncated` mode (first 8 KB) to manage context.

### URL handling

In the IDE, `web_fetch` keeps the URL's query string and fragment and upgrades HTTP URLs to HTTPS before fetching. If a URL contains a username or password, Kiro removes those credentials and notes the change in the result.

### Limitations

| Constraint | Value |
|-----------|-------|
| Maximum page size | 10 MB |
| Maximum selective output | 8,000 characters |
| Timeout | 30 seconds |
| Maximum redirects | 10 |
| CLI V3 redirect policy | Refuses redirects to another origin or to HTTP |
| Content type | text/HTML only |
| CLI V3 transient-failure retries | 1 automatic retry |

## Governance (enterprise)

**⚠️ Usage responsibility:** You are responsible for your use of output that incorporates web search or grounded information. Citations are provided for grounded content - retain and display them if you show the output to downstream users.

Administrators using IAM Identity Center can disable web tools for their organization:

1. Open the Kiro console
2. Choose **Settings**
3. Under **Shared settings**, toggle **Web search and web fetch tools** to **Off**

**⚠️ Warning:** This restriction is enforced on the client side. Be aware that your end users could circumvent it.

See [Enterprise governance - Web tools](https://kiro.dev/docs/enterprise/governance/web-tools.md) for details.

## Disabling web tools per agent

To prevent an agent from using web tools, exclude the `web` tag:

```json
{
  "tools": ["read", "write", "shell"],
  "excludedTools": ["web"]
}
```

Or use permissions to deny web access:

```yaml
rules:
  - capability: web_fetch
    effect: deny
  - capability: web_search
    effect: deny
```

## Next steps

- [Built-in tools overview](https://kiro.dev/docs/tools.md) - full tool catalog
- [Permissions](https://kiro.dev/docs/permissions.md) - configure capability-based access control
