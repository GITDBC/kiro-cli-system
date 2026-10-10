> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Fullscreen mode

> Use a dedicated terminal screen for longer Kiro CLI sessions

Fullscreen mode gives Kiro CLI a dedicated terminal screen with its own scrollable conversation view. Your existing terminal scrollback remains available when you return to inline mode.

Type `/fullscreen` to enter. Type `/fullscreen` again to leave.

## Why use fullscreen

By default, Kiro renders inline with your shell history. Fullscreen mode is useful for longer sessions because it separates the conversation from that history and provides application-managed scrolling.

In fullscreen mode:

- Your conversation scrolls independently from your shell history.
- You can use the mouse, touchpad, or keyboard to browse earlier messages.
- New messages remain available while you are scrolled up.
- Messages produced in fullscreen are added to the inline transcript when you leave.

**ℹ️ Info:** The `/fullscreen` session toggle is available in the TUI and Lite interfaces. The persistent startup setting applies to interactive TUI sessions.

## Entering and leaving

```
/fullscreen
```

A brief notification confirms the switch. The same command toggles you back:

| Current mode | Command | Result |
|--------------|---------|--------|
| Inline | `/fullscreen` | Enter fullscreen |
| Fullscreen | `/fullscreen` | Return to inline |

There is no keyboard shortcut for switching modes. Use `/fullscreen` to enter or leave fullscreen.

Switching modes does not reset the conversation or start a new session.

## Start new sessions in fullscreen

The `/fullscreen` command changes only the current session. To start future interactive TUI sessions in fullscreen:

1. Type `/settings`.
2. Open **Display**.
3. Turn on **Start fullscreen**.

The preference takes effect on your next interactive TUI launch. Turn it off from the same settings row to start future sessions inline again. You can still use `/fullscreen` at any time to change the current session without changing the saved preference.

## Scroll through the conversation

In fullscreen, you can scroll through the conversation using your mouse or keyboard.

| Shortcut | Action |
|----------|--------|
| `PageUp` / `PageDown` | Scroll one page up or down |
| `Home` | Jump to the oldest content when the prompt is empty |
| `End` | Return to the latest content when scrolled up |

When the prompt contains text, `Home` moves the cursor to the beginning of the input. `End` still returns to the latest content while you are scrolled up; at the latest content, it moves the cursor to the end of the input.

You can also use your mouse wheel or touchpad. When you scroll up, a control appears above the prompt showing how many new messages arrived. Click it or press `End` to return to the latest content.

The view follows incoming content while you are at the bottom. If you scroll up, Kiro keeps your position until you return to the latest content.

## Expanding tool output

Tool calls show a preview when their output is long. You can reveal more output in either of these ways:

- Press `Ctrl+O` to expand or collapse the 20 most recent tool outputs.
- Click the toggle text below a tool call to expand or collapse that output individually.

## Mouse selection

Fullscreen mode captures mouse events for scrolling and selection. Click and drag across text to copy the selected text to your clipboard. Kiro displays a confirmation after copying.

Kiro copies through your platform's clipboard tool when one is available: `pbcopy` on macOS, `Set-Clipboard` on Windows, and `wl-copy`, `xclip`, or `xsel` on Linux. When none is reachable — most often on a remote host over SSH — Kiro falls back to the OSC 52 terminal escape sequence, which asks your terminal to set the clipboard on your behalf. Terminal multiplexers and some terminals block OSC 52 by default. If your clipboard does not change, see [Copied text is not updating the clipboard](#copied-text-is-not-updating-the-clipboard).

**ℹ️ Info:** The confirmation reports the text Kiro captured from your drag. It does not verify that your terminal accepted the clipboard write, so the confirmation can appear even when the clipboard was not updated.

You can also use:

- `/copy` to copy the last assistant response
- `/transcript` to open the full conversation in your configured pager
- `/transcript save <path>` to save the conversation to a file

## When to use each mode

| Scenario | Recommended mode |
|----------|-----------------|
| Quick one-off questions | Inline |
| Long coding sessions | Fullscreen |
| Reading lengthy explanations or code reviews | Fullscreen |
| Keeping terminal history visible alongside Kiro | Inline |
| Presenting or sharing your screen | Fullscreen |

You can switch during a session without losing conversation context.

## Troubleshooting

### Fullscreen flickers or doesn't render correctly

Fullscreen uses your terminal's alternate screen buffer. If it does not render correctly:

- Confirm that your terminal or terminal multiplexer supports the alternate screen.
- If you use tmux, check whether your configuration disables its `alternate-screen` option. To enable it globally, add the following line to `~/.tmux.conf`:

  ```text
  set -g alternate-screen on
  ```

  Then start a new tmux server or reload the configuration.
- Try running Kiro directly in your terminal to determine whether a multiplexer configuration is interfering.

### Mouse scroll doesn't work in fullscreen

Mouse scrolling requires terminal mouse reporting. If it does not work:

- Confirm that Kiro shows the **Entered fullscreen** notification.
- Check whether your terminal or multiplexer has mouse reporting disabled.

### Can't select text with mouse

Click and drag to copy text using Kiro's fullscreen selection. If your terminal does not support that interaction, use `/copy` or `/transcript`.

Most terminals also let you hold `Shift` while dragging to bypass an application's mouse capture and use the terminal's own selection instead.

### Copied text is not updating the clipboard

Kiro confirms the copy, but pasting produces older content. This usually means the OSC 52 clipboard write was blocked between Kiro and your desktop, which is the default behavior in tmux.

**If you use tmux**, allow programs running inside it to set the clipboard by adding this line to `~/.tmux.conf`:

```text
set -g set-clipboard on
```

Then reload your configuration or start a new tmux server:

```bash
tmux source-file ~/.tmux.conf
```

tmux defaults to `set-clipboard external`, which lets tmux update the clipboard when tmux itself copies but refuses clipboard writes from applications running inside it. Check the value in a running session with:

```bash
tmux show -gv set-clipboard
```

`allow-passthrough` is a separate option for a different escape-sequence mechanism. Enabling it does not enable clipboard writes, so you need `set-clipboard on` even if you already set `allow-passthrough on`.

**Confirm your terminal accepts clipboard writes.** kitty, WezTerm, Ghostty, and Alacritty allow them by default. In iTerm2, enable **Settings → General → Selection → Applications in terminal may access clipboard**. In xterm, set the `allowWindowOps` resource. macOS Terminal.app does not support OSC 52; use `/transcript save <path>` there, or run Kiro in a terminal that does.

**On a remote Linux host**, install a clipboard tool so Kiro does not need the OSC 52 fallback: `wl-clipboard` on Wayland, or `xclip` or `xsel` on X11. Over SSH without X or Wayland forwarding, OSC 52 remains the only path, so the tmux and terminal settings above still apply.

**For large amounts of text**, prefer `/transcript save <path>`. Kiro and terminals both cap the size of an OSC 52 clipboard write, so a very large selection can be truncated or dropped when that fallback is used.
