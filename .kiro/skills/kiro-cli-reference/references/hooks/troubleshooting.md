> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Troubleshooting hooks

> Common issues and solutions for debugging hook issues

## Common issues

### Hook not triggering

    IDE
    CLI

    - For file-related hooks, verify the file pattern matches your target files
    - Check that the hook is enabled (look for the eye icon in the Agent Hooks panel)
    - Ensure the event type is correct for what you're trying to automate
    - For Pre/Post Tool Use hooks, verify the tool name matches the tool being invoked

    - Verify the hook is correctly defined in the agent configuration file
    - Check that the `hook_event_name` matches the expected event
    - For Pre/Post Tool Use hooks, verify the `matcher` field targets the correct tools
    - Ensure the hook script is executable and has correct permissions
    - Check that the hook script path is correct relative to the working directory

### Unexpected hook behavior

- Review the hook instructions for clarity
- Check for conflicting hooks that may interfere with each other
- Verify file patterns or tool matchers aren't too broad
- Test the hook with a minimal case to isolate the issue

### Performance issues

    IDE
    CLI

    - For file-related hooks, limit hook scope with more specific file patterns
    - For hooks with an agent prompt action, simplify any complex hook instructions
    - For hooks with a shell command action, ensure that the command completes quickly
    - Reduce the frequency of triggering events
    - Check that your timeout setting is appropriate (default: 60 seconds)

    - Ensure shell commands complete within the configured `timeout_ms` (default: 30,000ms)
    - Use `cache_ttl_seconds` to avoid re-running hooks that produce the same result
    - Narrow tool matchers to reduce unnecessary hook executions
    - Consider whether the hook needs to run on every invocation or can be scoped more tightly

### Shell command errors

- Verify the command works when run manually in a terminal
- Check that all required environment variables are available
- Ensure any external tools or dependencies are installed
- Review STDERR output for error messages

    IDE
    CLI

    - Check the Kiro output panel for hook execution logs

    - Exit code 2 on a PreToolUse hook blocks tool execution - verify this is intentional
    - Non-zero exit codes (other than 2) show STDERR as a warning but don't block execution
    - Check that JSON parsing of STDIN hook events is working correctly in your script
