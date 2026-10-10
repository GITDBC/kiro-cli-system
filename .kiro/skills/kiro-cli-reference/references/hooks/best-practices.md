> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Best practices

> Follow proven patterns for effective hook design and troubleshooting

Following these best practices will help you create reliable, efficient, and maintainable hooks that enhance your development workflow.

## Hook design

### Be specific and clear

- When using an agent prompt action, write detailed, unambiguous instructions for the agent
- Focus on one specific task per hook
- Use numbered steps for complex operations

### Test thoroughly

- Test hooks with some sample scenarios before deploying
- Verify hooks work with edge cases
- For file-related hooks, start with limited file patterns before expanding

### Monitor performance

- Ensure hooks don't slow down your workflow
- Consider the frequency of trigger events
- Optimize prompts for efficiency

## Security considerations

### Validate inputs

- Ensure hooks handle unexpected content gracefully
- Consider potential edge cases
- Test with malformed or unexpected input

### Limit scope

- For file-related hooks, target specific file types or directories when possible
- Use precise file patterns to avoid unnecessary executions
- Consider the impact of hooks on your entire codebase

    IDE
    CLI

    Use specific file glob patterns (e.g., `src/**/*.ts`) rather than broad patterns that match everything.

    Use precise `matcher` values in your hook configuration. Target specific tool names (e.g., `"fs_write"`) rather than matching all tools with `"*"` when possible.

### Review regularly

- Update hook logic as your project evolves
- Remove hooks that are no longer needed
- Refine prompts based on actual results

## Team collaboration

### Document hooks

- Maintain clear documentation of hook purposes
- Include examples of expected behavior
- Document any limitations or edge cases

### Share configurations

- Use consistent hooks across team members
- Store hook configurations in version control
- Create standard hooks for common team workflows

### Version control integration

- Consider hooks that integrate with your version control system
- Create hooks for code review workflows
- Use hooks to enforce team standards

## Performance tips

    IDE
    CLI

    - Use specific file patterns to reduce unnecessary hook executions
    - Keep agent prompt instructions concise to minimize response time
    - Set appropriate timeouts for shell command actions (default: 60 seconds)
    - Prefer shell command actions for deterministic tasks - they're faster and don't consume credits

    - Use specific tool matchers instead of wildcard (`"*"`) matching
    - Keep shell commands lightweight and fast-executing
    - Configure appropriate `timeout_ms` values (default: 30,000ms)
    - Use `cache_ttl_seconds` for hooks whose results don't change frequently
    - AgentSpawn hooks run once per session - use them for environment setup that only needs to happen once
