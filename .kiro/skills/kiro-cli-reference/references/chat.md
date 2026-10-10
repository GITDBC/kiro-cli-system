> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Chat

> Interacting with Kiro CLI

The Kiro CLI provides an interactive chat mode that lets you have natural conversations with AI directly in your terminal. The default experience uses a rich [terminal UI](https://kiro.dev/docs/cli/terminal-ui.md) with syntax-highlighted code, interactive panels, and visual tool progress.

## Starting a session

To start a chat session:

```bash
kiro-cli
```

Or start a chat with a specific context:

```bash
kiro-cli --agent myagent
```

To run the session in a managed cloud sandbox instead of on your machine, add `--cloud`, optionally binding repositories with `--repo` — see [Cloud sessions](https://kiro.dev/docs/cloud-sessions.md):

```bash
kiro-cli --cloud --repo owner/repository
```

## Entering multi-line statements

Insert a newline in your prompt using any of these methods:

- **Shift+Enter** — works in iTerm2, Ghostty, Kitty, Warp, and Zed
- **Ctrl+J** — works in all terminals including tmux
- **Alt+Enter** — works in Terminal.app and Ghostty
- **`/editor`** — opens your default editor (defaults to vi) for composing longer prompts

If `Shift+Enter` doesn't work in your terminal, run `/settings terminal` to auto-configure it. See [In-session settings](https://kiro.dev/docs/cli/chat/settings.md) for details.

You can also use the [`/reply`](https://kiro.dev/docs/cli/chat/responding.md) command to open your editor with the most recent assistant message quoted for reply.

## Running shell commands inline

Run shell commands without going through the AI by prefixing with `!`:

```bash
!npm run build
```

Output streams in real time. TTY commands like `vim`, `ssh`, and `top` get full terminal access. Long output collapses to a head + tail view — press Ctrl+O to expand.

## Managing context

Use `/context` to view and manage what files are included in your session:

```bash
/context show              # View context breakdown with per-file token usage
/context add "src/**/*.ts" # Add files by glob pattern
/context remove src/app.js # Remove a context rule
/context clear             # Remove all rules
```

See [Context Management](https://kiro.dev/docs/cli/chat/context.md) for detailed documentation.

## Conversation persistence

Kiro can remember your conversations based on the folder where you started them. When you start a session where you previously chatted with Kiro, you can tell Kiro to automatically load that conversation history, allowing you to seamlessly continue your discussion.

### Directory-based persistence

If it's your first time chatting in that directory, Kiro will start a new conversation (taking into consideration any designated context).

To explicitly resume a conversation in the current directory, use:

``` bash
$ kiro-cli chat --resume
```

To resume a specific session by ID:

``` bash
$ kiro-cli chat --resume-id <SESSION_ID>
```

To open an interactive session picker to choose from previous sessions:

``` bash
$ kiro-cli chat --resume-picker
```

### Starting a fresh conversation

You can start a fresh conversation without restarting the CLI using the `/chat new` command. This saves your current session to the database and begins a new one in place.

```bash
# Start a fresh conversation
/chat new

# Start a fresh conversation with an initial prompt
/chat new how do I set up a React project
```

Use `/chat resume` to return to any previous session.

### Manually saving and loading conversations

You can also manually save and load conversations using the following commands while in a chat session:

``` bash
    /chat save [path] – Saves your current conversation to a JSON file.

        Add -f or --force to overwrite an existing file

        Examples:

        /chat save ./my-project-conversation -f

        /chat save /home/user/project/my-project-conversation.json

        You cannot use ~ to denote your home directory.

    /chat load [path] – Loads a conversation from a previously saved JSON file

        Example: /chat load ./my-project-conversation.json
```

**ℹ️ Info:** The `/chat save` and `/chat load` commands operate independently of the directory where the conversation was originally created. When loading a conversation, be mindful that it will replace your current conversation regardless of which directory it was saved from.
