> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Permissions

> Control what the Kiro agent can do with capability-based permissions across IDE and CLI

Kiro uses a capability-based permissions system that gives you fine-grained, declarative control over what the agent can do. You define rules per capability with match patterns and explicit effects, replacing older binary trust models.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Permissions YAML configuration | ✓ | ✓ | N/A | — |
| Interactive approval prompts | ✓ | ✓ | N/A | — |
| Global + workspace scopes | ✓ | ✓ | N/A | — |
| Sandbox execution without per-action prompts | — | — | ✓ | — |

On Web, the `permissions.yaml` model and interactive approvals do not apply: the agent runs inside an isolated [cloud sandbox](https://kiro.dev/docs/web/sandbox.md) instead of prompting per action, so those rows are marked N/A rather than unsupported.

## How it works

The permissions system is built around three core concepts:

| Concept | Description |
|---------|-------------|
| **Capabilities** | `fs_read`, `fs_write`, `shell`, `web_fetch`, `web_search`, `mcp`, `subagent`, `skill`, `power`, `context`, `diagnostics`, `sandbox_network`. Meta-capabilities expand: `all` (everything), `builtin` (all built-in tools), `filesystem` (`fs_read` + `fs_write`) |
| **Effects** | `deny` (block always), `ask` (prompt you), `allow` (proceed silently) |
| **Priority** | deny > ask > allow - a deny rule always wins regardless of scope |

Additional rule properties:

| Property | Description |
|----------|-------------|
| **Match patterns** | Glob patterns scoping the rule (file paths for fs, command prefixes for shell, server/tool names for MCP) |
| **Exclude** | Optional glob patterns that must NOT match - enables "allow everything except X" |

## Defining rules

Permissions are defined in YAML files at two levels:

**User-scoped** (`~/.kiro/settings/permissions.yaml`) - applies across all projects. Use to pre-approve trusted operations:

```yaml
rules:
  - capability: shell
    match: ["git *", "npm *", "npx *"]
    effect: allow

  - capability: fs_write
    match: ["src/**", "tests/**"]
    effect: allow

  - capability: fs_read
    effect: allow

  - capability: mcp
    match: ["my-server/*"]
    effect: allow
```

**Workspace-scoped** (`~/.kiro/workspace-roots/<hash>/permissions.yaml`) - applies only to a specific project. Use to scope rules to one codebase:

```yaml
rules:
  - capability: fs_write
    match: ["*.env", "*.pem", "*.key"]
    effect: deny

  - capability: shell
    match: ["rm -rf *", "sudo *"]
    effect: deny
```

Both scopes support all effects (`deny`, `ask`, `allow`).

**ℹ️ Info:** Workspace permissions are stored **per-user outside the repository** at `~/.kiro/workspace-roots/<hash(workspaceRoot)>/`. A cloned repo cannot inject permission rules - trust is something you configure on your own machine.

### Exclude syntax

Rules support an `exclude` field for "allow everything except" patterns:

```yaml
rules:
  - capability: mcp
    match: ["my-server/*"]
    exclude: ["my-server/dangerous-tool"]
    effect: allow
```

### Pattern matching

Rules use glob patterns. The syntax differs by capability type:

**Filesystem patterns** (`fs_read`, `fs_write`):

- `*` matches within a single path component
- `**` matches across path separators
- `` brace expansion and `[abc]` character classes are supported
- Patterns without wildcards implicitly match children: `~/temp` matches `~/temp/child`

**Shell, web, and MCP patterns:**

- `*` matches any sequence of characters
- `**`, `?`, and character classes are not supported

```yaml
rules:
  # Allow npm commands except npm publish
  - capability: shell
    effect: allow
    match:
      - "npm *"
    exclude:
      - "npm publish*"

  # Deny reads to secrets at any depth
  - capability: fs_read
    effect: deny
    match:
      - "**/.env"
      - "**/.env.*"
      - "secrets/**"
      - "**/*.pem"
```

### Shell command parsing

Shell commands are parsed before pattern matching. Compound commands (using `;`, `&&`, `||`, `|`) are split and each sub-command is evaluated independently. This prevents a rule for `npm test *` from accidentally matching `npm test ; curl attacker.com`.

## Scopes

Permissions are evaluated across multiple scopes.

| Scope | Location | Allowed effects |
|-------|----------|-----------------|
| Kiro | Hardcoded security invariants (cannot be changed by configuration) | deny, ask |
| administration | [Enterprise permission policies](https://kiro.dev/docs/enterprise/governance/permissions.md) in `managed-settings.json` | deny, ask |
| user | `~/.kiro/settings/permissions.yaml` | deny, ask, allow |
| workspace | `~/.kiro/workspace-roots/<hash>/permissions.yaml` | deny, ask, allow |
| agent | Embedded in agent profile (`permissions` field) | deny, ask, allow |
| session | In-memory rules from consent decisions during the session | deny, ask, allow |

Rules are evaluated using a deny-overrides algorithm: deny > ask > allow. There is no precedence between scopes - the most restrictive effect wins regardless of which scope it came from.

**⚠️ Warning:** A `deny` rule in any scope blocks the action regardless of `allow` rules elsewhere. Be deliberate with deny rules, since no `allow` rule can override them.

## Policy presets

Policy presets are named, composable sets of session-scope `allow` rules. Clients that create agent sessions over the [Agent Client Protocol (ACP)](https://kiro.dev/docs/cli/acp.md), such as editor integrations, review bots, and CI harnesses, use them to seed a session with a well-defined capability profile without writing individual rules from scratch.

### How presets are applied

Presets are requested by an ACP client in the `_meta.kiro.policyPreset` field of a `session/new` or `session/load` request. Multiple presets can be combined; their rules are merged as a union.

```json
{
  "_meta": {
    "kiro": {
      "policyPreset": ["edit-workspace", "dev-shell"]
    }
  }
}
```

Preset rules are seeded into the session when the client opens it, separately from the rules you configured in `permissions.yaml`. This is why a session's active rules can include entries you never wrote.

Requesting an unknown preset ID rejects the session request. There is no silent fallback to a default policy.

**ℹ️ Info:** Preset rules are session-scope and held in memory only. On a cold session load (a full restart), the client must re-assert the preset. A session that resumes without a full restart keeps its already-seeded rules.

### Available presets

| Preset ID | What it allows |
|-----------|---------------|
| `allow-all` | Every capability except `sandbox_network` (equivalent to `capability: all, effect: allow`) |
| `edit-workspace` | `fs_read` and `fs_write` within `./**` only |
| `read-workspace` | `fs_read` within `./**` only |
| `read-all` | `fs_read` anywhere, plus `web_fetch` and `web_search` |
| `read-only-shell` | Read-only shell commands: system info plus `git`, `cargo`, `npm`, `docker`, `kubectl`, and `rustup` queries |
| `dev-shell` | Read-only shell commands (the `read-only-shell` set) plus git write commands; build tools `cargo`, `npm`, `bun`, `yarn`; workspace ops `mkdir`, `touch`, `mv`, `cp`; inspection commands `ls`, `cat`, `grep`, `echo` |

### Choosing presets for a session

Presets are allow-only profiles: they remove prompts for the operations a session is meant to perform, and everything else keeps the default of asking for approval. Pick the narrowest profile that matches the session's job.

| Session profile | Presets | What you get |
|-----------------|---------|--------------|
| Code review or audit | `read-workspace` | Workspace files are read silently. Writes and shell commands still ask, so the session prompts before any change. |
| Investigation and research | `read-all` | File reads anywhere on disk, plus `web_fetch` and `web_search`, for sessions that trace an issue across code and external documentation without needing write access. |
| Diagnostics and triage | `read-workspace` + `read-only-shell` | The agent reads workspace files and queries git, docker, kubectl, and other tool state. Nothing grants a write, so every change still asks. |
| Autonomous build-and-test loop | `edit-workspace` + `dev-shell` | The agent edits workspace files, runs git write commands and the standard build tools, and creates or moves files in the workspace without a prompt per action. Writes outside the workspace and unlisted commands still ask. |
| Disposable sandbox | `allow-all` | Every capability is allowed. Use it where the environment itself is the boundary, such as a container that is discarded after the run. |

Each profile is requested the same way: the preset IDs go in the `policyPreset` array of the session request. A code review bot opens its session with:

```json
{
  "_meta": {
    "kiro": {
      "policyPreset": ["read-workspace"]
    }
  }
}
```

A diagnostics session pairs workspace reads with read-only shell queries:

```json
{
  "_meta": {
    "kiro": {
      "policyPreset": ["read-workspace", "read-only-shell"]
    }
  }
}
```

A CI harness that edits, builds, and tests combines the two write-capable presets:

```json
{
  "_meta": {
    "kiro": {
      "policyPreset": ["edit-workspace", "dev-shell"]
    }
  }
}
```

`deny` rules and the Kiro scope invariants below still apply regardless of which profile is active.

### Presets in embedded and headless clients

The same profiles map onto common integration patterns. An editor integration that embeds Kiro typically requests `edit-workspace` so in-workspace file edits do not prompt. A code review bot requests `read-workspace` and nothing more. A CI or evaluation harness driving the agent programmatically combines `edit-workspace` with `dev-shell`, then adds its own `deny` rules for anything the pipeline must never touch.

**⚠️ Warning:** Headless execution raises the stakes: when no interactive client is available, every `ask` is treated as a deny, because the runtime has no interactive channel to deliver the prompt. A headless session can only perform operations that are explicitly allowed, so the presets it requests, plus any configured `allow` rules, define its entire grant surface.

### Trust invariants

Presets extend what a session is allowed to do, but they cannot override higher-precedence rules. The deny-overrides algorithm described in the Scopes section above still applies in full:

- Kiro-scope hard denies (writes to `~/.kiro/settings/`, `.kiro/settings/`, `~/.kiro/workspace-roots/`) block the action regardless of any preset.
- Kiro-scope ask rules (`.git/**`, `.kiro/agents/**`, `.kiro/hooks/**`, `.kiroignore`) still prompt, even when a preset grants broad write access.
- Any `deny` rule you have configured at the user, workspace, or administration scope wins over a preset `allow`.
- The `sandbox_network` capability is not part of the `all` meta-capability, so no preset, including `allow-all`, changes sandbox network gating.

Subagents inherit the parent session's full rule set via deny-wins intersection: every allow, deny, and ask from the parent applies, so a more restrictive rule on either side always wins.

## Default behavior

Without any `permissions.yaml` configured, the default agent policy allows:

- `fs_read` on `./**` - read any workspace file silently
- `shell` for common git read-only commands - `git status`, `git log`, `git diff`, `git branch`, and similar
- `shell` for system info commands - `pwd`, `whoami`, `uname`, and similar
- Utility tools (diagnostics, knowledge, and similar)

The Kiro scope (hardcoded, not changeable by configuration) enforces:

- **Always denied:** writes to `~/.kiro/settings/`, `.kiro/settings/`, and `~/.kiro/workspace-roots/` (prevents the agent from modifying its own permission files)
- **Always asks:** writes to `.git/**`, `.kiro/agents/**`, `.kiro/hooks/**`, `.kiroignore`

Everything else prompts for approval. Creating a `permissions.yaml` adds to these defaults; it does not replace them.

## Managing permissions by surface

    IDE
    CLI
    Web

### Agent autonomy setting

In addition to `permissions.yaml` rules, the IDE's agent autonomy is controlled via **Settings → Agent → Agent Autonomy** (settings key: `kiroAgent.agentAutonomy`). The two modes are:

- **Autopilot** - the agent proceeds with allowed operations without prompting
- **Supervised** - the agent prompts before any action

The capability-based permissions layer applies after the autonomy mode determines whether to proceed. Together, these two layers give you coarse-grained control (Autopilot vs Supervised) plus fine-grained rules (permissions.yaml) for specific capabilities.

### Interactive approval flow

When a tool requires approval, a prompt appears in chat. **Allow** and **Deny** are available for the current invocation. Kiro also shows persistent choices when it can derive a saved rule that will work for the requested command:

| Action | Effect |
|--------|--------|
| **Allow** | Approve this specific invocation once |
| **Always allow** | Create a persistent allow rule (opens pattern/scope picker) |
| **Deny** | Block this specific invocation once |
| **Always deny** | Create a persistent deny rule |

If Kiro cannot verify a working saved rule, it hides **Always allow** and **Always deny** and explains why in the prompt.

When you select **Always allow**, you configure two things:

- **Pattern** - choose the match scope for the rule (e.g., `cd *` for any cd command, or the exact command path)
- **Apply to** - choose where the rule persists:
  - **All workspaces** - saved to user-scoped `~/.kiro/settings/permissions.yaml`
  - **This workspace** - saved to `~/.kiro/workspace-roots/<hash>/permissions.yaml` (per-user, outside the repository)
  - **This session** - remembered in memory until the session ends

The pattern dropdown suggests a generalized version of the specific operation - for example, exact command `git add contents/docs/` becomes pattern `git add *`, and exact path `.env.local` becomes `.env*` or `**/.env*`. You can edit the suggestion to be more restrictive or more permissive.

For chained commands (e.g., `cd /path && cargo build`), each sub-command in the chain is presented separately for approval.

### Interactive tool management

Use the `/tools` command during a chat session to manage permissions interactively:

| Command | Description |
| --- | --- |
| `/tools` | Shows current permission status for all tools |
| `/tools help` | Shows help related to tools |
| `/tools trust <tool>` | Trusts a specific tool for the session |
| `/tools untrust <tool>` | Reverts a tool to per-request confirmation |
| `/tools trust-all` | Trusts all tools for the session |
| `/tools reset` | Resets all runtime permissions to defaults |

To view the current permission settings:

```bash
$ kiro-cli chat
Kiro> /tools
```

Tool permissions have two possible states during a session:

- **Trusted** - Kiro can use the tool without asking for confirmation each time
- **Per-request** - Kiro must ask for your confirmation before using the tool

Example usage:

```bash
Kiro> /tools trust read
Kiro> /tools untrust shell
Kiro> /tools trust-all
```

**⚠️ Warning:** Using `/tools trust-all` carries risks. In the terminal UI, both `--trust-all-tools` and `/tools trust-all` show a confirmation warning before granting access. You must acknowledge the risk before proceeding.

### Available built-in tools

| Tool | Description |
| --- | --- |
| `read` | Reads files and directories on your system |
| `write` | Creates and modifies files on your system |
| `shell` | Executes bash commands on your system |
| `aws` | Makes AWS CLI calls to interact with AWS services |
| `report` | Opens a browser to report an issue with the chat to AWS |

When Kiro attempts to use a tool that doesn't have explicit permission, it asks for your approval. A panel-based dropdown appears with Yes, Trust, and No options. When multiple tools need permission simultaneously, approvals are queued and presented one at a time. Choosing **Trust** also auto-approves any other pending invocations of that same tool in the current batch.

### Shell command trust levels

When Kiro asks to run a shell command, you can choose how broadly to trust it with a tiered interactive picker:

```text
Press (↑↓) to navigate (⏎) to select scope
> Full command          → git pull --rebase
  Partial command       → git pull *
  Base command          → git *
  Entire Tool           → *
```

| Tier | What it trusts | Example pattern |
| --- | --- | --- |
| Full command | The exact command as written | `git pull --rebase` |
| Partial command | The command and subcommand, with any arguments | `git pull *` |
| Base command | The base command with any arguments | `git *` |
| Entire Tool | All shell commands | `*` |

After you select a tier, Kiro confirms the trusted pattern (for example, `✓ Trusted: git pull --rebase`). The picker only shows tiers that are meaningfully different - if the command has no subcommand, the partial tier is skipped. For chained commands (pipes, `&&`), Kiro generates trust patterns for each command in the chain and deduplicates them.

Trusted patterns persist for the session and are stored as regex in the agent's `allowedCommands` setting. For more on how `allowedCommands` works, see [Shell tool settings](https://kiro.dev/docs/reference/built-in-tools.md#execute-shell-commands).

**⚠️ Warning:** If a command matches a `deniedCommands` pattern, granular trust options are not available. You can only allow the action once or trust the entire tool.

### Read and write path trust levels

The `read` and `write` tools support granular trust when accessing paths outside the current working directory. By default, both tools are trusted for the current working directory. When Kiro needs to access a file outside that directory, you get a tiered picker:

```text
Press (↑↓) to navigate (⏎) to select scope
> Specific paths       → ~/.config/app/settings.json
  Complete directory   → ~/.config/app
  Entire Tool          → *
```

| Tier | What it trusts | Example |
| --- | --- | --- |
| Specific paths | Only the exact file paths requested | `~/.config/app/settings.json` |
| Complete directory | All files in the containing directory | `~/.config/app` |
| Entire Tool | All read or write operations everywhere | `*` |

Paths within the current working directory do not trigger the picker.

### CI and headless environments

For CI pipelines, create a user-scoped permissions file in your CI environment:

```yaml
# ~/.kiro/settings/permissions.yaml (CI environment)
rules:
  - capability: all
    effect: allow
```

The `--trust-all-tools` flag still works as a session-scope override for CI use cases without configuration changes.

    Kiro Web does not use `permissions.yaml` or interactive approval prompts. The agent runs without per-action prompts inside an isolated [cloud sandbox](https://kiro.dev/docs/web/sandbox.md), so file changes and commands affect the sandbox rather than your computer.

    The sandbox boundary does not grant access to external systems by itself. You separately control its [internet access](https://kiro.dev/docs/web/sandbox/internet-access.md), [environment variables](https://kiro.dev/docs/web/sandbox/environment-variables.md), MCP servers, and any AWS role you configure. Grant only the access required for your work.

## Permission examples

Here are common patterns for configuring permissions:

| Scenario | Configuration |
| --- | --- |
| Trust file reads | `capability: fs_read`, `effect: allow` |
| Trust write in project dirs | `capability: fs_write`, `match: ["src/**", "tests/**"]`, `effect: allow` |
| Block sensitive files | `capability: fs_write`, `match: ["*.env", "*.pem", "*.key"]`, `effect: deny` |
| Block dangerous commands | `capability: shell`, `match: ["rm -rf *", "sudo *"]`, `effect: deny` |
| Trust specific MCP server | `capability: mcp`, `match: ["my-server/*"]`, `effect: allow` |
| Untrust shell in production | `capability: shell`, `effect: ask` (or use `/tools untrust shell` in CLI) |

## Migrating from older versions

If you're upgrading from CLI 2.x or IDE 0.x, see the reference pages for how permissions worked previously and what changed:

- [CLI 2.x reference - Permissions](https://kiro.dev/docs/cli/2x-reference.md#permissions-and-tool-trust)
- [IDE 0.x reference - Permissions](https://kiro.dev/docs/ide/0x-reference.md#permissions-autopilot--supervised-toggle)
- [What's new in CLI 3.0 - Permissions migration](https://kiro.dev/docs/cli/v3/permissions.md)
