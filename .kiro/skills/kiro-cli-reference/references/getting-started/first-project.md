> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Your first project

> A hands-on walkthrough of Kiro's core features - steering, specs, hooks, and MCP - using a real project

This guide walks you through Kiro's essential features by working with a real project. You'll learn how to set up steering files, build features with specs, automate workflows with hooks, and extend capabilities with MCP servers.

## Prerequisites

Before starting, ensure you have:
- [Installed Kiro](https://kiro.dev/docs/getting-started/installation.md)
- [Signed in](https://kiro.dev/docs/getting-started/authentication.md) with your Kiro account
- A project to work with (either an existing project or a new one)
- Basic familiarity with your project's structure and technology stack

## Open your project

    IDE
    CLI
    Web
    Mobile

    1. **Launch Kiro** and open your project:
       - Use `File > Open Folder` to select your project directory
       - Or drag and drop your project folder into Kiro
       - Or run `kiro .` from your project directory in the command line

    2. **Access the Kiro Panel**:
       - Click the Kiro Ghost icon in the activity bar (left sidebar)
       - This panel provides access to all of Kiro's AI-powered features

    3. **Start a Chat Session**:
       - The chat pane should be open by default
       - This opens Kiro's conversational interface where you interact with the AI

    [Video](https://kiro.dev/videos/open-your-project-ide.mp4)

    1. **Navigate to your project** directory in the terminal:
       ```bash
       cd /path/to/your-project
       ```

    2. **Start Kiro CLI**:
       ```bash
       kiro-cli
       ```
       This launches the interactive terminal UI in the context of your project.

    3. **Or start with a prompt**:
       ```bash
       kiro-cli chat "Help me understand this project"
       ```

    1. **Open Kiro Web** at [app.kiro.dev](https://app.kiro.dev) and sign in.

    2. **Connect a repository**:
       - If you haven't already, connect your [GitHub](https://kiro.dev/docs/web/github.md) or [GitLab](https://kiro.dev/docs/web/gitlab.md) account
       - Select the repository you want to work with

    3. **Create a task**:
       - Choose **New Task** to start working with the agent on your project
       - Describe what you'd like to accomplish

Coming soon to Mobile.

## Set up steering files

Steering files provide context about your project, helping Kiro understand your codebase, conventions, and requirements. They are stored in `.kiro/steering/` and shared across all Kiro surfaces.

    IDE
    CLI
    Web
    Mobile

    Choose **Generate Steering Docs** from the Kiro panel. Kiro analyzes your repository and generates steering documents that guide its behavior, including:
    - Your product and its purpose
    - Technical stack and frameworks
    - Project structure and conventions

    You can also create custom steering files by clicking the `+` button in the steering section to add coding standards, workflows, and team best practices.

    [Video](https://kiro.dev/videos/kiro-steering.mp4)

    Create steering files in your project:

    1. Add a `.kiro/steering/` folder in your project root (workspace scope) or `~/.kiro/steering/` (global scope)
    2. Add markdown files (`product.md`, `tech.md`, `structure.md`) with your project standards
    3. Kiro automatically loads these files in chat sessions

    You can also ask the agent to help generate them during a session - it will analyze your repository and create the files for you.

    When you connect a repository, Kiro Web reads existing steering files from `.kiro/steering/` in your repository. To create or update steering files:

    1. Ask the agent: "Generate steering files for this project"
    2. The agent analyzes your repository and creates the steering documents
    3. Changes are committed to a branch in your repository

Coming soon to Mobile.

Learn more about steering in the [Steering documentation](https://kiro.dev/docs/steering.md).

## Build features with specs

Specs transform high-level feature ideas into detailed implementation plans through three phases:
1. **Requirements** - User stories with acceptance criteria
2. **Design** - Technical architecture and implementation approach
3. **Tasks** - Discrete, trackable implementation steps

    IDE
    CLI
    Web
    Mobile

    ### Create your first spec

    1. **Start a new spec**:
       - Click the **Spec** button in your chat session
       - Or choose the `+` button in the Kiro panel's Specs section

    2. **Enter a feature description**:
       - Describe your feature in natural language
       - Example: "Add a user authentication system with login, logout, and password reset functionality"

    3. **Follow the guided workflow**:
       - **Requirements phase**: Kiro structures your requirements using EARS notation
       - **Design phase**: Technical architecture and component design are documented
       - **Implementation phase**: Discrete tasks are generated for execution

    [Video](https://kiro.dev/videos/specs-start.mp4)

    ### Execute spec tasks

    Once your spec is complete:

    1. **Review generated tasks** in the `tasks.md` file
    2. **Execute tasks** by clicking on individual task items
    3. **Track progress** as tasks automatically update to "In Progress" and "Done"

    [Video](https://kiro.dev/videos/spec-task.mp4)

    ### Create your first spec

    In an interactive session, use the `/spec` slash command:

    1. Run `/spec new <name>` to start a new spec. The agent switches to Spec mode and asks what kind of spec you want (Feature, Bug, or Quick Spec).
    2. Describe what you want to build or fix. The agent asks clarifying questions if needed.
    3. Follow the workflow through each phase - artifacts are generated in `.kiro/specs/<name>/`.

    ### Execute spec tasks

    Run `/spec run <name>` to execute all tasks autonomously, or resume a spec with `/spec <name>` and step through tasks interactively.

    ### Create your first spec

    1. Go to [app.kiro.dev](https://app.kiro.dev) and start a new session
    2. Select one or more repositories using **Select repo** at the bottom of the chat input
    3. Choose **Spec** from the chat input box, then describe what you want to build or fix
    4. Review and refine the plan directly in your browser

    ### Execute spec tasks

    When you're ready, the agent implements the tasks and opens a pull request. You can continue to provide feedback and have the agent push updates.

Coming soon to Mobile.

Learn more about specs in the [Specs documentation](https://kiro.dev/docs/specs.md).

## Automate workflows with hooks

Agent hooks eliminate manual work by automatically executing predefined actions when specific agent events occur, such as file changes, tool use, or task execution.

    IDE
    CLI
    Web
    Mobile

    1. **Access hook creation**:
       - Navigate to the **Agent Hooks** section in the Kiro panel
       - Click the `+` button to create a new hook

    2. **Define hook behavior**:
       - Describe what you want automated in natural language
       - Example: "When the agent saves a React component file, automatically create or update its corresponding test file"

    3. **Configure hook settings**:
       - **Event type**: Choose when the hook triggers - agent file events (created, saved, deleted), prompt and agent lifecycle events, or spec task events
       - **File pattern**: Specify which files should trigger the hook (e.g., `src/**/*.tsx`)
       - **Instructions**: Define the specific actions to perform

    [Video](https://kiro.dev/videos/hooks-ide.mp4)

    Hooks in the CLI are shell commands defined in your agent configuration file. They receive hook event data as JSON via STDIN and communicate results through exit codes.

    You can ask the agent to create hooks conversationally, or define them directly in your agent configuration file. See [Hook triggers](https://kiro.dev/docs/hooks/types.md) for available event types and the [Agent Configuration Reference](https://kiro.dev/docs/custom-agents/configuration-reference.md#hooks-field) for the complete syntax.

    Kiro Web loads project Hooks from `.kiro/hooks/` in your repository. You can ask the agent to create a Hook in `.kiro/hooks/`, or add a Hook JSON file there yourself. For personal Hooks, upload them from **Settings > Sync**, then manage them under **Settings > Hooks**. Hook command actions run inside the cloud sandbox.

Hooks aren't available on Mobile.

Learn more in the [Hooks documentation](https://kiro.dev/docs/hooks.md).

## Extend capabilities with MCP

Model Context Protocol (MCP) allows Kiro to access specialized tools, APIs, knowledge bases, and external services.

    IDE
    CLI
    Web
    Mobile

    ### Set up MCP

    1. Open the Kiro panel by clicking the Kiro Ghost icon in the activity bar. Enable MCPs, then click the edit button (pencil icon) next to MCP in the panel.
    2. By default, Kiro ships with the [fetch MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch). Set `disabled` to `false` to connect to it.
    3. Add any MCP server by editing the JSON file:

    ```json
    ,
          "disabled": false,
          "autoApprove": ["search"]
        }
      }
    }
    ```

    ### Use MCP tools

    Once configured, reference MCP tools in several ways:
    - **Direct questions**: Ask questions that leverage the server's capabilities
    - **Explicit tool usage**: Reference specific tools with the `#MCP` context provider
    - **Integration**: Combine MCP with hooks and specs for automated workflows

    ### Set up MCP

    Add an MCP server with a single command:

    ```bash
    kiro-cli mcp add \
      --name "web-search" \
      --scope global \
      --command "uvx" \
      --args "mcp-server-brave-search"
    ```

    Or edit the config file directly at `~/.kiro/settings/mcp.json` (global) or `.kiro/settings/mcp.json` (workspace).

    ### Use MCP tools

    MCP tools are available in your CLI chat sessions automatically. Kiro selects the appropriate tool based on your request.

    MCP servers can be configured for Kiro Web through the sandbox settings. See [Powers and MCP](https://kiro.dev/docs/web/sandbox/mcp.md) for setup instructions.

Coming soon to Mobile.

Learn more in the [MCP documentation](https://kiro.dev/docs/mcp.md).

## Next steps

Now that you've experienced Kiro's core features:

- **Try the interactive tutorial**: Work through the [hands-on game development tutorial](https://kiro.dev/docs/guides/learn-by-playing.md)
- **Explore specs in depth**: Check out the [Specs documentation](https://kiro.dev/docs/specs.md) for the full workflow
- **Learn about steering**: Read the [Steering documentation](https://kiro.dev/docs/steering.md) for advanced configuration
- **Join the community**: Connect with other Kiro users on [Discord](https://discord.gg/kirodotdev)
