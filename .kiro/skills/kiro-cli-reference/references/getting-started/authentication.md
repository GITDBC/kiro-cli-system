> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Authentication

> Sign in to Kiro using GitHub, Google, AWS Builder ID, IAM Identity Center, or your organization's identity provider

Kiro supports several authentication providers across all surfaces:

| Provider | IDE | CLI | Web | Mobile |
|----------|:---:|:---:|:---:|:------:|
| GitHub | ✓ | ✓ | ✓ | ✓ |
| Google | ✓ | ✓ | ✓ | ✓ |
| AWS Builder ID | ✓ | ✓ | ✓ | ✓ |
| AWS IAM Identity Center | ✓ | ✓ | ✓ | ✓ |
| External identity provider | ✓ | ✓ | ✓ | ✓ |
| API key (CI/headless) | | ✓ | | |

**ℹ️ Info:** Users with a paid Kiro subscription who access it through a social login provider (like GitHub or Google) or through AWS Builder ID are considered *individual subscribers*. We may use certain content from Kiro Free Tier and Kiro individual subscribers for service improvement. For more information on service improvement and how to opt out, see [Service improvement](https://kiro.dev/docs/privacy-and-security/data-protection.md#service-improvement).

## Sign in to Kiro

The providers work the same way everywhere, and sign-in completes in the browser:

- **GitHub, Google, and AWS Builder ID** — choose the provider, authenticate in your browser, and authorize the Kiro app (on GitHub, the app to authorize appears as **kirodotdev**).
- **AWS IAM Identity Center** — you'll need the **Start URL** and the **AWS Region** that hosts your identity directory, provided by your admin or help desk.
- **External identity provider** — choose **Your organization**, enter your work email to find your organization, then complete sign-in with your organization's identity provider. This is also the path for [AWS GovCloud (US) regions](#aws-govcloud-us-regions).

How you launch the flow differs per surface:

    IDE
    CLI
    Web
    Mobile

    1. On the welcome screen, choose your sign-in provider (or **Your organization** for an external identity provider). Kiro redirects to your default web browser to complete the sign-in process.
    2. For **AWS IAM Identity Center**, enter the Start URL and Region when prompted, then choose **Continue**.
    3. Complete authentication in the browser and authorize the Kiro app. You're returned to the IDE signed in.

    1. At the command line, enter `kiro-cli` or `kiro-cli login`. You are prompted to press Enter to complete sign-in in your browser.
    2. In your browser, choose your provider and authenticate. For remote machines without a browser, see [Remote machine authentication](#remote-machine-authentication-cli).
    3. After you authenticate, you receive a message in your browser directing you back to your terminal, where you're signed in.

    1. Navigate to [app.kiro.dev](https://app.kiro.dev) and sign in with your provider.
    2. Ensure you have a paid Kiro subscription (Pro or higher). Kiro Web is not available on the free tier.
    3. [Connect GitHub](#connect-github-web) to give the agent access to your repositories.

    If your organization uses **AWS Identity Center**: your administrator must enable the Kiro Web agent first, and Kiro Web requires a Kiro Profile — it does not work with Q Developer Profiles. See the [AWS Identity Center guide](https://kiro.dev/docs/web/identity-center.md) for details on shared settings and limitations.

    Sign in with the same account you use on other surfaces. Your sessions and preferences sync automatically between Kiro Web and iOS.

## Remote machine authentication (CLI)

When running Kiro CLI on a remote machine (via SSH, SSM, containers, etc.), authentication works differently since the remote machine cannot open a browser.

### Device flow

Builder ID, IAM Identity Center, Google, and GitHub support device flow authentication in remote environments. The CLI displays a URL and a one-time code that you enter in any browser - no port forwarding required.

**ℹ️ Info:** External identity provider (IdP) login is not currently supported with device flow authentication.

1. Run `kiro-cli login` and select your sign-in method (for example, **Use with Builder ID**, **Use with Google**, **Use with GitHub**, or **Use with Your Organization**).
2. The CLI displays a URL and a one-time code.
3. Open the URL in any browser (on your local machine, phone, or another device).
4. Enter the code and complete authentication.
5. The CLI detects the successful login automatically.

## API key authentication (CLI)

For CI/CD pipelines and automation scripts, you can authenticate using an API key instead of interactive sign-in.

**ℹ️ Info:** API key based authentication is only available for Kiro Pro, Pro+, Pro Max, and Power subscribers. If you are using a subscription managed by an administrator, your Kiro admin needs to enable API key authentication first. See [API key governance](https://kiro.dev/docs/enterprise/governance/api-keys.md).

### Generate an API key

1. Sign in to [app.kiro.dev](https://app.kiro.dev) with your Kiro Pro, Pro+, Pro Max, or Power account.
2. Navigate to the **API Keys** section.
3. Create a new API key and copy it. The full key value is only shown at creation time. Set a meaningful name to remember the context of the key.

**⚠️ Warning:** API keys are long-lived credentials. Store them securely and rotate them according to your organization's credential policy. If a key is compromised, revoke it immediately in the Kiro web console.

### Use the API key

Set the `KIRO_API_KEY` environment variable and run Kiro CLI in non-interactive mode:

```bash
export KIRO_API_KEY=ksk_xxxxxxxx
kiro-cli chat --no-interactive "your prompt here"
```

On Windows:

```powershell
$env:KIRO_API_KEY = "ksk_xxxxxxxx"
kiro-cli chat --no-interactive "your prompt here"
```

API key authentication supports all Kiro CLI features available in non-interactive mode. For interactive sessions, use browser-based sign-in instead. For CI/CD pipelines, automation scripts, and detailed headless usage, see [Headless mode](https://kiro.dev/docs/cli/headless.md).

### Authentication precedence

When multiple credentials are available, Kiro CLI uses this precedence order:

1. Active browser session (from `kiro-cli login`)
2. `KIRO_API_KEY` environment variable
3. No credentials - CLI prompts you to sign in

To check which authentication method is active, run `kiro-cli whoami`. Credits consumed using the API key are decremented from your subscription credits.

## Connect GitHub (Web)

Connect your GitHub account to give the agent access to your repositories:

1. Go to [Settings](https://app.kiro.dev/settings/agent) and select the **Agent** tab.
2. Under **GitHub**, click **Connect GitHub**.
3. Authorize the Kiro Agent GitHub app.
4. Select which repositories the agent can access.

You must have write permissions on repositories for the agent to create branches and open pull requests.

**How repository access works:** Kiro Web shows all repositories where both conditions are met:
1. Your GitHub user has access to the repository.
2. The Kiro Agent GitHub app has been installed and authorized for that repository.

This means you see repositories from personal accounts, shared repositories, and organizations - as long as both your GitHub user and the Kiro Agent app have access.

See the [GitHub integration guide](https://kiro.dev/docs/web/github.md) for detailed setup instructions.

## AWS GovCloud (US) regions

**ℹ️ Info:** The authentication methods supported in AWS GovCloud (US) regions are AWS IAM Identity Center and external identity providers. Social login methods such as GitHub, Google, and AWS Builder ID are not available in AWS GovCloud (US) regions.

To use Kiro with AWS GovCloud (US):

- Ensure the Start URL used during authentication contains "us-gov-home", for example: `https://start.us-gov-home.awsapps.com/directory/d-XXXXXXXXXX`
- Kiro uses the same download/installer for both commercial and AWS GovCloud (US) regions. IAM Identity Center authentication automatically routes traffic to the appropriate AWS GovCloud (US) region.
- Kiro IDE version 0.9.2+ and Kiro CLI version 1.25.0+ are required for AWS GovCloud (US) regions support.

## Sign out

    IDE
    CLI
    Web
    Mobile

    To sign out of Kiro IDE, open the command palette and run **Kiro: Sign Out**.

    At the command line, enter `kiro-cli logout`.

    Click your profile icon in the top-right corner and select **Sign out**.

    Coming soon.

## Troubleshooting

If you encounter problems during the authentication process, such as browser redirect failures or sign-in errors, check the [troubleshooting guide](https://kiro.dev/docs/ide/troubleshooting.md#authentication-issues) for platform-specific solutions and common fixes.

## Next steps

- [Set up your first project](https://kiro.dev/docs/getting-started/first-project.md)
- [Explore privacy and data protection](https://kiro.dev/docs/privacy-and-security/data-protection.md)
- [Configure enterprise identity providers](https://kiro.dev/docs/enterprise/identity-provider.md)
