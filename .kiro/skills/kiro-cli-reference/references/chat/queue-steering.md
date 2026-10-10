> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Queue steering

> Send messages to the agent while it's working to redirect its approach without cancelling

Mid-turn steering lets you type a follow-up message while the agent is actively processing. Instead of waiting for the agent to finish or cancelling and starting over, you can send guidance that the agent incorporates into its work.

Kiro offers two follow-up modes that control when your message reaches the agent:

| Mode | Behavior | Best for |
|------|----------|----------|
| Steer (default) | Message reaches the agent mid-turn so it can adjust course | Real-time course correction |
| Queue | Message buffered locally, sent after turn ends | Batching multiple follow-ups |

Press **Ctrl+S** to switch between steer and queue modes.

## How it works

### Steer mode

1. Type your message and press Enter while the agent is working
2. Your message is sent to the agent
3. The agent picks it up mid-turn at the next safe point and incorporates it
4. The agent sees your guidance and adjusts its approach
5. The agent acknowledges how it handled your input

### Queue mode

1. Type your message and press Enter while the agent is working
2. Your message is added to a local buffer (visible in activity tray)
3. The agent finishes its current turn normally
4. The first queued message is sent as a new prompt
5. Process continues until the queue is empty

### When the agent sees your message

In steer mode, your message reaches the agent during the current turn and is picked up at the next safe point in its work — without interrupting an action that's already in progress. Multiple messages sent in steer mode are concatenated and delivered together.

## Usage

Type and press Enter while the agent is working:

```bash
> Refactor the auth module

[Agent starts working, reading files...]

> Actually, focus on the login function first

[In steer mode: sent to the agent mid-turn]
[In queue mode: message added to local buffer]
```

### Viewing queued messages

The activity tray shows your pending messages:
- Press **Ctrl+X** to expand the activity tray
- The tab shows "Steer" (steer mode) or "Queue (N)" (queue mode with N items)
- Press **Delete** or **Backspace** to clear the message or selected item

### Cancel and redirect

Press **Ctrl+C** or **Esc** while a steering message is queued to implement "stop that and do this instead":

1. The current operation is cancelled
2. Your queued message is automatically sent as a new prompt

```bash
> Write unit tests for the user service

[Agent starts writing tests...]

> Actually, let's do integration tests
> [press Ctrl+C or Esc]

Redirecting to: Actually, let's do integration tests
[New turn starts with integration test focus]
```

## Steer vs. queue vs. cancel

| Action | What happens | Use when |
|--------|-------------|----------|
| Steer (type + Enter) | Agent adjusts mid-turn at the next safe point | You want immediate course correction |
| Queue (Ctrl+S, then type) | Messages buffer, sent after turn ends | You want to batch multiple follow-ups |
| Cancel (Ctrl+C or Esc) | Agent stops, queued steer message sent as new prompt | You want to stop and pivot immediately |

## Configuration

Set the startup default via `/settings` → `terminal` → `interrupt behaviour`.

## Limitations

- **Steer mode**: Only one message slot — multiple messages concatenate with `\n\n`
- **Queue mode**: Messages sent sequentially, not batched
- **Timing dependent**: If the agent finishes before your message is queued, it becomes a normal prompt

## Related

- [Goal](https://kiro.dev/docs/cli/chat/goal.md) — autonomous agent loop with built-in verification
- [Responding to messages](https://kiro.dev/docs/cli/chat/responding.md) — how to interact with agent responses
- [Rewind](https://kiro.dev/docs/checkpoints.md) — fork a conversation at an earlier turn
- [Settings](https://kiro.dev/docs/cli/chat/settings.md) — configure keybindings and display preferences
