> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Headless mode

> Run Kiro CLI non-interactively in CI/CD pipelines, automation scripts, and environments without a browser

Headless mode lets you run Kiro CLI as part of your CI/CD pipeline to automate code reviews, generate tests, or troubleshoot build failures — no interactive terminal required. Authenticate with an API key, pass a prompt, and Kiro executes it end-to-end.

## Authentication

Headless mode requires an API key set as the `KIRO_API_KEY` environment variable. If you haven't created one yet, follow the steps in [Generate an API key](https://kiro.dev/docs/getting-started/authentication.md#api-key-authentication-cli).

**ℹ️ Info:** API key authentication is only available for Kiro Pro, Pro+, Pro Max, and Power subscribers. If your subscription is managed by an administrator, they need to enable API key generation first. See [API key governance](https://kiro.dev/docs/enterprise/governance/api-keys.md).

For details on authentication precedence and checking your active credentials, see [Authentication](https://kiro.dev/docs/getting-started/authentication.md).

**ℹ️ Info:** API keys are associated with your user account. Any governance rules configured by your Kiro administrator — including MCP server restrictions, model access policies, and web fetch permissions — apply to headless sessions the same way they apply to interactive ones.

## Running headless commands

Pass `--no-interactive` with your initial instruction. The instruction can be a positional argument or supplied through piped stdin. When stdin is piped and no positional argument is given, Kiro reads the full stream as the instruction. A local headless run that names no harness runs V2, with the exceptions listed under [Scripts and CI](https://kiro.dev/docs/cli/agent-harness.md#scripts-and-ci); add `--v3` or `--v2` so the run does not depend on the default.

```bash
# Positional argument
kiro-cli chat --no-interactive "your prompt here"

# Stdin only: pipe the entire instruction
printf '%s\n' "your prompt here" | kiro-cli chat --no-interactive
```

Since there is no user to approve tool calls, local V3 sessions can use `--trust-all-tools` for session-wide approval or `--trust-tools` with a comma-separated list of tool IDs. Use scoped `permissions.yaml` rules for reusable capability policies. CLI 2.x uses its own tool names with `--trust-tools`.

In Kiro CLI 3.3.0 or later, a `--trust-tools` entry in a `--no-interactive` V3 run can also be a V2 tool name, `@server` or `@server/tool` for an MCP server's tools, `@builtin`, or a `*`/`?` pattern. A V2 name trusts every V3 tool in its permission capability, so `--trust-tools=write` also trusts `delete_file` and `str_replace`; `read` never trusts the `code` tool, and `grep`, `glob`, `code`, and `introspect` trust only their own tools. A trusted tool runs on any path it would ask about, outside the workspace too. A `--no-interactive` V2 run accepts the V3 shell IDs `run_command` and `execute_pwsh`, and patterns that name them, as its `shell` tool.

```bash
# V3: trust all tools for this session
kiro-cli chat --v3 --no-interactive --trust-all-tools "Write tests for the auth module and run them"

# V3: trust only the exact tools needed
kiro-cli chat --v3 --no-interactive --trust-tools=read_file,grep_search "Find all TODO comments in src/"
```

In V3, a sub-agent's tool call runs without approval only when the parent session's policy also allows it. Otherwise the call needs approval, so a headless run denies it with this error:

```text
[denied] tool permission approval is not supported in non-interactive mode. Use --trust-all-tools to auto-approve.
```

Adding the sub-agent to `trustedAgents` doesn't change this. Add the sub-agent's `allow` rules to the parent agent's `permissions.rules` or to `permissions.yaml`, or use `--trust-all-tools`. See [Sub-agent permissions](https://kiro.dev/docs/custom-agents/subagents.md#sub-agent-permissions).

### Run a prompt or SOP as the first message

In Kiro CLI 2.33 or later, a first message that starts with `@<prompt-name>` runs that prompt instead of sending the text as typed, both in an interactive session and with `--no-interactive`. The name matches a workspace, global, or MCP prompt, case-insensitively; `@agent-sop:<name>` runs the named SOP. Text after the name becomes the prompt's arguments. Before 2.33, a first message that named a prompt from an MCP server still starting was sent as typed.

```bash
kiro-cli chat --agent <agent> --no-interactive "@agent-sop:<name> Payments eu-west-1"
```

Kiro waits for the MCP servers that serve prompts to finish starting, up to 30 seconds by default, before it decides. A name that no prompt matches once every server has started is sent as typed. A path-like mention such as `@src/main.rs` stays a file reference. To confirm the SOP is available to the agent, start an interactive session with the same `--agent` and run `/prompts list`; the SOP appears under its `agent-sop:` name.

### V3 Hooks and built-in tools

Starting with Kiro CLI 2.27.1, V3 non-interactive runs load Hooks from the selected agent and workspace. `PreToolUse` Hooks run before a tool call and can deny it. See [Hooks](https://kiro.dev/docs/hooks.md) for supported triggers and actions.

`--trust-all-tools` approves Hook confirmation requests automatically. `--trust-tools` cannot, because a Hook request is not tied to a tool ID. Without `--trust-all-tools`, Kiro denies it. A Hook that blocks is final under either flag. For automation, write Hooks that return a final allow or deny decision.

V3 non-interactive runs enable knowledge and code intelligence by default. Set `chat.enableKnowledge` or `chat.enableCodeIntelligence` to `false` to turn either tool off. See [Built-in tools](https://kiro.dev/docs/tools.md) and the [settings reference](https://kiro.dev/docs/reference/settings.md#knowledge-base).

### Saved V3 settings

Kiro CLI 2.31.1 and later applies saved compaction and Tool Search settings to V3 non-interactive runs.

| Purpose | Settings |
|---|---|
| Automatic compaction | `chat.disableAutoCompaction`, `compaction.excludeMessages`, `compaction.excludeContextWindowPercent` |
| Tool Search | `toolSearch.enabled`, `toolSearch.minPct`, `toolSearch.minTokens` |

To apply saved Tool Search thresholds, also save `toolSearch.enabled true`.

Save values with `kiro-cli settings`, as you do for interactive sessions:

```bash
kiro-cli settings compaction.excludeMessages 4
kiro-cli settings toolSearch.enabled true
```

If a headless run behaves differently after upgrading, run `kiro-cli settings list` to find saved `compaction.*` or `toolSearch.*` values. Remove an unwanted global value with `kiro-cli settings --delete <name>`. For a value marked `(workspace)`, add `--workspace` after `settings`. Removing a value also affects interactive sessions.

See [Compaction](https://kiro.dev/docs/compaction.md#configuration), [Tool Search](https://kiro.dev/docs/mcp/tool-search.md), and the [settings reference](https://kiro.dev/docs/reference/settings.md) for each setting.

## Local command sandbox

Kiro CLI 2.31 and later V3 headless runs read global and project `sandbox.json` settings. When the resolved settings have `enabled: true`, Kiro requests sandboxing without an extra flag. If Kiro cannot activate the sandbox, the run warns and continues without sandboxing. If requested MCP wrapping fails, sandboxed commands stay protected, but the affected MCP servers do not.

Add `--sandbox` when your script must stop instead of continuing without all requested protection:

```bash
kiro-cli chat --v3 --sandbox --no-interactive "Run the test suite"
```

The run exits before the task starts when the sandbox cannot activate. It also exits when `mcpSandboxing` is enabled but local MCP servers cannot be wrapped. See [Local command sandbox](https://kiro.dev/docs/sandbox.md#require-the-sandbox-in-headless-runs/cli) for platform setup, configuration, and recovery.

## CI/CD examples

### GitHub Actions

```yaml
name: Kiro Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Kiro CLI
        run: curl -fsSL https://cli.kiro.dev/install | bash
      - name: Review PR changes
        env:
          KIRO_API_KEY: ${{ secrets.KIRO_API_KEY }}
        run: kiro-cli chat --v3 --no-interactive --trust-tools=read_file,grep_search "Review the changes in this PR for security issues"
```

### Other patterns

```bash
# Generate and run tests
kiro-cli chat --v3 --no-interactive --trust-all-tools "Write tests for the auth module and run them"

# Troubleshoot a failing build with the full instruction on stdin
{
  printf '%s\n\n' "Explain this build failure and suggest a fix:"
  cat build-error.log
} | kiro-cli chat --v3 --no-interactive --trust-tools=read_file
```

Use `--require-mcp-startup` when a non-interactive run depends on MCP tools. V2 and V3 wait for configured MCP servers before submitting the instruction. In V3, Kiro exits with code 3 if a server fails, its startup state cannot be determined, or it does not report a status within 30 seconds. Without the flag, Kiro logs MCP startup problems and continues. See [exit codes](https://kiro.dev/docs/reference/exit-codes.md) for handling failures in scripts.

### Agent selection

Pass `--agent <name>` to run a non-interactive command with a specific agent. Without `--agent`, a fresh V3 run uses `chat.defaultAgent` when configured. If no default is configured, it uses the built-in default. Without an explicit model, a new V3 run applies `chat.defaultModel` when configured; a selected agent that specifies a model can override it. V2 resolves its default agent and model internally.

```bash
kiro-cli settings chat.defaultAgent my-project-agent
kiro-cli chat --v3 --no-interactive "Write tests for the auth module"  # runs on my-project-agent
```

**⚠️ Warning:** If the agent named by `--agent` isn't available, the run exits with code 4. A fresh V3 run also exits with code 4 when its configured `chat.defaultAgent` is unavailable. See [exit codes](https://kiro.dev/docs/reference/exit-codes.md) for exact rules and script handling.

Pass `--model <id>` to pin the model for a run. On V2 and V3, an explicit value overrides the selected agent's configured model; on V3, it also overrides `chat.defaultModel`, and on V2, it overrides a resumed session's saved model. V2 trims surrounding whitespace before passing an unlisted, non-empty ID to the backend; a blank value sends no override and leaves the current model selection unchanged. Without `--model`, a resumed session keeps its original agent and model.

**ℹ️ Info:** V3 headless runs do not use the terminal UI's model availability check or session-start notices. If Kiro cannot set the requested model, it writes a warning to stderr and continues the run.

Pass `--effort <level>` to set the reasoning effort for a non-interactive run. Supported levels depend on the selected model. In V3, the flag applies only to the session Kiro starts and does not change the saved per-model default.

## Structured output

Pass `--output-format stream-json` to receive run events as [JSON Lines](https://jsonlines.org/) on stdout. Each line is a self-contained JSON object, making the output easier to process in scripts, logging pipelines, and CI jobs than formatted text.

```bash
kiro-cli chat --v3 --no-interactive --trust-all-tools --output-format stream-json "Summarize open TODOs in src/"
```

`--output-format stream-json` requires V2 or V3 (`--agent-engine v2` or `--agent-engine v3`).

### Handle interrupted runs

In V3, an interrupted non-interactive run writes a final interruption record to `stream-json`. Treat that final record as the end of the interrupted run instead of waiting for another completion record.

## Waiting for in-flight workflows

If your instruction starts a workflow and the turn ends before it settles, a non-interactive V3 run waits for it before exiting. The default timeout is six hours.

Override the timeout with the `KIRO_HEADLESS_WORKFLOW_TIMEOUT_SECS` environment variable, in seconds:

```bash
# Wait up to 10 minutes for workflows to settle
KIRO_HEADLESS_WORKFLOW_TIMEOUT_SECS=600 kiro-cli chat --v3 --no-interactive "Run the release-check workflow"
```

The value must be a positive whole number of seconds no greater than the six-hour default. An invalid, zero, or over-cap value falls back silently to the six-hour default rather than erroring.

Each workflow's progress is written to the run's output as it happens. When a workflow finishes, it reports one of these outcomes:

| Outcome | Meaning |
|---|---|
| `completed` | The workflow finished successfully. |
| `failed` | The workflow ended in a failure state. |
| `aborted` | The workflow was stopped before completion. |
| `paused` | The workflow is waiting at a pause point. |
| *(unknown status)* | Kiro couldn't determine the workflow's final state. |

If a workflow doesn't finish within the timeout, the run reports `workflow run incomplete (<outcomes>)` with a recovery hint. It does not report plain success.

## Cloud sessions in V3

Kiro CLI V3 can start a cloud session interactively or non-interactively. Add `--cloud` to run the task in a managed cloud sandbox, and `--repo` to start with one or more repositories.

```bash
kiro-cli --cloud --repo owner/repository
kiro-cli chat --v3 --no-interactive --cloud --repo owner/repository "Review the open pull request"
```

In Kiro CLI 3.4.0 or later, `--cloud --resume` continues your newest cloud session in a `--no-interactive` run. Kiro picks the newest cloud session across your account, not per directory. When you have no cloud session, the run stops with exit code 1 and prints `no cloud session to --resume; start one with --cloud`. Before 3.4.0, a headless run refused `--cloud` with `--resume`. `--repo` still cannot be combined with `--resume`.

```bash
kiro-cli chat --v3 --no-interactive --cloud --resume "Continue the task"
```

To confirm the run resumed, read stderr: a resumed run prints `[cloud] session <id>` with the existing session's ID, and the exit status is `0`.

For every cloud-session flag, the startup flow, repository setup, output, resume and delete behavior, and what differs from local sessions, see [Cloud sessions](https://kiro.dev/docs/cloud-sessions.md#cli).

## Plain-text failures and exit status

Plain-text runs explain when a turn was cancelled or refused. They also print why a session could not be created or resumed. A failed tool call includes its error message when one is available. If stdout closes before completion, Kiro exits with a nonzero status instead of finishing the turn.

In Kiro CLI 3.4.0 or later, a new V2 or V3 headless session whose prompt does not fit the model's context window, together with the agent's own system prompt, context files, and tool definitions, stops with exit code 1 and an error on stderr. Before 3.4.0, the run answered from a summarized or truncated copy of the prompt. A resumed session is not affected. Shorten the input, split it across several runs, or trim the agent's context files and tools, then run again. With `--output-format stream-json`, the run ends with an error record instead of a completion record; treat it as the end of the run. To confirm the cause, check the exit status after the run: it is `1`, and stderr says the prompt does not fit in the model's context window.

## Flags reference

| Flag | Description |
|------|-------------|
| `--no-interactive` | Run without an interactive session. Requires a non-empty instruction, either as a positional argument or via piped stdin |
| `--cloud` | Run the V3 task in a cloud session |
| `--repo <owner/repository>` | Add one or more comma-separated repositories to a V3 cloud session |
| `--resume-id <ID>` | Resume a local or cloud session by ID |
| `--resume` | Resume the newest matching session; see [session management](https://kiro.dev/docs/cli/chat/session-management.md). In Kiro CLI 3.4.0 or later, with `--cloud`, resume your newest cloud session, or exit with code 1 when there is none |
| `--agent <name>` | Run with a specific agent. When omitted, a fresh V3 run uses `chat.defaultAgent` when configured, or the built-in default otherwise |
| `--model <id>` | Pin the model for the run. Takes precedence over a model named in the agent configuration and, on V3, over `chat.defaultModel` |
| `--effort <level>` | Set reasoning effort for the run when the selected model supports it |
| `--agent-engine <v1\|v2\|v3>` | Select the agent harness version. Shorthand flags `--v2` and `--v3` are also accepted. In Kiro CLI 3.0.0 or later, a headless run that names no harness uses V2, with the exceptions under [Scripts and CI](https://kiro.dev/docs/cli/agent-harness.md#scripts-and-ci) |
| `--output-format stream-json` | Emit run events as JSON Lines on stdout for programmatic use (V2/V3 only) |
| `--trust-all-tools` | Auto-approve all tool calls without prompting |
| `--trust-tools=<tool-ids>` | Non-interactive V3: auto-approve the listed tool IDs; in Kiro CLI 3.3.0 or later, also V2 tool names, `@server` references, `@builtin`, and `*`/`?` patterns. CLI 2.x accepts its own tool names. Ignored by interactive V3 |
| `--sandbox` | Require the local command sandbox and exit if protection cannot start |
| `--require-mcp-startup` | Wait for required MCP servers and exit with code 3 if startup fails |

**Environment variables**

| Variable | Description |
|---|---|
| `KIRO_API_KEY` | API key used for headless authentication |
| `KIRO_HEADLESS_WORKFLOW_TIMEOUT_SECS` | Seconds a non-interactive V3 run waits for in-flight workflows to settle before exiting. Default: 21600 (six hours). Invalid, zero, or over-cap values fall back to the default |

## Best practices

- Store `KIRO_API_KEY` as a secret in your CI/CD platform — never hardcode it in pipeline configs or commit it to source control.
- Name the harness with `--v2` or `--v3` in every headless command, so the run does not change harness when you add or remove `--trust-all-tools`.
- In local headless V3 sessions, prefer `--trust-tools` with the tool IDs you need over `--trust-all-tools`. Use scoped `permissions.yaml` allow rules when the policy should be reusable.
- Add `--require-mcp-startup` when your pipeline depends on MCP servers, so the task stops before it begins instead of running without the expected tools.
- When using V2 or V3, supply your instruction as a positional argument or pipe it through stdin, but not both. V2 and V3 only read stdin when no positional argument is present.
- Check [exit codes](https://kiro.dev/docs/reference/exit-codes.md) in your pipeline to handle failures gracefully.
- Rotate API keys regularly and revoke any that are no longer in use from the [Kiro portal](https://app.kiro.dev).

## Limitations

- You must provide a non-empty initial instruction, either as a positional argument or through piped stdin.
- No mid-session user input is possible.
- Interactive slash commands (`/model` picker, `/agent` picker) are not available.
- Terminal UI features are disabled.

## Related

- [Authentication](https://kiro.dev/docs/getting-started/authentication.md) — API key setup and authentication methods
- [Exit codes](https://kiro.dev/docs/reference/exit-codes.md) — Handle failures in scripts
- [CLI commands](https://kiro.dev/docs/reference/cli-commands.md) — Full CLI flag reference
