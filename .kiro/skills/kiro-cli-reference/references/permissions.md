> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Permissions

> Control what the Kiro agent can do with capability-based permissions across IDE and CLI

Kiro uses a capability-based permissions system that gives you fine-grained, declarative control over what the agent can do. You define rules per capability with match patterns and explicit effects, replacing older binary trust models.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Permissions YAML configuration | ✓ | ✓ | N/A | — |
| Interactive approval prompts | ✓ | ✓ | ✓ | — |
| Global + workspace scopes | ✓ | ✓ | N/A | — |
| Managed cloud sandbox instead of permission prompts | N/A | N/A | ✓ | — |

On Web, the `permissions.yaml` model does not apply: the agent runs inside an isolated [cloud sandbox](https://kiro.dev/docs/web/sandbox.md) and approves every action by default, so those rows are marked N/A rather than unsupported. With [Approve for me](#approve-for-me-in-kiro-web) on, Web can also ask you before an action runs.

## How it works

The permissions system is built around three core concepts:

| Concept | Description |
|---------|-------------|
| **Capabilities** | `fs_read`, `fs_write`, `shell`, `web_fetch`, `web_search`, `mcp`, `subagent`, `skill`, `power`, `context`, `diagnostics`, `sandbox_network`. Meta-capabilities expand: `all` (every capability except `sandbox_network`), `builtin` (all built-in tools), `filesystem` (`fs_read` + `fs_write`) |
| **Effects** | `deny` (block always), `ask` (prompt you), `allow` (proceed silently), `evaluate` (Kiro judges the action; the weakest effect, added by the `approve-for-me` preset and active only when the trust classifier is available) |
| **Priority** | deny > ask > allow > evaluate - a deny rule always wins regardless of scope. `sandbox_network` host rules are the exception; see [Sandbox network rules](#sandbox-network-rules) |

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

Both scopes support all effects (`deny`, `ask`, `allow`, and `evaluate`).

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

In Kiro IDE 1.4.51 or later and Kiro CLI V3 sessions, Kiro blocks bash or PowerShell commands it cannot parse well enough to check against your permission rules. It asks the agent to rewrite the command instead of asking you to approve an unchecked command. Commands for `cmd.exe` still ask for approval. A rule that asks about every shell command still shows its normal prompt when no shell `deny` rule applies. An unconditional `allow` or `deny` rule still decides without parsing. If a valid command remains blocked after a few rewrites, the agent tells you it could not check the command.

## Scopes

Permissions are evaluated across multiple scopes. The table lists the scopes you configure or encounter directly; it is not an inventory of every scope the permission engine defines.

| Scope | Location | Allowed effects |
|-------|----------|-----------------|
| Kiro | Hardcoded security invariants (cannot be changed by configuration) | deny, ask |
| administration | [Enterprise permission policies](https://kiro.dev/docs/enterprise/governance/permissions.md) in `managed-settings.json` | deny, ask |
| user | `~/.kiro/settings/permissions.yaml` | deny, ask, allow, evaluate |
| workspace | `~/.kiro/workspace-roots/<hash>/permissions.yaml` | deny, ask, allow, evaluate |
| agent | Embedded in agent profile (`permissions` field) | deny, ask, allow, evaluate |
| session | In-memory rules from consent decisions during the session | deny, ask, allow, evaluate |

Rules are evaluated using a deny-overrides algorithm: deny > ask > allow > evaluate. There is no precedence between scopes - the most restrictive effect wins regardless of which scope it came from. `evaluate` is the effect the `approve-for-me` preset adds when it is listed under `policies:` in a user or workspace permissions file; see [Policy presets](#policy-presets). `sandbox_network` host filtering is the exception: it applies rules first-match, as described in [Sandbox network rules](#sandbox-network-rules).

**⚠️ Warning:** A `deny` rule in any scope blocks the action regardless of `allow` rules elsewhere. Be deliberate with deny rules, since no `allow` rule can override them. For `sandbox_network` host rules, order decides instead; see [Sandbox network rules](#sandbox-network-rules).

### Sub-agents

Kiro checks each sub-agent tool call against the parent session's policy and the sub-agent's own `permissions`. The stricter result wins:

- A `deny` from either policy denies the call.
- An `ask` rule in either policy prompts you.
- If the parent session's policy has no rule for the call, Kiro prompts you, even when the sub-agent's own rules allow it.

A call that the sub-agent's rules don't mention follows the parent session's policy. A sub-agent's `allow` rules never grant more than the parent session allows. A `subagent` capability rule only controls whether a sub-agent can start without a prompt. See [Sub-agent permissions](https://kiro.dev/docs/custom-agents/subagents.md#sub-agent-permissions).

## Policy presets

Policy presets are named, composable sets of rules. Every preset except `approve-for-me` consists only of `allow` rules. A preset reaches a session by one of two paths, and the path decides its scope:

- **Requested by a client.** Any ACP client, including Kiro's own surfaces and compatible third-party integrations such as editor integrations, review bots, and CI harnesses, can request the allow-only presets when it opens a session. Their rules are seeded at session scope and held in memory only.
- **Listed in a permissions file.** A preset named under `policies:` in a user or workspace `permissions.yaml` is expanded at that file's scope and persists with the file. This is how the **approve for me** option under `/permissions` turns on `approve-for-me`: it writes the preset to the workspace permissions file.

`approve-for-me` is the exception to allow-only. It adds an `evaluate` rule for every capability on top of a bounded set of `allow` rules, and it depends on Kiro's trust classifier: when the classifier is unavailable, the preset contributes no rules and the session keeps asking. Turn it on with the **approve for me** option under `/permissions` in a Kiro CLI V3 session, where that option appears, or with the **Approve for me** switch in Kiro Web; see [Approve for me](#approve-for-me).

### How client-requested presets are applied

An ACP client requests presets in the `_meta.kiro.policyPreset` field of a `session/new` or `session/load` request. Multiple presets can be combined; their rules are merged as a union.

```json
{
  "_meta": {
    "kiro": {
      "policyPreset": ["edit-workspace", "dev-shell"]
    }
  }
}
```

Client-requested preset rules are seeded into the session when the client opens it, separately from the rules you configured in `permissions.yaml`. This is why a session's active rules can include entries you never wrote.

Requesting an unknown preset ID rejects the session request. There is no silent fallback to a default policy.

**ℹ️ Info:** Client-requested preset rules are session-scope and held in memory only. On a cold session load (a full restart), the client must re-assert the preset. A session that resumes without a full restart keeps its already-seeded rules. A preset listed under `policies:` in a permissions file is not affected: it is read from the file at that file's scope each time the file loads.

### Available presets

| Preset ID | Rules it contributes |
|-----------|----------------------|
| `allow-all` | Every capability except `sandbox_network` (equivalent to `capability: all, effect: allow`) |
| `edit-workspace` | `fs_read` and `fs_write` within `./**` only |
| `read-workspace` | `fs_read` within `./**` only |
| `read-all` | `fs_read` anywhere, plus `web_fetch` and `web_search` |
| `read-only-shell` | Read-only shell commands: system info plus `git`, `cargo`, `npm`, `docker`, `kubectl`, and `rustup` queries |
| `dev-shell` | Read-only shell commands (the `read-only-shell` set) plus git write commands; build tools `cargo`, `npm`, `bun`, `yarn`; workspace ops `mkdir`, `touch`, `mv`, `cp`; inspection commands `ls`, `cat`, `grep`, `echo` |
| `approve-for-me` | The `edit-workspace` and `read-only-shell` sets, plus an `evaluate` rule for every capability, so Kiro judges each action that no deny, ask, or allow rule settles. Requires the trust classifier; when it is unavailable, this preset contributes no rules. Choosing **approve for me** under `/permissions` in a V3 session lists this preset under `policies:` in the workspace permissions file, so its rules apply at workspace scope. In Kiro Web, the **Approve for me** switch applies it to new sessions; see [Approve for me](#approve-for-me) |

### Choosing presets for a session

The allow-only presets remove prompts for the operations a session is meant to perform, and everything else keeps the default of asking for approval. Pick the narrowest profile that matches the session's job. `approve-for-me` is not in this table: it is chosen under `/permissions` in a Kiro CLI V3 session, which lists it in the workspace permissions file rather than requesting it for one session, or with the **Approve for me** switch in Kiro Web, and it only takes effect when the trust classifier is available.

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

- Kiro-scope hard denies (writes to `~/.kiro/settings/`, `.kiro/settings/`, `~/.kiro/workspace-roots/`, `.kiroignore`, and the other stores listed under [Default behavior](#default-behavior)) block the action regardless of any preset.
- Kiro-scope ask rules (`.git/**`, `.vscode/**`, `**/*.code-workspace`, and the `agents`, `hooks`, `workflows`, and `powers` directories under `.kiro` and `~/.kiro`) still prompt, even when a preset grants broad write access.
- Any `deny` rule you have configured at the user, workspace, or administration scope wins over a preset `allow`.
- The `sandbox_network` capability is not part of the `all` meta-capability, so no preset, including `allow-all`, changes sandbox network gating.

## Default behavior

Without any `permissions.yaml` configured, the default agent policy allows:

- `fs_read` on `./**` - read any workspace file silently
- `shell` for common git read-only commands - `git status`, `git log`, `git diff`, `git branch`, and similar
- `shell` for system info commands - `pwd`, `whoami`, `uname`, and similar
- Utility tools (diagnostics, knowledge, and similar)

The Kiro scope (hardcoded, not changeable by configuration) enforces:

- **Always denied:** writes to `~/.kiro/settings/`, `.kiro/settings/`, and `~/.kiro/workspace-roots/` (prevents the agent from modifying its own permission files), to `.kiroignore` at any depth (it defines the agent's own read boundary), to the MCP configuration of an installed Power (`~/.kiro/powers/installed/<name>/mcp.json`), and to Kiro's own state stores (`~/.kiro/sandbox-state/`, `~/.kiro/web-session/`, `~/.kiro/cloud-cache/`, `~/.kiro/sandbox-curl/`)
- **Always asks:** writes to `.git/**`, `.vscode/**`, `**/*.code-workspace`, and the `agents`, `hooks`, `workflows`, and `powers` directories of both the workspace `.kiro` and `~/.kiro`. These ask in trusted and untrusted workspaces alike, and no `allow` rule from any scope removes the prompt, with one exception inside the managed cloud sandbox described under [Workspace trust](#workspace-trust).
- **Asks while the workspace is untrusted:** writes to `.kiro/steering`, `.kiro/skills`, `.kiro/extensions`, the `.kiro/specs` directory itself, and any `.kiro` directory Kiro does not declare, even when a saved rule allows the write. See [Workspace trust](#workspace-trust).

Everything else prompts for approval. Creating a `permissions.yaml` adds to these defaults; it does not replace them.

## Workspace trust

Some agent inputs live inside the repository you open: custom agent profiles in `.kiro/agents/`, Steering files in `.kiro/steering/`, workspace MCP server configuration, Skills, and Workflow files. A cloned repository could use them to change how the agent behaves, so Kiro treats a workspace as untrusted until you trust it. Your decision is stored outside the workspace, so a repository cannot change its own trust status.

Until you trust a workspace, Kiro:

- Does not load the workspace's custom agents, Steering files, MCP server configuration, or Skills.
- Does not load Workflow files from the workspace, including files reached through a link from your home or cloud recipe directories. Your own home, cloud, bundled, and generated Workflows stay available.
- Asks before every shell command starts, including background processes, even when a saved or broad rule allows the command. The prompt shows the full command. A matching `deny` rule still refuses.
- Asks before every MCP tool call and before every Power activation, content read, or tool call, even when a saved rule or `autoApprove` allows it, and asks again when a call is retried after MCP authentication or a URL prompt. A matching `deny` rule still refuses.
- Asks before writing to `.kiro/steering`, `.kiro/skills`, `.kiro/extensions`, the `.kiro/specs` directory itself, or any `.kiro` directory Kiro does not declare, in both the workspace and `~/.kiro`, even when a saved rule allows the write. Writes to the `agents`, `hooks`, `workflows`, and `powers` directories ask in every workspace.
- Refuses writes to the memory database under `~/.kiro/memories/` and to the agent's session store (`~/.kiro/sessions/` by default) without prompting, so an untrusted session cannot rewrite another session's state.
- Does not let the agent add, change, or delete memories, knowledge bases, or remote learnings. Reading them still works.

Your user, administration, agent, and session rules still apply, and so does the per-workspace store under `~/.kiro/workspace-roots/`: it lives outside the repository, so it loads regardless of trust.

Trust changes one tier of `.kiro` writes and leaves the others alone. The table applies to both the workspace `.kiro` and `~/.kiro`; files under `.kiro/specs/` follow your ordinary rules.

| Path under `.kiro` | Untrusted workspace | Trusted workspace |
| --- | --- | --- |
| `steering`, `skills`, `extensions`, the `specs` directory itself, any directory Kiro does not declare | Asks, even when a saved rule allows the write | Follows your rules |
| `agents`, `hooks`, `powers`, `workflows` | Asks | Asks, except as described under the `fs_write` exception below |
| `settings` | Refused | Refused |

A matching `deny` rule wins in every row.

One rule lifts the untrusted-only asks for `.kiro` directories: an `fs_write` `allow` rule in your own `~/.kiro/settings/permissions.yaml` with no `match` restriction and no `exclude`. It does not remove the always-ask paths, does not override a matching `ask` or `deny`, and does not load the untrusted workspace inputs listed above. One environment widens that rule: in a trusted workspace inside the managed cloud sandbox that cloud sessions run in, the same unrestricted user-level `fs_write` `allow` also lifts the always-ask prompts for `.git/**`, `.vscode/**`, `**/*.code-workspace`, and the `agents`, `hooks`, `workflows`, and `powers` directories. Outside the cloud sandbox, those paths ask in every workspace.

### Trust a workspace in Kiro CLI

An interactive V3 session shows a **Trust this workspace?** screen the first time you start Kiro CLI in a folder, before it loads the folder's hooks, agents, MCP servers, steering, workflows, or language server configuration. Non-interactive runs (`--no-interactive`) and V1 sessions are not gated: they load workspace configuration without asking. The screen is specific to Kiro CLI.

1. Start Kiro CLI in the project folder. The screen shows the folder path and warns that the folder can contain hooks, agents, MCP servers, and workflows that run commands on your machine.
2. Choose **Trust, continue** to load the folder's configuration and start the session, or **Don't trust, exit** to leave. Declining exits Kiro CLI without loading anything from the folder and prints `Not trusted: <folder>. Kiro exited without loading this folder.`
3. Kiro saves a trusted answer as `workspaceTrusted` in the per-workspace permissions file under `~/.kiro/workspace-roots/`, so the screen appears once per folder. The screen names the exact file.

When the folder is your home directory, the screen notes that its `.kiro` configuration is your user-level configuration, and the answer lasts for that session only. Trust for your home directory is never saved, so Kiro asks at every launch there.

Pass `--trust-workspace` to trust the current folder for one V3 launch. The flag skips the prompt and does not save `workspaceTrusted`, so a later launch asks again unless you previously saved trust for that folder.

To revoke trust, remove the `workspaceTrusted` line from the file the screen named; the next launch in that folder shows the screen again. To confirm a folder is trusted, start Kiro CLI in it again: the screen does not appear and the session starts with the folder's configuration loaded.

## Managing permissions by surface

    IDE
    CLI
    Web

### Permission modes

The permission mode menu in the chat input sets how much Kiro does without asking in that chat: **Supervised**, **Accept file changes**, or **Approve for me**. Where Approve for me is not available, the chat shows the Autopilot switch instead, which toggles between Supervised and Accept file changes (formerly Autopilot). **Settings → Agent → Agent Autonomy** (settings key: `kiroAgent.agentAutonomy`) sets the starting mode for new chats; its values are still named Autopilot and Supervised.

The capability-based permissions layer applies after the mode decides whether to proceed. In Accept file changes, allowed operations run without prompting while your deny and ask rules still gate specific capabilities. In Supervised, Kiro asks before actions regardless. In Approve for me, a model judges only the actions no rule settles. See [Approve for me](#approve-for-me).

### Interactive approval flow

When a tool requires approval, a prompt appears in chat. **Allow** and **Deny** are available for the current invocation. Kiro also shows persistent choices when it can derive a saved rule that will work for the requested command:

| Action | Effect |
|--------|--------|
| **Allow** | Approve this specific invocation once |
| **Always allow** | Create a persistent allow rule (opens pattern/scope picker) |
| **Deny** | Block this specific invocation once |
| **Always deny** | Create a persistent deny rule |

If Kiro cannot verify a working saved rule, it hides **Always allow** and **Always deny** and explains why in the prompt.

When you select **Always allow** or **Always deny**, you configure two things:

- **Pattern** - choose the match scope for the rule (e.g., `cd *` for any cd command, or the exact command path)
- **Apply to** - choose where the rule persists:
  - **All workspaces** - saved to user-scoped `~/.kiro/settings/permissions.yaml`
  - **This workspace** - saved to `~/.kiro/workspace-roots/<hash>/permissions.yaml` (per-user, outside the repository). In Kiro IDE, when the window has more than one workspace folder, this choice reads **This workspace folder (*folder-name*)**, so you can see which folder the rule is saved for. The label does not change how the rule is enforced: shell command rules still apply to the whole session. In Kiro IDE, the choice is also hidden for files and folders outside every workspace folder.
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

Use the approval picker for a specific operation or tool, and use `permissions.yaml` for rules that should apply beyond the current session.

**⚠️ Warning:** Using `/tools trust-all` carries risks. In the terminal UI, both `--trust-all-tools` and `/tools trust-all` show a confirmation warning before granting access. You must acknowledge the risk before proceeding.

With trust-all on, a workflow plan approval is answered with its one-time Allow option and saves no rule; see [Start from the agent](https://kiro.dev/docs/workflows.md#start-from-the-agent).

### Available built-in tools

Kiro CLI V3 exposes the tools listed in the [built-in tools reference](https://kiro.dev/docs/tools.md). The `/tools` panel shows the exact set available in your current session, including MCP tools and the subset selected by the active agent.

Configure an [AWS MCP server](https://kiro.dev/docs/mcp/configuration.md) for AWS access. To report a Kiro CLI issue, run `kiro-cli issue`.

When Kiro attempts to use a tool that doesn't have explicit permission, it asks for your approval. A panel-based dropdown appears with Yes, Trust, and No options. When multiple tools need permission simultaneously, approvals are queued and presented one at a time. Choosing **Trust** also auto-approves any other pending invocations of that same tool in the current batch.

### Approval scopes in CLI V3

When Kiro asks to run a shell command and you choose **Trust**, the V3 picker can offer these match scopes, depending on the command:

```text
> Trust "git pull --rebase"   → exact command
  Trust "git pull *"          → subcommand with any arguments
  Trust "git *"               → base command with any arguments
  Trust entire tool           → every shell command
```

| Match | What it trusts | Example pattern |
| --- | --- | --- |
| Exact command | Only the command as written | `git pull --rebase` |
| Subcommand | The command's first two words with any arguments | `git pull *` |
| Base command | The executable with any arguments | `git *` |
| Entire tool | All shell commands | `*` |

The picker offers the subcommand match when the command's second word is a plain word, such as `pull` or `stash`, and differs from the command itself. It offers neither the subcommand nor the base command match for a command that starts with a privilege or environment wrapper such as `sudo` or `env`, or with an environment assignment. For which tier to pick, see [Approval rule tiers](#approval-rule-tiers).

The picker defaults to the current session. Press `s` to cycle the persistence scope among **session**, **workspace**, and **user** before saving the choice. Session approvals stay in memory until the session ends. Workspace and user approvals persist through the V3 permission store. For chained commands such as pipes or `&&`, Kiro evaluates each command separately.

For a write approval, choose **Allow a folder** to grant access to the selected folder and every folder under it. You can grant any eligible folder for the current session. A folder inside the workspace can also use workspace scope. A folder outside the workspace can use user scope. Later matching writes reuse the grant unless an `ask` or `deny` rule applies.

The chosen folder must contain every path in the pending write. Enter workspace-relative paths for workspace folders and full paths for folders outside the workspace. Folder patterns, `..`, and `~` are not accepted.

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

A headless run denies sub-agent tool calls that the parent session's policy doesn't allow, even when the sub-agent's own rules allow them. Add the sub-agent's `allow` rules to the parent agent or to `permissions.yaml`, or use `--trust-all-tools`. See [Sub-agent permissions](https://kiro.dev/docs/custom-agents/subagents.md#sub-agent-permissions).

    Kiro Web does not use `permissions.yaml`. By default, the agent runs without per-action prompts inside an isolated [cloud sandbox](https://kiro.dev/docs/web/sandbox.md), so file changes and commands affect the sandbox rather than your computer. To have a model approve, block, or send to you the actions that no rule settles, turn on [Approve for me](#approve-for-me-in-kiro-web).

    The sandbox boundary does not grant access to external systems by itself. You separately control its [internet access](https://kiro.dev/docs/web/sandbox/internet-access.md), [environment variables](https://kiro.dev/docs/web/sandbox/environment-variables.md), MCP servers, and any AWS role you configure. Grant only the access required for your work.

## Approve for me

Approve for me lets Kiro approve routine actions for you instead of asking at every prompt. Kiro approves actions it judges safe, blocks ones it judges unsafe, and asks you when it is unsure. Each action it approves is marked **Approved for you** on the tool card. It is available in Kiro IDE chats, interactive local V3 sessions of Kiro CLI, and Kiro Web, in sessions where Kiro offers it; where it is not offered, Kiro keeps asking.

    IDE
    CLI
    Web

A chat where Approve for me is available replaces the Autopilot toggle in the chat input with a permission mode menu. A chat where it is not available keeps the Autopilot toggle. The menu offers three modes:

- **Supervised:** Kiro pauses after each turn that edits files so you can accept or reject each change.
- **Accept file changes:** Kiro creates, edits, and deletes files without asking. It asks before it runs commands. This mode was called Autopilot and works the same way.
- **Approve for me:** For actions your rules do not cover, a model approves ones it judges safe, blocks ones it judges unsafe, and asks you when it is unsure.

To turn it on for the current chat, open the permission mode menu in the chat input and choose **Approve for me**. The mode applies from Kiro's next action and stays with that chat. To turn it off for that chat, choose **Supervised** or **Accept file changes**.

To turn it on for new chats, do one of the following:

- In **What's new**, turn on **Use Approve for me by default**. It applies to new chats in all workspaces.
- In Kiro IDE 1.4.178 or later, open the Command Palette and run **Kiro: Approve For Me (User)...** for every workspace, or **Kiro: Approve For Me (Workspace)...** for the folders open in the current window. Choose **Turn on (currently off)**. If the open folders have different settings, choose **Turn on for all folders (currently mixed)**. In Kiro IDE 1.4.154, run **Kiro: Enable Approve For Me (User)** or **Kiro: Enable Approve For Me (Workspace)** instead.

To check the setting, run the same command again. It offers **Turn off (currently on)** when Approve for me is on for new chats.

A new chat covered by that choice starts in Approve for me. A chat where you already chose a mode keeps your choice. An untrusted workspace starts in Supervised with Approve for me off. If your organization manages Approve for me, the switch in What's new says so and you cannot change it. If your organization requires Approve for me, the commands say it is always on and offer no change.

To turn it off for new chats, run **Kiro: Approve For Me (User)...** or **Kiro: Approve For Me (Workspace)...** and choose **Turn off (currently on)**, or **Turn off for all folders (currently mixed)** if the open folders have different settings. You can also turn off the switch in **What's new**. In Kiro IDE 1.4.154, run **Kiro: Disable Approve For Me (User)** or **Kiro: Disable Approve For Me (Workspace)**. These commands do not appear in a window connected to a cloud session.

An interactive local V3 session can let Kiro approve routine actions for you instead of asking at every prompt, when the **approve for me** option appears on the `/permissions` **Policies** page. The option appears only in sessions where Approve for me is available; otherwise the **Policies** page says so and Kiro keeps asking. The status line shows **Approve for me** while the mode is on. `/permissions` is not available in cloud sessions.

To turn it on:

1. Run `/permissions` and choose **Policies**.
2. Choose **approve for me** when the page offers it. When the page says instead that Approve for me is unavailable in your session, Kiro keeps asking and there is nothing to set. Otherwise, Kiro adds the `approve-for-me` policy preset to the workspace permissions file (`~/.kiro/workspace-roots/<hash>/permissions.yaml`), so the choice stays with that repository:

```yaml
policies:
  - approve-for-me
```

To turn it off, run `/permissions`, choose **Policies**, then **ask for approval**. Kiro removes the preset from the workspace file. If the preset is listed in your user-scoped `~/.kiro/settings/permissions.yaml`, remove it there by hand.

To verify, run `/permissions`, choose **Policies**, and confirm that **approve for me** is marked `[active]`.

### Approve for me in Kiro Web

By default, Kiro Web approves every agent action inside the [cloud sandbox](https://kiro.dev/docs/web/sandbox.md). To add a safety check, open **Agent Config > Tool approvals** and turn on **Approve for me**. A model then approves actions deemed safe, blocks ones deemed unsafe, and asks you when it's unsure, so a session may pause while it waits for your answer. If nobody is connected, the request waits for the next client that opens the session.

- The setting is read when a session is created, so it applies to sessions you start after turning it on. Sessions that are already running keep their current behavior.
- Autonomous sessions aren't affected. This includes sessions Kiro starts for you from a GitHub comment or a scheduled task, which run in autonomous mode.
- Each action the model approved is marked **Approved for you** on its tool call. A blocked action fails, and its tool call shows the reason. When Kiro asks you instead, the prompt says why the action was flagged, or that the action was too large to check automatically.
- If the model keeps blocking actions, in several responses in a row or many times in one session, Kiro stops blocking and asks you about each action it flags, and the prompt includes the reason.
- To turn it off, turn off the **Approve for me** switch. Sessions you start afterward approve every action again.

To verify, open **Agent Config > Tool approvals** and confirm that the **Approve for me** switch is on, then start a new session.

Approve for me works through the `evaluate` effect, the weakest effect in the rule chain. Every deny, ask, and allow rule you already have decides first, and Approve for me handles only what no rule settles. The preset also allows workspace reads and writes and the read-only shell commands outright, so those never wait for a verdict. The preset is listed with the others under [Available presets](#available-presets).

### Security and trust

- In Kiro Web, an approved action runs inside the [cloud sandbox](https://kiro.dev/docs/web/sandbox.md). Approve for me does not change the sandbox's [internet access](https://kiro.dev/docs/web/sandbox/internet-access.md), environment variables, MCP servers, or AWS role. The other points in this section cover Kiro IDE and CLI.
- With Approve for me on, Kiro can run shell commands and take other actions within the workspace that no rule settles without asking you first.
- Kiro judges each unsettled action with its trust classifier. This differs from the CLI's `--trust-all-tools` and `/tools trust-all`, which trust every tool action your rules do not deny: Approve for me can still block an action or ask you.
- Approve for me does not replace your security controls. Keep `deny` rules for the actions you never want run, and turn on the [local command sandbox](https://kiro.dev/docs/sandbox.md) so an approved command is also limited in what it can reach.
- A choice made for a workspace is workspace-scoped: it reaches only that workspace. A file operation outside the workspace is not judged by Approve for me and keeps its ordinary prompt.
- Your `deny` rules at every scope, Kiro's built-in ask rules for file writes listed under [Trust invariants](#trust-invariants), and any action Kiro judges unsafe still block or ask. Kiro also asks whenever it is unsure, and whenever the trust classifier is unavailable.
- Turn it off in the IDE by running **Kiro: Approve For Me (User)...** or **Kiro: Approve For Me (Workspace)...** and choosing **Turn off (currently on)**, in the CLI under `/permissions` → **Policies** → **ask for approval**, or remove `approve-for-me` from `policies:` in the permissions file that lists it.

## Approval rule tiers

When a V3 session asks about a shell command, the rule picker offers up to three match tiers for the rule it saves:

| Tier | Example for `git stash pop` | What it covers |
| --- | --- | --- |
| Exact match | `git stash pop` | Only the command as written |
| Subcommand | `git stash *` | The command's first two words with any arguments |
| Pattern | `git *` | The base command with any arguments |

The subcommand tier appears when the command's second word is a plain word, such as `stash` or `Makefile`, and differs from the command itself. Kiro offers neither pattern tier for a command that starts with a privilege or environment wrapper such as `sudo` or `env`, or with an environment assignment. Pick the narrowest tier that covers what you repeat; prefer the subcommand tier when you repeat one operation such as `git stash`, and the pattern tier when you trust a whole command. The persistence scopes and the write-folder picker are described under [Approval scopes in CLI V3](#approval-scopes-in-cli-v3).

To verify, run the same command again. A command that matches the saved rule no longer asks.

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

If you're upgrading from IDE 0.x, see the reference page for how permissions worked previously and what changed:

- [IDE 0.x reference - Permissions](https://kiro.dev/docs/ide/0x-reference.md#permissions-autopilot--supervised-toggle)
