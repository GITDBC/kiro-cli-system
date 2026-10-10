> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Managed updates

> Point Kiro IDE and Kiro CLI at a self-hosted update server with managed policies for phased rollouts, version pinning, and mirrored release artifacts.

Kiro IDE and Kiro CLI can each be redirected to a self-hosted update server so you control which versions reach your fleet. The two products use separate, independent mechanisms — configure whichever surfaces your organization runs.

**ℹ️ Two distinct mechanisms:** [Kiro IDE](#kiro-ide) uses the `UpdateUrl` policy in the `dev.kiro.desktop` domain with per-platform JSON metadata manifests. [Kiro CLI](#kiro-cli) uses the `update.baseUrl` policy in the `dev.kiro.cli` domain with platform-specific release metadata — `index.json` on macOS and `latest/manifest.json` on Windows. They are not interchangeable — set the policy for each product you deploy.

## Kiro IDE

Control which Kiro IDE versions reach your users by hosting a self-managed update site. Set the `UpdateUrl` managed policy to point Kiro at your server, serve per-platform JSON manifests, and host the installer binaries anywhere reachable over HTTPS.

### Configure the update URL

Set the `UpdateUrl` policy to your server's base URL.

    macOS
    Windows
    Linux

Use macOS managed preferences to set the policy:

```bash
sudo defaults write dev.kiro.desktop UpdateUrl -string "https://updates.example.com"
```

Or deploy via an MDM profile targeting the `dev.kiro.desktop` domain.

Set the policy in the Windows registry:

```
HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Kiro
  UpdateUrl (REG_SZ) = https://updates.example.com
```

Or deploy via Group Policy or an MDM solution.

Add the policy to `/etc/kiro/policy.json`:

```json
{
  "UpdateUrl": "https://updates.example.com"
}
```

| Requirement | Detail |
|-------------|--------|
| Scheme | `https://` only. Non-HTTPS or malformed values are logged and Kiro falls back to the built-in default. |
| Trailing slash | Stripped automatically. |
| When it applies | Resolved at startup — restart Kiro for the change to take effect. |
| UpdateMode | `UpdateMode=none` always wins and disables updates entirely, regardless of `UpdateUrl`. |

**ℹ️ Verifying the configuration:** Open **Help > About** in Kiro to confirm the update URL is active. If the URL or the app's commit hash is missing, Kiro shows updates as disabled with a `MissingConfiguration` status.

### Manifest paths

Kiro requests a JSON manifest at a per-platform path built from the base URL, channel, OS, and architecture:

| Platform | Path |
|----------|------|
| macOS | `//metadata-darwin--.json` |
| Linux | `//metadata-linux--.json` |
| Windows | `//metadata--.json` |

Where:
- `` is the release channel — always `stable` for self-hosted update servers
- `` is `x64` or `arm64`
- `` is `win32-` plus an install-type suffix: `-system` (default), `-user`, or `-archive` (portable)

**Examples:**
- macOS: `https://updates.example.com/stable/metadata-darwin-arm64-stable.json`
- Windows (user install): `https://updates.example.com/stable/metadata-win32-x64-user-stable.json`
- Linux: `https://updates.example.com/stable/metadata-linux-x64-stable.json`

Kiro appends `?bg=true` on automatic background checks. Your server can safely ignore this parameter.

### Manifest format

Kiro reads the first entry in `releases`. Here is an example manifest:

```json
{
  "currentRelease": "1.2.0",
  "releases": [
    {
      "version": "1.2.0",
      "updateTo": {
        "version": "1.2.0",
        "pub_date": "2026-07-10",
        "notes": "Kiro-darwin-arm64-1.2.0",
        "name": "Kiro-darwin-arm64-1.2.0",
        "url": "https://updates.example.com/releases/stable/darwin-arm64/signed/1.2.0/kiro-ide-1.2.0-stable-darwin-arm64.zip"
      }
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `currentRelease` | Latest release version string |
| `releases[0].version` | Compared against the installed version — an update is offered only if this is greater |
| `releases[0].updateTo.url` | Download URL for the signed binary. Must be HTTPS. Does not need to share the manifest's host. |
| `updateTo.pub_date` | Publish date in `YYYY-MM-DD` format |
| `updateTo.name` / `notes` | Metadata shown to the user in the update prompt |

#### Binary formats by platform

| Platform | Binary type |
|----------|-------------|
| macOS | Signed `.zip` — downloaded, installed, and relaunched automatically |
| Windows | `.exe` installer — Kiro downloads and launches it directly |
| Linux | Archive URL — Kiro opens it in the default browser for manual install |

**ℹ️ Info:** On macOS, the app must be properly code-signed or the update is rejected.

### Deployment strategies

#### Phased rollout

Release to a pilot group first, then roll out organization-wide after a validation period.

**Step 1: Mirror the release**

When a new Kiro version is published, download the installer binaries from `prod.download.desktop.kiro.dev` and create manifests pointing to your hosted copies.

**Step 2: Pilot group**

Configure your pilot group's machines with `UpdateUrl` pointing to a manifest that advertises the new version:

```json
{
  "currentRelease": "1.3.0",
  "releases": [
    {
      "version": "1.3.0",
      "updateTo": {
        "version": "1.3.0",
        "pub_date": "2026-07-15",
        "notes": "Kiro-darwin-arm64-1.3.0",
        "name": "Kiro-darwin-arm64-1.3.0",
        "url": "https://updates.example.com/releases/stable/darwin-arm64/signed/1.3.0/kiro-ide-1.3.0-stable-darwin-arm64.zip"
      }
    }
  ]
}
```

**Step 3: Validate**

Monitor the pilot group for issues over your validation period (commonly 3–7 days).

**Step 4: Broad rollout**

Update the manifests on your production endpoint to advertise the new version. All remaining users receive the update on their next check.

#### Version pinning

To hold your fleet on a specific version, set `releases[0].version` to the version your fleet currently runs. Kiro only offers an update when the manifest version is greater than the installed version, so advertising the same version effectively pins it.

This controls the auto-update check only — it does not prevent a user from manually installing a different version. To fully lock versions, combine pinning with [network controls](#combining-with-network-controls) that block access to the official download server.

### Disabling updates entirely

Set `UpdateMode=none` via managed policy (same delivery mechanism as `UpdateUrl`). When `UpdateMode` is `none`, Kiro skips all update checks regardless of the `UpdateUrl` value.

### Combining with network controls

You can combine the `UpdateUrl` policy with [firewall rules](https://kiro.dev/docs/privacy-and-security/firewalls.md) to ensure Kiro can only reach your internal update server. Block outbound access to `prod.download.desktop.kiro.dev` and allow your custom endpoint only. This guarantees that no user bypasses your version governance.

## Kiro CLI

Redirect Kiro CLI updates to your own server by setting a managed `update.baseUrl` policy value. On a managed machine, an enforced policy takes precedence over other release-URL configuration.

**ℹ️ Update mechanics differ by platform:** Kiro CLI's updater is not the same on every OS. macOS reads a cumulative `index.json` registry, while Windows reads a `latest/manifest.json` snapshot — and the `kiro-cli update` options, environment overrides, and metadata schema differ accordingly. Configure the mirror and policy for each platform you support.

### Configure the base URL

Set the `update.baseUrl` policy to your release server root.

    macOS
    Windows
    Linux

Deploy `update.baseUrl` as a **forced** value in the `dev.kiro.cli` managed preference domain through an MDM configuration profile.

Non-forced (user-level) values in this domain are ignored, so a local `defaults write` does not take effect on a managed machine.

Set the policy as a registry string value, typically deployed via Group Policy:

```
HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Kiro\CLI
  update.baseUrl (REG_SZ) = https://artifacts.example.com/mirrors/kiro-cli
```

Managed update redirection is not supported for Kiro CLI on Linux.

A base URL may include a path prefix (for example, `https://artifacts.example.com/mirrors/kiro-cli`). Trailing slashes are normalized. Values that fail URL validation are ignored in favor of the default release server.

### Base URL precedence

    macOS
    Windows

An enforced `update.baseUrl` policy takes precedence over other release-URL configuration.

On each update check, Kiro CLI resolves the base URL from three sources: the managed `update.baseUrl` policy value, the `KIRO_DESKTOP_RELEASE_URL` environment variable, and the built-in default release server. Which one wins depends on whether the policy is enforced:

- **With an enforced policy** — policy value, then environment variable, then default.
- **Otherwise** — environment variable, then policy value, then default.

So an enforced policy governs managed machines, while on an unmanaged machine the environment variable can still override the base URL — worth accounting for when you plan how tightly to lock updates down.

### Release metadata

Kiro CLI fetches release metadata from your server to decide whether to update. The file it requests and the schema it expects differ by platform, so a mirror must serve the right file for each platform you support. Each `packages[].download` is a path resolved relative to your base URL.

    macOS
    Windows

macOS requests a cumulative version registry at `<base>/index.json`:

```json
{
  "supported": [
    { "architecture": "universal", "targetTriple": "universal-apple-darwin", "variant": "full", "fileType": "dmg" }
  ],
  "versions": [
    {
      "version": "2.13.0",
      "packages": [
        {
          "kind": "dmg",
          "os": "macos",
          "architecture": "universal",
          "targetTriple": "universal-apple-darwin",
          "variant": "full",
          "fileType": "dmg",
          "download": "2.13.0/KiroCLI.dmg",
          "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
          "size": 52428800,
          "channel": "stable"
        }
      ],
      "rollout": { "start": 1731000000, "end": 1731600000 },
      "updateConditions": [{ "allowedAutoUpdateProductNames": ["Kiro CLI"] }]
    }
  ]
}
```

The registry is cumulative — it lists every version released to the channel, and requires a top-level `supported` array describing the build targets you publish. Every `supported` item requires `architecture` and `variant` (`targetTriple`, `os`, and `fileType` are optional selection fields); macOS ships a DMG. `rollout` is a `` window in epoch seconds, and `updateConditions` gate automatic updates — the product value `Kiro CLI` is the case-sensitive wire value. Replace `sha256` and `size` with your artifact's digest and byte count.

Windows requests a current-latest snapshot at `<base>/latest/manifest.json`:

```json
{
  "version": "2.13.0",
  "packages": [
    {
      "kind": "msi",
      "os": "windows",
      "architecture": "x86_64",
      "targetTriple": "x86_64-pc-windows-msvc",
      "variant": "full",
      "fileType": "msi",
      "download": "2.13.0/kiro-cli.msi",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "size": 47185920,
      "channel": "stable"
    }
  ]
}
```

The snapshot names only the current-latest version. Each package requires `kind`, `os`, `architecture`, `targetTriple`, `variant`, `fileType`, `download`, `sha256`, `size`, and `channel`; replace `sha256` and `size` with your artifact's digest and byte count.

### Mirror server layout

A mirror must serve the metadata file for each platform plus the artifact files its `packages[].download` paths declare:

    macOS
    Windows

```text
<base>/index.json                # cumulative version registry
<base>/<version>/<artifact>      # artifact files at the paths packages[].download declare
```


```text
<base>/latest/manifest.json      # names the current version and its artifacts
<base>/<version>/<artifact>      # artifact files at the paths packages[].download declare
```

`download` paths resolve relative to `<base>`, so a mirror controls its own artifact layout by writing matching paths in the metadata it hosts.

### Pinning and staged rollout

By default, Kiro CLI only updates to a version newer than the one installed, so you govern rollout through the metadata your mirror serves (on Windows, `--force` can override this):

    macOS
    Windows

Before `rollout.start`, Kiro CLI does not select the version. At or after the start, a plain `kiro-cli update` bypasses staged percentage selection, while `kiro-cli update --rollout` follows it. Both manual forms ignore `updateConditions`. Automatic updates follow rollout timing and enforce `updateConditions`. To pin, don't publish a `versions[]` entry higher than the release your fleet runs.

`manifest.json` names only the latest version. Pin by keeping its `version` at the release your fleet runs (a user can still reinstall or downgrade with `--force`); stage a rollout by pointing different groups' `update.baseUrl` at mirrors that advertise different versions.

### Disabling automatic updates

Set `app.disableAutoupdates` to disable automatic updates:

```bash
kiro-cli settings app.disableAutoupdates true
```

On Windows, defining the `KIRO_NO_AUTO_UPDATE` environment variable with any value also disables background updates.

### Checking for updates manually

The options for `kiro-cli update` differ by platform:

    macOS
    Windows

Supports `--non-interactive`, `--relaunch-dashboard`, and `--rollout`. It does not accept `--check` or `--force`.

Supports `--check`, `--force`, and `--help`.

```bash
# Check whether a newer version is available without installing it
kiro-cli update --check
```

### Combining CLI updates with network controls

Pair the `update.baseUrl` policy with [firewall rules](https://kiro.dev/docs/privacy-and-security/firewalls.md) so Kiro CLI can only reach your mirror. Block outbound access to the default CLI download endpoints and allow your mirror's host instead:

- `prod.download.cli.kiro.dev` — CLI downloads and updates
- `desktop-release.q.us-east-1.amazonaws.com` — CLI installer downloads

Blocking the default download endpoints prevents Kiro CLI's built-in updater and installer from falling back to them. Use additional software-distribution controls if your organization must prevent users from installing releases through other sources.
