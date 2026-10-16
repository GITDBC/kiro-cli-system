> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Code intelligence

> Tree-sitter and LSP-powered code understanding - symbol search, pattern matching, and codebase exploration

Code intelligence provides two complementary layers of code understanding:

- **Tree-sitter (built-in)** - Out-of-the-box code intelligence for 18 languages. Search symbols, get document outlines, and look up definitions without installing anything extra.
- **LSP integration (optional)** - Enhanced precision with find references, go-to-definition, hover docs, rename refactoring, and diagnostics. Requires language server installation.

All tree-sitter features below are cross-surface (IDE, CLI, Web, Mobile). LSP features require a language server and are available on IDE and CLI only.

| Capability | Requires LSP |
|-----------|:------------:|
| Symbol search (fuzzy) | — |
| Document symbols | — |
| Pattern search (AST) | — |
| Pattern rewrite (AST) | — |
| Codebase overview | — |
| Find references | ✓ |
| Go to definition | ✓ |
| Rename symbol | ✓ |
| Get diagnostics | ✓ |
| Hover documentation | ✓ |

**ℹ️ Info:** LSP features (find references, go-to-definition, rename, diagnostics, hover) are available on IDE and CLI only. They require a language server installed for your language.

## Supported languages

Bash, C, C++, C#, Elixir, Go, Java, JavaScript, Kotlin, Lua, PHP, Python, Ruby, Rust, Scala, Swift, TSX, TypeScript

## Symbol search

Find functions, classes, and methods by name with fuzzy matching:

```text
> Find the UserRepository class

Searching for symbols matching: "UserRepository" (using tool: code)
✓ Found 1 match

Class UserRepository at src/repositories/user.repository.ts:15:1
```

## Pattern search

AST-based structural code search. Find code by structure, not just text.

### Metavariables

| Pattern | Matches |
|---------|---------|
| `$VAR` | Single node (identifier, expression) |
| `$$$` | Zero or more nodes (statements, parameters) |

### Examples

```javascript
// Find all console.log calls
pattern: console.log($ARG)
language: javascript

// Find all async functions
pattern: async function $NAME($$$PARAMS) { $$$ }
language: typescript

// Find all .unwrap() calls
pattern: $E.unwrap()
language: rust
```

## Pattern rewrite

Automated code transformations using AST patterns:

```javascript
// Convert var to const
pattern: var $N = $V
replacement: const $N = $V
language: javascript

// Modernize hasOwnProperty
pattern: $O.hasOwnProperty($P)
replacement: Object.hasOwn($O, $P)
language: javascript

// Convert unwrap to expect
pattern: $E.unwrap()
replacement: $E.expect("unexpected None")
language: rust
```

## Codebase overview

Get a high-level overview of a workspace or directory:

IDE
CLI

The agent uses code intelligence automatically when exploring your project. Ask "give me an overview of this codebase" or "what does this project do?"

```bash
/code overview           # full workspace
/code overview ./src     # specific directory
/code overview --silent  # minimal output
```

## Documentation generation

Generate project documentation based on codebase analysis:

IDE
CLI

Ask the agent: "Generate a README for this project" or "Create an AGENTS.md file."

```bash
/code summary
```

Choose output format: AGENTS.md, README.md, or CONTRIBUTING.md.

## LSP integration

With a language server installed, code intelligence gains additional precision:

- **Find references** - locate all usages of a symbol
- **Go to definition** - navigate to where a symbol is defined
- **Rename symbol** - rename across the codebase
- **Get diagnostics** - errors and warnings for a file
- **Hover documentation** - type information at a position

