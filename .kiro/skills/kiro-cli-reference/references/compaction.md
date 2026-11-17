> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Compaction

> How Kiro automatically summarizes conversation history to keep sessions productive within model context limits

Compaction keeps long sessions productive by automatically summarizing older conversation history as your session grows. Your goals, decisions, and technical progress are preserved - only the verbose middle gets compressed.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Automatic compaction | ✓ | ✓ | ✓ | ✓ |
| Manual trigger (`/compact`) | — | ✓ | — | — |
| Context usage meter | ✓ | ✓ | ✓ | ✓ |

## How it works

When your conversation approaches the model's context limit, compaction triggers automatically:

1. **Summary generation** - Kiro creates a structured summary capturing your goals, decisions, progress, and next steps
2. **Context reduction** - Older conversation history is replaced by the summary, while your most recent messages are kept verbatim
3. **Continuation** - The session continues from where you left off with no interruption

In V3 CLI sessions, the active response and Thinking indicator remain visible while automatic compaction runs. Prompts already queued continue automatically when compaction finishes.

In Kiro CLI 3.1.0 or later, V3 sessions run `PreCompact` Hooks before compaction and `PostCompact` Hooks after it. A `PreCompact` Hook can refuse the compaction; a `PostCompact` Hook receives the summary. See [Hook types](https://kiro.dev/docs/hooks/types.md#pre-compaction).

Your goals, decisions, file modifications, and stated constraints survive compaction. What gets compressed is intermediate output - tool call details, exploratory discussion, and resolved error messages.

**💡 Tip:** If the agent seems to have lost a specific detail from earlier in the session, restate it. The agent will incorporate it immediately.

## Example

You've been working on a refactoring task for 45 minutes - the agent has modified 12 files, run tests, and fixed three build errors. Context usage is at 80%.

Compaction fires. The summary captures: which files were modified, what tests pass, the remaining 2 files to refactor, and your constraint that "all changes must be backward-compatible." The last two exchanges (your most recent instruction and the agent's response) stay verbatim.

The agent continues immediately. It knows what's done, what's next, and what your rules are - without carrying 45 minutes of intermediate tool output.

## What's preserved vs. summarized

| Always preserved | May be summarized |
|-----------------|-------------------|
| Task status (done / in-progress / pending) | Individual tool call details |
| File paths modified | Intermediate reasoning steps |
| Key decisions and constraints | Code snippets in earlier messages |
| Next steps | Error details from resolved issues |
| Your stated intent and requirements | Exploratory discussion |

In Kiro IDE 1.4.178 or later, Kiro tells the agent which loaded skills and steering files the summary dropped, and the agent reloads the ones you asked for. A skill or steering file of 30,000 characters or more loads in full when there is room for it after a summary, instead of as a shortened preview.

## Triggering compaction

    IDE
    CLI
    Web
    Mobile

Compaction is automatic in the IDE. There is no manual trigger.

The context usage meter in the chat panel shows how close you are to the model's limit. When compaction fires, the meter resets to reflect the freed space and the session continues.

Compaction triggers automatically when context fills up, but you can also trigger it manually:

```bash
/compact
```

Use this if a session feels slow due to accumulated context, or before starting a new phase of work within the same session.

Compaction is automatic in the Web client. There is no manual trigger.

Compaction is automatic on Mobile. There is no manual trigger.

## Configuration

The CLI exposes settings that control when automatic compaction starts and how much context is retained:

| Setting | Default | Description |
|---------|---------|-------------|
| `compaction.autoCompactionThreshold` | 80 | Context usage percentage at which automatic compaction starts in a V3 session (Kiro CLI 3.3.0 or later). A number from 0 to 100 with at most two decimal places |
| `compaction.excludeMessages` | 2 | Minimum number of recent message pairs to retain verbatim |
| `compaction.excludeContextWindowPercent` | 2 | Minimum percentage of the context window to keep as recent messages |

The two exclusion settings are evaluated together, and the more conservative (larger) value wins. This ensures enough recent context is always available for the agent to maintain continuity.

In Kiro CLI 3.3.0 or later, a V3 session can also set the threshold from `/settings`. Open **Compaction** to turn automatic compaction on or off, see the threshold the current session uses, and edit the **Global default**. The editor shows the range the agent harness accepts and its default; the value you save applies to the next session you start or load. `kiro-cli settings compaction.autoCompactionThreshold <value>` accepts 0 to 100, and an interactive session applies the range the agent harness advertises. A `compaction.autoCompactionThreshold` value in a workspace `.kiro/settings/cli.json` overrides the global default for that workspace. See [In-session settings](https://kiro.dev/docs/cli/chat/settings.md#compaction).

## Limitations

Compaction is one-way. The full conversation history before the compaction point is not recoverable within the session. If you need to preserve the complete history, export your session before compaction occurs.

## Previous versions

In IDE 0.x, this feature was called "Summarization." The behavior was similar (auto-trigger at 80% context usage) but created a new session with compacted context rather than continuing in the same session. See [0.x reference](https://kiro.dev/docs/ide/0x-reference.md#summarization-replaced-by-compaction-in-10) for the legacy behavior.
