> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Kiroignore

> Control which files Kiro can access using gitignore-style patterns

The `.kiroignore` file prevents Kiro from reading specific files in your workspace. Using familiar gitignore syntax, you define patterns for files that should remain private - credentials, secrets, or content you prefer to keep out of agent context.

Where supported, ignore patterns apply across the agent's tools - blocked files stay blocked regardless of which tool tries to read them. Before returning file or text search results, Kiro checks each result against your read permissions and ignore rules. Paths and matching content from ignored or unreadable files do not appear in search results. Check the table below for surface availability.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Workspace `.kiroignore` | ✓ | V3 | — | — |
| Global ignore file (`~/.kiro/settings/kiroignore`) | ✓ | — | — | — |

The IDE enforces `.kiroignore` across supported agent tools. In CLI V3, a workspace `.kiroignore` blocks matching files from direct reads and filters them from content and filename search results. Web support is not available yet.

## Why use .kiroignore?

- **Security** - Prevent Kiro from accessing files containing credentials, API keys, or other sensitive data
- **Privacy** - Exclude confidential information from AI interactions
- **Compliance** - Ensure Kiro doesn't access files that shouldn't be shared with external services
- **Focus** - Keep Kiro's context relevant by excluding large files or build artifacts

## Setting up workspace ignore

To exclude files in a specific project, create a `.kiroignore` file in your project root (or any subdirectory) and add patterns for files you want to exclude:

```bash
# Secrets and credentials
.env
.env.*
!.env.example
*.pem
*.key

# Private directories
secrets/
private/
```

Kiro skips any files matching your patterns.

    IDE
    CLI

    The IDE reads ignore filenames from the **Agent Ignore Files** setting. Open Settings (`Cmd+,` on Mac or `Ctrl+,` on Windows/Linux), search for **Agent Ignore Files** (setting: `kiroAgent.agentIgnoreFiles`), and add `.kiroignore` to the array.

    The `kiroAgent.agentIgnoreFiles` setting accepts an array of filenames:

    - Use multiple ignore file types simultaneously: `[".gitignore", ".kiroignore"]`
    - Set to `[]` to disable workspace-level ignore files

    In V3, a workspace `.kiroignore` blocks matching files from direct reads and omits them from content and filename search results. Global ignore files are not supported in the CLI.

**💡 Tip:** Start with credentials and secrets - these are the highest priority files to protect. You can always expand your patterns as your project evolves.

### Subdirectory ignore files

Like `.gitignore`, you can place `.kiroignore` files in subdirectories to override or extend patterns from parent directories. Patterns in subdirectory ignore files take precedence for files within that subdirectory.

## Global ignore files

Kiro automatically honors global ignore files if they exist - no configuration needed:

- `~/.kiro/settings/kiroignore` - Your global Kiro ignore patterns
- Git's global ignore file (configured via `core.excludesfile` in your git config) - only applied in git repositories

Use global ignore files for patterns you want applied across all your projects.

## Pattern syntax

`.kiroignore` uses standard gitignore syntax:

| Pattern | Effect |
|---------|--------|
| `file.txt` | Ignore specific file |
| `*.log` | Ignore by extension |
| `folder/` | Ignore directory |
| `**/temp` | Ignore in any subdirectory |
| `!keep.txt` | Don't ignore (negation) |

**ℹ️ Info:** You cannot re-include a file if a parent directory is excluded. For example, if you ignore `secrets/`, adding `!secrets/public.txt` won't work. To include specific files from a directory, use more specific patterns instead of excluding the entire directory.

## Examples

### Protecting API keys and secrets

```bash
# Environment files with credentials
.env
.env.local
.env.production

# Keep the template accessible
!.env.example

# Certificate and key files
*.pem
*.key
*.p12
credentials/
```

### Excluding build artifacts and data files

```bash
# Build outputs
dist/
build/
.next/

# Data files
*.sql
*.dump
data/exports/
```

### Team compliance setup

```bash
# Customer data directories
customer-data/
pii/

# Audit and compliance docs
compliance/internal/
audit-reports/
```

**ℹ️ Info:** Use `.kiroignore` when you need different rules for agent access vs. version control, or to block files that are tracked in git but shouldn't be read by Kiro.

## Best practices

- Use comments to document why files are ignored - helpful for team members
- Test patterns by asking Kiro to read an ignored file - it will indicate access is blocked
- Review patterns periodically as your project structure evolves
- Coordinate with your team on global patterns for consistent behavior across workspaces
