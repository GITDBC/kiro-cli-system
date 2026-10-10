> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Web tools

> Control whether Kiro users can use web search and web fetch tools.

The **Web Tools** setting controls whether users can use the `web_search` and `web_fetch` tools for searching the web and fetching content from URLs.

When web tools are enabled (the default), users can search the web and fetch content from URLs directly within Kiro. When disabled, these tools are hidden from users and a notification appears in `/tools` indicating that web access has been disabled by their administrator.

**⚠️ Warning:** Web tools use policy is enforced at the client level. As with any client-enforced configuration, they are subject to modification by users with administrative access to their local machine.

## Disabling web tools

To disable both the web fetch and web search tools for all Kiro users in your account or organization:

1. Open the Kiro console
1. Choose **Settings**
1. Under **Shared settings**, toggle **Web search and web fetch tools** to **Off**
