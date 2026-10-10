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

Pass `--no-interactive` with your initial instruction. The instruction can be a positional argument or supplied through piped stdin. When stdin is piped and no positional argument is given, Kiro reads the full stream as the instruction:

```bash
# Positional argument
kiro-cli chat --no-interactive "your prompt here"

# Stdin only: pipe the entire instruction
printf '%s\n' "your prompt here" | kiro-cli chat --no-interactive
```

Since there's no user to approve tool calls, use `--trust-all-tools` or `--trust-tools` to grant permissions upfront:

```bash
# Trust all tools
kiro-cli chat --no-interactive --trust-all-tools "Write tests for the auth module and run them"

# Trust only specific tool categories
kiro-cli chat --no-interactive --trust-tools=read,grep "Find all TODO comments in src/"
```

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
        run: kiro-cli chat --no-interactive --trust-tools=read,grep "Review the changes in this PR for security issues"
```

### Other patterns

```bash
# Generate and run tests
kiro-cli chat --no-interactive --trust-all-tools "Write tests for the auth module and run them"

# Troubleshoot a failing build with the full instruction on stdin
{
  printf '%s\n\n' "Explain this build failure and suggest a fix:"
  cat build-error.log
} | kiro-cli chat --no-interactive --trust-tools=read
```

Use `--require-mcp-startup` when a non-interactive run depends on MCP tools. V2 and V3 wait for configured MCP servers before submitting the instruction. In V3, Kiro exits with code 3 if a server fails, its startup state cannot be determined, or it does not report a status within 30 seconds. Without the flag, Kiro logs MCP startup problems and continues. See [exit codes](https://kiro.dev/docs/reference/exit-codes.md) for handling failures in scripts.

## Structured output

Pass `--output-format stream-json` to receive run events as [JSON Lines](https://jsonlines.org/) on stdout. Each line is a self-contained JSON object, making the output easier to process in scripts, logging pipelines, and CI jobs than formatted text.

```bash
kiro-cli chat --no-interactive --trust-all-tools --output-format stream-json "Summarize open TODOs in src/"
```

`--output-format stream-json` requires V2 or V3 (`--agent-engine v2` or `--agent-engine v3`).

### Handle interrupted runs

In V3, an interrupted non-interactive run writes a final interruption record to `stream-json`. Treat that final record as the end of the interrupted run instead of waiting for another completion record.

## Flags reference

| Flag | Description |
|------|-------------|
| `--no-interactive` | Run without an interactive session. Requires a non-empty instruction, either as a positional argument or via piped stdin |
| `--agent-engine <v1\|v2\|v3>` | Select the agent engine version. Shorthand flags `--v2` and `--v3` are also accepted |
| `--output-format stream-json` | Emit run events as JSON Lines on stdout for programmatic use (V2/V3 only) |
| `--trust-all-tools` | Auto-approve all tool calls without prompting |
| `--trust-tools=<categories>` | Auto-approve specific tool categories (e.g., `read`, `grep`, `write`) |
| `--require-mcp-startup` | Wait for required MCP servers and exit with code 3 if startup fails |

## Best practices

- Store `KIRO_API_KEY` as a secret in your CI/CD platform — never hardcode it in pipeline configs or commit it to source control.
- Use `--trust-tools` with specific categories instead of `--trust-all-tools` to follow the principle of least privilege.
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
