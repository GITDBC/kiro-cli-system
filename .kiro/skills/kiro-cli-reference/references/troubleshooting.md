> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Troubleshooting

> Match a Kiro CLI symptom to the page that owns the fix, from an unexpected harness or welcome message to a session, agent config, Hook, or ACP client that stopped working after an upgrade.

This page routes a Kiro CLI symptom to the page that owns the fix. It adds no steps of its own: find your symptom, then follow the link.

## Launch and harness

| Symptom | Where the fix lives |
| --- | --- |
| The session opens with **Kiro CLI V3 is here** and you expected V3 | [Confirm which harness is running](https://kiro.dev/docs/cli/agent-harness.md#confirm-which-harness-is-running), then [Save a default harness](https://kiro.dev/docs/cli/agent-harness.md#save-a-default-harness) |
| A launch with `--classic`, `--legacy-ui`, or `chat.ui` shows a message that offers **Continue with V3** | [If a launch still selects Classic](https://kiro.dev/docs/cli/agent-harness.md#if-a-launch-still-selects-classic) |
| On Linux, a launch that still selects Classic says this machine can't run the 3.0 agent | [Linux machines with older glibc](https://kiro.dev/docs/cli/agent-harness.md#linux-machines-with-older-glibc) |
| Kiro CLI prints a reinstall message because the terminal UI is missing | [Installation](https://kiro.dev/docs/getting-started/installation.md) |
| A script or pipeline ran on V2 when you expected V3 | [Scripts and CI](https://kiro.dev/docs/cli/agent-harness.md#scripts-and-ci) |
| An editor connected over ACP started on the wrong harness | [ACP clients](https://kiro.dev/docs/cli/agent-harness.md#acp-clients) |
| You want V2 back | [Return to V2](https://kiro.dev/docs/cli/agent-harness.md#return-to-v2) |
| The terminal UI does not load or renders incorrectly | [Terminal UI troubleshooting](https://kiro.dev/docs/cli/terminal-ui.md#troubleshooting) |

## Sessions and configuration after an upgrade

| Symptom | Where the fix lives |
| --- | --- |
| V2 cannot open a session you created in V3 | [Start V3 and keep V2 sessions available](https://kiro.dev/docs/cli/v3/migration-guide.md#1-start-v3-and-keep-v2-sessions-available) |
| A custom agent is skipped or shows an upgrade warning | [Reviewing diagnostics](https://kiro.dev/docs/cli/v3/upgrade-agent.md#reviewing-diagnostics) |
| A custom agent does not load or behaves unexpectedly | [Custom agents troubleshooting](https://kiro.dev/docs/custom-agents/troubleshooting.md) |
| Hooks from Kiro CLI 2.x no longer fire | [Hooks migration](https://kiro.dev/docs/cli/v3/hooks-migration.md) |
| Trust settings from Kiro CLI 2.x no longer apply | [Permissions migration](https://kiro.dev/docs/cli/v3/permissions.md) |
| An ACP client lost capabilities after moving to V3 | [Validate the migrated client](https://kiro.dev/docs/cli/v3/acp-migration.md#9-validate-the-migrated-client) |
| An MCP server fails to start or its tools are missing | [MCP troubleshooting](https://kiro.dev/docs/mcp.md#troubleshooting) |
| A setting is rejected or has no effect | [Troubleshooting settings](https://kiro.dev/docs/reference/settings.md#troubleshooting-settings) |
| A saved session is missing from `/sessions` | [Session management troubleshooting](https://kiro.dev/docs/cli/chat/session-management.md#troubleshooting) |

## Report a problem

When no page above covers your symptom, collect a diagnostic report and file an issue:

- [`kiro-cli diagnostic`](https://kiro.dev/docs/reference/cli-commands.md#kiro-cli-diagnostic) gathers the details Kiro needs.
- [`kiro-cli issue`](https://kiro.dev/docs/reference/cli-commands.md#kiro-cli-issue) opens a bug report.

## Next step

If your symptom started after an upgrade from Kiro CLI 2.x, work through [Upgrade from CLI 2.x](https://kiro.dev/docs/cli/v3.md) in order.
