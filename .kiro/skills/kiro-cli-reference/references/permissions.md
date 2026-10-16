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
| Managed cloud sandbox instead of permission prompts | N/A | N/A | ✓ | — |

On Web, the `permissions.yaml` model and interactive approvals do not apply: the agent runs inside an isolated [cloud sandbox](https://kiro.dev/docs/web/sandbox.md) instead of prompting per action, so those rows are marked N/A rather than unsupported.

## How it works

The permissions system is built around three core concepts:

| Concept | Description |
|---------|-------------|
| **Capabilities** | `fs_read`, `fs_write`, `shell`, `web_fetch`, `web_search`, `mcp`, `subagent`, `skill`, `power`, `context`, `diagnostics`, `sandbox_network`. Meta-capabilities expand: `all` (every capability except `sandbox_network`), `builtin` (all built-in tools), `filesystem` (`fs_read` + `fs_write`) |
| **Effects** | `deny` (block always), `ask` (prompt you), `allow` (proceed silently) |
| **Priority** | deny > ask > allow - a deny rule always wins regardless of scope. `sandbox_network` host rules are the exception; see [Sandbox network rules](#sandbox-network-rules) |

Additional rule properties:

| Property | Description |
|----------|-------------|
| **Match patterns** | Glob patterns scoping the rule (file paths for fs, command prefixes for shell, server/tool names for MCP) |
| **Exclude** | Optional glob patterns that must NOT match - enables "allow everything except X" |

### Sandbox network rules

The `sandbox_network` capability applies only when the [local command sandbox](https://kiro.dev/docs/sandbox.md) is active. Its `allow` and `deny` rules name the hosts that sandboxed shell commands can reach, and your `fs_read` and `fs_write` rules shape which paths those commands can see and write. It is excluded from the `all` meta-capability.

Host filtering does not use deny-overrides. `sandbox_network` rules are applied in order and the first rule that matches the host decides, so a specific `deny` must come before a broader wildcard `allow` that also matches. Deny-overrides still governs whether the agent may run a tool action. See [Local command sandbox](https://kiro.dev/docs/sandbox.md) for host patterns and network modes.

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

The parser evaluates flags inside combined short options, so a command such as `grep -iP` still prompts when one of its flags requires approval. Options that can launch another program are never treated as read-only: `tar --use-compress-program` and `tar --to-command` require approval even when the base `tar` command is trusted.

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

Rules are evaluated using a deny-overrides algorithm: deny > ask > allow. There is no precedence between scopes - the most restrictive effect wins regardless of which scope it came from. `sandbox_network` host filtering is the exception: it applies rules first-match, as described in [Sandbox network rules](#sandbox-network-rules).

**⚠️ Warning:** A `deny` rule in any scope blocks the action regardless of `allow` rules elsewhere. Be deliberate with deny rules, since no `allow` rule can override them. For `sandbox_network` host rules, order decides instead; see [Sandbox network rules](#sandbox-network-rules).

## Policy presets

Policy presets are named, composable sets of session-scope `allow` rules. Any ACP client, including Kiro's own surfaces and compatible third-party integrations such as editor integrations, review bots, and CI harnesses, can use them to seed a session with a well-defined capability profile without writing individual rules from scratch.

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

- Kiro-scope hard denies (writes to `~/.kiro/settings/`, `.kiro/settings/`, `~/.kiro/workspace-roots/`, and the other stores listed under [Default behavior](#default-behavior)) block the action regardless of any preset.
- Kiro-scope ask rules (`.git/**`, `.vscode/**`, `**/*.code-workspace`, `.kiroignore`, and the `agents`, `hooks`, `workflows`, and `powers` directories under `.kiro` and `~/.kiro`) still prompt, even when a preset grants broad write access.
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

- **Always denied:** writes to `~/.kiro/settings/`, `.kiro/settings/`, and `~/.kiro/workspace-roots/` (prevents the agent from modifying its own permission files), to the MCP configuration of an installed Power (`~/.kiro/powers/installed/<name>/mcp.json`), and to Kiro's own state stores (`~/.kiro/sandbox-state/`, `~/.kiro/web-session/`, `~/.kiro/cloud-cache/`, `~/.kiro/sandbox-curl/`)
- **Always asks:** writes to `.git/**`, `.vscode/**`, `**/*.code-workspace`, `.kiroignore`, and the `agents`, `hooks`, `workflows`, and `powers` directories of both the workspace `.kiro` and `~/.kiro`. These ask in trusted and untrusted workspaces alike, and no `allow` rule from any scope removes the prompt.
- **Asks while the workspace is untrusted:** writes to `.kiro/steering`, `.kiro/skills`, `.kiro/extensions`, and any `.kiro` directory Kiro does not declare. See [Workspace trust](#workspace-trust).

Everything else prompts for approval. Creating a `permissions.yaml` adds to these defaults; it does not replace them.

## Workspace trust

Some agent inputs live inside the repository you open: custom agent profiles in `.kiro/agents/`, Steering files in `.kiro/steering/`, workspace MCP server configuration, Skills, and Workflow files. A cloned repository could use them to change how the agent behaves, so Kiro treats a workspace as untrusted until you trust it. Your decision is stored outside the workspace, so a repository cannot change its own trust status.

Until you trust a workspace, Kiro:

- Does not load the workspace's custom agents, Steering files, MCP server configuration, or Skills.
- Does not load Workflow files from the workspace, including files reached through a link from your home or cloud recipe directories. Your own home, cloud, bundled, and generated Workflows stay available.
- Asks before every shell command starts, including background processes, even when a saved or broad rule allows the command. The prompt shows the full command. A matching `deny` rule still refuses.
- Asks before every MCP tool call and before every Power activation, content read, or tool call, even when a saved rule or `autoApprove` allows it, and asks again when a call is retried after MCP authentication or a URL prompt. A matching `deny` rule still refuses.
- Asks before writing to `.kiro/steering`, `.kiro/skills`, `.kiro/extensions`, or any `.kiro` directory Kiro does not declare, in both the workspace and `~/.kiro`. Writes to the `agents`, `hooks`, `workflows`, and `powers` directories ask in every workspace.
- Refuses writes to the memory database under `~/.kiro/memories/` and to the agent's session store (`~/.kiro/sessions/` by default) without prompting, so an untrusted session cannot rewrite another session's state.
- Does not let the agent add, change, or delete memories, knowledge bases, or remote learnings. Reading them still works.

Your user, administration, agent, and session rules still apply, and so does the per-workspace store under `~/.kiro/workspace-roots/`: it lives outside the repository, so it loads regardless of trust.

One rule lifts the untrusted-only asks for `.kiro` directories: an `fs_write` `allow` rule in your own `~/.kiro/settings/permissions.yaml` with no `match` restriction and no `exclude`. It does not remove the always-ask paths, does not override a matching `ask` or `deny`, and does not load the untrusted workspace inputs listed above.

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

In CLI V3, run `/tools` to inspect the tools available in the current session. The V3 slash command supports one trust subcommand:

| Command | Description |
| --- | --- |
| `/tools` | Show the tools available in the current session |
| `/tools trust-all` | Trust every tool for the rest of the current session |

```bash
Kiro> /tools
Kiro> /tools trust-all
```

Use the approval picker for a specific operation or tool, and use `permissions.yaml` for rules that should apply beyond the current session. The per-tool `/tools trust`, `/tools untrust`, and `/tools reset` commands belong to CLI 2.x and are not available in V3.

**⚠️ Warning:** Using `/tools trust-all` carries risks. In the terminal UI, both `--trust-all-tools` and `/tools trust-all` show a confirmation warning before granting access. You must acknowledge the risk before proceeding.

### Available built-in tools

Kiro CLI V3 exposes the tools listed in the [built-in tools reference](https://kiro.dev/docs/tools.md). The `/tools` panel shows the exact set available in your current session, including MCP tools and the subset selected by the active agent.

The CLI 2.x structured AWS tool (`use_aws`, preferred alias `aws`) is not a V3 built-in. Configure an [AWS MCP server](https://kiro.dev/docs/mcp/configuration.md) for AWS access. To report a Kiro CLI issue, run `kiro-cli issue`.

When Kiro attempts to use a tool that doesn't have explicit permission, it asks for your approval. A panel-based dropdown appears with Yes, Trust, and No options. When multiple tools need permission simultaneously, approvals are queued and presented one at a time. Choosing **Trust** also auto-approves any other pending invocations of that same tool in the current batch.

### Approval scopes in CLI V3

When Kiro asks to run a shell command and you choose **Trust**, the V3 picker can offer these match scopes, depending on the command:

```text
> Trust "git pull --rebase"   → exact command
  Trust "git *"               → base command with any arguments
  Trust entire tool           → every shell command
```

| Match | What it trusts | Example pattern |
| --- | --- | --- |
| Exact command | Only the command as written | `git pull --rebase` |
| Base command | The executable with any arguments | `git *` |
| Entire tool | All shell commands | `*` |

The picker defaults to the current session. Press `s` to cycle the persistence scope among **session**, **workspace**, and **always** before saving the choice. Session approvals stay in memory until the session ends; workspace and always approvals persist through the V3 permission store. For chained commands such as pipes or `&&`, Kiro evaluates each command separately.

For how shell commands are split and matched before these rules are evaluated, see [Shell command parsing](#shell-command-parsing).

**⚠️ Warning:** A `deny` rule from any scope blocks the command without an approval prompt. Neither session trust nor an `allow` rule from another scope can override it. An explicit `ask` rule prompts every time and does not offer a persistent **Always** allow.

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
| Require approval for shell in production | `capability: shell`, `effect: ask` |

## Migrating from older versions

If you're upgrading from CLI 2.x or IDE 0.x, see the reference pages for how permissions worked previously and what changed:

- [CLI 2.x reference - Permissions](https://kiro.dev/docs/cli/2x-reference.md#permissions-and-tool-trust)
- [IDE 0.x reference - Permissions](https://kiro.dev/docs/ide/0x-reference.md#permissions-autopilot--supervised-toggle)
- [What's new in CLI V3 - Permissions migration](https://kiro.dev/docs/cli/v3/permissions.md)
