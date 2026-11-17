> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Checkpoints and rewind

> Undo agent changes to your files or fork your conversation to explore a different path

Agent sessions are exploratory. Sometimes the agent heads down the wrong path, or you want to try a different approach without losing what you have. Kiro gives you two distinct ways to go back: **checkpoints** restore your files to an earlier point in the session, and **rewind** forks your conversation at an earlier turn.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Checkpoints - restore files to an earlier point | ✓ | Experimental (v2) | — | — |
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

The CLI gives you rewind for forking conversations, plus an experimental checkpointing feature (CLI v2) for file-level snapshots.

### Fork a conversation with /rewind

The `/rewind` command lets you go back to any previous turn in your conversation and branch off in a new direction. When you run `/rewind`, Kiro creates a new session that starts from the turn you select. The original session stays intact, so you can always switch back to it.

**ℹ️ Info:** Rewinding creates a new conversation branch - it does not undo file changes made in later turns. Your files on disk remain as they are. To revert file changes, use the experimental checkpointing feature below or your version control system.


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

### File checkpoints (experimental, CLI v2)

Checkpointing enables session-scoped snapshots for tracking file changes using Git-like commands. It creates a temporary shadow bare git repository that tracks file changes without affecting your actual git repo, and is automatically cleaned up when the session ends.

Enable it with:

```bash
kiro-cli settings chat.enableCheckpoint true
```

Or select **Checkpointing** from the `/experiment` list.

In git repositories, checkpointing auto-enables when you start a chat session. In non-git directories, initialize it manually with `/checkpoint init`.

| Command | Description |
|---------|-------------|
| `/checkpoint init` | Manually enable checkpoints (required outside git repositories) |
| `/checkpoint list [--limit N]` | Show turn-level checkpoints with file statistics |
| `/checkpoint expand <tag>` | Show tool-level checkpoints under a specific turn |
| `/checkpoint diff <tag1> [tag2\|HEAD]` | Compare checkpoints, or a checkpoint with the current state |
| `/checkpoint restore [<tag>] [--hard]` | Restore to a checkpoint (interactive picker if no tag given) |
| `/checkpoint clean` | Delete the session shadow repository and all checkpoint data |

Restore has two modes:

- **Default (soft)** - reverts tracked changes and deletions, but keeps files created after the checkpoint. Use this to undo changes while keeping new work.
- **`--hard`** - makes your workspace exactly match the checkpoint state, deleting tracked files created after it. Use with caution: hard restore permanently deletes files.

When you restore to a checkpoint, the conversation history also unwinds to that point - messages after the checkpoint are removed and Kiro's understanding resets, ensuring consistency between file state and conversation context.

Keep in mind the current limitations:

- Checkpoints only exist for the current session and are cleaned up when it ends - they can't be shared across sessions
- Only files modified during the session within the working directory are tracked
- Large files or many checkpoints can slow down checkpoint operations and consume disk space

## Related

- [Session management](https://kiro.dev/docs/cli/chat/session-management.md) - saving, loading, and resuming CLI sessions
- [Compaction](https://kiro.dev/docs/compaction.md) - how Kiro summarizes older history to keep long sessions productive
- [Permissions](https://kiro.dev/docs/permissions.md) - control what the agent can do before changes happen, rather than undoing them after
