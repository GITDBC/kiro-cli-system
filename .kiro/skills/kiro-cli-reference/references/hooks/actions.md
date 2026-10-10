> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Hook actions

> Learn about different hook actions and their use cases

Agent hooks support both an "agent prompt" and a "shell command" action. Once you have selected the specific event that [triggers](https://kiro.dev/docs/hooks/types.md) a hook, you can decide what action will be taken when that hook is triggered.

## Agent Prompt action

With this action, you can define a prompt that is sent to the agent each time the hook is triggered. The agent will respond and act on this prompt just like it does with a prompt provided in the chat panel.

In the case of the [Prompt Submit](https://kiro.dev/docs/hooks/types.md#prompt-submit) trigger, the prompt specified in the hook is _appended_ to the user prompt, and the combined prompt is sent to the agent.

## Shell Command action

With this action, you can define a shell command that is executed each time the hook is triggered.

    IDE
    CLI

    If the command returns an exit code of "0" indicating success, the *stdout* output of the command is added to the agent's context.

    If the command returns any other exit code, the *stderr* output of the command is sent to the agent, and the agent is notified that the hook returned an error. Additionally, in the case of the **Pre Tool Use** hook, the tool invocation is blocked, and for the **Prompt Submit** hook, the user prompt submission is blocked.

    An execution timeout can be specified. The default timeout is 60 seconds. Set to 0 to disable the timeout.

    Hooks receive hook event data in JSON format via STDIN. The output behavior depends on the exit code:

    - **Exit code 0**: Hook succeeded. STDOUT is added to context (SessionStart, UserPromptSubmit) or ignored (others).
    - **Exit code 2**: Block execution (PreToolUse, UserPromptSubmit, PreTaskExec only). STDERR is returned to the agent.
    - **Other exit codes**: Hook failed. STDERR is shown as warning to user and execution proceeds.

    Default timeout is 30 seconds (30,000ms). Configure with the `timeout_ms` field in the hook configuration.

    ### Caching

    Successful hook results can be cached based on `cache_ttl_seconds`:
    - `0`: No caching (default)
    - `> 0`: Cache successful results for specified seconds
    - AgentSpawn hooks are never cached

## Selecting an action type

You should use the **Agent Prompt** action when, in response to a trigger event, you want to use natural language to instruct the agent to perform some action based on context.

You should use the **Shell Command** action when you want to run a specific command or perform a deterministic set of actions that do not depend on the agent's current context.

**ℹ️ Info:** Agent Prompt actions consume credits as these actions trigger a new agent loop, whereas Shell Command actions do not. Shell Command actions are also generally faster as they are executed locally and do not use an LLM.
