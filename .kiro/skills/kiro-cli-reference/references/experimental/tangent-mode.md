> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Tangent mode

> Explore side topics without disrupting your main conversation flow

Tangent mode creates conversation checkpoints, allowing you to explore side topics without disrupting your main conversation flow. Enter tangent mode, ask questions or explore ideas, then return to your original conversation exactly where you left off.

**ℹ️ Info:** In CLI 3.0 (`kiro-cli --v3`), tangent graduates into named, nestable side-conversations with a visual picker. See [Tangent (CLI 3.0)](https://kiro.dev/docs/cli/v3/tangent.md).

## Enabling tangent mode

Tangent mode is experimental and must be enabled:

**Via Experiment Command:**
```bash
/experiment
# Select tangent mode from the list
```

**Via Settings:**
```bash
kiro-cli settings chat.enableTangentMode true
```

## Basic usage

### Enter tangent mode

Use `/tangent` or **Ctrl+T**:

```
> /tangent
Created a conversation checkpoint (↯). Use ctrl + t or /tangent to restore the conversation later.
```

### In tangent mode

You'll see a yellow `↯` symbol in your prompt:

```
↯ > What is the difference between async and sync functions?
```

### Exit tangent mode

Use `/tangent` or **Ctrl+T** again:

```
↯ > /tangent
Restored conversation from checkpoint (↯). - Returned to main conversation.
```

### Exit with tail

Use `/tangent tail` to preserve the last conversation entry (question + answer):

```
↯ > /tangent tail
Restored conversation from checkpoint (↯) with last conversation entry preserved.
```

## Usage examples

### Example 1: Exploring alternatives

```
> I need to process a large CSV file in Python. What's the best approach?

I recommend using pandas for CSV processing...

> /tangent
Created a conversation checkpoint (↯).

↯ > What about using the csv module instead of pandas?

The csv module is lighter weight...

↯ > /tangent
Restored conversation from checkpoint (↯).

> Thanks! I'll go with pandas. Can you show me error handling?
```

### Example 2: Getting Kiro CLI help

```
> Help me write a deployment script

I can help you create a deployment script...

> /tangent
Created a conversation checkpoint (↯).

↯ > What Kiro CLI commands are available for file operations?

Kiro CLI provides read, write, shell...

↯ > /tangent
Restored conversation from checkpoint (↯).

> It's a Node.js application for AWS
```

### Example 3: Clarifying requirements

```
> I need to optimize this SQL query

Could you share the query you'd like to optimize?

> /tangent
Created a conversation checkpoint (↯).

↯ > What information do you need to help optimize a query?

To optimize SQL queries effectively, I need:
1. The current query
2. Table schemas and indexes...

↯ > /tangent
Restored conversation from checkpoint (↯).

> Here's my query: SELECT * FROM orders...
```

### Example 4: Keeping useful information

```
> Help me debug this Python error

I can help you debug that. Could you share the error message?

> /tangent
Created a conversation checkpoint (↯).

↯ > What are the most common Python debugging techniques?

Here are the most effective Python debugging techniques:
1. Use print statements strategically
2. Leverage the Python debugger (pdb)...

↯ > /tangent tail
Restored conversation from checkpoint (↯) with last conversation entry preserved.

> Here's my error: TypeError: unsupported operand type(s)...

# The preserved entry about debugging techniques is now part of main conversation
```

## Configuration

### Keyboard shortcut

Change the shortcut key (default: t):

```bash
kiro-cli settings chat.tangentModeKey y
```

### Auto-tangent for introspect

Automatically enter tangent mode for Kiro CLI help questions:

```bash
kiro-cli settings introspect.tangentMode true
```

## Visual indicators

- **Normal mode**: `> ` (magenta)
- **Tangent mode**: `↯ > ` (yellow ↯ + magenta)
- **With agent**: `[dev] ↯ > ` (cyan + yellow ↯ + magenta)

## When to use tangent mode

### Good use cases

- **Asking clarifying questions** about the current topic
- **Exploring alternative approaches** before deciding
- **Getting help** with Kiro CLI commands or features
- **Testing understanding** of concepts
- **Quick side questions** that don't need to be in main context

### When not to use

- **Completely unrelated topics** - Start a new conversation instead
- **Long, complex discussions** - Use regular conversation flow
- **When you want the side discussion in main context** - Don't use tangent mode

## Tips

1. **Keep tangents focused**: Brief explorations, not extended discussions
2. **Return promptly**: Don't forget you're in tangent mode
3. **Use for clarification**: Perfect for "wait, what does X mean?" questions
4. **Experiment safely**: Test ideas without affecting main conversation
5. **Use `/tangent tail`**: When both the tangent question and answer are useful for main conversation

## How it works

### Checkpoint creation

When you enter tangent mode:
1. Current conversation state is saved as a checkpoint
2. You can continue the conversation in tangent mode
3. All tangent conversation is separate from main thread

### Restoration

When you exit tangent mode:
1. Conversation returns to the checkpoint state
2. Tangent conversation is discarded (unless using `tail`)
3. Main conversation continues as if tangent never happened

### Tail mode

Using `/tangent tail`:
1. Returns to checkpoint like normal exit
2. Preserves the last Q&A pair from tangent
3. Adds that Q&A to main conversation context
4. Useful when tangent provided valuable information

## Limitations

- **Tangent conversations are discarded** when you exit (unless using tail)
- **Only one level of tangent** supported (no nested tangents)
- **Experimental feature** that may change or be removed
- **Must be explicitly enabled** before use

## Troubleshooting

### Tangent mode not working

Enable via experiment:
```bash
/experiment
# Select tangent mode from the list
```

Or enable via settings:
```bash
kiro-cli settings chat.enableTangentMode true
```

### Keyboard shortcut not working

Check or reset the shortcut key:
```bash
kiro-cli settings chat.tangentModeKey t
```

Ensure you're using Ctrl+T (not just T).

### Lost in tangent mode

Look for the `↯` symbol in your prompt. Use `/tangent` to exit and return to main conversation.

### Accidentally discarded important information

If you exit tangent mode without using `tail` and lose important information:
1. Unfortunately, tangent conversations are not recoverable
2. You'll need to ask the question again in the main conversation
3. Consider using `/tangent tail` in the future to preserve important Q&A pairs

## Related features

- **Introspect**: Kiro CLI help (auto-enters tangent if configured)
- **Experiments**: Manage experimental features with `/experiment`
- **Checkpointing**: Similar concept but for file changes

## Best practices

### Workflow integration

1. **Start main task**: Begin your primary conversation
2. **Hit tangent**: When a side question arises, use `/tangent`
3. **Explore freely**: Ask clarifying questions without worry
4. **Decide on tail**: If the tangent was useful, use `/tangent tail`
5. **Continue main**: Return to your primary task

### Example workflow

```
> Help me refactor this React component

# Main conversation starts...

> /tangent
↯ > What's the difference between useMemo and useCallback?

# Get clarification...

↯ > /tangent tail  # This was useful, keep it

> Now I understand. Let's use useMemo for the expensive calculation...
```

## Next steps

- [Experimental Features Overview](https://kiro.dev/docs/cli/experimental.md)
- [Checkpointing](https://kiro.dev/docs/checkpoints.md)
- [Settings Configuration](https://kiro.dev/docs/reference/settings.md)
