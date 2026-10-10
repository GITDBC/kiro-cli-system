> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Privacy and security

> Comprehensive overview of Kiro's privacy practices, security measures, compliance standards, and user rights

Kiro is an AWS application that works as a standalone agentic IDE. Kiro's security framework is built around AWS's security infrastructure and follows practices to protect your development environment and data. Cloud security at AWS is the highest priority. As an AWS customer, you benefit from a data center and network architecture that is built to meet the requirements of the most security-sensitive organizations.

Security is a shared responsibility between AWS and you. The [shared responsibility model](https://aws.amazon.com/compliance/shared-responsibility-model/) describes this as security of the cloud and security in the cloud:

- Security of the cloud – AWS is responsible for protecting the infrastructure that runs AWS services in the AWS Cloud. AWS also provides you with services that you can use securely. Third-party auditors regularly test and verify the effectiveness of our security as part of the [AWS Compliance Programs](https://aws.amazon.com/compliance/programs/). To learn about the compliance programs that apply to Kiro, see [AWS Services in Scope by Compliance Program](https://aws.amazon.com/compliance/services-in-scope/).

- Security in the cloud – Your responsibility is determined by the AWS service that you use. You are also responsible for other factors including the sensitivity of your data, your company's requirements, and applicable laws and regulations

This documentation helps you understand how to apply the shared responsibility model when using Kiro. It shows you how to configure Kiro to meet your security and compliance objectives. You also learn how to use other AWS services that help you to monitor and secure your Kiro resources.

## URL fetching

In the Kiro chat module, you can paste a specific URL for your device to fetch and use it as context to help Kiro answer your query or solve your task. You are responsible for the URL content that you fetch and ensuring that your use complies with any applicable third-party terms and laws.

## Autopilot versus supervised mode

Kiro offers two interaction modes, Autopilot and Supervised, that control how you review agent actions. Both modes grant the agent the same capabilities: creating, modifying, searching, and deleting files in your codebase and running commands that impact the filesystem. The difference is the review workflow, not the underlying permissions or access scope.

**⚠️ Warning:** **Supervised mode is a code review workflow, not a security control.** It is designed to help you review and approve agent-generated changes. It does not function as a sandbox, isolation boundary, or access control mechanism. To restrict what the agent can access or modify, use [protected paths](#protected-paths), [trusted commands](#trusted-commands), workspace isolation, and credential scoping as described in [best practices](#best-practices).

| Capability | Autopilot | Supervised |
|-----------|-----------|------------|
| Agent can read files | Yes | Yes |
| Agent can write files to disk | Yes | Yes |
| Agent can run commands | Yes (with trusted commands policy) | Yes (with trusted commands policy) |
| Review step before changes are applied | No, changes are applied immediately | Yes, you review a diff and accept or reject |
| Revert capability | Manual (via **Revert all changes** or checkpoints) | Automatic on rejection; also manual revert available |
| Prevents writes to protected paths without approval | Yes | Yes |

### How supervised mode works

In both modes, the agent writes file changes to disk during tool execution. In supervised mode, these writes are tagged for your review. After the agent's turn completes, Kiro checks for pending file changes and prompts you to accept or reject before continuing. If you reject, files revert to their pre-turn state.

Kiro classifies the following operations as file-modifying. Any of these operations triggers a mandatory review prompt at the end of the agent's turn:

| Operation | Description |
|-----------|-------------|
| File creation or overwrite | Creating new files or replacing file contents |
| Text replacement | Replacing specific text within a file |
| Content append | Adding content to the end of a file |
| File deletion | Removing a file from the workspace |
| Code editing | Modifying code within a file |
| Symbol rename | Renaming a variable, function, or class across files |
| File relocation | Moving a file and updating its references |

This review check is built into Kiro's workflow and cannot be skipped by the AI model. If a file-modifying operation ran during the turn, the approval prompt will appear.

Shell commands follow a separate approval path. By default, all commands require your approval before execution (see [trusted commands](#trusted-commands)). To maintain full oversight, keep your trusted commands list minimal and avoid broad wildcards.

### What supervised mode provides

When supervised mode is enabled, Kiro enforces the following behaviors for file-modifying operations:

* **Turn-level review for file-modifying operations:** Every file-modifying operation listed above results in an approval prompt before changes are applied.
* **Automatic revert on rejection:** If you reject, files are restored to their exact state before the agent's turn began.
* **Protected path enforcement:** Writes to [protected paths](#protected-paths) require explicit approval before the write occurs, in both modes.
* **Command approval:** Unrecognized commands require your approval before execution, in both modes.

### Scope and limitations

Supervised mode reviews changes made through Kiro's file-editing operations. Other actions, such as shell commands you've added to your trusted list, follow their own approval policy. Supervised mode does not restrict which files the agent can read, which commands it can suggest, or what network access it has.

To maintain full oversight of your environment:
* Keep your [trusted commands](#trusted-commands) list minimal and avoid broad wildcards.
* Use [protected paths](#protected-paths) to require approval for writes to sensitive locations.
* Use workspace isolation and credential scoping as described in [best practices](#best-practices).

### Autopilot mode (default)

In Autopilot mode, Kiro works autonomously:

* Kiro executes multiple steps without requiring approval for each one.
* Kiro makes decisions based on its understanding of your requirements.
* You can toggle autopilot on/off in the chat interface.
* Changes are written and applied immediately. You can review them after the fact.
* You can interrupt at any time and revert changes via **Revert all changes** or [checkpoints](https://kiro.dev/docs/checkpoints.md).

### Supervised mode

In Supervised mode, Kiro works interactively, pausing for your review after each turn:

* After the agent modifies files, it pauses and presents a diff for your review.
* You can accept individual changes (hunk-level granularity) or reject them to revert.
* The agent asks clarifying questions when needed.
* To reduce interruptions, consecutive edits to the same file may be batched.

Supervised mode is best suited for situations where you want to closely review agent output. For example, when working in an unfamiliar codebase, making changes to critical paths, or onboarding a new team member to agent-assisted workflows.

### Choosing the right mode

Use **Autopilot** when you trust the task scope and want the agent to work efficiently without interruption. Use **Supervised** when you want to review each set of changes before they persist. In both cases, apply the security controls described in [best practices](#best-practices) to protect sensitive files, credentials, and infrastructure.

When operating in either mode, you can view individual or all file changes made by the agent by selecting **View all changes** in the **Chat** module. You can also select **Revert all changes** or revert to a [checkpoint](https://kiro.dev/docs/checkpoints.md) to restore your files to their previous state.

## Trusted commands

By default, Kiro requires approval before running any command. You can create your own trusted commands list by searching for **Kiro Agent: Trusted Commands** in your settings. 

Kiro uses simple string prefix matching to determine if a command should be automatically trusted:
- **Exact matching**: Commands must match exactly (e.g., `npm install`)
- **Wildcard matching**: Use `*` to trust command variations (e.g., `npm *` trusts all npm commands)
- **Universal trust**: Use `*` alone to trust all commands (use with extreme caution)

The system treats entire commands as single strings and only checks if they start with trusted patterns. It does not analyze command structure, chains, or special characters, putting full responsibility on you to carefully configure trusted patterns.

## Protected paths

Kiro requires explicit approval before writing to certain protected paths, preventing unintended modifications to sensitive workspace configuration files. This applies in both Autopilot and Supervised mode — when the agent attempts to create or modify a file matching a protected pattern, you see a confirmation prompt and the change is not applied until you approve it. If you decline, the agent skips the write and continues with the rest of the task.

**ℹ️ Info:** Protected paths are enforced in the Kiro IDE. In the CLI, trusted commands and workspace isolation serve as the primary access controls.

### Protected path patterns

The following path patterns are protected:

| Pattern | Match type | Description |
|---------|-----------|-------------|
| `.vscode/` | Path contains | VS Code workspace settings |
| `vscode~` | Path contains | VS Code backup and recovery files |
| `.git/` | Path contains | Files inside the `.git` directory |
| `git~` | Path contains | Git lock and backup files |
| `.code-workspace` | Path contains | Multi-root workspace files |
| `.git` | Exact basename | The `.git` directory or submodule file itself |
| `mcp.json` | Exact basename | MCP server configuration |
| `.kiroignore` | Exact basename | Kiro ignore rules |

### Match types

- **Path contains** — Matches if the pattern appears anywhere in the file path. For example, `.vscode/` matches both `.vscode/settings.json` and `.vscode/extensions.json`.
- **Exact basename** — Matches if the filename (the last segment of the path) exactly equals the pattern. For example, `mcp.json` matches `project/mcp.json` but not `mcp.json.bak`.

When a match is detected, Kiro pauses and displays a confirmation prompt. The file is not written until you approve.

## Best practices

Kiro provides a number of security features to consider as you develop and implement your own security policies. The following best practices are general guidelines and don't represent a complete security solution. Because these best practices might not be appropriate or sufficient for your environment, treat them as helpful considerations rather than prescriptions.

### Protecting your resources

When using GitHub or Google authentication with Kiro, be aware that the Kiro agent operates within your local environment and may access:

* Local files and repositories
* Environment variables
* AWS credentials stored in your environment
* Other configuration files with sensitive information

### Recommendations

1. **Workspace Isolation**
    * Keep sensitive projects in separate workspaces
    * Use .gitignore to prevent access to sensitive files
    * Consider using workspace trust features in your IDE
2. **Use a Clean Environment**
    * Consider creating a dedicated user account or container environment for Kiro
    * Limit access to only the repositories and resources needed for your current project
3. **Manage AWS Credentials Carefully**
    * Use temporary credentials with appropriate permissions
    * Consider using AWS named profiles to isolate Kiro's access
    * For sensitive work, remove AWS credentials from your environment when not needed
4. **Repository Access Control**
    * When using GitHub authentication, review which repositories Kiro can access
    * Use repository-specific access tokens when possible
    * Regularly audit access permissions

## Remote extensions security

**⚠️ Warning:** **Security Note**: Using remote extensions opens a connection between your local machine and the remote machine. Only connect to secure remote machines that you trust and that are owned by a party whom you trust. A compromised remote could use the connection to execute code on your local machine.
Third-party extensions including remote extensions are not developed, maintained, or managed by Kiro. We are not responsible for third-party extensions and cannot guarantee their stability, compatibility, or ongoing support.

Kiro supports Open VSX extensions, including remote SSH extensions (the community-maintained [Open Remote - SSH](https://open-vsx.org/extension/jeanp413/open-remote-ssh) extension on Open VSX is a popular choice), to provide a familiar development experience. For comprehensive information about extension compatibility and support in Kiro, see our [extension compatibility guide](https://kiro.dev/docs/upgrade-guides/migrating-from-vscode.md#extension-compatibility).

By following these practices, you can enjoy Kiro's capabilities while maintaining appropriate security boundaries for your development environment.
