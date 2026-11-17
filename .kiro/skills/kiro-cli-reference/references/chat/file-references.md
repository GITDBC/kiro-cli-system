> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# File references

> Include file contents or directory listings inline using @path syntax

File references let you include file contents or directory trees directly in your chat messages using `@path` syntax. This provides quick context without manually copying content, and since the content is expanded inline before sending, it avoids tool calls—saving tokens.

## Basic usage

Type `@` followed by a file or directory path:

```
@src/index.ts             # Include file contents
@src/                     # Include directory tree
@./relative/path          # Relative paths
@"path with spaces.txt"   # Quoted paths (required for spaces)
```

References can appear anywhere in your message:

```
Review @src/auth.ts for security issues
Compare @old.json with @new.json
What's in @src/ that handles authentication?
```

## Tab completion

Press Tab after `@` to auto-complete paths:

```
@src/<Tab>                # Shows files in src/
@package<Tab>             # Completes to @package.json
@"Screenshot 2024<Tab>     # Completes to @"Screenshot 2024-01.png"
```

Completion works anywhere in the input line. Tab completion automatically adds quotes when needed for paths with spaces.

## How references are resolved

When a reference could match both a prompt and a file:

1. **Prompts first**: If `@name` matches a prompt from `/prompts list`, it's treated as a prompt
2. **Files second**: Otherwise checked as a file path
3. **Directories third**: If not a file, checked as a directory

To force file resolution when a prompt has the same name, use an explicit path: `@./myfile`

## File handling

**Supported**: Text files (source code, config, markdown) up to 250KB.

**Not supported**: Binary files (images, executables, archives) show an error.

Large files are truncated at 250KB:

```
⚠ File 'large-file.json' was truncated (exceeds 250KB limit)
```

## Directory trees

Directory references expand to a tree listing:

```
@src/
```

Expands to:

```
src/
├── lib/
│   ├── auth.ts
│   └── utils.ts
├── index.ts
└── config.json
```

**Limits**:
- Max depth: 3 levels
- Max items per level: 10 (shows "... (N more items)" if exceeded)
- Ignores common directories: node_modules, .git, target, dist, build

## Examples

**Review a file**:
```
> Review @src/auth.ts for security issues
```

**Compare files**:
```
> What's different between @v1/handler.py and @v2/handler.py?
```

**Explore structure**:
```
> What's the structure of @infra/cdk/?
```

**Mixed context**:
```
> Using the config in @serverless.yml, update @src/lambda/index.ts
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Reference treated as prompt | A prompt with the same name exists. Use an explicit path: `@./myfile` |
| File not found | Verify the path is relative to your current directory, or use an absolute path |
| Directory too deep | Subdirectories beyond 3 levels aren't shown. Reference a specific subdirectory: `@src/deep/path/` |
| Path with spaces not recognized | Use quoted syntax: `@"path with spaces.txt"` |

## Current limitations

File references currently support:

- Text files up to 250KB (larger files are truncated)
- Directory trees up to 3 levels deep, 10 items per level
- Explicit file paths only (no glob patterns like `@*.ts`)
- Full file contents (no line ranges like `@file.ts:10-20`)
- Relative and absolute paths (no tilde expansion like `@~/file`)

In [cloud sessions](https://kiro.dev/docs/cloud-sessions.md), the `@` picker and Tab completion currently search your local filesystem, not the sandbox the session runs in.

Binary files (images, executables, archives) are not supported.

## Related

- [Manage Prompts](https://kiro.dev/docs/cli/chat/manage-prompts.md) - Prompt templates also use @ syntax
- [Context Management](https://kiro.dev/docs/cli/chat/context.md) - Persistent context files
