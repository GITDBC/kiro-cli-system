> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Goal

> Start an autonomous agent loop that iterates toward an objective with built-in verification

The `/goal` command launches a goal-driven agent loop where Kiro works autonomously toward an objective you define. Unlike a regular prompt, the agent cycles through implementation and self-verification, only marking the task complete when acceptance criteria are met. By default, the agent runs up to 5 iterations — increase this with `--max`:

```bash
# Default: 5 iterations
/goal refactor the auth module to use JWT tokens and ensure all tests pass

# Allow more iterations for complex tasks
/goal --max 10 migrate the entire test suite from Jest to Vitest
```

## How it works

When you set a goal, the agent enters an iterative loop:

1. Plans the steps needed to accomplish the objective
2. Implements changes
3. Verifies the result against the goal's acceptance criteria
4. If verification fails, iterates with corrections
5. Marks the goal complete once all criteria pass

This cycle continues until the agent confirms the work is done or you cancel the goal.

The agent derives acceptance criteria from your goal statement. Be explicit about what "done" looks like — "all tests pass" or "no TypeScript errors" gives the agent a concrete verification target. Vague goals like "improve the code" may cause the agent to iterate longer than necessary.

```bash
# Set a goal with clear acceptance criteria
/goal refactor the auth module to use JWT tokens and ensure all tests pass

# Cancel an active goal
/goal clear
```

**ℹ️ Info:** The agent keeps iterating until it verifies success. For complex goals, this may take several turns of autonomous work. You can monitor progress in real time as the agent works.

## When to use goals

Goals work best for multi-step tasks where you want autonomous execution with a built-in quality gate:

- **Refactoring with constraints** — "migrate all API routes from Express to Hono and make sure the test suite passes"
- **Bug fixing with verification** — "fix the race condition in the worker pool and add a regression test"
- **Code generation with criteria** — "add input validation to all form components and ensure accessibility tests pass"
- **Multi-file changes** — "rename the User model to Account across the entire codebase with no broken imports"

For simple, single-step tasks where you already know what you want, a regular prompt is faster. Use `/goal` when you want the agent to own the verification step.

## Managing an active goal

While a goal is running, you have two options:

- **Steer it** — use [queue steering](https://kiro.dev/docs/cli/chat/queue-steering.md) (Ctrl+S) to send a mid-loop correction without cancelling
- **Cancel it** — run `/goal clear` to stop the loop and return to standard interactive mode

```bash
/goal clear
```

File changes already made remain on disk. Use your version control system to revert if needed.

## Limits and safeguards

The agent respects the same turn limits and context window constraints as regular prompts. If it exhausts its context or hits a repeated failure pattern, it stops and reports what it tried. You can also use [queue steering](https://kiro.dev/docs/cli/chat/queue-steering.md) to nudge the agent mid-loop without cancelling the goal entirely.

## Related

- [Queue steering](https://kiro.dev/docs/cli/chat/queue-steering.md) — redirect the agent mid-turn without cancelling
- [Effort](https://kiro.dev/docs/models/effort.md) — control reasoning depth for the model
- [Rewind](https://kiro.dev/docs/checkpoints.md) — fork a conversation at an earlier turn
