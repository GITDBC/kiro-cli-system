---
name: kiro-cli-reference
description: >
  Kiro CLI official documentation reference. Use when answering questions about Kiro CLI
  features, configuration, commands, agents, skills, steering, specs, MCP, hooks,
  permissions, or any Kiro CLI capability. Triggers: 'kiro', 'kiro-cli', 'agent config',
  'steering files', 'skills spec', 'slash commands', 'MCP servers', 'knowledge base',
  'subagents', 'headless mode'. Not for general coding tasks unrelated to Kiro CLI
  itself.
---

# Kiro CLI Reference

Official documentation for Kiro CLI, synced from https://kiro.dev/docs/.

## Mirror Scope

Upstream reorganised its documentation: the sections shared by every Kiro product moved
from `/docs/cli/<section>/` to top-level `/docs/<section>/`. The mirror therefore tracks
two upstream shapes and flattens neither:

| Upstream URL                    | Local path                             |
| ------------------------------- | -------------------------------------- |
| `/docs/cli/chat/context/`       | `references/chat/context.md`           |
| `/docs/billing/managing-taxes/` | `references/billing/managing-taxes.md` |
| `/docs/hooks/`                  | `references/hooks.md`                  |

A page below `/docs/cli/` keeps its position with the section stripped; a top-level
section keeps its own name, so a relocated page stays where the mirror already had it.
The sections belonging to the other Kiro products (`crew`, `ide`, `web`, `mobile`) and
the cross-product `guides` tutorials are out of scope. The authoritative section list
lives in `CLI_SECTIONS` in `tools/docsync/docsync/sources/kiro.py`.

A relocated page still answers HTTP 200 at its old `/docs/cli/` URL, but the body is a
`# Moved` stub naming the new location. A status code alone therefore cannot tell a live
page from a relocated one — only the sitemap listing can, which is why discovery is
sitemap-driven.

## Freshness Check

A startup hook performs a cheap local age check by reading the `.last-sync.json` marker
— it does not hit the network. When the vendored documentation looks stale, run an
explicit, user-initiated network check to compare the local mirror against kiro.dev:

```bash
make sync-docs-check        # or: uv run --project tools/docsync docsync kiro --dry-run
```

If updates are reported, fetch them (this also refreshes the `.last-sync.json` marker,
which records the page total):

```bash
make sync-docs              # or: uv run --project tools/docsync docsync kiro
```

To additionally remove local pages that no longer exist in the sitemap, pass `--prune`
explicitly (never removes anything by default):

```bash
uv run --project tools/docsync docsync kiro --prune
```

## Reference Index

### Getting Started

| File                                                                              | Topic                                                                                                               |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [getting-started/authentication.md](references/getting-started/authentication.md) | Sign in to Kiro using GitHub, Google, AWS Builder ID, IAM Identity Center, or your organization's identity provider |
| [getting-started/first-project.md](references/getting-started/first-project.md)   | A hands-on walkthrough of Kiro's core features - steering, specs, hooks, and MCP - using a real project             |
| [getting-started/installation.md](references/getting-started/installation.md)     | Install Kiro as an IDE, CLI, web app, or mobile app and start building in minutes                                   |
| [setup.md](references/setup.md)                                                   | Get up and running with Kiro CLI in minutes — from first install to productive coding                               |

### Core Concepts and Configuration

| File                                              | Topic                                                                                                                                         |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| [how-kiro-works.md](references/how-kiro-works.md) | One unified agent harness powers every Kiro surface. Learn how it connects the IDE, CLI, Web, and Mobile, and why your setup travels with you |
| [configuration.md](references/configuration.md)   | How Kiro resolves configuration across global, project, and agent scopes — complete reference of all configurable features                    |
| [steering.md](references/steering.md)             | Guide Kiro's AI with persistent context through markdown documents that define your standards, architecture, and conventions                  |
| [skills.md](references/skills.md)                 | Extend Kiro with portable instruction packages using the open Agent Skills standard                                                           |
| [permissions.md](references/permissions.md)       | Control what the Kiro agent can do with capability-based permissions across IDE and CLI                                                       |
| [checkpoints.md](references/checkpoints.md)       | Undo agent changes to your files or fork your conversation to explore a different path                                                        |
| [compaction.md](references/compaction.md)         | How Kiro automatically summarizes conversation history to keep sessions productive within model context limits                                |
| [kiroignore.md](references/kiroignore.md)         | Control which files Kiro can access using gitignore-style patterns                                                                            |
| [cloud-sessions.md](references/cloud-sessions.md) | Run agent sessions in a managed cloud sandbox and pick them up from the IDE, CLI, Web, or Mobile                                              |

