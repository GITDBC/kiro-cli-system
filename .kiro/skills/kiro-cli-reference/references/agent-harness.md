> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Choose an agent harness

> Pick the V3 or V2 agent harness for interactive chat, scripts, and ACP clients in Kiro CLI, confirm which one is running, and return to V2 when you need it.

Kiro CLI runs each conversation on an agent harness, the process that plans, calls tools, and talks to the model. In Kiro CLI 3.0.0 or later, an interactive chat that names no harness starts the V3 harness on a machine that can run it. Use this page to learn which harness a launch starts, choose one for a single run or save it as your default, confirm the choice, and go back to V2. V2 still runs but receives no new features. The Classic interface no longer runs for interactive chat.

| Harness | Status in Kiro CLI 3.0.0 or later | Choose it when |
| --- | --- | --- |
| **V3** | Default for interactive chat on a machine that can run it. The same [unified agent harness](https://kiro.dev/docs/how-kiro-works.md) as the Kiro IDE and Kiro Web | You want current CLI features, such as [Approve for me](https://kiro.dev/docs/permissions.md#approve-for-me), [Memory](https://kiro.dev/docs/memory.md), and [cloud sessions](https://kiro.dev/docs/cloud-sessions.md) |
| **V2** | Available by explicit choice. Receives no new features | A script or setup still depends on 2.x behavior, or your Linux machine cannot run V3 |
| **Classic** | Retired for interactive chat | Never for new work. A launch that still selects Classic is offered V3; see [If a launch still selects Classic](#if-a-launch-still-selects-classic) |

Prefer V3 unless a workflow you depend on still needs V2, and keep `kiro-cli --v2` at hand until your V3 checks pass. If you are moving from Kiro CLI 2.x, follow [Upgrade from CLI 2.x](https://kiro.dev/docs/cli/v3.md) after you read this page.

## Which harness starts

When nothing on the launch line or in your settings names a harness, Kiro CLI picks one by launch type:

| Launch | Default harness |
| --- | --- |
| Interactive chat (`kiro-cli` or `kiro-cli chat`) | V3 on a machine that can run it. On a Linux machine with older glibc, V2; see [Linux machines with older glibc](#linux-machines-with-older-glibc) |
| Local headless run (`--no-interactive`, or standard input that is not a terminal) | V2, with the exceptions listed under [Scripts and CI](#scripts-and-ci): `--trust-all-tools` takes the interactive default, and `--cloud`, `--repo`, or a V3 session ID selects V3 |
| ACP client (`kiro-cli acp`) | V3 on a machine that can run it, with the exceptions listed under [ACP clients](#acp-clients) |
| `--cloud` or `--repo` | V3 |
| `--resume-id` naming a session created by V1 or V2 | V2 |

An explicit choice overrides these ordinary defaults. Kiro CLI resolves the harness in this order:

1. `--v3` or `--v2` on the launch line.
2. `kiro-cli chat --agent-engine <value>`.
3. The V3 implied by `--cloud` or `--repo`.
4. The saved `chat.agentEngine` setting.
5. The launch default from the table above.

Two launch types run only on V3. `--cloud` and `--repo` reject an explicit V1 or V2 choice. `--sessions` has its own rule: when nothing explicit or saved selects V1 or V2, it opens the session dashboard on V3; when a flag or the saved `chat.agentEngine` selects V1 or V2, the launch stops and tells you to run with `--v3`.

The exact flag values, their conflicts, and the setting's accepted values are in [CLI commands](https://kiro.dev/docs/reference/cli-commands.md#kiro-cli-chat) and [Settings](https://kiro.dev/docs/reference/settings.md#chat-interface).

**ℹ️ Info:** `chat.agentEngine` applies to `kiro-cli` and `kiro-cli chat`. It is never consulted for `kiro-cli acp`, which has its own setting, `acp.agentEngine`.

## Choose a harness for one run

Pass `--v3` or `--v2` to `kiro-cli` or `kiro-cli chat`. The flag applies to that run and leaves your saved default unchanged.

```bash
# Start this session on V3
kiro-cli --v3

# Start this session on V2
kiro-cli --v2
```

`--v2` and `--v3` cannot be combined, and neither can be combined with `--agent-engine` or `--legacy-ui`.

To verify, read the first lines of the session. A V3 session opens with **Welcome to Kiro CLI V3**. A V2 session opens with **Kiro CLI V3 is here**; see [Confirm which harness is running](#confirm-which-harness-is-running).

Next, save the harness you want as your default so you can drop the flag.

## Save a default harness

Save the harness for every interactive launch with the global `chat.agentEngine` setting; a workspace cannot override it. For a current harness, save `v3` or `v2`. The setting also accepts the retired `v1` value; see [Settings](https://kiro.dev/docs/reference/settings.md#chat-interface).

```bash
# Start every interactive session on V3
kiro-cli settings chat.agentEngine v3

# Start every interactive session on V2
kiro-cli settings chat.agentEngine v2
```

To verify, run `kiro-cli settings chat.agentEngine` and confirm the value you saved. A `--v2` or `--v3` flag on a later launch still wins for that run.

For ACP clients, save the harness with `acp.agentEngine` instead; see [ACP clients](#acp-clients).

## Answer the first-launch prompt

In Kiro CLI 3.0.0 or later, the first interactive launch after you upgrade asks before V3 applies if you have saved Kiro CLI 2.x sessions and have never chosen a harness. A fresh install, or an upgrade with no saved sessions, starts V3 without asking. The prompt offers three answers:

| Answer | What happens |
| --- | --- |
| **Continue with V3** | Saves `chat.agentEngine` as `v3` and starts this session on V3 |
| **Stay on V2, remind me later** | Saves `chat.agentEngine` as `v2`, starts this session on V2, and asks again after 14 days |
| **Stay on V2, don't ask again** | Saves `chat.agentEngine` as `v2` and starts this session on V2 |

If you had already saved `chat.agentEngine` as `v2` before upgrading, you see a one-time notice instead, with **Switch to V3** and **Keep V2**.

Kiro CLI skips the prompt when the launch already names a harness (so `kiro-cli --v3` starts V3 without asking and saves no default), when it resumes a session with `--resume-id`, when it opens the session dashboard with `--sessions`, when it runs headless, and on a machine that cannot run V3.

When V3 starts, it upgrades your V2 agent configs automatically unless `chat.enableAutoAgentUpgrade` is `false`. See [Upgrading agent configs](https://kiro.dev/docs/cli/v3/upgrade-agent.md#automatic-upgrade-when-v3-starts) for what the upgrade changes and how to review it.

To verify your answer, run `kiro-cli settings chat.agentEngine`. To change it later, follow [Save a default harness](#save-a-default-harness).

## Scripts and CI

A local headless run with no explicit or saved harness runs V2, with three exceptions: `--trust-all-tools` takes the interactive default (V3 on a machine that can run it), `--cloud` or `--repo` selects V3, and a `--resume-id` that names a V3 session selects V3. Name the harness in every script so a change to the defaults does not change your pipeline:

```bash
# Headless run on V3
kiro-cli chat --v3 --no-interactive "your prompt here"

# Headless run on V2
kiro-cli chat --v2 --no-interactive "your prompt here"
```

A headless run that selects Classic is moved to the headless default and prints a notice.

To verify, check the run's output for the harness you expect. For the flags that control approvals and output in a headless run, see [Headless mode](https://kiro.dev/docs/cli/headless.md).

## ACP clients

In Kiro CLI 3.0.0 or later, `kiro-cli acp` starts the V3 harness when neither the `--agent-engine` flag nor the `acp.agentEngine` setting names one, with three exceptions:

- The launch line carries a V2-only flag: `--agent`, `--model`, `--effort`, `--trust-all-tools`, or `--trust-tools`. The run stays on V2.
- Kiro recognizes the client as one that still needs V2. The run stays on V2.
- The machine cannot run V3; see [Linux machines with older glibc](#linux-machines-with-older-glibc). The run uses V2.

A named harness always wins. With `--agent-engine v3`, the V2-only flags are rejected. `chat.agentEngine` is never consulted for `kiro-cli acp`.

To choose explicitly, save the setting or pass the flag in your editor's command arguments:

```bash
kiro-cli settings acp.agentEngine v3
```

To verify, run `kiro-cli settings acp.agentEngine`. For the editor setup and the full flag list, see [ACP](https://kiro.dev/docs/cli/acp.md) and [`kiro-cli acp`](https://kiro.dev/docs/reference/cli-commands.md#kiro-cli-acp). For what changes when a client moves to V3, see [Migrate an ACP client to CLI V3](https://kiro.dev/docs/cli/v3/acp-migration.md).

## If a launch still selects Classic

In Kiro CLI 3.0.0 or later, the Classic interface no longer runs for interactive chat. A launch that still selects it, through `--classic` or `--legacy-ui`, `--agent-engine v1`, the `KIRO_CHAT_UI` environment variable, the `chat.ui` setting, or `chat.agentEngine` set to `v1`, shows the Kiro CLI 3.0 message and offers two choices:

- **Continue with V3** saves `chat.agentEngine` and reruns the launch in the terminal UI.
- **Exit** leaves the harness unchanged and ends the launch.

On a machine that cannot run V3, the button reads **Switch to the terminal UI and launch** and saves `chat.agentEngine` as `v2`.

A saved `v2` or `v3` value in `chat.agentEngine` outranks a Classic flag left in a shell alias, so after you choose **Continue with V3** once, the alias keeps working. If the terminal UI is missing from the installation, this launch prints a reinstall message that links to [Installation](https://kiro.dev/docs/getting-started/installation.md) instead of starting a chat.

To verify, launch again and confirm the session opens in the terminal UI with one of the welcome messages under [Confirm which harness is running](#confirm-which-harness-is-running).

## Linux machines with older glibc

On a Linux machine whose glibc is older than the V3 harness needs, a launch that names no harness opens the terminal UI with the V2 harness and the ordinary V2 welcome. Only a launch that selected Classic shows a message saying that this machine can't run the 3.0 agent. `kiro-cli --v3` on such a machine stops with **V3 is currently not supported on this system**. macOS and Windows machines can always run V3.

To verify, read the welcome message. For installation options on Linux, see [Installation](https://kiro.dev/docs/getting-started/installation.md).

## Confirm which harness is running

Read the first lines of the session:

- A V3 session opens with **Welcome to Kiro CLI V3** and lists `kiro-cli --v2` as the way to launch the previous experience instead.
- A V2 session opens with **Kiro CLI V3 is here. This version will no longer receive feature updates. To upgrade, run: kiro-cli --v3**.

Both messages link to [Upgrade from CLI 2.x](https://kiro.dev/docs/cli/v3.md).

To confirm your saved default, run `kiro-cli settings chat.agentEngine`, or `kiro-cli settings acp.agentEngine` for ACP clients.

## Return to V2

To run V2 once, launch with `kiro-cli --v2`. To make V2 your default, run `kiro-cli settings chat.agentEngine v2`. Neither command changes your V3 sessions or configuration.

V3 and V2 keep separate session stores. V3 can resume a V2 session as a V3 copy; V2 cannot open a V3 session. See [Start V3 and keep V2 sessions available](https://kiro.dev/docs/cli/v3/migration-guide.md#1-start-v3-and-keep-v2-sessions-available) for the resume commands.

To verify, start a session and confirm it opens with **Kiro CLI V3 is here**.

## Next step

Start a V3 session with `kiro-cli --v3` and follow [Upgrade from CLI 2.x](https://kiro.dev/docs/cli/v3.md) to move your sessions, agent configs, permissions, and Hooks.
