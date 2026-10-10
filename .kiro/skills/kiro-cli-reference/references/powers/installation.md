> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Install powers

> How to install powers from the curated marketplace or GitHub repositories

Install powers from curated partners, the community, or your team's private tooling. Kiro supports both the [Agent Plugins](https://agent-plugins.org/) format (`plugin.json`) and the legacy format (`POWER.md`) — the installation experience is the same regardless of format.

**⚠️ Warning:** Kiro powers are third-party tools that may be subject to separate terms. Only install powers from trusted sources and review their documentation and licensing. Kiro is not responsible for third-party powers.

    IDE
    CLI
    Web

## Install curated powers

Browse powers from our official [registry](https://kiro.dev/powers) including Datadog, Dynatrace, Figma, Neon, Netlify, Postman, Supabase, Stripe, Strands SDK, and AWS Aurora.

### From kiro.dev

1. Browse powers at [kiro.dev/powers](https://kiro.dev/powers)
2. Select a power and click **Add to Kiro**
3. The Kiro IDE will open, allowing you to complete the installation with one click

### From the IDE

1. Open the powers panel → click on the **Ghosty icon with the lightning bolt**
2. Choose a power to view details
3. Choose **+ Install**

You can now **Try the power** to run through the power onboarding. Any time you ask a question related to that power, the Kiro agent will automatically activate and use it.

### Powers with MCPs

When you install a power that includes Model Context Protocol (MCP) integrations, Kiro automatically namespaces server names to avoid conflicts and manages the MCP servers for you.

- **Agent Plugins format (plugin.json):** MCP servers are managed internally by Kiro and are not added to your user-level `~/.kiro/settings/mcp.json` file. They activate and deactivate with the power.
- **Legacy format (POWER.md):** MCP servers are registered in your `~/.kiro/settings/mcp.json` configuration file under the Powers section.

## Install custom powers

### From public GitHub URL

1. Powers panel → **Add Custom Power**
2. Select **Import power from GitHub**
3. Enter repository URL
4. Click **Install**

Each power must have a valid `plugin.json` or `POWER.md` file at its package root. A single repository can contain multiple powers, each in its own directory.

### From local path

For powers you create or manage in private repositories, clone the repository locally and install from the local path.

1. Powers panel → **Add Custom Power**
2. Select **Import power from a folder**
3. Select power directory containing plugin.json or POWER.md
4. Click **Install**

**Example structure (Agent Plugins format):**
```text
my-custom-power/
├── plugin.json           # Required manifest
├── mcp.json              # Optional MCP server configuration
└── skills/               # Optional Agent Skills
    └── setup/
        └── SKILL.md
```

## Update powers

To update a power to the latest version:

1. Powers panel → power → **Check for updates**
2. If updates are available, click on **Install updates**

The power refreshes from the remote repository and applies the latest version.

## Using powers in the CLI

Kiro CLI v3 supports using installed powers. Powers activate automatically based on keywords in your prompts, just like in the IDE.

To install powers, use the Kiro IDE or manually add them to your powers configuration. Once installed, powers are available in both the IDE and CLI.

## Managing powers on Web

Powers on Kiro Web are a set of integrations that add specialized tools and context to the agent. To manage which powers are enabled:

1. Go to [Settings > Powers](https://app.kiro.dev/settings/powers/catalog) to view the list installed powers.
2. Click on **Install from catalog** or **Upload folder** to add a power

Enabled powers are loaded automatically when the sandbox starts and remain available throughout task execution.

## Related documentation

- [Powers overview](https://kiro.dev/docs/powers.md) - What powers are and how they work
- [Create powers](https://kiro.dev/docs/powers/create.md) - Build your own powers
- [MCP configuration](https://kiro.dev/docs/mcp/configuration.md) - MCP server configuration reference
