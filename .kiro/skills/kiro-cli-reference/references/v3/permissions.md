> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Permissions migration

> Migrating from CLI 2.x trust flags to the capability-based permissions model in CLI 3.0

> **New to Kiro CLI 3.0?** This page covers changes from CLI 2.x. If you're setting up permissions for the first time, start here: **Default behavior (no permissions.yaml):** All operations prompt for approval. Nothing is silently allowed or denied. Create a `permissions.yaml` to pre-approve trusted operations and reduce interruptions.

The permissions system is the most significant change in CLI 3.0. Trust flags and slash commands are replaced by a structured `permissions.yaml` policy that gives you fine-grained, auditable control over what the agent can do.

**ℹ️ Info:** Run `kiro-cli agent migrate` to auto-convert compatible permission rules and get a report of what needs manual attention.

The core shift: instead of flags enabling broad access, you declare exactly which capabilities are allowed and for which operations. Everything else prompts or blocks by default.

## Behavioral changes from 2.x

| 2.x Behavior | 3.0 Behavior | Migration |
|--------------|--------------|-----------|
| `toolsSettings` removed | Per-tool settings block (`allowedCommands`, `deniedPaths`, etc.) | Unified `permissions.rules` with `capability`/`match`/`effect` | Rewrite using the [toolsSettings migration table →](https://kiro.dev/docs/cli/v3/migration-guide.md#4-update-agent-configs) |
| `autoAllowReadonly` auto-approved read-only shell commands | No equivalent — explicitly list allowed commands | Add `shell` allow rules for read-only commands you use |
| `denyByDefault` blocked unlisted tools | No equivalent | Use `exclude` to allow exceptions: `` denies everything except the excluded patterns |
| Regex patterns in permissions | Glob patterns only (no regex) | Rewrite `.*` as `*`, `\.ts$` as `*.ts`, etc. |
| `?` single-char wildcard | Not supported for shell/URL patterns | Use `*` or spell out alternatives. File path patterns (`fs_read`, `fs_write`) still support `?` |
| Separate `fs_read`/`fs_write` per tool | Unified — a single `fs_read` deny blocks ALL read tools (read, glob, grep, code) | Be aware of broader blast radius |
| Per-tool deny was independent | deny-always-wins across all scopes | A deny anywhere blocks the action regardless of allows elsewhere |

## Old approach

```bash
kiro-cli --trust-all-tools
kiro-cli --trust-tools shell,write

/tools trust write
/tools trust-all
```

## New approach

Create `~/.kiro/settings/permissions.yaml` for user-scoped rules:

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

Workspace-scoped rules (`~/.kiro/workspace-roots/<hash>/permissions.yaml`) are stored per-user outside the repository, so a cloned repo cannot inject permission rules. Use them to scope rules to one project: repo cannot inject permission rules. Use them to scope rules to one project:

```yaml
rules:
  - capability: shell
    match: ["rm -rf *", "sudo *"]
    effect: deny

  - capability: fs_write
    match: ["*.env", "*.pem", "*.key"]
    effect: deny
```

Rules are evaluated using a deny-overrides algorithm: deny > ask > allow. There is no precedence between scopes — the most restrictive effect wins regardless of which scope it came from.

## Scopes

| Scope | Location | Allowed effects |
|-------|----------|-----------------|
| Kiro | Hardcoded security invariants (cannot be overridden) | deny, ask |
| administration | Enterprise/MDM-managed policy (enterprise plans only) | deny, ask |
| user | `~/.kiro/settings/permissions.yaml` | deny, ask, allow |
| workspace | `~/.kiro/workspace-roots/<hash>/permissions.yaml` | deny, ask, allow |
| agent | Embedded in agent profile (`permissions` field) | deny, ask, allow |
| session | Runtime (e.g., `--trust-all-tools`) | deny, ask, allow |

### Default permissions (no permissions.yaml)

Without any configuration, the agent applies these built-in defaults:

- `fs_read` on `./**` — read any workspace file silently
- `shell` for common git read-only commands — `git status`, `git log`, `git diff`, and similar
- `shell` for system info commands — `pwd`, `whoami`, `uname`, and similar
- `fs_write` to `~/.kiro/settings/` and `.kiro/settings/` — **always denied** (prevents privilege escalation)
- Everything else — prompts for approval

Creating a `permissions.yaml` adds to these defaults; it does not replace them. The deny on settings paths is always enforced.

### CI and headless environments

For CI pipelines that previously used `--trust-all-tools`, create a user-scoped permissions file in your CI environment:

```yaml
# ~/.kiro/settings/permissions.yaml (CI environment)
rules:
  - capability: all
    effect: allow
```

The `--trust-all-tools` flag still works as a session-scope override and continues to function for CI use cases without configuration changes.

## Available capabilities

`fs_read`, `fs_write`, `shell`, `web_fetch`, `web_search`, `mcp`, `subagent`, `skill`, `power`, `context`, `diagnostics`, `sandbox_network`. Meta-capabilities: `all` (everything), `builtin` (all built-in tools), `filesystem` (`fs_read` + `fs_write`).

## Exclude syntax

Rules also support an `exclude` field for "allow everything except" patterns:

```yaml
rules:
  - capability: mcp
    match: ["my-server/*"]
    exclude: ["my-server/dangerous-tool"]
    effect: allow
```
