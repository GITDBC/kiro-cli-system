> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Terminal UI vs classic

> A comparison of the terminal UI and classic interface in Kiro CLI, including what's new, what changed, and what's not available yet

A guide for users coming from the classic interface or choosing between the two.

## What's new in the terminal UI

These capabilities are only available in the terminal UI.

| Feature | What it does |
|---------|-------------|
| Overlay panels | `/help`, `/context`, `/tools`, and more open as searchable, scrollable panels instead of inline text |
| Themes | 3 built-in themes (dark, light, safe) with `/theme` customization and auto-detection |
| Activity tray | `Ctrl+X` shows task progress and queued messages at a glance |
| Crew monitor | `Ctrl+G` visualizes subagent activity and spawned sessions in real time during multi-agent workflows |
| Message queuing | Type and edit your next message while the agent is still working |
| `/copy` | Copy the last response to clipboard (works over SSH) |
| `/spawn` | Run parallel agent sessions with a task |
| `/feedback` | Submit feedback directly (replaces `/issue`) |
| `/guide` | Switch to the Kiro guide agent for help and onboarding |
| `/transcript` | Open conversation transcript in `$PAGER` (`Ctrl+T`) |
| Rich tool rendering | 12+ specialized components with status icons, collapsible output, and syntax-highlighted diffs |
| Reverse history search | `Ctrl+R` to search through previous inputs |
| Kill ring and undo | Full Emacs-style editing with `Ctrl+W`/`K`/`U`/`Y` and `Ctrl+_` for undo |

## What changed

These features work differently in the terminal UI.

| Area | Classic | Terminal UI |
|------|---------|-------------|
| Shell tool output | Streams in real time | Buffered — appears after the command completes |
| Interactive commands | `rm -i`, `sudo`, `ssh` prompts work | Not supported — use non-interactive alternatives |
| `/help` | Launches a help agent for interactive Q&A | Opens a searchable command panel |
| Approval flow | y/n/t text menu | Notification bar with drill-in feedback |
| Multi-line input | `Alt+Enter`, `Ctrl+J`, backslash continuation | `Shift+Enter`, `Alt+Enter`, `Ctrl+J` (no backslash) |
| Prompt indicators | Profile, context % | Agent chip, model chip, context %, git branch, cwd |
| Notifications | System notifications | System notifications + in-app notification bar |

## What's not available yet

A few classic features haven't been ported to the terminal UI.

| Feature | Workaround |
|---------|------------|
| `/changelog` | Check release notes on the Kiro website |
| `/logdump` | Use `kiro-cli` outside chat for log management |
| `/experiment` | Knowledge and Tasks are always on. Other experiments are being re-evaluated |
| `/settings` in chat | Use `kiro-cli settings` from your shell |
| Vi edit mode | Not yet available — the terminal UI uses Emacs keybindings |
| External diff tools | The built-in diff viewer is used for all diffs |
| `/tangent` | Not yet available in the terminal UI |
| Inline hints and tips | Not yet available |

## Switching back to classic

The classic interface is fully maintained and available anytime. Use `kiro-cli --classic` for a single session, or `kiro-cli settings chat.ui "classic"` to switch permanently. Sessions are compatible between both interfaces.
