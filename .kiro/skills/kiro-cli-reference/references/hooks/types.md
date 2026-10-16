> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Hook types

> Learn about different hook trigger types and their use cases

Agent hooks support various trigger types, each designed for specific automation scenarios. Understanding these types helps you choose the right approach for your workflow needs.

## Availability by surface

This page describes standalone Hook definitions stored in `.kiro/hooks/*.json`. Inline profile Hooks have separate current and legacy forms; see the [agent configuration reference](https://kiro.dev/docs/custom-agents/configuration-reference.md#hooks-field).

File and task triggers are available in the IDE and CLI V3. Web can store Hook configuration for later local use, but Web sessions do not run these triggers. The table below shows what's supported where.

| Trigger | IDE | CLI | Web |
|---------|:---:|:---:|:---:|
| [Prompt Submit](#prompt-submit) | ✓ | ✓ | — |
| [Agent Stop](#agent-stop) | ✓ | ✓ | — |
| [Session Start](#session-start) | ✓ | V3 | — |
| [Agent Spawn](#agent-spawn-cli-2x-and-v3-alias) | — | 2.x / V3 alias | — |
| [Session End](#session-end-cli-v3-only) | — | V3 | — |
| [Pre Tool Use](#pre-tool-use) | ✓ | ✓ | — |
| [Post Tool Use](#post-tool-use) | ✓ | ✓ | — |
| [File Create](#file-create) | ✓ | V3 | — |
| [File Save](#file-save) | ✓ | V3 | — |
| [File Delete](#file-delete) | ✓ | V3 | — |
| [Pre Task Execution](#pre-task-execution) | ✓ | V3 | — |
| [Post Task Execution](#post-task-execution) | ✓ | V3 | — |
| [Manual](#manual-cli-v3) | — | Listed in V3 | — |
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
    - **Other (including 2)**: The prompt is still sent. CLI V3 forwards the Hook output and exit code to the agent as context; it does not reject the prompt.

    
**ℹ️ Info:** CLI Prompt Submit Hooks cannot block a prompt. To block an action in the CLI, use a `PreToolUse` Hook.

**Use Cases:**
- Provide additional context to the agent relevant to the prompt
- Block certain prompts based on their content (IDE only; CLI Prompt Submit Hooks cannot block)
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
    - **0** without a continue decision: Hook succeeded and the response remains finished.
    - **0** with a `decision: "block"` response: Start another agent turn using the supplied reason.
    - **1**: Start another agent turn. If the Hook does not supply a reason, Kiro uses a default continue instruction.
    - **Other**: Leave the response finished; Hook output is not forwarded.

    Return a continue decision as JSON on STDOUT:

    ```json
    
    ```

    The name `"block"` is retained for compatibility, but for `Stop` it asks the agent to keep working; it does not use the exit-code-2 blocking behavior of pre-event Hooks.

    
**ℹ️ Info:** Stop Hooks do not use matchers.

**Use Cases:**
- Compile code and report any failures to the agent
- Format or review any agent-generated code
- Review changes made by agent and provide additional instructions

## Session Start

Triggers when a new chat session starts in the IDE or CLI V3.

**ℹ️ Info:** CLI 2.x embedded Hooks used `agentSpawn`. CLI V3 uses `SessionStart` as the canonical trigger and accepts `AgentSpawn` and `agentSpawn` as compatibility spellings. See [Hooks migration](https://kiro.dev/docs/cli/v3/hooks-migration.md) for the complete mapping.

**Use Cases:**
- Inject workspace-specific instructions into the agent's context
- Run environment checks (verify dependencies, validate credentials)
- Load project-specific configuration at session start

## Agent Spawn (CLI 2.x and V3 alias)

CLI 2.x used `agentSpawn` when the agent was first activated. CLI V3 uses `SessionStart` as the canonical trigger but accepts `AgentSpawn` and `agentSpawn` for compatibility. The event provides no tool context.

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

## Session End (CLI V3 only)

The `SessionEnd` trigger fires when a CLI V3 session is torn down.

## Pre Tool Use

Triggers when the agent is about to invoke a tool. Can validate and block tool usage.

    IDE
    CLI

    In the **Tool name pattern** field, provide an exact tool ID, a built-in category, a source selector, or a regular expression. You can specify multiple entries. The following built-in categories are supported:

    * **read** - all built-in file read tools
    * **write** - all built-in file write tools
    * **shell** - all built-in shell command-related tools
    * **web** - all built-in web tools
    * **spec** - all built-in spec tools

    You can also use source selectors:

    * **@mcp** - all MCP tools
    * **@powers** - all Powers tools
    * **@builtin** - all built-in tools
    * **`@<server>`** - all tools from one MCP server, for example `@postgres`
    * **`@<server>/<tool>`** - one tool from one MCP server, for example `@postgres/query`

    The editor checks each entry as a regular expression matched against tool IDs. A plain name such as `read` can therefore match any tool ID containing that text. Leave the field blank to match every tool.

    Hook JSON files also accept wildcard patterns. Use `*` to match any number of characters and `?` to match a single character. Edit the Hook JSON file directly to use these patterns because the IDE editor rejects them as invalid regular expressions.

    You can ask Kiro for the names of the available tools.

    The `matcher` field accepts a tool selector or a regular expression. Built-in tool IDs include `read_file`, `execute_bash` on macOS and Linux, and `execute_pwsh` on Windows. MCP display names use `@server/tool`, but Hook events report lowercased, sanitized IDs in the form `mcp_<server>_<tool>`.

    A matcher without regex metacharacters (`\ ^ $ ( ) [ ]  | +`) is a selector. It matches a tool whose ID or tags equal the selector; `*` and `?` act as wildcards against the ID and tags. Tags include the categories `read`, `write`, `shell`, `web`, `subagent`, `spec`, and `context`; the source selectors `@builtin`, `@mcp`, and `@powers`; and `@<server>` and `@<server>/<tool>` for MCP tools. `execute_bash` and `execute_pwsh` match each other, so one selector covers both operating systems. A selector is also compiled as an unanchored regex, so `read` matches any ID containing `read`.

    A matcher that contains regex metacharacters is evaluated only as an unanchored regular expression against the tool ID. Anchor it (`^...$`) to match exactly.

    **Matcher examples:**
    - `"shell"` - Match every shell tool by tag (`execute_bash` or `execute_pwsh`)
    - `"@mcp"` - Match every MCP tool
    - `"@git/git_status"` - Match one MCP tool by server and tool name
    - `"mcp_git_*"` - Match internal tool IDs from the git MCP server by wildcard
    - `"^(fs_write|fs_append|str_replace|delete_file)$"` - Match the built-in write family by anchored regex
    - `"^mcp_git_status$"` - Match one exact MCP tool ID by anchored regex
    - No matcher - Apply to all tools

    
**ℹ️ Match V3 tool IDs or tags:** V3 does not expand CLI 2.x tool names. `fs_read` and `grep` are not V3 IDs or tags; use the category tag (`read`) or the V3 ID (`read_file`, `grep_search`). The [Hooks migration](https://kiro.dev/docs/cli/v3/hooks-migration.md#migrate-tool-matchers) page lists the group each CLI 2.x name maps to.

    **Hook Event:**

    ```json
    
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
    ,
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

## Pre Task Execution

Triggers before a spec task begins execution.

**Use Cases:**
- Run setup scripts or environment preparation before task execution
- Validate prerequisites are met before a task starts
- Log task start events for tracking

## Post Task Execution

Triggers after a spec task completes execution.

**Use Cases:**
- Run tests after a task completes to verify correctness
- Run linting or formatting on changed files
- Generate documentation for completed work
- Notify external systems of task completion

## Manual (CLI V3)

CLI V3 recognizes and lists `Manual` Hook definitions, but `/hooks` doesn't provide an action to invoke them.

## Legacy manual Hooks (IDE only)

Manual Hooks created in IDE 0.x continue to appear in the Agent Hooks panel with a **legacy** label. Enabled legacy manual Hooks remain runnable using the play button next to the Hook name or `Start Hook` in the Hook view.

IDE 0.x `userTriggered` Hooks don't have a v1 IDE trigger equivalent, and you can't create a new Manual-trigger Hook in the IDE. For a new IDE on-demand workflow, create a [manually included Steering file](https://kiro.dev/docs/steering.md#manual-inclusion); it runs as a `/<filename>` slash command.

## MCP tool hooks

For MCP tools, V3 Hook events use the sanitized internal tool ID `mcp_<server>_<tool>`, not the `@server/tool` display name:

```json
{
  "hook_event_name": "PreToolUse",
  "cwd": "/current/working/directory",
  "session_id": "abc123-def456-789",
  "tool_name": "mcp_postgres_query",
  "tool_input": {
    "sql": "SELECT * FROM orders LIMIT 10;"
  }
}
```

This applies to both Pre Tool Use and Post Tool Use Hooks when targeting MCP server tools. In the Hook's `matcher`, use either the `@<server>` or `@<server>/<tool>` selector or a regex against the internal ID.
