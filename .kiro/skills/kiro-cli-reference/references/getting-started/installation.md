> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Installation

> Install Kiro as an IDE, CLI, web app, or mobile app and start building in minutes.

Kiro is available as a desktop IDE, a command-line interface, a web app, a mobile app, and a personal AI agent (Crew). Pick the surface that fits your workflow. You can use more than one, and your `.kiro` configuration is shared across all of them.

## System requirements

**IDE** - macOS (Intel + Apple Silicon), Windows 10/11 on x64 or ARM64, or Linux (Ubuntu 24+, Debian 13+, Fedora 40+, Arch, Mint 22+) on x86_64 or ARM64.

**CLI** - macOS, Windows 11 (PowerShell), or Linux (glibc 2.34+ or musl variant).

**Web** - Any modern browser. No local installation required.

**Mobile** - iOS, distributed through Apple TestFlight during early access.

**Crew** - macOS, Linux (x86_64 and ARM), or Windows. Python 3.9+ required for source installs.

## Install Kiro

    IDE
    CLI
    Web
    Mobile
    Crew

### Download Kiro

Go to [kiro.dev](https://kiro.dev) and download the installer for your operating system (macOS, Windows, or Linux).

      
### Run the installer

Open the downloaded file and follow the installation instructions for your platform.

      
### Sign in

When you open Kiro for the first time, sign in with a provider of your choice (Google, GitHub, AWS Builder ID, or organization identity). Learn more about [authentication](https://kiro.dev/docs/getting-started/authentication.md).

      
### Import settings (optional)

You can [import your VS Code settings and extensions](https://kiro.dev/docs/upgrade-guides/migrating-from-vscode.md). If you use another editor, skip this step and select your preferred theme.

      
### Open a project

From the welcome page, open a folder to start your first session. See [Your first project](https://kiro.dev/docs/getting-started/first-project.md) for a guided walkthrough.

### Install the CLI

**macOS and Linux:**

        `curl -fsSL https://cli.kiro.dev/install | bash`

        **Windows (PowerShell):**

        `irm 'https://cli.kiro.dev/install.ps1' | iex`

        Windows requires Windows 11 and Windows Terminal or PowerShell (not Command Prompt).

        
**ℹ️ Info:** The official Kiro CLI binary is not available for installation through the Homebrew package manager and is not supported. To install it on macOS or Linux, use the install script above.

      
### Authenticate

Run `kiro-cli` and follow the browser sign-in prompt. See [Authentication](https://kiro.dev/docs/getting-started/authentication.md) for details.

      
### Start building

Open a project directory and start a chat session:

        ```bash
        cd my-project
        kiro-cli chat
        ```

    

    ### Linux alternative installs

    The one-liner above works on most Linux distributions. If you prefer a specific package format or have an older glibc version, use one of the options below.

    #### Check your glibc version

    The standard zip install requires glibc 2.34 or newer. Check your version:

    ```bash
    ldd --version
    ```

    If the version is older than 2.34, use the musl variant instead.

    #### Amazon Linux 2023 (RPM repository)

    On Amazon Linux 2023 (x86_64 and aarch64), Kiro CLI installs from the official RPM repository, so installs, upgrades, and removal go through `dnf`.

    Add the repository:

    `sudo curl --proto '=https' --tlsv1.2 -sSf https://prod.download.cli.kiro.dev/rpm/kiro-cli.repo -o /etc/yum.repos.d/kiro-cli.repo`

    Install the package:

    ```bash
    sudo dnf install kiro-cli
    ```

    On first install, `dnf` asks you to import the repository's GPG signing key. Confirm the fingerprint matches before accepting:

    ```
    9600 944A F4B4 0FA8 1C3F 6EE8 724E 8BC8 D4F7 DD61
    ```

    Every package and the repository metadata are signed with this key, and `dnf` verifies them on each install and upgrade. To inspect the key before installing:

    ```bash
    curl -s https://prod.download.cli.kiro.dev/rpm/kiro-cli.gpg | gpg --show-keys --with-fingerprint
    ```

    Upgrades go through the package manager: `sudo dnf upgrade kiro-cli`. `kiro-cli update` reports when a new version is available but does not install it.

    The repository serves only the latest release, so previous versions can't be installed. To hold your current version, skip it for one upgrade with `sudo dnf upgrade --exclude=kiro-cli`, or add `exclude=kiro-cli` to `/etc/dnf/dnf.conf` to hold it persistently. If an update breaks your workflow, report it with `kiro-cli issue`.

    If you hit repository errors, re-download the repo file with the `curl` command above, then run `sudo dnf clean all`.

    #### AppImage

    A portable format that works on most Linux distributions without installation:

    `wget https://desktop-release.q.us-east-1.amazonaws.com/latest/kiro-cli.appimage`

    ```bash
    chmod +x kiro-cli.appimage
    ./kiro-cli.appimage
    ```

    #### Ubuntu .deb

    `wget https://desktop-release.q.us-east-1.amazonaws.com/latest/kiro-cli.deb`

    ```bash
    sudo dpkg -i kiro-cli.deb
    sudo apt-get install -f
    ```

    #### Zip (glibc 2.34+)

    **x86-64:**

    `curl --proto '=https' --tlsv1.2 -sSf 'https://desktop-release.q.us-east-1.amazonaws.com/latest/kirocli-x86_64-linux.zip' -o 'kirocli.zip'`

    **ARM (aarch64):**

    `curl --proto '=https' --tlsv1.2 -sSf 'https://desktop-release.q.us-east-1.amazonaws.com/latest/kirocli-aarch64-linux.zip' -o 'kirocli.zip'`

    Then unzip and install:

    ```bash
    unzip kirocli.zip && ./kirocli/install.sh
    ```

    Files install to `~/.local/bin` by default.

    #### Zip (musl, for glibc older than 2.34)

    **x86-64:**

    `curl --proto '=https' --tlsv1.2 -sSf 'https://desktop-release.q.us-east-1.amazonaws.com/latest/kirocli-x86_64-linux-musl.zip' -o 'kirocli.zip'`

    **ARM (aarch64):**

    `curl --proto '=https' --tlsv1.2 -sSf 'https://desktop-release.q.us-east-1.amazonaws.com/latest/kirocli-aarch64-linux-musl.zip' -o 'kirocli.zip'`

    Then unzip and install:

    ```bash
    unzip kirocli.zip && ./kirocli/install.sh
    ```

### Navigate to Kiro Web

Open [app.kiro.dev](https://app.kiro.dev) in your browser and sign in with your AWS Builder ID or Identity Center credentials.

      
### Confirm your subscription

Kiro Web requires a paid subscription (Pro or higher). It is not available on the free tier.

      
### Connect your repository provider

Go to [Settings > Agent](https://app.kiro.dev/settings/agent) and connect [GitHub](https://kiro.dev/docs/web/github.md) or [GitLab](https://kiro.dev/docs/web/gitlab.md). Select which repositories the agent can access.

        You must have write permissions on repositories for the agent to create branches and open pull requests or merge requests.

    

    
**⚠️ Warning:** If you use **AWS Identity Center**, Kiro Web is available in **US East (N. Virginia) `us-east-1`** only. Your administrator must enable **Cloud Sessions** from **Settings > Kiro Settings** in the configured AWS account before users can access it.

    Kiro for iOS is in early access, distributed through Apple TestFlight. [Request early access](https://kiro.dev/mobile/) — invites go out to a limited number of people as the rollout gradually expands. Once invited, install the app from the TestFlight link and sign in with the same account you use on other surfaces.

    Kiro Mobile is not available for Android. See [Mobile](https://kiro.dev/docs/mobile.md) for details.

    Crew is an open-source personal AI agent that runs locally on your machine. For full installation steps — desktop app, one-line install, Docker, and source builds — see the [Crew quick start](https://kiro.dev/docs/crew.md).

## Upgrading

    IDE
    CLI
    Web

    Kiro IDE downloads updates automatically in the background. When an update is ready, you'll see a notification to restart and apply it.

    To check manually, open the **Kiro** menu and select **Check for Updates...** On Windows or Linux, open the Command Palette (`Ctrl + Shift + P`) and run `Kiro: Check for Updates`.

    Kiro CLI auto-updates in the background. When a new version is available, it downloads silently and installs when you exit the application.

    Installs from the Amazon Linux RPM repository update through the package manager instead: `sudo dnf upgrade kiro-cli`.

    To disable auto-update:

    ```bash
    kiro-cli settings "app.disableAutoupdates" "true"
    ```

    Kiro Web always runs the latest version. No upgrade action needed.

    Updates ship through TestFlight. Install new builds from the TestFlight app when they become available — TestFlight can also install updates automatically if you have automatic updates turned on.

## Downgrade to a previous version

    IDE
    CLI

    You can revert to an earlier version of Kiro IDE if an update introduces issues with your workflow.

    1. Go to the [downloads page](https://kiro.dev/downloads)
    2. Scroll past the main download cards to the version list
    3. Expand the version you want to install (for example, "IDE 0.12.x")
    4. Download the installer for your platform
    5. Uninstall your current version of Kiro:
       - **macOS:** drag Kiro from Applications to the Trash
       - **Windows:** uninstall from **Settings > Apps > Installed apps**
       - **Linux:** run `sudo apt remove kiro` or `sudo dnf remove kiro` depending on your package manager
    6. Run the downloaded installer

    Your settings, extensions, and sign-in state are preserved across reinstalls. When you're ready to move back to the latest version, download it from the [downloads page](https://kiro.dev/downloads) or let the application update automatically.

    CLI builds are distributed as the latest release only — the install script and package URLs all point at the latest build, and previous CLI versions aren't offered on the downloads page.

    If your current version is working well and you want to hold it, disable auto-update before the next release lands:

    ```bash
    kiro-cli settings "app.disableAutoupdates" "true"
    ```

    Re-enable it (set to `"false"`) when you're ready to pick up the latest version again. If a CLI update breaks your workflow, report it with `kiro-cli issue` so the team can fix it in a follow-up release.

## Uninstalling

    IDE
    CLI

    Uninstall Kiro IDE using your operating system's standard application removal process (drag to Trash on macOS, Apps & Features on Windows, or your package manager on Linux).

    **macOS / Linux:**

    ```bash
    kiro-cli uninstall
    ```

    **Windows (PowerShell):**

    ```powershell
    kiro-cli uninstall
    ```

    Or uninstall through **Windows Settings > Apps**.

    **Ubuntu (.deb):**

    ```bash
    sudo apt-get remove kiro-cli
    sudo apt-get purge kiro-cli
    ```

    **Amazon Linux 2023 (RPM repository):**

    ```bash
    sudo dnf remove kiro-cli
    sudo rm /etc/yum.repos.d/kiro-cli.repo
    ```

## Proxy configuration

Kiro respects standard proxy environment variables (`HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`) on both the IDE and the CLI. Set these in your shell:

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1,.company.com
```

For proxies that require authentication:

```bash
export HTTPS_PROXY=http://username:password@proxy.company.com:8080
```

IDE
    CLI

    In addition to the environment variables, you can configure proxy settings in **Settings > Proxy** inside Kiro.

    
**⚠️ Browser-based sign-in bypasses proxy settings:** When you sign in, Kiro opens your default browser. This browser traffic uses your operating system's network stack, not the IDE's proxy configuration.

    Kiro CLI (v1.8.0+) picks up the proxy environment variables from your shell — no additional configuration needed.

For the full reference, including URLs to allowlist and data perimeter guidance, see [Firewalls, proxies, and data perimeters](https://kiro.dev/docs/privacy-and-security/firewalls.md).

## Troubleshooting

    IDE
    CLI

    For installation failures, network connectivity problems, sign-in errors, shell integration, and Windows-specific issues, see the [IDE troubleshooting guide](https://kiro.dev/docs/ide/troubleshooting.md).

    If you run into issues with the CLI, run `kiro-cli doctor` to identify and fix common problems.

    ### Log file locations

    | Platform | Path |
    |----------|------|
    | macOS | `$TMPDIR/kiro-log/kiro-chat.log` |
    | Linux | `$XDG_RUNTIME_DIR/kiro-log/kiro-chat.log` |
    | Windows | `%TEMP%\kiro-log\logs\kiro-chat.log` |

    Override the log path with the `KIRO_CHAT_LOG_FILE` environment variable:

    ```bash
    KIRO_CHAT_LOG_FILE=/tmp/my-debug.log kiro-cli chat
    ```

    ### Common issues

    - **Authentication failures** — Run `kiro-cli login` to re-authenticate.
    - **Autocomplete not working** — Run `kiro-cli doctor` to verify shell integration.
    - **SSH integration issues** — Verify your SSH server accepts the required environment variables.

    If problems persist, report them with `kiro-cli issue`.

## Next steps

- [Authentication](https://kiro.dev/docs/getting-started/authentication.md) — set up your sign-in method
- [Your first project](https://kiro.dev/docs/getting-started/first-project.md) — guided walkthrough for new users
- [Language support](https://kiro.dev/docs/guides/languages-and-frameworks/typescript-javascript-guide.md) — environment setup per language
