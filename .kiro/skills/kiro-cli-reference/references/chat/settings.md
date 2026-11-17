> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# In-session settings

> Configure response output, theme, keybindings, terminal input, display preferences, feature toggles, and prompt history from within a chat session

Run `/settings` to change how Kiro responds, looks, and behaves — output style, colors, keyboard shortcuts, multi-line input, display toggles, tool-call detail, feature toggles, and prompt history scope — without leaving your chat session. Run `/settings` on its own to open the menu, or jump straight to a subcommand with `/settings <subcommand>`.

Available subcommands: `theme`, `keybindings`, `terminal`, `display`, `output-details` (Kiro CLI 3.2.1 or later), `features`, and `history`.

## Menu controls

Every settings menu shares the same controls. `Up` and `Down` move between rows. `Left` reverses a toggle or cycle. `Right` and `Enter` toggle or cycle a value, select a radio option, or open a navigation row, and `Enter` also runs action rows. `Esc` closes the top-level menu or returns from a submenu. These controls apply to `/settings`, Display, Output details, Status line, Theme, and `/verbosity`. In Output details and `/verbosity`, `Ctrl+X` cycles the preview through hidden, mini, and expanded.

## Output styles in V3

In a V3 session, run `/settings display` and use the **Output style** row to choose how Kiro formats responses. Built-in choices include **Proactive**, **Explanatory**, and **Learning**. The active agent can supply other choices when the Display menu opens.

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
- **Show thinking** (`chat.showThinking`) — before Kiro CLI 3.2.1, when off, hides the agent's reasoning blocks from chat output. In Kiro CLI 3.2.1 or later, this row has moved to [Output details](#settings-output-details)
- **Status line** — choose whether the status line shows the date, time, current usage percentage, remaining credits, and, in Kiro CLI 3.1.0 or later, **Session credits**, the credits the current session has used so far. These optional segments are hidden by default. Changes take effect immediately and persist across sessions
- **Terminal title** (`chat.terminalTitle`) — when on, sets the terminal window title from a name you give with [`/title`](https://kiro.dev/docs/reference/slash-commands.md#title); otherwise from the session's title, or the workspace folder name when the session has none. In Kiro CLI 2.33 or later, a V3 session shows its session title; before 2.33, a V3 session fell back to the workspace folder name. Off by default and global only. To confirm it is on, run `/title`: when the feature is off, `/title` reports that it is disabled and how to enable it
- **Preserve scrollback**: when on, keeps terminal history available during overflow and resize redraws
- **Screen reader** (`chat.screenReader`): full terminal UI only. Choose `auto` (default), `on`, or `off`. See [Screen reader support](#screen-reader-support)

Animations, ASCII art, icons, and status-line changes take effect immediately. Before Kiro CLI 3.2.1, the **Show thinking** toggle is startup-only — it persists right away, but the change applies to your next chat session. See [Thinking display](#thinking-display) below.

**ℹ️ Info:** Setting the environment variable `KIRO_ASCII_MODE=1` forces ASCII mode regardless of the ASCII art toggle.

### `/settings output-details`

In Kiro CLI 3.2.1 or later, choose how much detail tool calls show in the transcript. Select **Output details** in `/settings`, or run the subcommand directly. `/settings verbosity` still opens the same menu, and bare `/verbosity` opens its density picker when a preset is active.

```bash
/settings output-details
```

The menu has these rows:

- **Density preset** — choose `collapsed` (one line per tool call: title, time, and status), `lean` (inline arguments, no reasoning), `default`, or `full` (everything the agent sees, with all output filters on and no truncation), or **custom** to set the rows below one by one
- **Tool calls** — tool arguments off, in the title, inline, or as a block, with the agent's reasoning and elapsed time on or off
- **Subagent** — subagent steps, step instructions, step role labels, and full output.
- **Thinking** — `expanded`, `collapsed`, or `off` for the agent's reasoning blocks. The choice is also saved to `chat.showThinking`
- **Task list** — show or hide the task list
- **Show output** — which tool categories keep their output in the transcript
- **Truncation** — line and character caps for arguments and output

Add a section name to open it directly, for example `/settings output-details truncation`. `Esc` returns to `/settings`.

These settings shape finished tool calls. A tool call that is waiting for your approval always shows its full arguments, and a file-write approval always shows its complete diff, whatever preset or caps you choose.

Changes made in Output details apply to the current session. A value set from the command line with `kiro-cli settings chat.showThinking <mode>` applies at your next session start, unless an Output details record saved by an earlier release still holds its own thinking value; changing the thinking display in Output details once replaces it.

#### Screen reader support

In the full terminal UI, screen reader support lets a screen reader follow Kiro's replies. While a reply streams and your prompt is empty, the hidden terminal cursor follows the reply text. When you start typing, open a menu, or respond to an approval, the cursor returns to that input.

- **auto** (default): Kiro checks once whether VoiceOver is running on your local Mac, usually at startup or when you open `/settings display`. Over SSH or another remote connection, on other platforms, or when the check fails or takes too long, support stays off. Choose **on** in those cases.
- **on**: always active.
- **off**: never active.

When support is active, IME input may appear in a different position. The setting is global only. To override it for a single launch, set `KIRO_SCREEN_READER` to `auto`, `on`, or `off`:

```bash
KIRO_SCREEN_READER=on kiro-cli chat
```

### Compaction

In Kiro CLI 3.3.0 or later, a V3 session shows a **Compaction** entry in the `/settings` menu. It has no subcommand; run `/settings` and open **Compaction**. The screen has three rows:

- **Automatic compaction** — turn automatic compaction on or off for sessions you start or load from now on. The choice is stored as `chat.disableAutoCompaction`; when a workspace `.kiro/settings/cli.json` sets that key, the row says so and the workspace value stays in effect there
- **Current session** — the threshold the running session uses, as the agent harness confirmed it
- **Global default** — open the threshold editor. Type a context usage percentage with at most two decimal places, use the arrow keys to adjust it, or press `d` to follow the agent harness default. The editor shows the accepted range and the default. The value is stored as `compaction.autoCompactionThreshold` and applies to the next session you start or load; a workspace `cli.json` value overrides it for that workspace

The entry does not appear when the agent harness does not support a configurable threshold. See [Compaction](https://kiro.dev/docs/compaction.md#configuration) for the settings reference.

### `/settings features`

Enable account-available agent features for future Kiro CLI processes.

```bash
/settings features
```

Enable **Workflows** to expose declarative workflow commands and controls. The choice is stored as `chat.enableWorkflows`. Exit and restart Kiro CLI after changing it; the current process does not add or remove workflow commands dynamically.

When Workflows are enabled, **Workflow use** appears below the Workflows toggle. Choose how often Kiro starts a workflow from the main chat:

- **Only when asked** (default) — Kiro starts a workflow only when you request one.
- **Only for large tasks** — Kiro can start one for multi-step work or work needing more context.
- **As much as possible** — Kiro tries to route most code reading, implementation, testing, and review work through Workflows.

The choice is stored as `chat.workflowLaunch`. It applies to the current session when available and to new sessions afterward.

If **Workflows** does not appear, it is not available for your account. See [Workflows](https://kiro.dev/docs/workflows.md) for recipes, commands, and run behavior.

In Kiro CLI 3.1.0 or later, **Session recap** appears in the same menu and is stored as `chat.enableSessionRecap`. Start a new session after changing it.

- **Disabled** (default): Kiro makes no recap call and shows no recap.
- **Enabled**: Kiro makes one extra billed model call after each completed turn; the full terminal UI displays the recap above the prompt after three fully idle seconds. Lite mode does not display it, but the call still runs while enabled.

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

When the agent reasons through a complex request, it can stream those reasoning ("thinking") blocks inline above its response. This is controlled by the `chat.showThinking` setting, which is **enabled by default**.

In Kiro CLI 3.2.1 or later, set it from [Output details](#settings-output-details):

```bash
/settings output-details
# Select "Thinking" and choose expanded, collapsed, or off
```

Before Kiro CLI 3.2.1, toggle it from the display menu:

```bash
/settings display
# Select "Show thinking" and press Enter to toggle
```

Or set it directly from the command line:

```bash
# Hide reasoning blocks
kiro-cli settings chat.showThinking off

# Show reasoning blocks again
kiro-cli settings chat.showThinking expanded
```

The values are `expanded`, `collapsed`, and `off`. `true` and `false` still work and mean `collapsed` and `off`.

A few things to know:
- A command-line change applies to your next chat session, not the current one. In Kiro CLI 3.2.1 or later, a change in Output details applies to the current session.
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
