> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Checkpoints and rewind

> Undo agent changes to your files or fork your conversation to explore a different path

Agent sessions are exploratory. Sometimes the agent heads down the wrong path, or you want to try a different approach without losing what you have. Kiro gives you two distinct ways to go back: **checkpoints** restore your files to an earlier point in the session, and **rewind** forks your conversation at an earlier turn.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Checkpoints - restore files to an earlier point | ✓ | — | — | — |
| Rewind - fork the conversation at an earlier turn | — | ✓ | — | — |
| Revert the last turn's file changes | ✓ | — | — | — |

## Checkpoints vs. rewind

The two mechanics solve different problems:

- **Checkpoints** snapshot your files as the agent modifies them. Restoring a checkpoint rolls your workspace back to that point - and rewinds the conversation context along with it, so the agent's understanding matches the restored file state.
- **Rewind** never touches your files. It forks the conversation at an earlier turn into a new session, leaving the original session and your files on disk exactly as they are.

Reach for a checkpoint when you want to **undo the agent's work**. Reach for rewind when you want to **redirect the conversation** - for example, to try a different prompt from the same starting point - while keeping the file changes made so far.

## Using checkpoints and rewind

    IDE
    CLI

Each time you send a prompt to Kiro, it creates a checkpoint. Checkpoints appear as markers in your chat history. Select **Restore** on a checkpoint marker to rewind both your codebase and Kiro's context back to that point in time. Any changes made to your codebase by Kiro after that checkpoint are reverted, and any context additions (chat interactions) after that point are discarded as well.

Checkpoints act as a safety net that enables you to confidently explore multiple approaches to a problem, try different models for a given task, and recover from mistakes or misunderstandings by the agent.

[Video](https://kiro.dev/videos/checkpoint-restore.mp4)

### What checkpoints track

Checkpoints work by snapshotting the contents of a file each time the Kiro agent modifies it using one of its built-in file modification tools, and then restoring that snapshot when you revert to that checkpoint.

Kiro does not track changes to a file made *outside* of the Kiro agent. If Kiro snapshots a file and you then manually edit that same file or run a code formatting tool on it, your changes will be lost when you revert to that checkpoint. Kiro also does not track file changes made by MCP tools or bash commands that it runs as part of its execution.

### Reverts vs. checkpoints

Whenever the Kiro agent modifies one or more files and then completes its turn, you will see an option to **Revert** the changes made by the agent immediately above the chat input box.

Reverts are similar to checkpoints, but differ in two key aspects. First, reverts only undo changes made by the *latest* turn of the agent, whereas checkpoints can undo changes made over multiple turns. Second, reverts only revert *file* changes, whereas checkpoints undo file changes as well as discard context additions past the checkpoint.

The CLI gives you rewind for forking conversations.

### Fork a conversation with /rewind

The `/rewind` command lets you go back to any previous turn in your conversation and branch off in a new direction. When you run `/rewind`, Kiro creates a new session that starts from the turn you select. The original session stays intact, so you can always switch back to it.

**ℹ️ Info:** Rewinding creates a new conversation branch - it does not undo file changes made in later turns. Your files on disk remain as they are. To revert file changes, use your version control system.


```bash
# Open interactive turn picker
/rewind

# Jump directly to turn 4
/rewind 4
```

The interactive picker displays:

- A preview of your prompt at each turn
- Tool calls made during that turn (file edits, commands, searches)
- The context window usage percentage at that point
- Turns listed newest-first for quick access to recent history

A typical workflow: you're mid-conversation and realize the agent went down the wrong path a few turns ago. Run `/rewind`, select the turn where things were still on track, and send a different prompt to guide the conversation in a better direction. To return to the original session, use `/chat resume` - the original is never modified.

Rewind is useful for:

- **Backtracking** - the agent made a wrong assumption three turns ago and everything since built on it
- **Exploring alternatives** - try a different approach to the same problem without losing your first attempt
- **Recovering from context pollution** - too much irrelevant context accumulated and you want a cleaner starting point
- **A/B testing prompts** - fork at the same turn with different instructions to compare results

## Related

- [Session management](https://kiro.dev/docs/cli/chat/session-management.md) - saving, loading, and resuming CLI sessions
- [Compaction](https://kiro.dev/docs/compaction.md) - how Kiro summarizes older history to keep long sessions productive
- [Permissions](https://kiro.dev/docs/permissions.md) - control what the agent can do before changes happen, rather than undoing them after
