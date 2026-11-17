> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Permissions in CLI V3

> How trust and approvals work in CLI V3: persistent rules in `permissions.yaml`, session-scoped trust, and headless runs

> Without a `permissions.yaml`, Kiro allows workspace reads and common read-only commands, blocks writes to its own settings, and asks before other operations. The [current permissions reference](https://kiro.dev/docs/permissions.md) covers the full model.

CLI V3 keeps persistent trust in structured `permissions.yaml` policies. The `--trust-all-tools` startup flag and `/tools trust-all` slash command grant session-wide trust. In non-interactive V3 runs, `--trust-tools` can pre-approve exact V3 tool IDs; the interactive V3 terminal UI ignores that flag. Use scoped `permissions.yaml` allow rules for reusable capability policies.

The rule schema, scopes, effects, presets, and pattern syntax are documented once in [Permissions](https://kiro.dev/docs/permissions.md). This page covers the V3 session-scoped controls, persistent rule locations, and headless behavior.

## Session-scoped commands

These controls apply only to the current session:

```bash
# Trust every tool in a V3 session
kiro-cli chat --v3 --trust-all-tools

# In headless V3, trust exact tool IDs
kiro-cli chat --v3 --no-interactive --trust-tools=read_file,grep_search "Review this repository"

# In interactive V3, trust every tool after startup
/tools trust-all
```

In V3, `--trust-tools` is honored only with `--no-interactive`. It matches tool IDs and also accepts `@server` references, `@builtin`, and `*`/`?` patterns (see [Headless mode](https://kiro.dev/docs/cli/headless.md)). The interactive V3 terminal UI ignores it. For reusable or capability-level rules, use `permissions.yaml`.

## Persistent rules

Create `~/.kiro/settings/permissions.yaml` for user-scoped rules, or a workspace-scoped file at `~/.kiro/workspace-roots/<hash>/permissions.yaml` to scope rules to one project. Workspace files are stored per-user outside the repository, so a cloned repo cannot inject permission rules. For the file format, scopes, and worked examples, see [Defining rules](https://kiro.dev/docs/permissions.md#defining-rules) and [Scopes](https://kiro.dev/docs/permissions.md#scopes).

## Approve for me

Approve for me and its `evaluate` effect are documented in [Permissions](https://kiro.dev/docs/permissions.md#approve-for-me).

## Approval rule tiers

The three-tier rule picker that appears when a V3 session asks about a shell command is documented in [Permissions](https://kiro.dev/docs/permissions.md#approval-rule-tiers).

## CI and headless environments

For CI pipelines, create a user-scoped permissions file in your CI environment:

```yaml
# ~/.kiro/settings/permissions.yaml (CI environment)
rules:
  - capability: all
    effect: allow
```

The `--trust-all-tools` flag works as a session-scope override in CI runs.

A headless run denies sub-agent tool calls that the parent session's policy doesn't allow, even when the sub-agent's own rules allow them. `--trust-all-tools` approves sub-agent tool calls that would otherwise prompt. `deny` rules still apply.