### Chat

| File                                                                  | Topic                                                                                                                                                                                                                                       |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [chat.md](references/chat.md)                                         | Interacting with Kiro CLI                                                                                                                                                                                                                   |
| [chat/context.md](references/chat/context.md)                         | Managing conversation context in Kiro CLI                                                                                                                                                                                                   |
| [chat/diff-tools.md](references/chat/diff-tools.md)                   | Configure external diff tools to view code changes in Kiro CLI                                                                                                                                                                              |
| [chat/file-references.md](references/chat/file-references.md)         | Include file contents or directory listings inline using @path syntax                                                                                                                                                                       |
| [chat/git-aware-selection.md](references/chat/git-aware-selection.md) | When working with Git repositories, Kiro CLI's fuzzy finder is Git-aware, making it easier to select and add relevant files to your context. This feature helps you quickly identify and include files that are part of your Git repository |
| [chat/goal.md](references/chat/goal.md)                               | Start an autonomous agent loop that iterates toward an objective with built-in verification                                                                                                                                                 |
| [chat/images.md](references/chat/images.md)                           | Kiro can analyze and discuss images directly in your chat session. You can share images with Kiro by dragging and dropping them into your terminal window or by using the `read` tool with the Image mode                                   |
| [chat/manage-prompts.md](references/chat/manage-prompts.md)           | Create, organize, and reuse custom prompts for efficient CLI interactions                                                                                                                                                                   |
| [chat/queue-steering.md](references/chat/queue-steering.md)           | Send messages to the agent while it's working to redirect its approach without cancelling                                                                                                                                                   |
| [chat/responding.md](references/chat/responding.md)                   | Learn how to interact with and respond to Kiro CLI messages effectively                                                                                                                                                                     |
| [chat/session-management.md](references/chat/session-management.md)   | Automatic session saving, resumption, and custom storage integration                                                                                                                                                                        |
| [chat/settings.md](references/chat/settings.md)                       | Configure theme, keybindings, terminal input, display preferences, and prompt history from within a chat session                                                                                                                            |

### Custom Agents

| File                                                                                            | Topic                                                                                                               |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [custom-agents.md](references/custom-agents.md)                                                 | Create and deploy specialized AI agents for your workflows                                                          |
| [custom-agents/built-in.md](references/custom-agents/built-in.md)                               | Pre-configured agents that ship with Kiro for common workflows - planning, specs, debugging, and documentation help |
| [custom-agents/configuration-reference.md](references/custom-agents/configuration-reference.md) | Complete reference for agent configuration file format and advanced settings                                        |
| [custom-agents/creating.md](references/custom-agents/creating.md)                               | Learn how to create and configure custom agents for specialized workflows                                           |
| [custom-agents/examples.md](references/custom-agents/examples.md)                               | Real-world examples of custom agents for common development workflows                                               |
| [custom-agents/subagents.md](references/custom-agents/subagents.md)                             | Delegate focused tasks to agents that run in parallel with isolated context                                         |
| [custom-agents/troubleshooting.md](references/custom-agents/troubleshooting.md)                 | Common issues and solutions when working with custom agents                                                         |

### Specs

| File                                                                                              | Topic                                                                                                                |
| ------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| [specs.md](references/specs.md)                                                                   | Use Kiro's structured specifications to break down complex features into detailed implementation plans with tracking |
| [specs/analyze-requirements.md](references/specs/analyze-requirements.md)                         | Deep analysis that catches logical inconsistencies, ambiguities, and gaps in your requirements before implementation |
| [specs/best-practices.md](references/specs/best-practices.md)                                     | Best practices when using Specs with Kiro                                                                            |
| [specs/bugfix-specs.md](references/specs/bugfix-specs.md)                                         | Systematically diagnose and fix bugs with surgical precision while preventing regressions                            |
| [specs/correctness.md](references/specs/correctness.md)                                           | Ensuring specification quality through property-based testing and validation                                         |
| [specs/feature-specs/requirements-first.md](references/specs/feature-specs/requirements-first.md) | Start with the behavior of the system you want to create, then generate technical design                             |
| [specs/feature-specs/tech-design-first.md](references/specs/feature-specs/tech-design-first.md)   | Start with technical design and system architecture, then derive feasible requirements                               |
| [specs/feature-specs.md](references/specs/feature-specs.md)                                       | Build new features with structured requirements, technical design, and implementation planning                       |
| [specs/plan.md](references/specs/plan.md)                                                         | Structured planning before execution - explore your codebase, gather requirements, and create implementation plans   |
| [specs/quick-spec.md](references/specs/quick-spec.md)                                             | Generate requirements, design, and tasks in one pass without approval gates between phases                           |

