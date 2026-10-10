> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Permission policies

> Deploy managed permission rules to control what Kiro's agent can do across your organization.

Deploy permission policies to your fleet to restrict what the agent can do. You can block dangerous shell commands, deny web access, or force prompts for specific capabilities. These rules take precedence over a user's own permission settings.

**⚠️ Warning:** Permission policies are enforced at the client level. As with any client-enforced configuration, they can be circumvented by users, e.g., via administrative access to their local machine.

## How it works

When an admin rule and a user rule target the same capability, the more restrictive effect wins:

**deny > ask > allow**

An admin `deny` blocks the operation regardless of what the user's personal permissions allow. An admin `ask` forces a prompt even if the user has an `allow` rule for that capability.

Admin policies can only use `deny` or `ask`, never `allow`. They can restrict access but cannot grant it. This holds for every grant path a session can carry, including [policy presets](https://kiro.dev/docs/permissions.md#policy-presets) requested by a client: a preset `allow` never overrides an admin `deny` or `ask`.

## Deploy a permission policy

Place a JSON policy file at the OS-protected path for your platform. These paths require administrator or root access to modify, which keeps the policy out of reach of a standard user account. The policy applies to every Kiro surface on the machine, because the IDE and the CLI read the same file.

    macOS
    Windows
    Linux

Create or edit the managed settings file:

```bash
sudo mkdir -p "/Library/Application Support/Kiro"
sudo nano "/Library/Application Support/Kiro/managed-settings.json"
```

Add your policy rules:

```json
{
  "rules": [
    { "capability": "web_fetch", "effect": "deny" },
    { "capability": "shell", "match": ["rm *", "sudo *"], "effect": "deny" }
  ]
}
```

You can also deploy this file via MDM (e.g., Jamf, Kandji) to manage it at scale.

Create or edit the managed settings file at:

```
C:\ProgramData\Kiro\managed-settings.json
```

Add your policy rules:

```json
{
  "rules": [
    { "capability": "web_fetch", "effect": "deny" },
    { "capability": "shell", "match": ["rm *", "sudo *"], "effect": "deny" }
  ]
}
```

Deploy via Group Policy, SCCM, or your MDM solution to manage at scale.

Create or edit the managed settings file:

```bash
sudo mkdir -p /etc/kiro
sudo nano /etc/kiro/managed-settings.json
```

Add your policy rules:

```json
{
  "rules": [
    { "capability": "web_fetch", "effect": "deny" },
    { "capability": "shell", "match": ["rm *", "sudo *"], "effect": "deny" }
  ]
}
```

Restart Kiro for the policy to take effect.

## Rule format

Each rule follows the same schema as user-authored permissions:

| Field | Description | Required |
|-------|-------------|----------|
| `capability` | The operation type to control (`shell`, `fs_read`, `fs_write`, `web_fetch`, `mcp`, etc.) | Yes |
| `match` | Glob patterns the resource must match | No (defaults to all resources) |
| `exclude` | Glob patterns that exempt a resource from the rule | No |
| `effect` | `deny` or `ask` (admin rules cannot use `allow`) | Yes |

For the full list of capabilities and pattern syntax, see [Permissions](https://kiro.dev/docs/permissions.md).

## Examples

### Block web access entirely

```json
{
  "rules": [
    { "capability": "web_fetch", "match": ["*"], "effect": "deny" },
    { "capability": "web_search", "effect": "deny" },
    { "capability": "shell", "match": ["curl *", "wget *"], "effect": "deny" }
  ]
}
```

Prevents the agent from fetching URLs, searching the web, or using shell commands that could exfiltrate data.

### Allowlist specific domains

```json
{
  "rules": [
    {
      "capability": "web_fetch",
      "exclude": ["docs.aws.amazon.com", "*.amazonaws.com", "*.github.com"],
      "effect": "deny"
    }
  ]
}
```

Denies web fetch to any domain *except* those in the exclude list. Domains matching the exclude patterns have no admin rule, so they fall through to the user's own permissions, which may allow or ask.

### Force prompts for MCP tools

```json
{
  "rules": [
    { "capability": "mcp", "effect": "ask" }
  ]
}
```

Even if a user has `` in their personal permissions, the admin `ask` wins, so every MCP tool call prompts for confirmation.

### Deny destructive shell commands

```json
{
  "rules": [
    {
      "capability": "shell",
      "match": ["rm *", "sudo *", "chmod *", "chown *", "mkfs *"],
      "effect": "deny"
    }
  ]
}
```

### Deny writes outside the workspace

```json
{
  "rules": [
    {
      "capability": "fs_write",
      "match": ["~/**"],
      "exclude": ["~/.kiro/**"],
      "effect": "deny"
    }
  ]
}
```

Blocks the agent from writing to the user's home directory (except Kiro's own config directory), even if the user has broader write permissions configured.

## Validation and error handling

Permission policies are validated when Kiro starts:

- **Malformed JSON:** The entire file is rejected and Kiro fails closed. All tool calls are denied until the file is fixed or removed.
- **Invalid effect:** Rules with `effect: "allow"` are rejected (admin policies only permit `deny` and `ask`). The entire file fails, with the same fail-closed result.
- **Unknown capabilities:** Rules with unrecognized capability names are skipped with a warning, but the remaining valid rules still load. This allows newer policies to work on older Kiro versions.
- **Unknown fields:** Rules with extra fields not in the schema cause the entire file to be rejected. This prevents typos (like `effct` instead of `effect`) from silently disabling admin rules.

**ℹ️ Info:** When a policy file fails validation, Kiro notifies the user that the policy could not be loaded. If your users report "all tools are denied" unexpectedly, check that the admin policy file is valid JSON with correct field names.

## Verifying the policy

After deploying the policy:

1. Restart Kiro on a test machine
2. Confirm no policy-validation warning appears on startup. Kiro notifies the user if the policy file failed to load
3. Attempt an action that should be denied (e.g., ask the agent to search the web if you denied `web_search`)
4. Verify the agent reports a denial with the rule source showing "administration"

When a tool call is denied by an admin policy, the user sees a message indicating the restriction is managed by their organization and that their own permission settings cannot override it.

## Combining with other governance controls

Permission policies work alongside Kiro's other enterprise governance features:

- **[Model governance](https://kiro.dev/docs/enterprise/governance/model.md)** controls which AI models are available
- **[MCP governance](https://kiro.dev/docs/enterprise/governance/mcp.md)** controls which MCP servers users can connect
- **[Web tools governance](https://kiro.dev/docs/enterprise/governance/web-tools.md)** disables web tools entirely from the console
- **[Managed updates](https://kiro.dev/docs/enterprise/managed-updates.md)** controls which IDE versions reach your fleet

Use permission policies when you need pattern matching, allowlisting, or capability-specific restrictions. To turn a whole feature on or off, use the console governance settings instead.
