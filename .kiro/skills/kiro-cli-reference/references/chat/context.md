> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Context management

> Managing conversation context in Kiro CLI

## Choosing the right context approach

Kiro offers three ways to provide context, each optimized for different use cases:

| Approach | Context Window Impact | Persistence | Best For |
|----------|----------------------|-------------|----------|
| Agent Resources | Always active (consumes tokens) | Persistent across sessions | Essential project files, standards, configs |
| Skills | On demand | Persistent across sessions | Large guides, reference docs, specialized knowledge |
| Session Context | Always active (consumes tokens) | Current session only | Temporary files, quick experiments |
| Knowledge Bases | Only when searched | Persistent across sessions | Large codebases, extensive documentation |

## Decision flowchart

1. Use this decision tree to choose the appropriate context approach:
   - Is your content larger than 10MB or contains thousands of files?
     - Yes → Use Knowledge Bases
     - No → Continue to step 2

2. Do you need this context in every conversation?
   - Yes → Use Agent Resources
   - No → Use Session Context

### Quick reference
- Essential project files (README, configs, standards) → Agent Resources
- Large codebases or documentation sets → Knowledge Bases
- Temporary files for current task → Session Context

## Understanding context window impact

Kiro automatically includes your working directory and operating system as context in every session. You don't need to configure this.

- Context files and agent resources consume tokens from your context window on every request, whether referenced or not. 

``` bash
> /context show

Agent 
  - .kiro/steering/**/*.md  <project-root>/.kiro/steering/product.md
<project-root>/.kiro/steering/structure.md
<project-root>/.kiro/steering/tech.md
<project-root>/.kiro/steering/testing.md
  - README.md <project-root>/snake/README.md
  - ~/.kiro/steering/**/*.md (no matches)

Session (temporary)
  <none>

5 matched files in use
- <project-root>/.kiro/steering/testing.md (0.1% of context window)
- <project-root>/snake/.kiro/steering/tech.md (0.1% of context window)
- <project-root>/snake/README.md (0.1% of context window)
- <project-root>/snake/.kiro/steering/structure.md (0.2% of context window)
- <project-root>/snake/.kiro/steering/product.md (0.1% of context window)

Context files total: 0.5% of context window
```

- The output shows:
  - **Agent**: Persistent context from your agent's resources field
  - **Session**: Temporary context added during the current session

- Context files are limited to 75% of your model's context window. Files exceeding this limit are automatically dropped.

- Knowledge bases don't consume context window space until searched, making them ideal for large reference materials. For more information, see Knowledge base context (for large datasets).

## Managing context

Context files contain information you want Kiro to consider during your conversations. These can include project requirements, coding standards, development rules, or any other information that helps Kiro provide more relevant responses.

### Configuring persistent context with agent resources

The recommended way to configure context is through the resources field in your agent configuration file. This creates persistent context that is available every time you use the agent.

Add file paths or glob patterns to the resources array in your agent config:

```json
{
  "name": "my-agent",
  "description": "My development agent",
  "resources": [
    "file://README.md",
    "file://docs/**/*.md",
    "file://src/config.py"
  ]
}
```

Resources use URI schemes to specify the type:
- `file://` — Files loaded directly into context at startup
- `skill://` — Skills with metadata loaded at startup, full content loaded on demand
- `knowledgeBase` — Indexed content searched on demand (configured as objects, not URI strings)

