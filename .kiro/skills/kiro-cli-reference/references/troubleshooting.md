> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Troubleshooting

> Match a Kiro CLI symptom to the page that owns the fix, from a launch that opens unexpectedly to a session, agent config, Hook, or ACP client that stopped working.

This page routes a Kiro CLI symptom to the page that owns the fix. It adds no steps of its own: find your symptom, then follow the link.

## Launch

| Symptom | Where the fix lives |
| --- | --- |
| Kiro CLI prints a reinstall message because the terminal UI is missing | [Installation](https://kiro.dev/docs/getting-started/installation.md) |
| The terminal UI does not load or renders incorrectly | [Terminal UI troubleshooting](https://kiro.dev/docs/cli/terminal-ui.md#troubleshooting) |

## Sessions and configuration

| Symptom | Where the fix lives |
| --- | --- |
| A custom agent does not load or behaves unexpectedly | [Custom agents troubleshooting](https://kiro.dev/docs/custom-agents/troubleshooting.md) |
| An MCP server fails to start or its tools are missing | [MCP troubleshooting](https://kiro.dev/docs/mcp.md#troubleshooting) |
| A setting is rejected or has no effect | [Troubleshooting settings](https://kiro.dev/docs/reference/settings.md#troubleshooting-settings) |
| A saved session is missing from `/sessions` | [Session management troubleshooting](https://kiro.dev/docs/cli/chat/session-management.md#troubleshooting) |

## Report a problem

When no page above covers your symptom, collect a diagnostic report and file an issue:

- [`kiro-cli diagnostic`](https://kiro.dev/docs/reference/cli-commands.md#kiro-cli-diagnostic) gathers the details Kiro needs.
- [`kiro-cli issue`](https://kiro.dev/docs/reference/cli-commands.md#kiro-cli-issue) opens a bug report.
