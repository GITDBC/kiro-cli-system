> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Hook management

> Learn how to organize, edit, and maintain your hooks

Effective hook management ensures your automation workflows remain organized, maintainable, and efficient as your project grows.

## Managing your hooks

    IDE
    CLI

    Access all your hooks through the Agent Hooks section in the Kiro panel.

    ### Creating hooks

    Click the **+** button in the Agent Hooks section. You'll see two options:

    - **Manually create a steering file** - Author a markdown steering file invoked as a `/<filename>` slash command
    - **Ask Kiro to create a hook** - Pre-fills a prompt in chat where you describe the hook in natural language and converse with the agent to configure it

    When you select **Ask Kiro to create a hook**, the chat input is pre-filled with a prompt asking Kiro for an overview of hook capabilities. From there, you describe what you want and Kiro generates the hook configuration through conversation.

    ### Enable/disable hooks

    Toggle hooks on/off without deleting them:

    - **Quick toggle**: Click the `eye icon` next to any hook in the Agent Hooks panel
    - **From hook view**: Select a hook and use the `Hook Enabled` switch in the top-right corner

    ### Edit existing hooks

    Hooks evolve with your workflow. Update them anytime by selecting your hook in the Agent Hooks panel and modifying settings. Updates apply immediately.

    ### Delete hooks

    Select the hook in the Agent Hooks panel, click `Delete Hook` located at the bottom view, then click `delete`. This action cannot be undone.

    ### Run legacy manual hooks

    Manual Hooks created in IDE 0.x continue to appear with a **legacy** label. You can still run an enabled legacy manual Hook using:

    - **Quick run**: Click the `play button (▷)` next to the Hook name in the Agent Hooks panel
    - **From Hook view**: Select the Hook and click `Start Hook` in the top-right corner

    To create a new on-demand workflow, create a [manually included Steering file](https://kiro.dev/docs/steering.md#manual-inclusion) instead.

    Hooks are managed through the agent configuration file. You can add, modify, or remove hooks by editing the hooks section of your agent configuration.

    ### Enable/disable hooks

    Remove or comment out the hook definition in the configuration file to disable it. Re-add it to enable.

    ### Edit existing hooks

    Modify the hook definition in the agent configuration file. Changes take effect the next time the agent is activated.

    ### Timeout configuration

    Set the `timeout_ms` field to control how long a hook can run before timing out. The default is 30 seconds (30,000ms).

    ### Caching

    Use the `cache_ttl_seconds` field to cache successful hook results:
    - `0`: No caching (default)
    - `> 0`: Cache successful results for the specified number of seconds

    AgentSpawn hooks are never cached regardless of this setting.

    For the complete configuration syntax, see the [Agent Configuration Reference](https://kiro.dev/docs/custom-agents/configuration-reference.md#hooks-field).