### Hooks

| File                                                            | Topic                                                                              |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| [hooks.md](references/hooks.md)                                 | Automate repetitive tasks and enforce best practices with event-driven agent hooks |
| [hooks/actions.md](references/hooks/actions.md)                 | Learn about different hook actions and their use cases                             |
| [hooks/best-practices.md](references/hooks/best-practices.md)   | Follow proven patterns for effective hook design and troubleshooting               |
| [hooks/examples.md](references/hooks/examples.md)               | Practical examples and templates you can use in your projects                      |
| [hooks/management.md](references/hooks/management.md)           | Learn how to organize, edit, and maintain your hooks                               |
| [hooks/troubleshooting.md](references/hooks/troubleshooting.md) | Common issues and solutions for debugging hook issues                              |
| [hooks/types.md](references/hooks/types.md)                     | Learn about different hook trigger types and their use cases                       |

### MCP (Model Context Protocol)

| File                                                    | Topic                                                                                                                                                                                                          |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [mcp.md](references/mcp.md)                             | Model Context Protocol (MCP) extends Kiro's capabilities by connecting to specialized servers that provide additional tools and context. This guide helps you set up, configure, and use MCP servers with Kiro |
| [mcp/configuration.md](references/mcp/configuration.md) | Configure Model Context Protocol (MCP) servers across IDE, CLI, and Web including configuration file structure, server setup, and management                                                                   |
| [mcp/examples.md](references/mcp/examples.md)           | Practical examples of using MCP servers with Kiro CLI                                                                                                                                                          |
| [mcp/registry.md](references/mcp/registry.md)           | Centrally managed MCP server access for enterprise teams using IAM Identity Center                                                                                                                             |
| [mcp/security.md](references/mcp/security.md)           | Security best practices for configuring and using Model Context Protocol (MCP) servers with Kiro, protecting sensitive information and maintaining system security                                             |
| [mcp/servers.md](references/mcp/servers.md)             | Directory of available Model Context Protocol (MCP) servers and their capabilities                                                                                                                             |
| [mcp/tool-search.md](references/mcp/tool-search.md)     | Reduce context window usage by loading MCP tools on demand                                                                                                                                                     |
| [mcp/usage.md](references/mcp/usage.md)                 | Learn how to use MCP tools, prompts, resource templates, and elicitation with Kiro for enhanced productivity and specialized capabilities                                                                      |

### Tools

| File                                                                | Topic                                                                                                          |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| [tools.md](references/tools.md)                                     | The tools available to Kiro's agent - file operations, shell commands, web access, code intelligence, and more |
| [tools/code-intelligence.md](references/tools/code-intelligence.md) | Tree-sitter and LSP-powered code understanding - symbol search, pattern matching, and codebase exploration     |
| [tools/web.md](references/tools/web.md)                             | Search the web and fetch page content - real-time internet access for the Kiro agent                           |

### Models

| File                                                                | Topic                                                                                                                         |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| [models.md](references/models.md)                                   | Choose the right AI model for your development tasks in Kiro                                                                  |
| [models/available-models.md](references/models/available-models.md) | Detailed descriptions of every AI model available in Kiro, including capabilities, behavior differences, and lifecycle status |
| [models/effort.md](references/models/effort.md)                     | Control how much reasoning the model applies to balance speed, depth, and cost                                                |

### Powers

| File                                                        | Topic                                                                                                        |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [powers.md](references/powers.md)                           | Dynamic loading of context and MCP servers, giving your AI agent instant expertise for any framework or tool |
| [powers/create.md](references/powers/create.md)             | How to build your own powers using the Agent Plugins specification and share them with the community         |
| [powers/installation.md](references/powers/installation.md) | How to install powers from the curated marketplace or GitHub repositories                                    |

