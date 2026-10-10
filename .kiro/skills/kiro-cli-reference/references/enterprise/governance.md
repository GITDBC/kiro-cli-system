> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Governance

> Administrators can manage how developers using Kiro can access models and MCP tools.

As an administrator, you can control which models and MCP servers are available to your users. These governance controls are managed through the Kiro console under **Settings** > **Shared settings**.

## Model governance

By default, users can access any model supported by Kiro. You can restrict this by toggling on model access management and selecting an approved list of models. You can also set a default model that is automatically applied to all clients.

For details, see [Models](model).

## MCP governance

By default, users can use any MCP server in their Kiro client. You can either disable MCP entirely or specify an allow-list of vetted MCP servers through an MCP registry. These policies can be set at the organization level or overridden per account.

For details, see [MCP tools](mcp).

## API key governance

By default, users cannot generate API keys to use with Kiro CLI. You can enable users to generate API keys.

For details, see [API keys](api-keys).

## Web tools governance

By default, users can use the `web_search` and `web_fetch` tools to search the web and fetch content from URLs. You can disable web tools for all users in your account or organization.

For details, see [Web tools](web-tools).

## Cloud sessions governance

For organizations using IAM Identity Center, Cloud Sessions are off by default. Administrators enable them from **Settings > Kiro Settings** by toggling on **Cloud Sessions** in the AWS account where the Kiro profile is configured.

This setting was previously labeled **Kiro Web (Preview)**. Organizations that already enabled it stay enabled, so they do not need to take action. For organizations setting up Kiro for the first time, Cloud Sessions stay disabled until an administrator opts in.

Every Kiro Web session now runs as a cloud session. Until Cloud Sessions are enabled, users cannot start sessions in Kiro Web. The same toggle also controls cloud sessions in [Agent Focus Mode](https://kiro.dev/docs/ide/experimental/focus-mode.md) and the Kiro CLI with `kiro-cli --cloud`.

Cloud Sessions and API-key generation are independent controls. Enabling one does not enable the other. To control API-key generation, use the separate toggle described in [API keys](https://kiro.dev/docs/enterprise/governance/api-keys.md).

Some shared administrator settings, including MCP configuration, model availability, and Customer Managed Keys, do not apply to Kiro Web sessions. See [Kiro Web with AWS Identity Center](https://kiro.dev/docs/web/identity-center.md) for the enablement steps, requirements, and the full list of settings that don't carry over.
