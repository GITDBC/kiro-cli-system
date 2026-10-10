> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Custom Diff Tools

> Configure external diff tools to view code changes in Kiro CLI

When Kiro proposes file changes, it displays them using a built-in diff tool. If you prefer a different diff experience—whether that's syntax highlighting, side-by-side views, or your favorite GUI tool—you can configure Kiro to use an external diff tool instead.

## Configuration

Configure your preferred diff tool with the `chat.diffTool` setting:

```bash
kiro-cli settings chat.diffTool <tool-name>
```

For example, to use delta:

```bash
kiro-cli settings chat.diffTool delta
```

To reset to the built-in diff:

```bash
kiro-cli settings -d chat.diffTool
```

## Terminal tools

These tools display diffs directly in your terminal, keeping you in your workflow:

| Tool | Config value | Best for |
|------|--------------|----------|
| [delta](https://github.com/dandavison/delta) | `delta` | Git users who want syntax highlighting and line numbers |
| [difftastic](https://github.com/Wilfred/difftastic) | `difft` | Language-aware structural diffs that ignore formatting |
| [icdiff](https://github.com/jeffkaufman/icdiff) | `icdiff` | Quick side-by-side colored comparisons |
| [diff-so-fancy](https://github.com/so-fancy/diff-so-fancy) | `diff-so-fancy` | Clean, human-readable output |
| [colordiff](https://www.colordiff.org/) | `colordiff` | Simple colorized diffs |
| [diff-highlight](https://github.com/git/git/tree/master/contrib/diff-highlight) | `diff-highlight` | Word-level highlighting (ships with Git) |
| [ydiff](https://github.com/ymattw/ydiff) | `ydiff` | Side-by-side with word-level highlighting |
| [bat](https://github.com/sharkdp/bat) | `bat` | Syntax highlighting with Git integration |

## GUI tools

These open a separate window for reviewing changes:

| Tool | Config value |
|------|--------------|
| VS Code | `code` |
| VSCodium | `codium` |
| Meld | `meld` |
| KDiff3 | `kdiff3` |
| FileMerge (macOS) | `opendiff` |
| Vim | `vimdiff` or `vim` |
| Neovim | `nvim` |

**⚠️ Warning:** GUI diff tools open temporary files for viewing only. Any edits you make in the GUI tool will not be saved or applied to Kiro's proposed changes.

## Custom arguments

You can customize tool behavior by including arguments in quotes:

```bash
# Enable side-by-side view in delta
kiro-cli settings chat.diffTool "delta --side-by-side"
```

## Other tools

Kiro can work with diff tools not listed above. When you configure a tool, Kiro tries two approaches:

1. Pipes a unified diff to the tool via stdin
2. Invokes the tool with two temporary file paths as arguments

If neither approach works, Kiro falls back to the built-in inline diff.

## Troubleshooting

If you see the error "Couldn't find the diff tool", the tool isn't installed or isn't in your PATH. Verify the tool is accessible:

```bash
which delta
```

If nothing is returned, install the tool first. For example, to install delta:

```bash
# macOS
brew install git-delta

# Ubuntu/Debian
sudo apt install git-delta
```

For other tools, check the tool's documentation for installation instructions.