**ℹ️ Info:** LSP features require language server installation. See language-specific guides: [TypeScript/JavaScript](https://kiro.dev/docs/guides/languages-and-frameworks/typescript-javascript-guide.md), [Python](https://kiro.dev/docs/guides/languages-and-frameworks/python-guide.md), [Java](https://kiro.dev/docs/guides/languages-and-frameworks/java-guide.md).

In the IDE, LSP-backed capabilities come from the language extensions you already have installed. On the CLI, enable them per workspace with `/code init` - see the setup reference below.

## Setting up LSP on the CLI

**ℹ️ LSP is optional and workspace-scoped:** The built-in tree-sitter features work out of the box with no initialization needed. You only need `/code init` for the enhanced LSP features. Code intelligence is configured per workspace, not globally - each project maintains its own LSP settings independently.

  [Video](https://kiro.dev/videos/code-intelligence.mp4)

### How it works

Kiro CLI spawns LSP server processes in the background that communicate via JSON-RPC over stdio. When you initialize a workspace, it detects languages from project markers (like `package.json`, `Cargo.toml`) and file extensions, then starts the appropriate language servers. These servers continuously analyze your code and maintain an index of symbols, types, and references. When you make queries, Kiro translates your natural language into LSP protocol requests, sends them to the relevant server, and formats the responses back into readable output.

### Initialize LSP

Run this slash command in your project root:

```
/code init
```

This creates `.kiro/settings/lsp.json` and starts language servers:

```
✓ Workspace initialization started

Workspace: /path/to/your/project
Detected Languages: ["python", "rust", "typescript"]
Project Markers: ["Cargo.toml", "package.json"]

Available LSPs:
○ clangd (cpp) - available
○ gopls (go) - not installed
◐ jdtls (java) - initializing...
✓ pyright (python) - initialized (687ms)
✓ rust-analyzer (rust) - initialized (488ms)
○ solargraph (ruby) - not installed
✓ typescript-language-server (typescript) - initialized (214ms)
```

**Status indicators:** ✓ initialized and ready · ◐ currently initializing · ○ available (installed but not needed) · ○ not installed

- **Restart LSP servers:** if language servers shut down or become unresponsive, use `/code init -f`.
- **Auto-initialization:** after the first `/code init`, Kiro CLI automatically initializes code intelligence on startup when `.kiro/settings/lsp.json` exists in the workspace.
- **Disabling:** delete `.kiro/settings/lsp.json` to disable. Re-enable anytime with `/code init`.

### Supported LSP servers

| Language | Extensions | Server | Install command |
| -- | -- | -- | -- |
| TypeScript/JavaScript | `.ts`, `.js`, `.tsx`, `.jsx` | `typescript-language-server` | `npm install -g typescript-language-server typescript` |
| Rust | `.rs` | `rust-analyzer` | `rustup component add rust-analyzer` |
| Python | `.py` | `pyright` | `pip install pyright` |
| Go | `.go` | `gopls` | `go install golang.org/x/tools/gopls@latest` |
| Java | `.java` | `jdtls` | `brew install jdtls` (macOS) |
| Ruby | `.rb` | `solargraph` | `gem install solargraph` |
| C/C++ | `.c`, `.cpp`, `.h`, `.hpp` | `clangd` | `brew install llvm` (macOS) or `apt install clangd` (Linux) |
| Kotlin | `.kt`, `.kts` | `kotlin-language-server` | `brew install kotlin-language-server` |

### Using language servers

Query semantic code intelligence with natural language - search symbols, navigate definitions, find references, rename across files, get diagnostics, view documentation, and discover available APIs:

```
> Find references of Person class

Finding all references at: auth.ts:42:10
  1. src/auth.ts:42:10 - export function authenticate(...)
  2. src/handlers/login.ts:15:5 - authenticate(credentials)
  3. src/handlers/api.ts:89:12 - await authenticate(token)
```


```
> Dry run: rename the method "FetchUser" to "fetchUserData"

Dry run: Would rename 12 occurrences in 5 files
```


```
> What methods are available on the s3Client instance?

Available completions:
  1. putObject - Function: (params: PutObjectRequest) => Promise<PutObjectOutput>
  2. getObject - Function: (params: GetObjectRequest) => Promise<GetObjectOutput>
  3. deleteObject - Function: (params: DeleteObjectRequest) => Promise<DeleteObjectOutput>
```

### Custom language servers

Add custom language servers by editing `.kiro/settings/lsp.json`:

```json
{
  "languages": {
    "mylang": {
      "name": "my-language-server",
      "command": "my-lsp-binary",
      "args": ["--stdio"],
      "file_extensions": ["mylang", "ml"],
      "file_patterns": ["Mylangfile", "mylang.config.*"],
      "project_patterns": ["mylang.config"],
      "exclude_patterns": ["**/build/**"],
      "multi_workspace": false,
      "initialization_options": { "custom": "options" },
      "request_timeout_secs": 60
    }
  }
}
```

**Fields:**

- **name**: Display name for the language server
- **command**: Binary/command to execute
- **args**: Command line arguments (usually `["--stdio"]`)
- **file_extensions**: File extensions this server handles
- **file_patterns**: Optional list of glob patterns matched against the full filename. Use this for language servers that target specific filenames without a standard extension, like `Dockerfile`, `Dockerfile.*`, or `docker-compose*.yml`. Exact matches win over globs, and more specific globs win over broader ones regardless of declaration order.
- **project_patterns**: Files that indicate a project root (e.g., `package.json`)
- **exclude_patterns**: Glob patterns to exclude from analysis
- **multi_workspace**: Set to true if the LSP supports multiple workspace folders (default: false)
- **initialization_options**: LSP-specific configuration passed during initialization
- **request_timeout_secs**: Timeout in seconds for LSP requests. Default is 60.

After editing, restart Kiro CLI to load the new configuration.

### CLI commands

| Command | Purpose |
|---------|---------|
| `/code init` | Initialize code intelligence in the current directory |
| `/code init -f` | Force re-initialization (restart all LSP servers) |
| `/code status` | Show workspace status and LSP server states |
| `/code overview [path] [--silent]` | Codebase structure overview |
| `/code summary` | Interactive documentation generation |
| `/code logs` | Display LSP logs for troubleshooting |

`/code logs` options: `-l, --level <LEVEL>` filter (ERROR, WARN, INFO, DEBUG, TRACE; default ERROR) · `-n, --lines <N>` number of lines (default 20) · `-p, --path <PATH>` export logs to a JSON file.

### Troubleshooting

| Issue | Cause(s) | Solution |
| -- | -- | -- |
| Code tool is not enabled for this agent | Agent doesn't have the code tool in its tool list | Add `"code"` to the agent's tools array, or use `@builtin` to include all built-in tools, or use `@builtin/code` |
| Workspace is still initializing | LSP servers are starting up | Wait and try again. If servers crashed, use `/code init -f` to restart |
| LSP initialization failed | | Check logs for details: `/code logs -l ERROR` |
| No symbols found | Language server is still indexing, file has syntax errors, or symbol name doesn't match | Check the file for errors, try broader search terms |
| No definition found | Position doesn't point to a symbol | Verify the row and column numbers point to a symbol name |

Not every language server supports every operation (some may not support rename or formatting), and large codebases can be slow to index initially.

## Permissions

Symbol lookups and code analysis within your workspace run without prompting. Operations targeting files outside the workspace require approval.

A rename or format asks before each file it changes, one prompt per file, including files the language server adds to the edit beyond the one you named. A `deny` rule on any file in the edit refuses the whole edit, and nothing is written. Kiro computes the edit against each file as you last saved it; if a file changes before the edit is applied, Kiro refuses the edit instead of applying it at stale positions.

## Next steps

- [Built-in tools overview](https://kiro.dev/docs/tools.md) - full tool catalog
- [Language support guides](https://kiro.dev/docs/guides/languages-and-frameworks.md) - per-language setup