These files will be automatically available in all chat sessions using this agent. For more details on resource types, see the [Agent Configuration Reference](https://kiro.dev/docs/custom-agents/configuration-reference.md#resources-field).

### Adding temporary session context

You can temporarily add files to your current chat session using the /context add command. These additions are only available for the current session and will not persist when you start a new chat session.

```bash 
> /context add README.md
Added 1 path(s) to context.
```

**Note**: Context modifications via slash command is temporary.

You can also add multiple files at once using glob patterns:

``` bash
> /context add docs/*.md
Added 3 path(s) to context.

```

To make context changes permanent, add the files to your agent's resources field instead. For more information, see Configuring persistent context with agent resources.

### Knowledge base context (for large datasets)

For large codebases, documentation sets, or reference materials that would exceed context window limits, use knowledge bases. Knowledge bases provide semantic search capabilities without consuming context window space until searched.

Enable knowledge bases:

kiro-cli settings chat.enableKnowledge true

Add content to a knowledge base:

kiro-cli chat
> /knowledge add /path/to/large-codebase --include "**/*.py" --exclude "node_modules/**"

Knowledge bases are searched on-demand by Kiro when relevant information is needed, making them ideal for large reference materials.

### Conversation compaction

Compaction summarizes older messages while retaining recent ones, freeing up context window space.

- **Manual**: Run [`/compact`](https://kiro.dev/docs/reference/slash-commands.md#compact)
- **Automatic**: Triggers when context window overflows

#### Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `compaction.excludeMessages` | 2 | Minimum message pairs to retain |
| `compaction.excludeContextWindowPercent` | 2 | Minimum % of context window to retain |

Both settings are evaluated, and the more conservative (larger) value wins.

Compaction will create a new session. You can resume the original via `/chat resume`.

**ℹ️ Context % updates after your next prompt:** After running `/compact`, the context usage percentage shown in the status bar may not change immediately. The accurate usage is only calculated when you send your next message, because the backend determines actual token counts during request processing. Send a prompt after compacting to see the updated percentage.

### Viewing context usage

To view your current context, use the /context show command:

```bash
> /context show

Current context window (5.9% used)
|||████████████████████████████████████████████████████████████████ 5.9%

█ Context files 0.9%
█ Tools 0.5%
█ Kiro responses 0.7%
█ Your prompts 3.8%
```

The output shows glob patterns for context entries, making it easier to identify and remove them.

### Removing context

To remove files from your current session context:

```bash
> /context remove src/temp-file.py
Removed 1 path(s) from context.
```

To clear all session context, use the /context clear command:

```bash 
> /context clear
Cleared context
Note: Context modifications via slash command is temporary.
```

Note: You cannot remove agent-defined context using /context commands. To permanently remove context, edit your agent's resources field.

## Context management actions

Here are some common reasons for actively managing your context window:

1. If you find yourself repeatedly adding the same context files using `/context add` commands, consider moving them to your agent's resources field for persistence:

```bash
# Instead of running these commands every session:
> /context add README.md
> /context add docs/*.md

# Add them to your agent config once:
{
  "resources": [
    "file://README.md",
    "file://docs/**/*.md"
  ]
}
```

You can configure a default agent that includes your preferred context files. This ensures your context is automatically available in new chat sessions without needing to specify the agent each time.
```bash  
   >kiro-cli settings chat.defaultAgent my-project-agent
```

2. If you have large context files (consume significant part of context window) consider using knowledge base instead of including those files as is. Use cases to consider knowledge:
   - You have large codebases or documentation sets
   - You need semantic search across extensive materials
   - You want to avoid constant context window consumption
   - Example: Instead of adding a large codebase as context files:

```bash
# This would consume too many tokens:
> /context add src/**/*.py

# Use knowledge base instead:
> /knowledge add src/ --include "**/*.py" --exclude "__pycache__/**"
```

## Best practices

### Context file organization
1. Keep context files focused and relevant to avoid token limits
2. Use descriptive filenames that indicate their purpose
3. Organize rules and documentation in logical directory structures
4. Consider file size - very large files may consume significant tokens

### Performance considerations
1. Monitor token usage with /context show to stay within limits
2. Use specific glob patterns rather than overly broad ones
3. Remove unused context files from agent configurations
4. Consider splitting large context files into smaller, focused files
5. Use knowledge bases for large datasets to avoid context window consumption

### Security considerations
1. Avoid including sensitive information in context files
2. Use `.gitignore` to prevent accidental commits of sensitive context
3. Review context files regularly to ensure they don't contain outdated information
4. Be mindful of what information is shared when using context in conversations

## Related documentation

- [Slash Commands](https://kiro.dev/docs/reference/slash-commands.md) - In-chat context commands
- [CLI Commands](https://kiro.dev/docs/reference/cli-commands.md) - Terminal context commands
- [Interactive Chat Mode](https://kiro.dev/docs/cli/chat.md) - Using context in chat
