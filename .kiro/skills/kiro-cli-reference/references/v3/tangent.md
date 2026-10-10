> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Tangent

> Branch your conversation into side-conversations, explore freely, then jump back to exactly where you left off

Need to ask something unrelated mid-task, like looking up an API limit, debugging a side error, or exploring an alternative, without polluting your main thread? `/tangent` lets you branch into a side-conversation that inherits everything discussed so far, explore freely, then jump back to exactly where you left off.

**ℹ️ Info:** This page covers tangent in CLI 3.0 (`kiro-cli --v3`), built on the unified agent harness. The earlier experimental tangent mode behaves differently — a single checkpoint toggled with `/tangent` or `Ctrl+T`, with no naming or nesting. See [Tangent mode (experimental)](https://kiro.dev/docs/cli/experimental/tangent-mode.md) for that behavior.

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

## Related

- [CLI 3.0 overview](https://kiro.dev/docs/cli/v3.md) for the unified agent harness and how to opt in
- [New features in 3.0](https://kiro.dev/docs/cli/v3/new-features.md) for what else is new in the v3 engine
- [Tangent mode (experimental)](https://kiro.dev/docs/cli/experimental/tangent-mode.md) for the earlier single-checkpoint behavior
