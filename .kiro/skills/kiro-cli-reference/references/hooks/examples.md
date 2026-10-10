> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Hook examples

> Practical examples and templates you can use in your projects

These examples demonstrate real-world hook implementations that you can adapt for your own projects. Each example includes the trigger type, target patterns, and complete hook instructions.

## Security pre-commit scanner

This hook helps prevent security leaks by scanning files before they're committed.

**Trigger Type:** Agent Stop

**Agent Prompt:**
```text
Review changed files for potential security issues:
1. Look for API keys, tokens, or credentials in source code
2. Check for private keys or sensitive credentials
3. Scan for encryption keys or certificates
4. Identify authentication tokens or session IDs
5. Flag passwords or secrets in configuration files
6. Detect IP addresses containing sensitive data
7. Find hardcoded internal URLs
8. Spot database connection credentials

For each issue found:
1. Highlight the specific security risk
2. Suggest a secure alternative approach
3. Recommend security best practices
```

## Centralized user prompt logging

This hook logs all user prompts to a centralized logging system for analysis and auditing.

**Trigger Type:** Prompt Submit

    IDE
    CLI

    **Shell Command:**
    ```bash
    # Log user prompt to Grafana Loki
    curl -H "Content-Type: application/json" -XPOST \
         "http://loghost/loki/api/v1/push" --data-raw \
         "\"  },
            'values': [ [\"$(date +%s%N)\", \"$\"] ]
          }]}"
    ```

    The `USER_PROMPT` environment variable contains the submitted prompt text.

    **Shell Command:**
    ```bash
    #!/bin/bash
    # Read hook event from STDIN (contains "prompt" field)
    HOOK_EVENT=$(cat)
    PROMPT=$(echo "$HOOK_EVENT" | jq -r '.prompt')

    # Log to Grafana Loki
    curl -H "Content-Type: application/json" -XPOST \
         "http://loghost/loki/api/v1/push" --data-raw \
         "\"  },
            'values': [ [\"$(date +%s%N)\", \"$\"] ]
          }]}"
    ```

    In CLI, hook event data is received via STDIN in JSON format. Use `jq` or similar tools to extract fields.

## Internationalization helper

This hook ensures that when you update text in your primary language file, translations are kept in sync.

**Trigger Type:** File Save  
**Target:** `src/locales/en/*.json`

**Agent Prompt:**
```text
When an English locale file is updated:
1. Identify which string keys were added or modified
2. Check all other language files for these keys
3. For missing keys, add them with a "NEEDS_TRANSLATION" marker
4. For modified keys, mark them as "NEEDS_REVIEW"
5. Generate a summary of changes needed across all languages
```

## Test coverage maintainer

This hook ensures test coverage remains high as code evolves.

**Trigger Type:** File Save  
**Target:** `src/**/*.`

**Agent Prompt:**
```text
When a source file is modified:
1. Identify new or modified functions and methods
2. Check if corresponding tests exist and cover the changes
3. If coverage is missing, generate test cases for the new code
4. Run the tests to verify they pass
5. Update coverage reports
```

## Integration with MCP

Agent hooks can be enhanced with Model Context Protocol (MCP) capabilities to extend their functionality:

1. **Access to External Tools**: Hooks can use MCP servers to access specialized tools and APIs
2. **Enhanced Context**: MCP provides additional context for more intelligent hook actions
3. **Domain-Specific Knowledge**: Specialized MCP servers can provide domain expertise

To use MCP with hooks:
1. [Configure MCP servers](https://kiro.dev/docs/mcp/configuration.md)
2. Reference MCP tools in your hook instructions
3. Set appropriate auto-approval settings for frequently used tools

**Use Cases:**
- Make sure that your Figma design system is respected
- Update ticket status after a task is done
- Sync a database from sample files within the project folder

### Example: validate Figma design

This hook monitors HTML and CSS files and validates that they follow a Figma design using the Figma MCP.

**Trigger Type:** File Save  
**Target:** `*.css` `*.html`

**Agent Prompt:**
```text
Use the Figma MCP to analyze the updated html or css files and check that they follow
established design patterns in the figma design. Verify elements like hero sections,
feature highlights, navigation elements, colors, and button placements align.
```
