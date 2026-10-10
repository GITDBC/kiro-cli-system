> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Hook types

> Learn about different hook trigger types and their use cases

Agent hooks support various trigger types, each designed for specific automation scenarios. Understanding these types helps you choose the right approach for your workflow needs.

## Availability by surface

Not all hook triggers are available on every surface. Some triggers are specific to the IDE (task execution, session start) or CLI (agent spawn). The table below shows what's supported where.

| Trigger | IDE | CLI | Web |
|---------|:---:|:---:|:---:|
| [Prompt Submit](#prompt-submit) | ✓ | ✓ | — |
| [Agent Stop](#agent-stop) | ✓ | ✓ | — |
| [Session Start](#session-start-ide-only) | ✓ | — | — |
| [Agent Spawn](#agent-spawn-cli-only) | — | ✓ | — |
| [Pre Tool Use](#pre-tool-use) | ✓ | ✓ | — |
| [Post Tool Use](#post-tool-use) | ✓ | ✓ | — |
| [File Create](#file-create) | ✓ | — | — |
| [File Save](#file-save) | ✓ | — | — |
| [File Delete](#file-delete) | ✓ | — | — |
| [Pre Task Execution](#pre-task-execution-ide-only) | ✓ | — | — |
| [Post Task Execution](#post-task-execution-ide-only) | ✓ | — | — |
| [Legacy Manual Hook](#legacy-manual-hooks-ide-only) | Legacy only | — | — |

## Prompt Submit

Triggers when the user submits a prompt.

    IDE
    CLI

    When using the shell command action, the user prompt can be accessed via the `USER_PROMPT` environment variable.

    The hook receives the prompt in the hook event JSON via STDIN:

    ```json
    
    ```

    **Exit Code Behavior:**
    - **0**: Hook succeeded, STDOUT is added to agent's context
    - **Other**: Show STDERR warning to user

**Use Cases:**
- Provide additional context to the agent relevant to the prompt
- Block certain prompts based on their content
- Log all user prompts to a central location

## Agent Stop

Triggers when the agent has completed its turn and finished responding to the user.

    IDE
    CLI

    This is useful for running post-processing tasks like code compilation, testing, formatting, or cleanup after the agent's response.

    The hook receives the event via STDIN:

    ```json
    
    ```

    **Exit Code Behavior:**
    - **0**: Hook succeeded. If STDOUT contains a block decision (see below), the agent continues instead of stopping.
    - **Other**: Show STDERR warning to user.

    **Block Decision:** A stop hook can prevent the agent from stopping by returning JSON on STDOUT:

    ```json
    
    ```

    When a stop hook returns `"decision": "block"`, the `reason` is sent as a new user message to the agent, continuing the conversation. This enables a feedback loop where a script can evaluate the agent's work and nudge it to keep going - for example, checking if tests pass or verifying lint rules before allowing the agent to stop.

    
**ℹ️ Info:** Stop hooks do not use matchers since they don't relate to specific tools.

**Use Cases:**
- Compile code and report any failures to the agent
- Format or review any agent-generated code
- Review changes made by agent and provide additional instructions

## Session Start (IDE only)

Triggers when a new chat session starts in the IDE.

**ℹ️ Info:** In the CLI, this trigger is called [Agent Spawn](#agent-spawn-cli-only) and uses the hook event name `agentSpawn`.

**Use Cases:**
- Inject workspace-specific instructions into the agent's context
- Run environment checks (verify dependencies, validate credentials)
- Load project-specific configuration at session start

## Agent Spawn (CLI only)

Runs when the agent is first activated. No tool context is provided.

```json
{
  "hook_event_name": "agentSpawn",
  "cwd": "/current/working/directory",
  "session_id": "abc123-def456-789"
}
```

**Exit Code Behavior:**
- **0**: Hook succeeded, STDOUT is added to agent's context
- **Other**: Show STDERR warning to user

**Use Cases:**
- Set up environment context when a session starts
- Load project-specific configuration
- Initialize logging or auditing systems

## Pre Tool Use

Triggers when the agent is about to invoke a tool. Can validate and block tool usage.

    IDE
    CLI

    In the **Tool name** field, provide the names of the specific tools for which this hook should execute. You can specify multiple entries. The following built-in categories are supported:

    * **read** - all built-in file read tools
    * **write** - all built-in file write tools
    * **shell** - all built-in shell command-related tools
    * **web** - all built-in web tools
    * **spec** - all built-in spec tools
    * **\*** - all tools (built-in and MCP)

    You can also use prefix filters to target tools by source:

    * **@mcp** - all MCP tools
    * **@powers** - all Powers tools
    * **@builtin** - all built-in tools

    Prefixes starting with `@` are matched by regex, so you can use patterns like `@mcp.*sql.*` to match specific MCP tools by name.

    You can ask Kiro for the names of the available tools.

    Use the `matcher` field to specify which tools the hook applies to. You can use either canonical tool names or their aliases.

    **Matcher examples:**
    - `"fs_write"` or `"write"` - Match write tool
    - `"fs_read"` or `"read"` - Match read tool
    - `"execute_bash"` or `"shell"` - Match shell command execution
    - `"use_aws"` or `"aws"` - Match AWS CLI tool
    - `"@git"` - All tools from git MCP server
    - `"@git/status"` - Specific tool from git MCP server
    - `"*"` - All tools (built-in and MCP)
    - `"@builtin"` - All built-in tools only
    - No matcher - Applies to all tools

    
**ℹ️ Tool name aliases:** Hook matchers support both canonical names (`fs_read`, `fs_write`, `execute_bash`, `use_aws`) and their aliases (`read`, `write`, `shell`, `aws`). Use whichever you prefer.

    **Hook Event:**

    ```json
    
        ]
      }
    }
    ```

    **Exit Code Behavior:**
    - **0**: Allow tool execution
    - **2**: Block tool execution, return STDERR to LLM
    - **Other**: Show STDERR warning to user, allow tool execution

**Use Cases:**
- Block certain tool invocations
- Validate tool inputs before execution
- Provide additional instructions to the agent before it invokes a tool

## Post Tool Use

Triggers after the agent has invoked a tool, with access to tool results.

    IDE
    CLI

    For details on the **Tool name** field, refer to the [Pre Tool Use](#pre-tool-use) section above.

    For details on tool matching, refer to the [Pre Tool Use](#pre-tool-use) section above.

    **Hook Event:**

    ```json
    
        ]
      },
      "tool_response": 
    }
    ```

    **Exit Code Behavior:**
    - **0**: Hook succeeded
    - **Other**: Show STDERR warning to user. Tool already ran.

**Use Cases:**
- Log tool invocations for auditing purposes
- Format or review any updated files after a "write" tool call
- Provide additional instructions to the agent on top of the tool response

## File Create

Triggers when the agent creates new files matching specific patterns in your workspace.

**ℹ️ Info:** File triggers respond only to changes made by the agent. Manual editor changes do not trigger File Create, File Save, or File Delete hooks.

**Use Cases:**
- Generate boilerplate code for new components
- Add license headers to new files
- Set up test files when creating implementation files

## File Save

Triggers when the agent saves or modifies files matching specific patterns.

**Use Cases:**
- Run linting and formatting
- Update related files
- Generate documentation
- Run tests for changed files

## File Delete

Triggers when the agent deletes files matching specific patterns.

**Use Cases:**
- Clean up related files
- Update import references in other files
- Maintain project integrity

## Pre Task Execution (IDE only)

Triggers before a spec task begins execution, when its status changes to in_progress.

**Use Cases:**
- Run setup scripts or environment preparation before task execution
- Validate prerequisites are met before a task starts
- Log task start events for tracking

## Post Task Execution (IDE only)

Triggers after a spec task completes execution, when its status changes to completed.

**Use Cases:**
- Run tests after a task completes to verify correctness
- Run linting or formatting on changed files
- Generate documentation for completed work
- Notify external systems of task completion

## Legacy manual Hooks (IDE only)

Manual Hooks created in IDE 0.x continue to appear in the Agent Hooks panel with a **legacy** label. Enabled legacy manual Hooks remain runnable using the play button next to the Hook name or `Start Hook` in the Hook view.

Legacy manual Hooks don't have a v1 trigger equivalent, and you can't create a new Manual-trigger Hook. For a new on-demand workflow, create a [manually included Steering file](https://kiro.dev/docs/steering.md#manual-inclusion); it runs as a `/<filename>` slash command.

## MCP tool hooks

For MCP tools, the tool name includes the full namespaced format including the MCP server name:

```json
{
  "hook_event_name": "preToolUse",
  "cwd": "/current/working/directory",
  "session_id": "abc123-def456-789",
  "tool_name": "@postgres/query",
  "tool_input": {
    "sql": "SELECT * FROM orders LIMIT 10;"
  }
}
```

This applies to both Pre Tool Use and Post Tool Use hooks when targeting MCP server tools.
