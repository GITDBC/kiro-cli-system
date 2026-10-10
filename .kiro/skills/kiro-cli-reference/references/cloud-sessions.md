> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Cloud sessions

> Run agent sessions in a managed cloud sandbox and pick them up from the IDE, CLI, Web, or Mobile.

A cloud session runs the [Kiro agent harness](https://kiro.dev/docs/how-kiro-works.md) in a managed cloud sandbox instead of on your machine. The session belongs to your Kiro account, not to any one app: start it in the browser, hand it a long task, close your laptop, and check on it later from your phone, your terminal, or the IDE. The agent keeps working in the sandbox whether or not you're connected.

Cloud sessions are the execution environment behind [Kiro Web](https://kiro.dev/docs/web.md) and [Mobile](https://kiro.dev/docs/mobile.md), and the IDE and CLI can create and attach to the same sessions. Because every surface talks to the same harness through the same protocol, cloud sessions retain Kiro's core agent behavior while running against sandbox-backed files, tools, and configuration. The main difference is where the work happens; client-specific limitations are described below.

**ℹ️ Info:** Cloud sessions are included with your existing Kiro plan, with no separate charge for cloud compute. You can run up to **10 concurrent cloud sessions**. Creating and attaching from the IDE requires **Kiro IDE v1.0.293 or later**, and from the CLI requires **Kiro CLI v2.17 or later**. If you don't see the entry points described below, update to the latest version.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Create a cloud session | ✓ | ✓ | ✓ | ✓ |
| Resume and steer an existing cloud session | ✓ | ✓ | ✓ | ✓ |
| Autonomous mode | ✓ | ✓ | ✓ | ✓ |
| Scheduled [automations](https://kiro.dev/docs/web/automations.md) | — | — | ✓ | — |

## How cloud sessions work

When you create a cloud session, Kiro provisions an isolated sandbox and starts the same agent harness that runs locally in the IDE and CLI. If you attach repositories, Kiro clones them **server-side** through your connected source provider; your local working copy is never uploaded. The agent reads, edits, builds, and runs shell commands inside the sandbox, and delivers results back through your source provider (typically as a pull request) or directly in the conversation.

The session itself lives in a cloud session store, separate from any client:

- **Clients attach and detach:** the Web app, Mobile app, IDE, and CLI are all views onto the same session. Disconnecting a client doesn't stop the agent, and an in-flight task keeps running.
- **State survives your machine:** conversation history, bound repositories, and the sandbox's file state persist in the cloud. Reattach from any surface and the transcript replays where you left off.
- **Approvals wait for you:** if the agent needs [permission](https://kiro.dev/docs/permissions.md) for an action while nobody is connected, the request waits and is presented to the next client that attaches.

For details on the sandbox itself (network access, environment variables, and environment configuration), see the [Sandbox](https://kiro.dev/docs/web/sandbox.md) documentation.

## Prerequisites

- A Pro, Pro+, Pro Max, or Power subscription. Cloud sessions use the existing credit model, with no separate charge for cloud compute
- A connected [GitHub](https://kiro.dev/docs/web/github.md) or [GitLab](https://kiro.dev/docs/web/gitlab.md) account, if you want to work on repositories
- For AWS Identity Center organizations: an administrator must first enable Cloud Sessions by toggling on **Cloud Sessions** in **Settings > Kiro Settings**, in the AWS account where Kiro is configured. See [AWS Identity Center](https://kiro.dev/docs/web/identity-center.md) for the full steps. Cloud sessions run in **US East (N. Virginia) `us-east-1`** only
- For organizations using Okta or Microsoft Entra ID as an external identity provider (IdP): an administrator must enable **Cloud Sessions** and add `https://app.kiro.dev/signin/oauth` to the existing Kiro OIDC application. Follow the [Okta redirect URI setup](https://kiro.dev/docs/enterprise/identity-provider/okta.md#create-new-app-integration) or [Microsoft Entra ID redirect URI setup](https://kiro.dev/docs/enterprise/identity-provider/microsoft-entra.md#add-a-redirect-uri)

## Work with cloud sessions

    IDE
    CLI
    Web

In the IDE, cloud sessions live in [Agent Focus Mode](https://kiro.dev/docs/ide/experimental/focus-mode.md). Open Agent Focus from the top-right corner of the IDE window, and the session rail shows a **Cloud Sessions** section alongside your local projects. The section appears when cloud sessions are available for your account.

### Start a cloud session

1. Select **+** (**New Cloud Session**) in the Cloud Sessions section header. This opens a draft; nothing is created in the cloud yet.
2. Optionally select **Select repos** below the composer to attach one or more repositories from your connected source provider. Selected repositories appear as removable pills.
3. Choose your model, agent or workflow, and autonomy level. Cloud sessions offer **Autopilot** and **Autonomous**; selecting Autonomous hands mode and model choice to the agent.
4. Type your first prompt and submit. Kiro provisions the sandbox, clones the selected repositories, and sends your prompt. The composer is locked while the session is being set up.

Once the session starts, its bound repositories stay visible below the chat input. Repositories are chosen at creation time. To work on a different set, start a new cloud session.

### Manage cloud sessions

Cloud sessions appear in the rail ordered by recent activity, with the same status indicators as local sessions. From a session's context menu you can:

- **Pin Session** to keep it at the top of the section
- **Open in Kiro Web** to continue the same session in the browser
- **Open with Kiro CLI** to attach from a terminal (requires Kiro CLI 2.17 or later)
- **Delete Session** to permanently remove the session and its sandbox

### What works differently from local sessions

The session's files live in the sandbox, not your workspace, so affordances that operate on local files are unavailable in cloud sessions: opening files or diffs in the editor, checkpoints and revert, the `#File`/`#Folder`/`#Terminal`/`#Problems` context pickers, hook configuration links, and clickable spec task actions. Prompt attachments (images and documents) work; their contents are sent to the session. Renaming a cloud session and Supervised mode aren't available yet.

The CLI creates and attaches to cloud sessions with the `--cloud` flag.

### Start a cloud session

```bash
# Empty cloud workspace
kiro-cli --cloud

# Start with one repository
kiro-cli --cloud --repo owner/repository

# Start with multiple repositories (comma-separated)
kiro-cli --cloud --repo owner/repo-one,owner/repo-two
```

During startup the CLI walks through a checklist so you can see the session come up:

```text
✓ Connected to kiro.dev
✓ Connected to GitHub
✓ Cloud session created
✓ 12 repositories found, /repo to select (optional)
```

If your source provider isn't connected yet, the CLI directs you to Kiro Web to connect one. The footer keeps the execution location visible for the life of the session, along with the bound repository and branch.

### Attach repositories after startup

Use `/repo` to open a multi-select repository picker, or name a repository directly:

```text
/repo
/repo owner/repository
```

### Disconnect, resume, and manage

Cloud sessions survive the CLI exiting. `/disconnect` (or closing the terminal) detaches without stopping the agent, and `/quit` asks whether the agent should keep working:

```text
Would you like the agent to continue working?

Yes (agent continues)
No (agent stops)
```

Resume from any machine. The CLI detects that the ID belongs to a cloud session, so no `--cloud` flag is needed:

```bash
# List local and cloud sessions
kiro-cli chat --list-sessions

# Resume by ID (or a unique prefix)
kiro-cli --resume-id <session-id>

# Delete a session
kiro-cli chat --delete-session <session-id>
```

Inside a session, `/sessions` opens a combined picker of local and cloud sessions with environment and status columns.

### What works differently from local sessions

Agent file operations, shell commands, and search run in the sandbox, but a few interactive commands still refer to your local machine and are unavailable in cloud sessions for now: `/spec`, `/rewind`, `/agent create` and `/agent edit`, `/context add`/`remove`/`clear` (`/context show` works), `/chat save`/`load`, and the `!command` local shell escape. The `@` file picker and Tab path completion currently search your local filesystem, not the sandbox. `/mcp`, `/tools`, and `/hooks` reflect the sandbox's configuration, not your laptop's.

Every [Kiro Web](https://kiro.dev/docs/web.md) session is a cloud session; the browser is the native surface for this feature. After your administrator enables **Cloud Sessions** and, if your organization uses an external IdP, configures the IdP for Kiro Web, you do not need to complete any per-user setup beyond signing in.

### Start a cloud session

1. Sign in at [app.kiro.dev](https://app.kiro.dev).
2. Select the repository (or repositories) to work on from your connected [GitHub](https://kiro.dev/docs/web/github.md) or [GitLab](https://kiro.dev/docs/web/gitlab.md) account. When a branch selector is shown next to a repository in the picker, you can open it to clone a branch other than the repository's default; otherwise Kiro clones the default branch.
3. Chat with the agent to explore, implement, and iterate. When you're ready, ask it to open a pull request, or toggle on [autonomous mode](https://kiro.dev/docs/web/autonomous-mode.md) to let it plan, implement, and open the PR on its own.

### Manage cloud sessions

Your sessions persist across browser tabs and devices. Close the tab mid-task and the agent keeps working; the session list shows live status when you return. For recurring work, [automations](https://kiro.dev/docs/web/automations.md) run cloud sessions on a schedule without you starting them at all.

The [Mobile app](https://kiro.dev/docs/mobile.md) connects to the same sessions, so you can review diffs and answer approval requests from your phone.

See [Working with the agent](https://kiro.dev/docs/web/using-the-agent.md) for the full Web experience, including task creation and PR workflows.

## What runs where

Cloud sessions draw a clear boundary between your machine and the sandbox:

| | Local machine | Cloud sandbox |
|---|---|---|
| Your prompts and attachments | Composed here | Delivered to the session (attachment contents are uploaded) |
| Repository code | Never uploaded | Cloned server-side via your source provider connection |
| Agent file reads and edits | — | Run in the sandbox |
| Shell commands and builds | — | Run in the sandbox |
| Project configuration (`.kiro/` in the repo) | — | Arrives with the repository clone |
| Local personal configuration (`~/.kiro/`) | Stays local | Not applied; use personal Cloud configuration for supported account-backed items |

## Configuration in the cloud

Cloud sessions and personal Cloud configuration are related account-backed capabilities, but they serve different purposes. A cloud session determines where the agent works. Personal Cloud configuration determines which account-level configuration Kiro makes available across supported surfaces.

Configuration follows the same [scopes](https://kiro.dev/docs/configuration.md) as everywhere else:

- **Project configuration travels with the repo:** steering, specs, custom agents, hooks, and MCP servers committed under `.kiro/` in your repository apply in cloud sessions automatically, because the sandbox clones the repository.
- **Personal configuration can sync through your account:** your local `~/.kiro/` directory stays local and isn't applied to a cloud session. Use **Settings > Configuration Sync** in [Kiro Web](https://app.kiro.dev/settings/cloud-config) to upload supported personal configuration. Manage the cloud copy from its feature-specific settings page, including account-backed [Powers](https://kiro.dev/docs/powers.md) under **Settings > Powers**. See [Configuration Sync](https://kiro.dev/docs/web/cloud-configuration.md) for supported folders and the upload workflow.
- **Sandbox environment:** internet access, environment variables, and setup commands are covered in the [Sandbox documentation](https://kiro.dev/docs/web/sandbox.md).

### Use personal Cloud configuration in the IDE

When personal Cloud configuration is enabled for your account and supplies cloud-managed items, Kiro IDE 1.0.437 or later shows personal Steering, custom agents, Skills, Powers, and Hooks in their usual IDE surfaces. A cloud indicator identifies items managed in Kiro Web. Cloud Steering, Skills, and Hooks open as read-only previews with an **Edit in web** action. Agent Focus settings show the same cloud source and links for managing those items in Kiro Web.

If Cloud configuration is enabled but your account supplies no cloud items, these indicators and management actions don't appear, and the IDE surfaces remain unchanged.

The IDE's personal Cloud configuration surfaces do not include standalone MCP servers. Configuration Sync handles MCP server settings separately: uploading `settings/mcp.json` sends those servers to Kiro Web sandbox MCP server settings, not to the IDE as cloud-managed MCP servers. This is also separate from MCP configuration bundled inside a [Power](https://kiro.dev/docs/powers.md): bundled MCP configuration belongs to that Power and becomes available when the Power is active. Project-level MCP servers committed under `.kiro/` continue to follow project configuration scope.

## Move between surfaces

A cloud session is one session, whichever app you view it through:

| From | To | How |
|------|----|----|
| Web or Mobile | CLI | `kiro-cli --resume-id <session-id>` |
| IDE (Agent Focus) | Web | **Open in Kiro Web** on the session's menu |
| IDE (Agent Focus) | CLI | **Open with Kiro CLI** on the session's menu |
| CLI | Web | Open the session at `app.kiro.dev` |
| Any | Mobile | The session appears in the Mobile app's session list |

## Current limitations

- **Concurrency limit:** you can run up to 10 cloud sessions in parallel.
- **Repository set is fixed:** you choose repositories when you create the session (the CLI can also add them later with `/repo`). To work on different repositories, start a new session.
- **No Supervised mode:** cloud sessions run in Autopilot or Autonomous; per-change approval isn't available.
- **No renaming:** cloud sessions can't be renamed from the IDE or CLI.
- **Surface gaps:** each tab above lists commands and affordances that don't work in cloud sessions yet. These gaps can differ by surface and release.

## Related

- [How Kiro works](https://kiro.dev/docs/how-kiro-works.md) - the Kiro agent harness and where it runs
- [Kiro Web](https://kiro.dev/docs/web.md) - the browser-native cloud session experience
- [Configuration Sync](https://kiro.dev/docs/web/cloud-configuration.md) - upload personal `.kiro` configuration for cloud sessions
- [Sandbox](https://kiro.dev/docs/web/sandbox.md) - network access, environment variables, and environment configuration
- [Agent Focus Mode](https://kiro.dev/docs/ide/experimental/focus-mode.md) - the IDE surface for cloud sessions
- [CLI session management](https://kiro.dev/docs/cli/chat/session-management.md) - listing, resuming, and deleting sessions
- [Configuration scopes](https://kiro.dev/docs/configuration.md) - where settings live and how they travel
