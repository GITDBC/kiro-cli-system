> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Powers

> Dynamic loading of context and MCP servers, giving your AI agent instant expertise for any framework or tool

Kiro powers give your AI agent instant access to specialized knowledge for any technology. Powers package your tools, workflows, and best practices into a format that Kiro can activate on-demand. When you mention relevant keywords, Kiro loads the power's context and tools automatically.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Install and use powers | ✓ | v3 | ✓ | — |
| Create powers | ✓ | v3 | — | — |

## Get Started

  - [Explore powers](https://kiro.dev/powers) — Browse curated powers from our launch partners and install them with one click
  - [Install power](https://kiro.dev/docs/powers/installation.md) — Install powers from the marketplace or GitHub repositories
  - [Create power](https://kiro.dev/docs/powers/create.md) — Build your own powers and share them with the community

## Concept

### The problem: context overload

**Without framework context, agents guess.** Your agent can call Stripe APIs, but does it know to use idempotent keys? It can query Neon, but does it understand connection pooling for serverless? Without built-in expertise, you're both manually reading documentation and refining approaches until the output is right. Powers give your agent (and by extension, you) instant access to specialized knowledge, so you can work in unfamiliar domains faster.

**With too much context, agents slow down.** Connect five MCP servers and your agent loads 100+ tool definitions before writing a single line of code. Five servers might consume 50,000+ tokens, 40% of your context window, before your first prompt. More tools should mean better results, but unstructured context overwhelms the agent, leading to slower responses and lower quality output.

``` mermaid
flowchart TD
    A["User starts task:<br/>'Add a database on Supabase'"] --> B["Agent Context"]
    B --> C["Figma MCP<br/>10+ tools loaded"]
    B --> D["Supabase MCP<br/>50+ tools loaded"]
    B --> E["Netlify MCP<br/>10+ tools loaded"]
    B --> F["Postman MCP<br/>80+ tools loaded"]
    B --> G["Datadog MCP<br/>20+ tools loaded"]
    C --> H["Context Overload<br/>180+ tools total"]
    D --> H
    E --> H
    F --> H
    G --> H
    H --> I["Slow responses<br/>Lower quality<br/>Irrelevant suggestions"]
    
    style H fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px
    style I fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px
```

### How powers work

Instead of loading all MCP tools at once, powers activate dynamically based on keywords in your conversation.

``` mermaid
flowchart TD
    A["User starts task:<br/>'Add a database on Supabase'"] --> B["Kiro analyzes task"]
    B --> C{"Which powers<br/>are relevant?"}
    C -->|Relevant| D["Supabase power<br/>activated"]
    C -->|Not relevant| E["Other powers<br/>not loaded"]
    D --> I["Agent Context<br/>Only relevant tools"]
    I --> J["Fast responses<br/>High quality<br/>Focused suggestions"]
    
    style D fill:#51cf66,stroke:#2f9e44,stroke-width:2px
    style I fill:#51cf66,stroke:#2f9e44,stroke-width:2px
    style J fill:#51cf66,stroke:#2f9e44,stroke-width:2px
```

When you start a task, Kiro:
1. Reads the task description
2. Evaluates installed powers against the task
3. Loads only relevant powers into context

### What's in a power?

Powers follow the [Agent Plugins](https://agent-plugins.org/) specification — an open, vendor-neutral format for packaging reusable components that extend AI agents. A power is a directory with a required manifest and optional components:

1. **plugin.json** — The manifest that identifies the power and declares its keywords for activation
2. **skills/** — Agent Skills that provide task-specific instructions, scripts, and reference material
3. **mcp.json** — MCP server configuration for tool integrations (optional)
4. **dev.kiro/** — Kiro-specific extensions like steering files (optional)

```text
my-power/
├── plugin.json          # Required manifest
├── skills/              # Agent Skills
│   └── setup/
│       ├── SKILL.md
│       └── references/
└── mcp.json             # MCP server configuration
```

Install the Stripe power with one click. When you mention "payment" or "checkout," the power activates, loading Stripe's MCP tools and skills into context. When you're done with payments and move to database work, the Supabase power activates and Stripe deactivates.

**ℹ️ Info:** Powers built with the original POWER.md format continue to work. For new powers, we recommend using the Agent Plugins format. You can convert existing powers using the [Power Builder](https://kiro.dev/launch/powers/add/?name=power-builder).

### What makes powers different

**Portable plugin format** — Powers follow the [Agent Plugins](https://agent-plugins.org/) specification, an open standard with maintainers from Amazon, Cursor, Microsoft, OpenAI, and Vercel. Build once and your power works across compatible agent clients.

**Dynamic MCP tool loading** — Traditional MCP servers load all tools upfront. Powers load tools on-demand, reducing baseline context usage while giving your agent access to dozens of technologies.

**Open ecosystem** — Browse curated powers from the [registry](https://kiro.dev/powers) including Datadog, Dynatrace, Figma, Neon, Netlify, Postman, Supabase, Stripe, Strands SDK, and AWS Aurora. Install community-built powers from GitHub URLs, or create and share your own.

**One-click install** — Browse powers directly in Kiro or on [kiro.dev/powers](https://kiro.dev/powers). Click "Install" and the power registers automatically. No JSON configuration files, no command-line setup.

## How powers differ from skills and steering

**[Powers](https://kiro.dev/docs/powers.md)** are plugins that bundle MCP tools, skills, and knowledge into a single installable package. They activate dynamically based on context. Use for integrations where you need both tools and guidance. Powers can contain skills as components.

**[Skills](https://kiro.dev/docs/skills.md)** are standalone portable instruction packages that guide agents through specific tasks. They can exist independently or be bundled inside a power. Use for reusable workflows you want to share or import.

**[Steering](https://kiro.dev/docs/steering.md)** is Kiro-specific context that shapes agent behavior. It supports `always`, `auto`, `fileMatch`, and `manual` modes. Use for project standards and conventions.

## Use cloud-synced Powers in the IDE

Cloud-synced Powers are account-backed configuration. They are separate from [cloud sessions](https://kiro.dev/docs/cloud-sessions.md), which run the agent in a managed sandbox. Use [Configuration Sync](https://kiro.dev/docs/web/cloud-configuration.md) to upload a supported local Power to your Kiro Web account. Powers you manage under **Settings > Powers** in [Kiro Web](https://app.kiro.dev/settings/powers) appear in the installed Powers list in Kiro IDE 1.0.437 or later. A cloud indicator identifies each Power. Select **Try power** to use it directly, or open its details to review its bundled Skills and MCP configuration.

Bundled MCP configuration stays attached to its Power and activates with it; it is not a standalone synced MCP server. Project MCP servers under `.kiro/settings/mcp.json` remain project configuration and travel with the repository. See [Configuration in the cloud](https://kiro.dev/docs/cloud-sessions.md#configuration-in-the-cloud) for how personal Cloud configuration differs from cloud sessions and project configuration.

## Related documentation

- [Install powers](https://kiro.dev/docs/powers/installation.md) - Install from the marketplace or GitHub
- [Create powers](https://kiro.dev/docs/powers/create.md) - Build your own powers
- [Skills](https://kiro.dev/docs/skills.md) - Portable instruction packages
- [MCP Servers](https://kiro.dev/docs/mcp.md) - Model Context Protocol configuration
