> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Plan mode

> Structured planning before execution - explore your codebase, gather requirements, and create implementation plans

Plan mode helps you think before you act. It guides you through structured requirements gathering and codebase exploration, then produces an implementation plan that hands off to execution. Unlike full Feature Specs, Plan mode doesn't generate formal requirements/design/tasks documents - it's faster and more conversational while still providing structured output.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Plan mode | ✓ | ✓ | — | — |

## When to use Plan mode

- Complex tasks where you want to think through the approach before writing code
- Multi-file changes where understanding existing architecture matters
- Situations where you'd normally say "let me understand this first, then we'll implement"

For well-defined features that need formal requirements and design documents, use [Feature Specs](https://kiro.dev/docs/specs/feature-specs.md) instead. For quick, well-understood changes, skip planning and work directly with the default agent.

## How to invoke

    IDE
    CLI

    Choose **Plan** from the workflow options on the **"Let's build"** screen when starting a new session. To switch mid-session, click the agent name in the bottom bar of the chat input and select **Plan** from the agent picker.

    The agent name in the chat input shows which agent is active.

    Press `Shift+Tab` or run:

    ```bash
    > /plan
    ```

    Or start with an immediate prompt:

    ```bash
    > /plan Build a REST API for user authentication
    ```

    When active, you'll see `[plan]` in your prompt.

## Workflow

### 1. Requirements gathering

The planner asks structured questions to refine your initial idea:

```bash
[plan] > I want to build a todo app

I understand you want to build a todo app. Let me help you plan this.

[1]: What platform should this target?
a. Web Application
b. Mobile App
c. CLI Tool
d. Other

[2]: What's the primary use case?
a. Personal Task Management
b. Team Collaboration
c. Project Management
d. Other

(Answer with "1=a, 2=b" or provide your own answers)
```

You can answer individual questions, provide free-form responses, or skip questions entirely.

### 2. Research and analysis

The planner explores your codebase in read-only mode:

- Reads files and uses code intelligence to understand existing architecture
- Uses grep and glob to find relevant patterns
- Researches technologies via web search
- Adapts the plan to your existing conventions

### 3. Implementation plan

Creates a step-by-step plan with clear objectives:

```bash
**Implementation Plan - Todo CLI Command**

**Problem Statement:** Add todo management to existing application.

**Requirements:**
- CRUD operations for todos
- Local SQLite storage
- Priority and due date support

**Task Breakdown:**

Task 1: Create database schema and models
- Define Todo struct with required fields
- Create database migration
- Demo: Can create and query todos

Task 2: Implement command structure
- Add subcommand with add/list/complete operations
- Demo: CLI accepts todo commands

Task 3: Add advanced features
- Implement due dates and priority sorting
- Demo: Complete system with all features
```

### 4. Handoff to execution

Once you approve the plan, execution begins automatically:

1. Plan mode exits and the agent transitions to execution mode
2. The complete plan is passed to the execution agent as context
3. Implementation begins immediately with the approved plan as the guide

**ℹ️ Info:** In the CLI, automatic plan execution requires the v3 engine. In classic mode, you are prompted to confirm the handoff before execution begins. If a plan doesn't transfer to execution, make sure you explicitly approved it when asked.

## Read-only access

Plan mode intentionally cannot modify your project. This keeps the focus on thinking and planning:

| Operation | Available |
|-----------|:---------:|
| File reading | ✓ |
| Code intelligence (symbols, definitions) | ✓ |
| Search (grep, glob) | ✓ |
| Web search | ✓ |
| File writing | — |
| Command execution | — |
| MCP tools | — |

## Plan mode vs Specs

| | Plan mode | Feature Specs |
|---|---|---|
| **Output** | Conversational plan with task breakdown | Formal requirements.md, design.md, tasks.md |
| **Process** | Interactive Q&A → plan → handoff | Requirements → design → tasks with approval gates |
| **Speed** | Minutes | Longer (multi-phase with reviews) |
| **Best for** | Medium complexity, explore-then-build | High complexity, team collaboration, audit trail |
| **Artifacts** | Plan lives in conversation context | Persisted in `.kiro/specs/` |

## Tips

- Use Plan mode for tasks that need 15–60 minutes of implementation - long enough to benefit from planning, short enough that formal specs would be overkill
- Engage with the structured questions - better input produces better plans
- Let the planner explore your codebase - it finds patterns you might miss
- Review the plan before approving handoff - iterate until it matches your expectations
