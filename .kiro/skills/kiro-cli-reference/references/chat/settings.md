> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# In-session settings

> Configure response output, theme, keybindings, terminal input, display preferences, feature toggles, and prompt history from within a chat session

Run `/settings` to change how Kiro responds, looks, and behaves — output style, colors, keyboard shortcuts, multi-line input, display toggles, feature toggles, and prompt history scope — without leaving your chat session. Run `/settings` on its own to open the menu, or jump straight to a subcommand with `/settings <subcommand>`.

Available subcommands: `theme`, `keybindings`, `terminal`, `display`, `features`, and `history`.

## Menu controls

Every settings menu shares the same controls. `Up` and `Down` move between rows. `Left` reverses a toggle or cycle. `Right` and `Enter` toggle or cycle a value, select a radio option, or open a navigation row, and `Enter` also runs action rows. `Esc` closes the top-level menu or returns from a submenu. These controls apply to `/settings`, Display, Status line, Theme, and `/verbosity`. In `/verbosity`, `Ctrl+X` cycles the preview through hidden, mini, and expanded.

## Output styles in V3

In a V3 session, run `/settings display` and use the **Output style** row to choose how Kiro formats responses. The available styles come from the active agent when the Display menu opens, so an upgraded agent can supply new choices without a CLI update.

Your selection is saved as the global `chat.outputStyle` preference and applies to subsequent prompts. Choosing the agent's default removes the global override. A workspace-level `chat.outputStyle` value continues to take precedence; in that case, the row shows the active workspace style while you edit the global default.

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
- **Output style** (V3) — choose how Kiro formats responses; the active agent supplies the available styles
- **Animations** (`chat.allowAnimations`) — when off, spinners and shimmers show static frames instead of animating
- **ASCII art** (`chat.allowAsciiArt`) — when off, replaces braille dots, box-drawing, and Unicode symbols with plain ASCII
- **Icons** (`chat.allowIcons`) — when off, hides status indicator icons (●, ○, ⚠) in favor of text-only labels
- **Show thinking** (`chat.showThinking`) — when off, hides the agent's reasoning blocks from chat output
- **Status line** — choose whether the status line shows the date, time, current usage percentage, and remaining credits. These optional segments are hidden by default. Changes take effect immediately and persist across sessions
- **Terminal title** — when on, sets the terminal window title from a custom name you provide with [`/title`](https://kiro.dev/docs/reference/slash-commands.md#title). Enable from `/settings display`
- **Preserve scrollback**: when on, keeps terminal history available during overflow and resize redraws
- **Screen reader** (`chat.screenReader`): full terminal UI only. Choose `auto` (default), `on`, or `off`. See [Screen reader support](#screen-reader-support)

Animations, ASCII art, icons, and status-line changes take effect immediately. The **Show thinking** toggle is startup-only — it persists right away, but the change applies to your next chat session. See [Thinking display](#thinking-display) below.

**ℹ️ Info:** Setting the environment variable `KIRO_ASCII_MODE=1` forces ASCII mode regardless of the ASCII art toggle.

#### Screen reader support

In the full terminal UI, screen reader support lets a screen reader follow Kiro's replies. While a reply streams and your prompt is empty, the hidden terminal cursor follows the reply text. When you start typing, open a menu, or respond to an approval, the cursor returns to that input.

- **auto** (default): Kiro checks once whether VoiceOver is running on your local Mac, usually at startup or when you open `/settings display`. Over SSH or another remote connection, on other platforms, or when the check fails or takes too long, support stays off. Choose **on** in those cases.
- **on**: always active.
- **off**: never active.

When support is active, IME input may appear in a different position. The setting is global only. To override it for a single launch, set `KIRO_SCREEN_READER` to `auto`, `on`, or `off`:

```bash
KIRO_SCREEN_READER=on kiro-cli chat
```

### `/settings features`

Enable account-available agent features for future Kiro CLI processes.

```bash
/settings features
```

Enable **Workflows** to expose declarative workflow commands and controls. The choice is stored as `chat.enableWorkflows`. Exit and restart Kiro CLI after changing it; the current process does not add or remove workflow commands dynamically.

When Workflows are enabled in V3, **Workflows: sub-agent tool** appears directly below the Workflows toggle. It is on by default, so the main chat can delegate directly to sub-agents or through Workflows. Turn it off to make Workflows the main chat's only delegation route; workflow steps can still use sub-agents when their agent configuration permits them. The choice is stored as `chat.enableMainAgentSubagentTool` and applies to new sessions.

If **Workflows** does not appear, it is not available for your account. See [Workflows](https://kiro.dev/docs/workflows.md) for recipes, commands, and run behavior.

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

Preferences changed through `/settings` persist across sessions. Most are saved to `~/.kiro/settings/cli.json`, while theme preferences are saved to `~/.kiro/settings/kiro_cli_theme.json`. You can edit the main settings file directly with `kiro-cli settings open`.

### Model and effort preferences

Your `/model` selection applies to the current session only. To save the current model as the default for future sessions, run `/model set-current-as-default`; Kiro stores the default in `~/.kiro/settings/cli.json`.

Effort works differently. Choosing a level in the `/model` picker persists it for that model. Using `/effort <level>` directly changes the current session only — run `/effort set-current-as-default` afterward to save it, or choose the level in `/model` instead. In V3, the `--effort` flag applies only to the session Kiro starts with.

Per-model effort defaults live under `chat.modelDefaults`. See [Effort](https://kiro.dev/docs/models/effort.md) for the full reference.

## Related

- [Settings reference](https://kiro.dev/docs/reference/settings.md) — full list of all CLI settings
- [Terminal UI](https://kiro.dev/docs/cli/terminal-ui.md) — terminal UI features and configuration
- [Configuration](https://kiro.dev/docs/configuration.md) — configuration file paths and scopes
- [Workflows](https://kiro.dev/docs/workflows.md) — enable and run declarative workflows
