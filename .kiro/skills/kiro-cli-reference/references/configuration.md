> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Configuration scopes

> How Kiro resolves configuration across global, project, and agent scopes — complete reference of all configurable features

Kiro uses a layered configuration system with three scopes. Configuration closer to your current context takes priority over broader settings.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Global scope (`~/.kiro/`) | ✓ | ✓ | — | — |
| Project scope (`.kiro/`) | ✓ | ✓ | ✓ | ✓ |
| Agent scope (`.kiro/agents/` or `~/.kiro/agents/`) | ✓ | ✓ | — | — |

## Scopes

1. **Global** — applies across all projects. Stored in `~/.kiro/`.
2. **Project** — specific to a workspace. Stored in `<project-root>/.kiro/`.
3. **Agent** — defined per agent in `~/.kiro/agents/` (global) or `.kiro/agents/` (project).

**💡 Override the global directory with KIRO_HOME:** Set the `KIRO_HOME` environment variable to redirect the global `~/.kiro` directory to a different location. Agents, skills, steering, settings, and sessions all resolve against `KIRO_HOME` when it's set — useful for keeping separate Kiro profiles on the same machine.

## Inspect configuration in V3

In a local or cloud V3 session, run `/config` to review the configuration used by that session:

```bash
# Open the category summary
/config

# Open a category directly
/config steering
```

The summary covers agents, MCP servers, Powers, Steering, Skills, and Hooks. It shows the number or status of configured items and lets you open each category. `/config` is not available in V1 or V2.

### Source labels

When Kiro has configuration-origin information, the **Source** column identifies items as `local`, `cloud`, or `local + cloud`. If a local session has no source information for any item, Kiro omits the column instead of labeling every item by guesswork. In a cloud session, the session's configuration is shown as cloud-sourced.

A `cloud` label reports where the active configuration came from. Opening `/config` does not upload your local files or synchronize them with cloud configuration. If cloud configuration is not enabled for your account, the panel remains available and shows local configuration without cloud-backed items.

### Apply cloud configuration to local sessions