### Terminal UI

| File                                                              | Topic                                                                                                                               |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| [terminal-ui.md](references/terminal-ui.md)                       | A rich chat experience for Kiro CLI with syntax highlighting, interactive panels, and a polished terminal-native interface          |
| [terminal-ui/comparison.md](references/terminal-ui/comparison.md) | A comparison of the terminal UI and classic interface in Kiro CLI, including what's new, what changed, and what's not available yet |
| [fullscreen.md](references/fullscreen.md)                         | A dedicated terminal screen for longer Kiro CLI sessions, toggled with `/fullscreen`                                                |

### Other CLI Features

| File                                          | Topic                                                                                                                               |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| [acp.md](references/acp.md)                   | Use Kiro in JetBrains IDEs, Zed, and other ACP-compatible editors by running Kiro CLI as an Agent Client Protocol agent             |
| [autocomplete.md](references/autocomplete.md) | AI-powered command completions and suggestions for hundreds of popular CLI tools                                                    |
| [headless.md](references/headless.md)         | Run Kiro CLI non-interactively in CI/CD pipelines, automation scripts, and environments without a browser                           |
| [voice.md](references/voice.md)               | Speech-to-text for Kiro CLI chat using local Whisper transcription, with push-to-talk and a remote server option for cloud desktops |
| [2x-reference.md](references/2x-reference.md) | Reference documentation for Kiro CLI 2.x hooks, agent config, and formats that changed in 3.0                                       |

### Reference

| File                                                                  | Topic                                                                |
| --------------------------------------------------------------------- | -------------------------------------------------------------------- |
| [reference/built-in-tools.md](references/reference/built-in-tools.md) | Explore Kiro CLI's built-in tools for enhanced terminal productivity |
| [reference/cli-commands.md](references/reference/cli-commands.md)     | Complete reference for all Kiro CLI commands                         |
| [reference/exit-codes.md](references/reference/exit-codes.md)         | CLI exit codes for scripting and CI/CD integration                   |
| [reference/settings.md](references/reference/settings.md)             | Configure Kiro CLI behavior through settings                         |
| [reference/slash-commands.md](references/reference/slash-commands.md) | Quick reference for in-chat slash commands in Kiro CLI               |

### CLI 3.0

