> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Configuring a firewall, proxy server, or data perimeter for Kiro

> Allowlist the URLs and configure proxy settings that Kiro needs to connect to its backend services.

If your network uses a firewall, proxy server, or [data perimeter](https://aws.amazon.com/identity/data-perimeters-on-aws/), you need to allowlist specific URLs so Kiro can reach its backend services. This page lists every domain Kiro contacts, grouped by function.

## Network traffic overview

Kiro makes two types of outbound connections:

- **Application traffic** — Requests from the Kiro process (chat, completions, telemetry, and updates in IDE/CLI). In the IDE and CLI, this traffic respects your [proxy settings](#proxy-configuration). In Kiro Web, it flows through backend services.
- **Browser traffic** — Sign-in opens your default browser. This traffic uses your OS network stack and bypasses any proxy settings configured in the IDE or CLI.

Your firewall must allow both at the network level.

## Core URLs

The following URLs are required by all Kiro products (IDE, CLI, and Web):

| URL | Purpose |
|-----|---------|
| `app.kiro.dev` | Sign-in portal |
| `assets.app.kiro.dev` | Application assets |

### Surface-specific URLs

    IDE
    CLI
    Web

    Every Kiro IDE installation also needs the following URLs. These cover chat and code assistance, telemetry, and auto-updates.

    | URL | Purpose |
    |-----|---------|
    | `prod.us-east-1.auth.desktop.kiro.dev` | Token exchange, refresh, and logout |
    | `prod.us-east-1.telemetry.desktop.kiro.dev` | Telemetry |
    | `prod.download.desktop.kiro.dev` | Auto-updates, Powers registry, and icons |
    | `q.us-east-1.amazonaws.com` | Kiro service (US East) |
    | `q.eu-central-1.amazonaws.com` | Kiro service (Europe) |
    | `runtime.us-east-1.kiro.dev` | Kiro service (US East) |
    | `runtime.eu-central-1.kiro.dev` | Kiro service (Europe) |
    | `management.us-east-1.kiro.dev` | Configuration, access management (US East) |
    | `management.eu-central-1.kiro.dev` | Configuration, access management (Europe) |
    | `telemetry.us-east-1.kiro.dev` | Telemetry (US East) |
    | `telemetry.eu-central-1.kiro.dev` | Telemetry (Europe) |

    Every Kiro CLI installation also needs the following URLs. These cover chat and code assistance, telemetry, and auto-updates.

    | URL | Purpose |
    |-----|---------|
    | `cli.kiro.dev` | CLI application |
    | `prod.us-east-1.auth.desktop.kiro.dev` | Token exchange, refresh, and logout |
    | `prod.us-east-1.telemetry.desktop.kiro.dev` | Telemetry |
    | `prod.download.desktop.kiro.dev` | Auto-updates, Powers registry, and icons |
    | `prod.download.cli.kiro.dev` | CLI downloads and updates |
    | `desktop-release.q.us-east-1.amazonaws.com` | CLI installer downloads |
    | `q.us-east-1.amazonaws.com` | Kiro service (US East) |
    | `q.eu-central-1.amazonaws.com` | Kiro service (Europe) |
    | `runtime.us-east-1.kiro.dev` | Kiro service (US East) |
    | `runtime.eu-central-1.kiro.dev` | Kiro service (Europe) |
    | `management.us-east-1.kiro.dev` | Configuration, access management (US East) |
    | `management.eu-central-1.kiro.dev` | Configuration, access management (Europe) |
    | `telemetry.us-east-1.kiro.dev` | Telemetry (US East) |
    | `telemetry.eu-central-1.kiro.dev` | Telemetry (Europe) |

    Every Kiro Web deployment also needs the following URLs. These cover AI services and telemetry.

    | URL | Purpose |
    |-----|---------|
    | `kaa-assets.app.kiro.dev` | Agent application assets |
    | `kiro.dev` | Kiro website and documentation |
    | `prod.us-east-1.auth.desktop.kiro.dev` | Token exchange, refresh, and logout |
    | `kiro-prod-us-east-1.auth.us-east-1.amazoncognito.com` | Cognito authentication |
    | `management.us-east-1.kiro.dev` | Configuration, access management |
    | `q.*.amazonaws.com` | Kiro service endpoints |
    | `prod.us-east-1.telemetry.kiro.aws.dev` | Telemetry and metrics |
    | `prod.download.desktop.kiro.dev` | Downloads and updates |
    | `a0.awsstatic.com` | AWS static assets |
    | `dataplane.rum.us-east-1.amazonaws.com` | CloudWatch RUM (US East) |
    | `dataplane.rum.eu-central-1.amazonaws.com` | CloudWatch RUM (Europe) |
    | `prod.assets.shortbread.aws.dev` | Cookie consent assets |
    | `prod.log.shortbread.aws.dev` | Cookie consent logging |
    | `prod.tools.shortbread.aws.dev` | Cookie consent tools |
    | `rendering.aperture-public-api.feedback.console.aws.dev` | Feedback form |

**⚠️ Legacy endpoints still required:** The `q.<region>.amazonaws.com` endpoints are legacy and will be deprecated in a future release. Until deprecation is complete, you must still allowlist them alongside the `runtime`, `management`, and `telemetry` endpoints.

If your network policy allows wildcard rules, you can allowlist `*.kiro.dev` and `*.app.kiro.dev` instead of the individual `kiro.dev` domains above. Note that some firewalls only match a single subdomain level, so `*.kiro.dev` would cover `app.kiro.dev` but not `assets.app.kiro.dev`. If your firewall behaves this way, also add `*.app.kiro.dev` or list multi-level subdomains explicitly. See [Wildcard rules](#wildcard-rules) for a complete summary.

## Social sign-in

If you sign in with Google or GitHub, allowlist this additional endpoint for the Cognito identity federation flow.

| URL | Purpose |
|-----|---------|
| `cognito-identity.us-east-1.amazonaws.com` | Federated identity for social sign-in |

## IAM Identity Center

If your organization uses AWS IAM Identity Center for authentication, allowlist these additional endpoints.

Replace `idc-directory-id-or-alias` with your IAM Identity Center instance's directory ID or alias, and `sso-region` with the AWS Region where your instance is enabled. For more information, see [What is IAM Identity Center?](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html) in the IAM Identity Center User Guide.

| URL | Purpose |
|-----|---------|
| `<region>.signin.aws` | AWS sign-in |
| `<sso-region>.signin.aws.amazon.com` | AWS sign-in (alternate) |
| `<idc-directory-id-or-alias>.awsapps.com` | IAM Identity Center portal |
| `portal.sso.<sso-region>.amazonaws.com` | SSO portal |
| `assets.sso-portal.<sso-region>.amazonaws.com` | SSO portal assets |
| `oidc.<sso-region>.amazonaws.com` | OIDC token exchange |

### External identity providers

If your organization uses an external identity provider (IdP) with IAM Identity Center, the sign-in flow redirects through your IdP's domain. You need to allowlist that domain too.

| Identity provider | Domain to allowlist |
|-------------------|---------------------|
| Microsoft Entra ID | `login.microsoftonline.com` |
| Okta | `<your-org>.okta.com` |

Check with your identity team for the exact domain if you are unsure which IdP is configured.

### AWS GovCloud (US)

If you use Kiro in AWS GovCloud (US), allowlist these FIPS endpoints for each Region your organization uses:

| URL | Purpose |
|-----|---------|
| `runtime-fips.us-gov-east-1.kiro.dev` | Kiro service, AWS GovCloud (US-East) |
| `runtime-fips.us-gov-west-1.kiro.dev` | Kiro service, AWS GovCloud (US-West) |
| `management-fips.us-gov-east-1.kiro.dev` | Configuration and access management, AWS GovCloud (US-East) |
| `management-fips.us-gov-west-1.kiro.dev` | Configuration and access management, AWS GovCloud (US-West) |

**⚠️ Keep existing Q endpoint rules:** Add these FIPS endpoints alongside your existing `q` or `q-fips` rules. Older Kiro client versions may still require those Q endpoints.

## Subscription management

If you sign in with Google, GitHub, or AWS Builder ID, Kiro uses Stripe for subscription billing. Allowlist these domains to access the billing portal and upgrade plans.

| URL | Purpose |
|-----|---------|
| `billing.stripe.com` | Billing portal for paid plans |
| `checkout.stripe.com` | Checkout for plan upgrades |

Enterprise customers using IAM Identity Center don't need these domains.

## Optional URLs

You only need these if you use the corresponding Kiro feature. Skip any that don't apply to your environment.

    IDE
    CLI

    | URL | Feature | Purpose |
    |-----|---------|---------|
    | `open-vsx.org` | [Extensions](https://open-vsx.org/) | Search and metadata |
    | `openvsx.eclipsecontent.org` | Extensions | Icons and VSIX downloads |
    | `github.com` | [Powers](https://kiro.dev/docs/powers.md) / MCP | Repository cloning |
    | `raw.githubusercontent.com` | Powers / MCP | Config files and readme images |

    | URL | Feature | Purpose |
    |-----|---------|---------|
    | `github.com` | MCP | Repository cloning |
    | `raw.githubusercontent.com` | MCP | Config files and readme images |

## Proxy configuration

    IDE
    CLI

    Kiro respects standard proxy environment variables for all IDE traffic:

    - `HTTP_PROXY`
    - `HTTPS_PROXY`
    - `NO_PROXY`

    You can also configure proxy settings in **Settings > Proxy** inside Kiro.

    
**⚠️ Browser-based sign-in bypasses proxy settings:** When you sign in, Kiro opens your default browser to `app.kiro.dev`. This browser traffic uses your operating system's network stack, not the IDE's proxy configuration. Your firewall must allow the [IAM Identity Center URLs](#iam-identity-center) and `app.kiro.dev` at the network level regardless of how the IDE proxy is configured.

    Kiro respects standard proxy environment variables for all CLI traffic:

    - `HTTP_PROXY`
    - `HTTPS_PROXY`
    - `NO_PROXY`

    
**⚠️ Browser-based sign-in bypasses proxy settings:** When you sign in, Kiro opens your default browser to `app.kiro.dev`. This browser traffic uses your operating system's network stack, not the CLI's proxy configuration. Your firewall must allow the [IAM Identity Center URLs](#iam-identity-center) and `app.kiro.dev` at the network level regardless of how the CLI proxy is configured.

## Troubleshooting connection issues

If some users can connect to Kiro but others cannot, see [Network connectivity issues](https://kiro.dev/docs/ide/troubleshooting.md#network-connectivity-issues) in the troubleshooting guide.

## Data perimeters

If you use [data perimeters on AWS](https://aws.amazon.com/identity/data-perimeters-on-aws/) to restrict access to trusted identities and resources, make sure your policies allow Kiro's service principals to reach the endpoints listed on this page. For VPC-level controls, see [VPC endpoints (AWS PrivateLink)](https://kiro.dev/docs/privacy-and-security/vpc-endpoints.md).

## Wildcard rules

If your network policy allows wildcard rules, you can simplify the allowlist:

| Wildcard | Covers |
|----------|--------|
| `*.kiro.dev` | All single-level Kiro subdomains |
| `*.app.kiro.dev` | Application and CDN assets |
| `*.kiro.aws.dev` | Telemetry endpoints |
| `*.amazonaws.com` | All AWS service endpoints (Kiro service, RUM, OIDC, SSO, Cognito) |
| `*.shortbread.aws.dev` | Cookie consent |
| `*.signin.aws` | IAM Identity Center sign-in |
