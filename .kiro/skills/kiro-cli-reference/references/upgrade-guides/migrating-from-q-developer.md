> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Migrating from Amazon Q Developer

> Guide for transitioning from Amazon Q Developer extensions and plugins to Kiro

If you've been using Amazon Q Developer in your IDE, everything you rely on today (inline suggestions, chat, and code generation) is available in Kiro. The table below shows the additional capabilities you gain by switching. For migration steps, jump to [your IDE](#vs-code) below.

## Feature comparison

This comparison covers Amazon Q Developer's IDE extensions. For CLI-specific differences, see [Upgrading from Q CLI](https://kiro.dev/docs/upgrade-guides/migrating-from-q.md).

| Capability | Q Developer IDE extensions | Kiro IDE | Kiro CLI |
|------------|:--------------------------:|:--------:|:--------:|
| [MCP (Model Context Protocol)](https://kiro.dev/docs/mcp.md) | ✓ | ✓ | ✓ |
| Terminal command allow/denylist | - | ✓ | ✓ |
| [Steering files](https://kiro.dev/docs/steering.md) | - | ✓ | ✓ |
| [Hooks (event-driven automation)](https://kiro.dev/docs/hooks.md) | - | ✓ | ✓ |
| [Custom subagents](https://kiro.dev/docs/custom-agents/subagents.md) / [agent skills](https://kiro.dev/docs/skills.md) | - | ✓ | ✓ |
| [Powers](https://kiro.dev/docs/powers.md) | - | ✓ | ✓ |
| [Spec-driven development](https://kiro.dev/docs/specs.md) | - | ✓ | - |

Select your current IDE below for migration steps.

## VS Code

Kiro IDE is built on the same VS Code foundation, so your extensions, themes, keybindings, and settings carry over directly. For a complete walkthrough, see the [detailed VS Code migration guide](https://kiro.dev/docs/upgrade-guides/migrating-from-vscode.md).

At a high level:

1. [Download and install Kiro IDE](https://kiro.dev/docs/getting-started/installation.md).
2. On first startup, Kiro will prompt you to import your VS Code profile. Accept to bring over your extensions, settings, and keybindings.
3. Sign in to Kiro with your preferred authentication method: GitHub, Google, AWS Builder ID, or IAM Identity Center.

If you skip the profile import on first launch or want to import a profile later, follow the [manual profile migration steps](https://kiro.dev/docs/upgrade-guides/migrating-from-vscode.md#profile-migration).

## JetBrains IDEs

Kiro works inside JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, and others) through JetBrains AI Assistant via the Agent Client Protocol (ACP).

1. [Install the Kiro CLI](https://kiro.dev/docs/getting-started/installation.md).
2. Sign in to Kiro through the CLI authentication flow.
3. Add Kiro as a custom agent in JetBrains AI Assistant. For the configuration steps, see the [JetBrains ACP setup guide](https://kiro.dev/docs/cli/acp.md#jetbrains-ides).

## Visual Studio and Eclipse

Amazon Q Developer offered extensions for Visual Studio and Eclipse, but Kiro does not have native plugins for either. You have two options to continue using AI-assisted development:

- **Kiro IDE**: A standalone editor built on VS Code with full agentic capabilities, specs, hooks, and powers built in. [Get started with Kiro IDE](https://kiro.dev/docs/getting-started/installation.md).
- **Kiro CLI**: A terminal-based experience you can run alongside your existing editor. Use it for chat, code generation, and agentic workflows without switching IDEs. [Get started with Kiro CLI](https://kiro.dev/docs/getting-started/installation.md).

## Already using Q Developer CLI?

If you're migrating from the Amazon Q Developer CLI specifically, see the dedicated [Upgrading from Q CLI](https://kiro.dev/docs/upgrade-guides/migrating-from-q.md) guide for details on configuration migration, command changes, and backward compatibility.
