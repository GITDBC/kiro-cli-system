> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Tangent

> Branch your conversation into side-conversations, explore freely, then jump back to exactly where you left off

Need to ask something unrelated mid-task, like looking up an API limit, debugging a side error, or exploring an alternative, without polluting your main thread? `/tangent` lets you branch into a side-conversation that inherits everything discussed so far, explore freely, then jump back to exactly where you left off.

**ℹ️ Info:** This page covers `/tangent` in a V3 session. On the V2 harness, the experimental tangent mode behaves differently: a single checkpoint toggled with `/tangent` or `Ctrl+T`, with no naming or nesting. See [Tangent mode (experimental)](https://kiro.dev/docs/cli/experimental/tangent-mode.md) for that behavior, and [Choose an agent harness](https://kiro.dev/docs/cli/agent-harness.md) for which harness your session runs.

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

**ℹ️ Info:** The tangent itself is never removed or truncated by a merge. Kiro sends one summarization turn inside the tangent, then injects only that distilled summary into the destination as a real prompt turn. The destination never receives the tangent's full transcript.

### Merge errors

| Message | Cause |
|---|---|
| `Already on the root session — nothing to merge into` | You ran bare `/tangent merge` at the root, with no destination to merge into. |
| `No session named "<name>" to merge into` | The named destination doesn't exist. Merge never creates one. |
| `Cannot merge a session into itself` | The resolved destination is the current session. |
| `Nothing to merge yet — this conversation has no findings of its own` | The tangent has no prompts of its own to summarize. |
| `Merge cancelled — ...` | The summarization turn was interrupted or failed, or the destination session was busy when the summary was ready. |

## Related

- [`/tangent`](https://kiro.dev/docs/reference/slash-commands.md#tangent) for the command syntax
- [Session management](https://kiro.dev/docs/cli/chat/session-management.md) for resuming and browsing sessions, including tangents
- [Tangent mode (experimental)](https://kiro.dev/docs/cli/experimental/tangent-mode.md) for the V2 single-checkpoint behavior