| File                                                      | Topic                                                                                                                                      |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| [v3.md](references/v3.md)                                 | CLI 3.0 runs the unified agent harness in your terminal. What changed from 2.x, breaking changes, step-by-step migration, and new features |
| [v3/agent-config.md](references/v3/agent-config.md)       | New optional fields and Markdown format for agent profiles in CLI 3.0                                                                      |
| [v3/hooks-migration.md](references/v3/hooks-migration.md) | Migrating from CLI 2.x embedded hooks to the new standalone .kiro/hooks/*.json format                                                      |
| [v3/migration-guide.md](references/v3/migration-guide.md) | Step-by-step guide to migrate from Kiro CLI 2.x to 3.0                                                                                     |
| [v3/new-features.md](references/v3/new-features.md)       | New capabilities in Kiro CLI 3.0 — plan mode, permissions, hooks, built-in tools, and more                                                 |
| [v3/permissions.md](references/v3/permissions.md)         | Migrating from CLI 2.x trust flags to the capability-based permissions model in CLI 3.0                                                    |
| [v3/tangent.md](references/v3/tangent.md)                 | Branch your conversation into side-conversations, explore freely, then jump back to exactly where you left off                             |
| [v3/upgrade-agent.md](references/v3/upgrade-agent.md)     | Migrate older agent configurations to the v3 format with tag-based tools and unified permissions                                           |

### Experimental

| File                                                                                    | Topic                                                                             |
| --------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [experimental.md](references/experimental.md)                                           | Advanced features in active development for Kiro CLI                              |
| [experimental/delegate.md](references/experimental/delegate.md)                         | Launch background tasks and delegate complex work to specialized agents           |
| [experimental/knowledge-management.md](references/experimental/knowledge-management.md) | Store and search contextual information across chat sessions with knowledge bases |
| [experimental/tangent-mode.md](references/experimental/tangent-mode.md)                 | Explore side topics without disrupting your main conversation flow                |
| [experimental/thinking.md](references/experimental/thinking.md)                         | See AI reasoning process for complex problems                                     |
| [experimental/todo-lists.md](references/experimental/todo-lists.md)                     | Automatic TODO list creation and management for multi-step tasks                  |

### Billing

| File                                                                                            | Topic                                                                                                                   |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| [billing.md](references/billing.md)                                                             | Detailed breakdown of Kiro's service tiers and feature comparison                                                       |
| [billing/add-on-credits.md](references/billing/add-on-credits.md)                               | Understanding how you can continue using Kiro beyond your plan's usage limits                                           |
| [billing/cancelling.md](references/billing/cancelling.md)                                       | Complete guide to cancelling your Kiro subscription and switching to the Kiro Free tier                                 |
| [billing/contact-support.md](references/billing/contact-support.md)                             | Get help with billing questions, payment issues, and account-related concerns through AWS support                       |
| [billing/deleting-account.md](references/billing/deleting-account.md)                           | Learn how to permanently delete your Kiro account and what happens to your data                                         |
| [billing/downgrading.md](references/billing/downgrading.md)                                     | Step-by-step guide to downgrading your Kiro subscription plan or switching to the Kiro Free tier                        |
| [billing/managing-taxes.md](references/billing/managing-taxes.md)                               | Understanding tax collection, VAT, and billing practices for Kiro purchases                                             |
| [billing/managing.md](references/billing/managing.md)                                           | Learn how to manage your Kiro subscription, view usage, and update billing information                                  |
| [billing/proactive-usage-notifications.md](references/billing/proactive-usage-notifications.md) | Stay informed about your credit usage with automated notifications so you can take action before running out of credits |
| [billing/related-questions.md](references/billing/related-questions.md)                         | Frequently asked questions about Kiro billing, subscriptions, and payment issues                                        |
| [billing/subscription-portal.md](references/billing/subscription-portal.md)                     | Learn how to access and manage your Kiro subscription portal                                                            |
| [billing/upgrading.md](references/billing/upgrading.md)                                         | Step-by-step guide to upgrading your Kiro subscription plan                                                             |

### Enterprise

| File                                                                                                                                  | Topic                                                                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| [enterprise/billing.md](references/enterprise/billing.md)                                                                             | Understand Kiro subscription tiers, pricing, proration, and how to view your bill in AWS                                                   |
| [enterprise/concepts.md](references/enterprise/concepts.md)                                                                           | Key terms and concepts for administrators managing Kiro subscriptions and users                                                            |
| [enterprise/deployment-options.md](references/enterprise/deployment-options.md)                                                       | Decide where to enable IAM Identity Center, create your Kiro profile, and subscribe users before rolling out Kiro across your organization |
| [enterprise/getting-started.md](references/enterprise/getting-started.md)                                                             | Deploy Kiro to your organization with confidence. Learn how to subscribe users, manage subscriptions, and track usage                      |
| [enterprise/governance/api-keys.md](references/enterprise/governance/api-keys.md)                                                     | Enterprise governance of API keys for Kiro                                                                                                 |
| [enterprise/governance/mcp.md](references/enterprise/governance/mcp.md)                                                               | Enterprise governance of MCP servers for Kiro                                                                                              |
| [enterprise/governance/model.md](references/enterprise/governance/model.md)                                                           | Enterprise governance of models for Kiro                                                                                                   |
| [enterprise/governance/permissions.md](references/enterprise/governance/permissions.md)                                               | Deploy managed permission rules to control what Kiro's agent can do across your organization                                               |
| [enterprise/governance/web-tools.md](references/enterprise/governance/web-tools.md)                                                   | Control whether Kiro users can use web search and web fetch tools                                                                          |
| [enterprise/governance.md](references/enterprise/governance.md)                                                                       | Administrators can manage how developers using Kiro can access models and MCP tools                                                        |
| [enterprise/iam.md](references/enterprise/iam.md)                                                                                     | Understand AWS IAM and how to configure permissions for Kiro administrators                                                                |
| [enterprise/identity-provider/iam-identity-center.md](references/enterprise/identity-provider/iam-identity-center.md)                 | How to connect IAM Identity Center (IdC) with Kiro                                                                                         |
| [enterprise/identity-provider/microsoft-entra.md](references/enterprise/identity-provider/microsoft-entra.md)                         | How to connect Microsoft Entra ID with Kiro                                                                                                |
| [enterprise/identity-provider/okta.md](references/enterprise/identity-provider/okta.md)                                               | How to connect Okta with Kiro                                                                                                              |
| [enterprise/identity-provider.md](references/enterprise/identity-provider.md)                                                         | How to connect an identity provider with Kiro                                                                                              |
| [enterprise/managed-updates.md](references/enterprise/managed-updates.md)                                                             | Configure the UpdateUrl managed policy to point Kiro IDE at a self-hosted update server for phased rollouts and version pinning            |
| [enterprise/monitor-and-track/dashboard.md](references/enterprise/monitor-and-track/dashboard.md)                                     | Docs to help admins monitor and track Kiro usage through a dashboard                                                                       |
| [enterprise/monitor-and-track/prompt-logging.md](references/enterprise/monitor-and-track/prompt-logging.md)                           | Docs to help admins understand what Kiro users are entering as prompts into the Kiro IDE                                                   |
| [enterprise/monitor-and-track/user-activity/opentelemetry.md](references/enterprise/monitor-and-track/user-activity/opentelemetry.md) | Configure daily OpenTelemetry exports to monitor per-user Kiro activity in your observability platform                                     |
| [enterprise/monitor-and-track/user-activity.md](references/enterprise/monitor-and-track/user-activity.md)                             | Configure daily CSV and OpenTelemetry exports to monitor per-user Kiro activity                                                            |
| [enterprise/monitor-and-track.md](references/enterprise/monitor-and-track.md)                                                         | Track Kiro usage through dashboards, user activity reports, prompt logs, and AWS monitoring tools                                          |
| [enterprise/settings.md](references/enterprise/settings.md)                                                                           | Configure encryption, code references, usage tracking, prompt logging, and other administrative settings                                   |
| [enterprise/subscribe.md](references/enterprise/subscribe.md)                                                                         | Step-by-step guide to creating a Kiro profile and subscribing users through AWS IAM Identity Center                                        |
| [enterprise/subscription-management.md](references/enterprise/subscription-management.md)                                             | Learn how to manage Kiro subscriptions for your users                                                                                      |
| [enterprise/supported-regions.md](references/enterprise/supported-regions.md)                                                         | Learn about the AWS Regions where Kiro Enterprise is supported                                                                             |

### Privacy and Security

| File                                                                                                          | Topic                                                                                                        |
| ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [privacy-and-security.md](references/privacy-and-security.md)                                                 | Comprehensive overview of Kiro's privacy practices, security measures, compliance standards, and user rights |
| [privacy-and-security/code-references.md](references/privacy-and-security/code-references.md)                 | Learn how Kiro provides attribution when AI-generated code matches open-source projects                      |
| [privacy-and-security/compliance-validation.md](references/privacy-and-security/compliance-validation.md)     | Understand how users can validate compliance for their specific regulatory requirements                      |
| [privacy-and-security/data-protection.md](references/privacy-and-security/data-protection.md)                 | Understand how your code, personal data, and project information is protected when using Kiro                |
| [privacy-and-security/firewalls.md](references/privacy-and-security/firewalls.md)                             | Allowlist the URLs and configure proxy settings that Kiro needs to connect to its backend services           |
| [privacy-and-security/iam-permissions.md](references/privacy-and-security/iam-permissions.md)                 | AWS Identity and Access Management (IAM) permissions required for Kiro                                       |
| [privacy-and-security/infrastructure-security.md](references/privacy-and-security/infrastructure-security.md) | This page explains the foundational security measures that protect Kiro at the infrastructure level          |
| [privacy-and-security/vpc-endpoints.md](references/privacy-and-security/vpc-endpoints.md)                     | Understand how to establish a private connection between your VPC (Virtual Private Cloud) and Kiro           |

### Upgrade Guides

| File                                                                                                    | Topic                                                                                                      |
| ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [upgrade-guides/migrating-from-q-developer.md](references/upgrade-guides/migrating-from-q-developer.md) | Guide for transitioning from Amazon Q Developer extensions and plugins to Kiro                             |
| [upgrade-guides/migrating-from-q.md](references/upgrade-guides/migrating-from-q.md)                     | Guide for transitioning from Amazon Q Developer CLI to Kiro CLI                                            |
| [upgrade-guides/migrating-from-vscode.md](references/upgrade-guides/migrating-from-vscode.md)           | Comprehensive guide for transitioning from Visual Studio Code to Kiro's AI-powered development environment |
