> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Create powers

> How to build your own powers using the Agent Plugins specification and share them with the community

Developers can use our curated powers from the powers registry, including Datadog, Figma, Neon, Netlify, Postman, Supabase, and Stripe, or build and share their own powers for any tool or framework. Community members have also created powers for building SaaS applications, managing AWS CDK infrastructure, and building agents with Pydantic AI.

Powers follow the [Agent Plugins](https://agent-plugins.org/) specification — an open, vendor-neutral format for packaging reusable components that extend AI agents. When you mention relevant keywords, Kiro loads the power's context and tools automatically.

View our curated powers at [kiro.dev/powers](https://kiro.dev/powers)

**ℹ️ Info:** Powers built with the legacy POWER.md format continue to work. For new powers, we recommend using the Agent Plugins format. You can convert existing powers or create new ones using the [Power Builder](https://kiro.dev/launch/powers/add/?name=power-builder).

## What you need

Every power needs a `plugin.json` manifest. Optionally, you can add:
- `skills/` — Agent Skills with task-specific instructions
- `mcp.json` — MCP server configuration for tool integrations

## Creating plugin.json

Your `plugin.json` manifest identifies the power and tells Kiro when to activate it. At minimum, it requires:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "supabase",
  "version": "1.0.0",
  "description": "Build fullstack applications with Supabase's Postgres database, authentication, storage, and real-time subscriptions",
  "author": {
    "name": "Supabase"
  },
  "keywords": ["database", "postgres", "auth", "storage", "realtime", "backend", "supabase", "rls"]
}
```

### Required fields

| Field | Description |
|-------|-------------|
| `$schema` | Schema URL: `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` |
| `name` | Plugin identifier (kebab-case, no spaces). Used internally by Kiro to identify the power. |
| `version` | Semantic version of the power (e.g., `1.0.0`). |
| `description` | Short description of what the power does. |
| `author` | Object with at minimum a `name` field. Can also include `email` and `url`. |
| `keywords` | Array of strings that trigger activation. Use terms that match how developers talk about your tool. |

**⚠️ Warning:** The `name` field is used internally by Kiro to identify the power. Changing it after installation may require users to uninstall and reinstall the power.

When someone says "Let's set up the database," Kiro sees "database" in the keywords and activates the Supabase power. The power's MCP tools and skills load into context automatically.

### Optional fields

You can also include these fields in your manifest:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "supabase",
  "version": "1.0.0",
  "description": "Build fullstack applications with Supabase",
  "author": {
    "name": "Supabase",
    "url": "https://supabase.com"
  },
  "keywords": ["database", "postgres", "supabase"],
  "homepage": "https://supabase.com/docs",
  "repository": "https://github.com/supabase/kiro-power",
  "license": "Apache-2.0"
}
```

## Adding skills

Skills are instructions that guide the agent through specific tasks. Each skill lives in its own directory under `skills/` and requires a `SKILL.md` file.

```text
skills/
└── setup/
    ├── SKILL.md
    ├── scripts/
    │   └── validate-setup.sh
    └── references/
        └── schema-patterns.md
```

### SKILL.md

The `SKILL.md` file contains the instructions the agent follows when the skill is invoked. Structure it with clear steps:

```markdown
---
name: setup
description: Set up a new Supabase project with local development
---

# Set up Supabase

## Step 1: Validate dependencies

Before using Supabase, ensure the following are installed:
- **Docker Desktop**: Required for the local development stack
  - Verify with: `docker --version`
- **Supabase CLI**: Install via npm or Homebrew
  - Verify with: `supabase --version`

## Step 2: Initialize the project

Run `supabase init` to create the project configuration.

## Step 3: Start local services

Run `supabase start` to spin up the local Supabase stack.
```

### Scripts

The `scripts/` directory holds executable files the agent can run during skill execution. Use scripts for validation, setup automation, or code generation tasks.

### References

The `references/` directory contains supplementary material like documentation, examples, or schema definitions that the agent can consult while executing the skill.

## Adding MCP servers

If your power provides MCP tools, create an `mcp.json` file at the power root:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "supabase-local": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase"],
      "env": {
        "SUPABASE_URL": "${SUPABASE_URL}",
        "SUPABASE_ANON_KEY": "${SUPABASE_ANON_KEY}"
      }
    }
  }
}
```

Use environment variables for API keys and secrets. During installation, Kiro automatically namespaces server names to avoid conflicts (e.g., `supabase-local` becomes `power-supabase-supabase-local`).

## Directory structure

Here's what a complete power looks like:

```text
power-supabase/
├── plugin.json                           # Required manifest
├── mcp.json                              # MCP server configuration
└── skills/                               # Agent Skills
    ├── setup/
    │   ├── SKILL.md
    │   └── scripts/
    │       └── validate-deps.sh
    └── migrations/
        ├── SKILL.md
        └── references/
            └── migration-patterns.md
```

## Testing locally

1. Create your power directory with the files above
2. Open Kiro → Powers panel → **Add Custom Power**
3. Select **Import power from a folder**
4. Select your power directory
5. Test activation by using keywords from your power in a conversation

## Sharing your power

Push your power to a public GitHub repository:

```bash
git init
git add plugin.json mcp.json skills/ dev.kiro/
git commit -m "Initial release"
git push origin main
```

**ℹ️ Info:** Make sure your repository is public if you want to share it broadly. Private repositories require users to have access permissions.

Others can install it via **Add Custom Power** → **Import power from GitHub** using your repository URL.

## Examples

**Minimal power (manifest only):**
```text
power-simple-tool/
├── plugin.json           # Keywords and description
└── mcp.json              # MCP server configuration
```

**Skills-only power (no MCP):**
```text
power-react-patterns/
├── plugin.json
└── skills/
    ├── component-patterns/
    │   └── SKILL.md
    └── hooks-patterns/
        └── SKILL.md
```

**Full power with all components:**
```text
power-full-stack/
├── plugin.json
├── mcp.json
└── skills/
    ├── setup/
    │   ├── SKILL.md
    │   └── scripts/
    └── deployment/
        ├── SKILL.md
        └── references/
```

## Related documentation

- [Agent Plugins specification](https://agent-plugins.org/) - The open standard powers are built on
- [Powers overview](https://kiro.dev/docs/powers.md) - What powers are and how they work
- [Install powers](https://kiro.dev/docs/powers/installation.md) - Install from the marketplace or GitHub
- [Skills](https://kiro.dev/docs/skills.md) - Standalone portable instruction packages
- [MCP configuration](https://kiro.dev/docs/mcp/configuration.md) - MCP server configuration reference