Use [Configuration Sync](https://kiro.dev/docs/web/cloud-configuration.md) in Kiro Web to upload supported folders from your personal `.kiro` directory. The uploaded configuration applies to cloud sessions automatically.

To use the cloud copy in local work, enable **Apply your cloud configuration to local sessions** on the Configuration Sync page. New local CLI sessions then load your cloud Steering files, custom agents, Skills, Powers, and Hooks. This option does not write cloud content to your local `.kiro` directory or replace existing local files.

### Read-only and routed views

The category summary and the in-panel Powers, Steering, and Skills lists are read-only. Selecting Agents opens the existing agent picker, where you can switch agents. MCP servers and Hooks open their existing panels. `/config` does not edit or upload configuration files itself, but some linked views are interactive.

## File paths

| Configuration | Global scope | Project scope |
|---------------|-------------|---------------|
| [MCP servers](https://kiro.dev/docs/mcp/configuration.md) | `~/.kiro/settings/mcp.json` | `.kiro/settings/mcp.json` |
| [Permissions](https://kiro.dev/docs/permissions.md) | `~/.kiro/settings/permissions.yaml` | `~/.kiro/workspace-roots/<hash>/permissions.yaml` (per-user, outside the repo) |
| [Custom agents](https://kiro.dev/docs/custom-agents.md) | `~/.kiro/agents/` | `.kiro/agents/` |
| [Steering](https://kiro.dev/docs/steering.md) | `~/.kiro/steering/` | `.kiro/steering/` |
| [Skills](https://kiro.dev/docs/skills.md) | `~/.kiro/skills/` | `.kiro/skills/` |
| [Hooks](https://kiro.dev/docs/hooks.md) | `~/.kiro/hooks/` | `.kiro/hooks/` |
| [Powers](https://kiro.dev/docs/powers.md) | `~/.kiro/powers/` | — |
| [Specs](https://kiro.dev/docs/specs.md) | — | `.kiro/specs/` |
| Settings (CLI) | `~/.kiro/settings/cli.json` | — |

## What each scope supports

Not every feature is available at every scope. The table below shows where each configuration can be defined and whether it can be embedded in an agent profile.

| Configuration | Global | Project | Agent scope |
|---------------|:------:|:-------:|:-----------:|
| MCP servers | ✓ | ✓ | ✓ (`mcpServers` field or `includeMcpJson`) |
| Permissions | ✓ | ✓ | ✓ (`permissions` field) |
| Custom agents | ✓ | ✓ | N/A |
| Steering | ✓ | ✓ | ✓ (`resources` field) |
| Skills | ✓ | ✓ | ✓ (`resources` field) |
| Hooks | ✓ | ✓ | ✓ (CLI only, `hooks` field) |
| Powers | ✓ | — | ✓ (`includePowers` field) |
| Specs | — | ✓ | — |
| Settings | ✓ | — | — |

## Resolving conflicts

When the same configuration exists in multiple scopes, the scope closest to your current context wins:

| Configuration | Priority (highest → lowest) |
|---------------|---------------------------|
| MCP servers | Agent > Project > Global |
| Permissions | deny wins regardless of scope (deny-overrides algorithm) |
| Custom agents | Project > Global (same-name: project wins with warning) |
| Steering | All scopes merged (not overridden) |
| Skills | All scopes merged |
| Hooks | All scopes merged |

**💡 Tip:** Permissions use a deny-overrides algorithm — a `deny` rule in any scope blocks the action regardless of `allow` rules elsewhere. See [Permissions](https://kiro.dev/docs/permissions.md) for details.

Since MCP servers can be configured in three scopes and agents have an `includeMcpJson` setting, MCP server resolution has additional rules. See [MCP server loading priority](https://kiro.dev/docs/mcp/configuration.md#mcp-server-loading-priority) for details.

## Web and Mobile

Web and Mobile read project configuration committed to the repository, but their coverage differs: Mobile reads project steering and skills, while Kiro Web additionally reads project MCP servers, custom agents, and Hooks (see the table below). Neither surface reads global `~/.kiro/` configuration, since there is no local filesystem. Kiro Web can also use selected personal configuration that you upload through [Configuration Sync](https://kiro.dev/docs/web/cloud-configuration.md).

| Configuration | Web | Mobile |
|---------------|:---:|:------:|
| Project steering (`.kiro/steering/`) | ✓ | ✓ |
| Project skills (`.kiro/skills/`) | ✓ | ✓ |
| Project MCP servers (`.kiro/settings/mcp.json`) | ✓ | — |
| Project custom agents (`.kiro/agents/`, sub-agent delegation) | ✓ | — |
| Project Hooks (`.kiro/hooks/`) | ✓ | — |
| Sandbox MCP (configured via Web settings) | ✓ | — |
| Permissions YAML and interactive approvals | — | — |

For cloud sessions, open **Settings > Sync** in [Kiro Web](https://app.kiro.dev/settings/cloud-config) to upload personal Steering, custom agents, Skills, and Hooks. Manage the uploaded items from their feature-specific settings pages. This managed cloud configuration is separate from the `~/.kiro/` directory on your computer and does not modify your local files.

See [Custom agents: surface behavior](https://kiro.dev/docs/custom-agents.md#surface-behavior) for details on Web and Mobile limitations.

## Next steps

- [Configuration Sync](https://kiro.dev/docs/web/cloud-configuration.md) - upload personal configuration for cloud sessions
- [Custom agents](https://kiro.dev/docs/custom-agents.md) — create and configure specialized agents
- [Steering](https://kiro.dev/docs/steering.md) — project context and conventions
- [Permissions](https://kiro.dev/docs/permissions.md) — capability-based access control
- [MCP configuration](https://kiro.dev/docs/mcp/configuration.md) — connect external tools
- [Hooks](https://kiro.dev/docs/hooks.md) — automate workflows with event-driven actions
- [Skills](https://kiro.dev/docs/skills.md) — reusable instruction packages
- [Powers](https://kiro.dev/docs/powers.md) — extend with packaged MCP servers and docs
