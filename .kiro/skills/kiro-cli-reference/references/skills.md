> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Agent Skills

> Extend Kiro with portable instruction packages using the open Agent Skills standard

## What are skills?

Skills are portable instruction packages that follow the open [Agent Skills](https://agentskills.io) standard. They bundle instructions, scripts, and templates into reusable packages that Kiro can activate when relevant to your task.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Skill activation | ✓ | ✓ | ✓ | ✓ |
| Workspace skills (`.kiro/skills/`) | ✓ | ✓ | ✓ | ✓ |
| Global skills (`~/.kiro/skills/`) | ✓ | ✓ | — | — |
| Upload local skills to [cloud configuration](https://kiro.dev/docs/web/cloud-configuration.md) | Opt-in | Opt-in | ✓ | — |

Kiro supports the Agent Skills standard, so you can import skills from the community or other compatible AI tools, and share your own skills across the ecosystem.

## How skills work

AI agents are increasingly capable, but they often lack the specific context needed for real work. Without knowledge of your team's deployment process, your company's code review standards, or your project's data analysis pipeline, agents guess and iterate - just like you would when learning something new.

Loading all this context upfront isn't practical either. Too much information overwhelms the agent, slowing responses and reducing quality.

Skills solve this with progressive disclosure:

1. **Discovery** - At startup, Kiro loads only the name and description of each skill
2. **Activation** - When your request matches a skill's description, Kiro loads the full instructions
3. **Execution** - Kiro follows the instructions, loading scripts or reference files only as needed

This keeps context focused while giving Kiro access to extensive specialized knowledge on demand.

## Using skills

Skills can activate in two ways:

- **Automatically** - Kiro matches your request against skill descriptions and loads the relevant skill
- **As slash commands** - Type `/` followed by the skill name to invoke it directly

    IDE
    CLI
    Web

    Kiro automatically activates skills when your request matches a skill's description. You can also invoke a skill directly by typing `/` in the chat input to see available skills as slash commands. Selecting a slash command loads the full skill instructions, giving you explicit control over when a skill activates.

    You can add text after the skill name, for example `/explain-file src/api/client.ts`, and it is passed along to the agent as extra context. `$ARGUMENTS` and `$` placeholder substitution into the skill body is currently CLI-only; see [Passing arguments to a skill](#passing-arguments-to-a-skill).

    View and manage skills in the **Agent Steering & Skills** section in the Kiro panel.

    When you start a chat session, Kiro discovers available skills by reading their names and descriptions. Type `/` followed by the skill name to invoke it directly. For example, a skill named `pr-review` becomes the `/pr-review` slash command.

    ```text
    > Review this PR for security issues

    I'll review the PR using the security checklist...
    ```

    ```text
    > /pr-review

    I'll review the PR using the security checklist...
    ```

    ### Passing arguments to a skill

    If the skill body contains `$ARGUMENTS` or `$` placeholders, text after the slash command is substituted into them. If the skill has no placeholders, any trailing text is still passed along as extra context to the agent:

    ```text
    > /pr-review focus on the authentication changes

    I'll review the PR using the security checklist, with extra attention to the authentication changes.
    ```

    To see what skills are available in your current session, use the `/context show` command or ask Kiro directly:

    ```bash
    > /context show
    ```

    Kiro Web loads project Skills from `.kiro/skills/` in your repository. Personal Skills are available from **Settings > Skills**. The agent activates a Skill when your request matches its description.

## Skill scope

Skills can be created with a workspace scope or a global scope.

| Location | Scope | Use case |
|----------|-------|----------|
| `.kiro/skills/` | Workspace | Project-specific workflows, team conventions |
| `~/.kiro/skills/` | Global | Personal workflows across all projects |

When skills share the same name, workspace skills take priority over global skills. This allows you to define global skills that generally apply to all your workspaces, while preserving the ability to override them for specific projects.

### Custom agents and skills

**ℹ️ Info:** By default, the agent automatically loads skills from both workspace and global locations. [Custom agents](https://kiro.dev/docs/custom-agents.md) don't load skills by default - you need to explicitly add them to the agent's `resources` field using the `skill://` URI scheme.


```json
{
  "name": "my-agent",
  "resources": [
    "skill://.kiro/skills/*/SKILL.md",
    "skill://~/.kiro/skills/*/SKILL.md"
  ]
}
```

The `skill://` URI scheme supports specific paths, glob patterns, and home directory expansion.

## Importing skills

    IDE
    CLI
    Web

    1. Open **Agent Steering & Skills** section in the Kiro panel
    2. Click **+** and select **Import a skill**
    3. Choose your source:
       - **GitHub** - Import from a public repository URL. You can paste a URL pointing to the skill folder or directly to the `SKILL.md` file. The URL must point to a subdirectory in the repository, not the repository root.
       - **Local folder** - Import from your filesystem

    Imported skills are copied to your skills directory and work immediately.

    To add a skill to CLI, place the skill folder in one of the skill locations:

    - **Workspace**: Copy the skill folder into `.kiro/skills/` in your project
    - **Global**: Copy the skill folder into `~/.kiro/skills/`

    Skills are discovered automatically when you start a new chat session.

    In Kiro Web, open **Settings > Skills** and choose **Add skill**. Create a Skill manually from a `SKILL.md` template, or upload a zip archive. Uploading a zip with the exact name of an existing Skill updates it to match the archive. From the Skills list you can also edit a Skill's content, download it as a zip, or delete it.

## Creating a skill

A skill is a folder containing a `SKILL.md` file:

```text
my-skill/
├── SKILL.md           # Required
├── scripts/           # Optional executable code
├── references/        # Optional documentation
└── assets/            # Optional templates
```

### SKILL.md format

The file starts with YAML frontmatter followed by markdown instructions:

```markdown
---
name: pr-review
description: Review pull requests for code quality, security issues, and test coverage. Use when reviewing PRs or preparing code for review.
---

## Review checklist

When reviewing a pull request:

1. Check for vulnerabilities, injection risks, exposed secrets
2. Verify edge cases and failure modes are handled
3. Confirm new code has appropriate tests
4. Ensure variables and functions have clear names

## Common issues to flag

- Hardcoded credentials or API keys
- Missing input validation
- Unhandled promise rejections
- Console.log statements left in production code
```

### Frontmatter fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Must match folder name. Lowercase letters, numbers, and hyphens only (max 64 chars). |
| `description` | Yes | When to use this skill. Kiro matches this against your requests (max 1024 chars). |
| `license` | No | License name or reference to a bundled license file. |
| `compatibility` | No | Environment requirements (e.g., required tools, network access). |
| `metadata` | No | Additional key-value data like author or version. |

See the [full specification](https://agentskills.io/specification) for detailed field constraints.

### Reference files

For extensive documentation, use a `references/` folder:

```text
aws-deployment/
├── SKILL.md
└── references/
    ├── ecs-guide.md
    └── troubleshooting.md
```

Reference the files in your SKILL.md:

```markdown
For ECS deployments, follow the guide in `references/ecs-guide.md`.
```

Kiro loads reference files only when the instructions direct it to.

## Example

A CDK deployment skill:

```text
cdk-deploy/
├── SKILL.md
└── references/
    └── stack-patterns.md
```

**SKILL.md:**
```markdown
---
name: cdk-deploy
description: Deploy AWS CDK stacks with best practices. Use when deploying infrastructure, running cdk deploy, or troubleshooting CDK issues.
---

## Deployment workflow

1. Run `cdk synth` to validate templates before deploying
2. Use `cdk diff` to preview what will change
3. Run `cdk deploy` and review IAM changes

## Pre-deployment checks

- Verify AWS credentials are configured for the target account
- Check that the CDK version matches the project's requirements
- Review `references/stack-patterns.md` for environment-specific patterns

## Rollback procedure

If deployment fails:
1. Check CloudFormation console for the specific error
2. Run `cdk destroy` only if the stack is in a failed state
3. Fix the issue and redeploy
```

Usage:
```bash
> Deploy my CDK stack to staging

I'll follow the deployment workflow. First, let me synthesize the templates...
```

## How skills differ from steering and powers

**Skills** are portable packages following an open standard. They load on-demand and can include scripts. Use for reusable workflows you want to share or import from others.

**[Steering](https://kiro.dev/docs/steering.md)** is Kiro-specific context that shapes agent behavior. It supports `always`, `auto`, `fileMatch`, and `manual` modes. Use for project standards and conventions.

**[Powers](https://kiro.dev/docs/powers.md)** bundle MCP tools with knowledge and workflows. They activate dynamically based on context. Use for integrations where you need both tools and guidance.

**💡 Tip:** For MCP integrations, [powers](https://kiro.dev/docs/powers.md) are usually a better fit - they bundle tools with built-in guidance and activate automatically based on what you're working on.

## Best practices

**Write precise descriptions** - The description determines when Kiro activates the skill. Include specific keywords and actions that match how you'd phrase requests:
- Good: `Review pull requests for security vulnerabilities and test coverage. Use when reviewing PRs or preparing code for review.`
- Vague: `Helps with code review`

**Keep SKILL.md focused** - Put detailed reference material in `references/` files. Kiro loads the full SKILL.md on activation, so keep it actionable.

**Use scripts for deterministic tasks** - Validation, file generation, and API calls work better as scripts than LLM-generated code.

**Choose the right scope** - Global for personal workflows you use everywhere (your review checklist). Workspace for team procedures and project-specific conventions.

**Version control workspace skills** - Commit `.kiro/skills/` to your repository so the team shares the same workflows.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Skill not activating | Make the description more specific with keywords matching your request |
| Slash command not found | Verify the skill folder name matches what you're typing. Skills must have valid SKILL.md with frontmatter |
| Skill not found | Verify SKILL.md exists with valid frontmatter in the correct location |
| Custom agent missing skills | Add `skill://` URIs to the agent's `resources` field |
| Wrong skill activating | Differentiate descriptions with more specific keywords |

## Related documentation

- [Steering](https://kiro.dev/docs/steering.md) - Project-specific context and standards
- [Powers](https://kiro.dev/docs/powers.md) - MCP integrations with bundled knowledge
- [Custom agents](https://kiro.dev/docs/custom-agents.md) - Agent configuration and resources
- [Agent Skills specification](https://agentskills.io/specification) - Full format details
