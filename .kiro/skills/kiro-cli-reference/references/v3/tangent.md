> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Tangent

> Branch your conversation into side-conversations, explore freely, then jump back to exactly where you left off

Need to ask something unrelated mid-task, like looking up an API limit, debugging a side error, or exploring an alternative, without polluting your main thread? `/tangent` lets you branch into a side-conversation that inherits everything discussed so far, explore freely, then jump back to exactly where you left off.

**ℹ️ Info:** This page covers tangent in CLI V3 (`kiro-cli --v3`), built on the unified agent harness. The earlier experimental tangent mode behaves differently — a single checkpoint toggled with `/tangent` or `Ctrl+T`, with no naming or nesting. See [Tangent mode (experimental)](https://kiro.dev/docs/cli/experimental/tangent-mode.md) for that behavior.

## Commands

| Command | What it does |
|---------|--------------|
| `/tangent` | At the root, branches into a side-conversation (auto-named `tangent-N`) that inherits your conversation so far. Inside a tangent, goes back one level toward the parent. |
| `/tangent <name>` | Branches into a named side-conversation (e.g. `/tangent ddb`). Creates it if new, switches to it if it already exists. |
| `/tangent ls` | Opens a visual picker showing your whole conversation tree. Select any session to switch to it. |
| `/tangent root` | Jumps straight back to the main conversation from any depth. |

While in a tangent, a `↯ name` chip in the footer shows where you are.

## How tangents work

Each tangent is a full session: it starts with your conversation's history up to the branch point, but everything after stays isolated. Nothing you do inside a tangent touches the parent conversation's context. Because a tangent branches from your conversation's history, you can't branch an empty chat — send a message first.

Tangents can also have tangents. Nest as deep as you need — `/tangent ls` shows the whole tree, and `/tangent root` gets you home from anywhere.

## Ways to use tangents

1. **Quick lookups without derailing.** Mid-refactor and need to check DynamoDB item size limits? `/tangent`, ask, get the answer, `/tangent` back. Your main thread never sees the detour.
2. **Compare alternatives in parallel.** Branch `/tangent approach-a` and `/tangent approach-b` off the same design discussion, explore each with full shared context, then return to the root and commit to the winner.
3. **Contain noisy debugging.** A failing test needs 15 turns of log-dumping? Do it in a tangent. The noise stays out of your main conversation's context, keeping it focused and cheap.
4. **Ask the "dumb question" freely.** Want to ask something basic without the model anchoring on it for the rest of the session? Tangent it.
5. **Nest as deep as you need.** A tangent mid-tangent is fine — the tree keeps track for you.

**💡 Tip:** Name tangents after what they're for (`ddb`, `pricing`, `flaky-test`). Names are how you switch back by command, and they show in the picker.

## Merging a tangent back

Exploring in a tangent and want its findings folded into another session, without dragging in the whole side-conversation? `/tangent merge [dest]` sends a short summary of the tangent to a destination session instead.

```bash
# Merge into the parent session (default)
> /tangent merge

# Merge findings into the conversation root
> /tangent merge root

# Merge into a specific named session
> /tangent merge ddb
```

| Destination | Behavior |
|---|---|
| *(none)* | Merges into the parent of the current tangent. |
| `root` | Merges into the main conversation, regardless of nesting depth. |
| `<name>` | Merges into that named session, if it exists. |

Merge never creates a session. An unresolvable named destination is an error.

**ℹ️ Info:** The tangent itself is never removed or truncated by a merge. Kiro sends one summarization turn inside the tangent, then injects only that distilled summary into the destination as a real prompt turn. The destination never receives the tangent's full transcript. The short line you see for this (e.g. "Merging findings from...") is saved as that turn's own content, so reopening or resuming the session later shows the same summary line instead of replaying the original merge instruction.

### Merge errors

| Message | Cause |
|---|---|
| `Already on the root session — nothing to merge into` | You ran bare `/tangent merge` at the root, with no destination to merge into. |
| `No session named "<name>" to merge into` | The named destination doesn't exist. Merge never creates one. |
| `Cannot merge a session into itself` | The resolved destination is the current session. |
| `Nothing to merge yet — this conversation has no findings of its own` | The tangent has no prompts of its own to summarize. |
| `Merge cancelled — ...` | The summarization turn was cancelled or failed to send. |

## Related

- [CLI V3 overview](https://kiro.dev/docs/cli/v3.md) for the unified agent harness and how to opt in
- [New features in V3](https://kiro.dev/docs/cli/v3/new-features.md) for what else is new in the V3 harness
- [Tangent mode (experimental)](https://kiro.dev/docs/cli/experimental/tangent-mode.md) for the earlier single-checkpoint behavior
