> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# In-session settings

> Configure theme, keybindings, terminal input, display preferences, and prompt history from within a chat session

Run `/settings` to change how Kiro looks and behaves — colors, keyboard shortcuts, multi-line input, display toggles, and prompt history scope — without leaving your chat session. Run `/settings` on its own to open the menu, or jump straight to a subcommand with `/settings <subcommand>`.

Available subcommands: `theme`, `keybindings`, `terminal`, `display`, and `history`.

## Menu controls

Every settings menu shares the same controls. `Up` and `Down` move between rows. `Left` reverses a toggle or cycle. `Right` and `Enter` toggle or cycle a value, select a radio option, or open a navigation row, and `Enter` also runs action rows. `Esc` closes the top-level menu or returns from a submenu. These controls apply to `/settings`, Display, Status line, Theme, and `/verbosity`. In `/verbosity`, `Ctrl+X` cycles the preview through hidden, mini, and expanded.

## Subcommands

### `/settings theme`

Customize the colors used for prompt input and agent response text. The theme wizard walks you through customization step by step — pick a base theme, adjust specific elements, then confirm. The live preview renders actual conversation output so you see exactly how your theme looks in practice.

```bash
/settings theme
```

The theme system uses named ANSI colors, so your customizations render correctly across terminals with different color palettes. Falls back to safe ANSI colors when terminal color detection has low confidence.

### `/settings keybindings`

View the current keyboard shortcut configuration. This is a read-only reference showing all configurable bindings and their current values.

```bash
/settings keybindings
```

To change keybindings, use the `kiro-cli settings` command:

```bash
kiro-cli settings chat.keybindings.cancelStream "ctrl+x"
kiro-cli settings chat.keybindings.closeMenu "ctrl+["
kiro-cli settings chat.keybindings.quit "ctrl+shift+q"
```

See [Key bindings (terminal UI)](https://kiro.dev/docs/reference/settings.md#key-bindings-terminal-ui) for the full reference.

### `/settings terminal`

Enable `Shift+Enter` and `Option+Enter` as newline shortcuts in your terminal. If pressing Shift+Enter currently submits your prompt instead of inserting a newline, this command fixes it by auto-detecting your terminal and applying the appropriate key binding configuration.

```bash
/settings terminal
```

**Terminals that need configuration** (auto-applied by `/settings terminal`):
- VS Code integrated terminal
- Alacritty
- Zed
- Apple Terminal

**Terminals with native support** (no configuration needed):
- iTerm2
- Kitty
- Ghostty
- WezTerm
- Warp

For terminals that don't support automatic configuration, Kiro shows manual workaround instructions.

**ℹ️ Info:** A `.bak` backup is created before any terminal configuration file is modified. If something goes wrong, you can restore from the backup.

**tmux users:** Add both lines to your `tmux.conf` for `Shift+Enter` to pass through correctly:

```bash
set -s extended-keys on
set -as terminal-features 'xterm*:extkeys'
```

### `/settings display`

Toggle visual features for accessibility or personal preference, using the [menu controls](#menu-controls) above.

```bash
/settings display
```

Available toggles:
- **Animations** (`chat.allowAnimations`) — when off, spinners and shimmers show static frames instead of animating
- **ASCII art** (`chat.allowAsciiArt`) — when off, replaces braille dots, box-drawing, and Unicode symbols with plain ASCII
- **Icons** (`chat.allowIcons`) — when off, hides status indicator icons (●, ○, ⚠) in favor of text-only labels
- **Show thinking** (`chat.showThinking`) — when off, hides the agent's reasoning blocks from chat output
- **Status line** — choose whether the status line shows the date, time, current usage percentage, and remaining credits. These optional segments are hidden by default. Changes take effect immediately and persist across sessions
- **Terminal title** — when on, sets the terminal window title from a custom name you provide with [`/title`](https://kiro.dev/docs/reference/slash-commands.md#title). Enable from `/settings display`
- **Preserve scrollback**: when on, keeps terminal history available during overflow and resize redraws

Animations, ASCII art, icons, and status-line changes take effect immediately. The **Show thinking** toggle is startup-only — it persists right away, but the change applies to your next chat session. See [Thinking display](#thinking-display) below.

**ℹ️ Info:** Setting the environment variable `KIRO_ASCII_MODE=1` forces ASCII mode regardless of the ASCII art toggle.

### `/settings history`

Choose whether prompt history (the Up/Down arrow recall in the input) is tracked per session or shared across all sessions.

```bash
/settings history
```

Options:
- **session** (default) — each chat session keeps its own prompt history, so Up/Down only recalls prompts from the current session
- **global** — all sessions share a single prompt history

The change is written to `chat.historyMode` and takes effect on your next session.

## Thinking display

When the agent reasons through a complex request, it can stream those reasoning ("thinking") blocks inline above its response. This is controlled by the `chat.showThinking` setting, which is **enabled by default** in Kiro CLI 2.5.0 and later.

Toggle it from the display menu:

```bash
/settings display
# Select "Show thinking" and press Enter to toggle
```

Or set it directly from the command line:

```bash
# Hide reasoning blocks
kiro-cli settings chat.showThinking false

# Show reasoning blocks again
kiro-cli settings chat.showThinking true
```

A few things to know:
- The setting is **startup-only**. Changes apply to your next chat session, not the current one.
- The live "Thinking..." spinner always appears while the agent is processing, regardless of this setting.
- Long reasoning traces collapse to a tail view. Press `Ctrl+O` to expand or collapse the full thinking block.
- Reasoning blocks typically appear for complex, multi-step requests. Simple prompts may not produce any.

## Persistence

All changes made through `/settings` are saved to `~/.kiro/settings/cli.json` and apply to future sessions. You can also edit this file directly with `kiro-cli settings open`.

### Model and effort preferences

Your `/model` and `/effort` selections persist automatically. Switch models or change the reasoning effort level once, and Kiro carries that preference into future sessions — you no longer need to run `/model set-current-as-default` to make a selection stick.

These preferences are written to `~/.kiro/settings/cli.json`, the same file used for other CLI settings. Per-model effort defaults live under `chat.modelDefaults`. See [Effort](https://kiro.dev/docs/models/effort.md) for the full reference.

## Related

- [Settings reference](https://kiro.dev/docs/reference/settings.md) — full list of all CLI settings
- [Terminal UI](https://kiro.dev/docs/cli/terminal-ui.md) — terminal UI features and configuration
- [Configuration](https://kiro.dev/docs/configuration.md) — configuration file paths and scopes
