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

The CLI exposes two settings that control how much context is retained during compaction:

| Setting | Default | Description |
|---------|---------|-------------|
| `compaction.excludeMessages` | 2 | Minimum number of recent message pairs to retain verbatim |
| `compaction.excludeContextWindowPercent` | 2 | Minimum percentage of the context window to keep as recent messages |

Both settings are evaluated, and the more conservative (larger) value wins. This ensures enough recent context is always available for the agent to maintain continuity.

## Limitations

Compaction is one-way. The full conversation history before the compaction point is not recoverable within the session. If you need to preserve the complete history, export your session before compaction occurs.

## Previous versions

In IDE 0.x, this feature was called "Summarization." The behavior was similar (auto-trigger at 80% context usage) but created a new session with compacted context rather than continuing in the same session. See [0.x reference](https://kiro.dev/docs/ide/0x-reference.md#summarization-replaced-by-compaction-in-10) for the legacy behavior.
