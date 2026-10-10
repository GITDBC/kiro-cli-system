> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Upgrading agent configs

> Migrate older agent configurations to the v3 format with tag-based tools and unified permissions

CLI 3.0 agent profiles use [tag-based tools and unified permissions](https://kiro.dev/docs/cli/v3/agent-config.md). If you have agents created before this format was introduced, the `/upgrade-agent` command converts them in place. It adds the new permission fields alongside your existing configuration and backs up originals before writing.

Run it once, pick which agents to upgrade, and you're done. You can run it any time you spot older fields like `toolsSettings` or `allowedTools` in your configs.

## Usage

```bash
# Scan agents and open the selection menu
/upgrade-agent

# Same as above (explicit subcommand)
/upgrade-agent run

# Review previously upgraded agents and any conversion warnings
/upgrade-agent diagnostics
```

The `run` subcommand (default) scans `.kiro/agents/` in your workspace and `~/.kiro/agents/` globally, then shows a selection menu grouped by scope. Only agents that need upgrading appear. Agents already in the latest format are hidden.

## What happens during upgrade

When you select a group of agents to upgrade:

1. Each original file is copied to `<filename>.json.bak` as a backup
2. New-format permission fields are added alongside your existing configuration
3. Your original settings (tool names, allowed commands, path restrictions) are preserved with equivalent rules in the new format
4. A confirmation alert shows how many agents were upgraded

If a backup file already exists, numbered suffixes are used (`.bak.1`, `.bak.2`, etc.).

### Reverting an upgrade

If you want to undo the upgrade, rename the `.json.bak` file back to `.json`:

```bash
mv .kiro/agents/my-agent.json.bak .kiro/agents/my-agent.json
```

## What gets converted

The upgrade translates your existing permission settings into the v3 format:

- **Tool names:** Old names (like `fs_read`, `execute_bash`) are mapped to v3 capability tags (like `read`, `shell`). Both are preserved for compatibility.
- **`toolsSettings`:** Per-tool allow/deny rules become `permissions.rules` entries with capability, match pattern, and effect.
- **`allowedTools`:** Trusted-tool entries become capability-level allow rules.
- **Regex patterns:** Regex patterns are translated to simple wildcard globs where possible. Complex patterns that can't be safely converted generate a warning.
- **`autoAllowReadonly`:** Converts to a read-only-shell policy.
- **Object-form hooks:** Converted to the array format the v3 schema requires.

All other fields (`name`, `description`, `model`, `prompt`, `resources`, `mcpServers`, `welcomeMessage`) pass through unchanged.

## Example

Here's a typical first run. You have 3 workspace agents and 1 global agent in older formats:

```bash
/upgrade-agent
```

**Selection menu:**

```text
V2 [3 agents]               Workspace    Upgrade to universal (V2 + V3) config
V2 [1 agent]                Global       Upgrade to universal (V2 + V3) config
```

Select "V2 [3 agents] - Workspace" to upgrade all 3 workspace-level agents. The "universal (V2 + V3)" label means the upgraded config retains your original fields for backward compatibility while adding newer permission rules.

**Post-upgrade alert:**

```text
Upgraded 3 agents (backed up to .json.bak)
```

## Reviewing diagnostics

Run diagnostics to check for conversion warnings, patterns that couldn't be perfectly translated:

```bash
/upgrade-agent diagnostics
```


```text
2 Universal agents

  my-agent     Workspace   ⚠ regex-shell-pattern: ^git\s
  strict-dev   Global      ⚠ deny-by-default-readonly
```

### Warning types

| Warning | Meaning | What to do |
|---------|---------|------------|
| `regex-shell-pattern` | A shell regex was approximated as a glob | Review the converted pattern in `permissions.rules` |
| `regex-web-pattern` | A URL regex was approximated as a glob | Review the converted URL pattern |
| `unconvertible-pattern` | A regex couldn't be safely converted | Manually add the rule to `permissions.rules` |
| `unmapped-allowed-tool` | A tool entry couldn't be mapped to a capability | Check if the tool has a new name or was removed |
| `deprecated-aws-tool` | `aws` / `use_aws` tool is deprecated | Remove the deprecated tool reference |
| `deny-by-default-readonly` | Conflicting deny-by-default and auto-allow-readonly settings | Review your permission intent and adjust manually |
| `file-prompt` | Absolute or `~/` file prompt paths may not resolve in all environments | Use relative paths instead |
| `unconvertible-hook` | A hook couldn't be converted to the new format | Recreate the hook using the supported trigger format |

## Agents that are skipped

The following are excluded from the scan:

- Backup files (`.bak`) are excluded from the scan
- Files that aren't valid agent configs (JSON files without `prompt`, `tools`, `hooks`, or permission fields) are ignored

## Troubleshooting

### No agents appear in the selection menu

All your agents are already in the latest format. Run `/upgrade-agent diagnostics` to review their current state.

### Warnings after upgrade

Some patterns can't be perfectly translated from regex to glob format. Run `/upgrade-agent diagnostics`, review the flagged agents, and manually edit the `permissions.rules` in the upgraded config if needed.

### Agent missing from the scan

Verify the file is valid JSON and contains at least a `prompt`, `tools`, or `hooks` field. Files that don't look like agent configurations are ignored.

## Related

- [Agent config](https://kiro.dev/docs/cli/v3/agent-config.md) for the v3 agent config format reference
- [Permissions](https://kiro.dev/docs/permissions.md) for the capability-based permission rules
- [Custom agents](https://kiro.dev/docs/custom-agents.md) for creating and managing agents
