> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Connect your Microsoft Entra ID IdP

> How to connect Microsoft Entra ID with Kiro.

Connecting Microsoft Entra ID to Kiro takes about 30–45 minutes. You'll create an Entra application, configure a Kiro profile in the AWS console, and set up SCIM provisioning so user and group assignments sync automatically.

**Before you start**, have these open:
- The [Microsoft Entra admin center](https://entra.microsoft.com/) (requires Application Administrator or higher)
- The [AWS Management Console](https://console.aws.amazon.com/) with [Kiro admin permissions](https://kiro.dev/docs/privacy-and-security/iam-permissions.md)

AWS access is only needed for the administrator managing the Kiro profile — end users don't need an AWS account.

The integration connects two systems:

- **Microsoft Entra ID** — manages identity. You define which users and groups can access Kiro here.
- **Kiro profile** (in the AWS console) — manages subscriptions and billing.

SCIM provisioning connects them: you provide a SCIM endpoint and token from Kiro to Entra, and the Application (client) ID and Directory (tenant) ID from Entra to Kiro.

## Step 1: Create an application for Kiro

Sign in to the [Microsoft Entra admin center](https://entra.microsoft.com/), then create a new application from *Enterprise applications -> New application*. In the Microsoft Entra App Gallery, select "Create your own application".

![identity store selection](https://kiro.dev/images/enterprise/Entra-application-gallery.png)

Set a descriptive name, for example, **Kiro-Entra**. Then, select the **"Integrate any other application you don't find in the gallery (Non-gallery)"** option for the "What are you looking to do with your application?" field, and select "Create" to create the application.

![Entra create custom application](https://kiro.dev/images/enterprise/Entra-create-application.png)

## Step 2: Configure the Kiro application

Configure the application so user identities can present the right authorization to access Kiro.

### Expose API endpoint

Kiro syncs user identities through the application's API endpoint. For the "Kiro-Entra" application (*App registrations -> All applications -> Kiro-Entra*), select "Expose an API", then select "Add" next to the "Application ID URI" field and save the default value. Next, add two scopes that define the permissions an identity must present to Kiro.

![identity store selection](https://kiro.dev/images/enterprise/Entra-application-expose-api.png)

**ℹ️ Scope reference:** Both scopes are required for full Kiro functionality. `codewhisperer:completions` enables inline code suggestions; `codewhisperer:conversations` enables chat.

Add the first scope, which gives users access to inline code completion:

- **Scope Name**: codewhisperer:completions
- **Who can consent?**: Admins and Users
- **Admin consent display name**: codewhisperer:completions
- **Admin consent description**: codewhisperer:completions
- **State**: Enabled

![Endpoint add scope](https://kiro.dev/images/enterprise/Entra-add-scope.png)

Add the second scope, which gives users access to chat:
- **Scope Name**: codewhisperer:conversations
- **Who can consent?**: Admins and Users
- **Admin consent display name**: codewhisperer:conversations
- **Admin consent description**: codewhisperer:conversations
- **State**: Enabled

After you have completed adding the scopes, "Expose an API" page should look like this:
![identity store selection](https://kiro.dev/images/enterprise/Entra-endpoint-scopes.png)

### Add a redirect URI

A redirect URI is where Entra sends the user and delivers tokens after authentication.

For the Kiro application, select **Authentication**, then under **Redirect URI configuration**, select **Add Redirect URI**. Choose **Mobile and desktop application**, and add `kiro://kiro.oauth/callback` and `http://localhost/oauth/callback`, selecting **Configure** after each.

To support Kiro Web, add a separate redirect URI:

1. Under **Redirect URI configuration**, select **Add Redirect URI**.
2. Under **Web app**, choose **Single-page application**.
3. Add `https://app.kiro.dev/signin/oauth`.

**ℹ️ Existing Kiro app registrations:** If you already configured Kiro with Microsoft Entra ID, open the Kiro app registration and go to **Authentication > Redirect URI configuration > Add Redirect URI**. Under **Web app**, choose **Single-page application** and add `https://app.kiro.dev/signin/oauth`. Keep this separate from the existing **Mobile and desktop application** redirects.

After adding the redirect URIs, the page should look like this:

![identity store selection](https://kiro.dev/images/enterprise/Entra-redirect-uri.png)

### Set Access Token version

Last, set the access token format that Kiro will request. By default, Entra ID issues v1-format access tokens. Kiro requires v2-format tokens. In the App Registration, select **Manifest** from the left navigation. Find the `requestedAccessTokenVersion` field under the `api` section and set its value to `2`. Select **Save**.

![identity store selection](https://kiro.dev/images/enterprise/Entra-access-token-version.png)

**ℹ️ Values you'll need for Step 3:** Before proceeding, note the **Application (client) ID** and **Directory (tenant) ID** from the application's Overview page — you'll need these when creating the Kiro profile.

These values, along with the SCIM endpoint and access token you'll generate in Step 4, are the key credentials that connect Entra to Kiro:

| Value | Source | Used in |
|---|---|---|
| Application (client) ID | Entra → App registrations → Overview | Kiro profile creation |
| Directory (tenant) ID | Entra → App registrations → Overview | Kiro profile creation |
| SCIM Endpoint | Kiro → Settings → Identity Management | Entra provisioning config |
| Access Token | Kiro → Settings → Identity Management → Access Tokens | Entra provisioning config |

Now, you are ready to set up the Kiro profile.

## Step 3: Set up the Kiro profile

**ℹ️ Prerequisites:** Creating a Kiro profile requires specific AWS IAM permissions. See [IAM permissions](https://kiro.dev/docs/privacy-and-security/iam-permissions.md) for the required permissions to create profiles and manage subscriptions.

Setting up the Kiro profile and connecting it to your Microsoft Entra ID IdP consists of two steps:

- Configure your Microsoft Entra ID application details in Kiro
- Add and verify your domain in Kiro

### Create the Kiro profile

In the AWS Management Console, search for **Kiro** and open the Kiro service. Select **Onboard your team to Kiro**. In the **Select your identity management source** dialog, choose **External Identity Provider** to connect an existing external identity provider, then select **Next**.

![Kiro create profile](https://kiro.dev/images/enterprise/Entra-IdP-selection.png)

In the **Welcome to Kiro!** dialog, select an identity provider from the dropdown. The currently supported providers are Microsoft Entra ID and Okta. Choose **Microsoft Entra ID**. The dialog then shows **Application ID** and **Tenant ID** fields, which you'll fill in with values from your Entra application.

To find those values, go to Microsoft Entra and select *App registrations -> All applications -> Kiro-Entra*. This opens the "Overview" tab.

![identity store endpoints](https://kiro.dev/images/enterprise/Entra-Kiro-app-overview.png)

First, copy the **Application (client) ID** field value and paste it into the **Application ID** field in the Kiro profile you are creating. Copy the **Directory (tenant) ID** into the **Tenant ID** field in the Kiro profile, then select **Enable** to create the profile.

If you configure a customer managed KMS key to encrypt the data for your external identity provider, you must add the following statements to your key policy so that Kiro can access the users and groups provisioned through SCIM.

```json
{
    "Sid": "AllowKiroToUseKey",
    "Effect": "Allow",
    "Principal": {
        "Service": "q.amazonaws.com"
    },
    "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:GenerateDataKeyWithoutPlaintext",
        "kms:DescribeKey"
    ],
    "Resource": "*"
},
{
    "Sid": "AllowIdentityStoreToUseKey",
    "Effect": "Allow",
    "Principal": {
        "Service": "identitystore.amazonaws.com"
    },
    "Action": [
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:GenerateDataKeyWithoutPlaintext",
        "kms:ReEncryptTo",
        "kms:DescribeKey",
        "kms:ReEncryptFrom"
    ],
    "Resource": "*"
}
```

### Add and verify domain

**⚠️ Important configuration requirement:** To connect your Microsoft Entra ID with Kiro, you have to verify ownership of your company domain by adding a TXT record in your DNS provider. This ensures that no unauthorized party can associate your domain with their own Kiro profile and intercept user sign-ins.

Select the "Settings" button and in the *Identity management -> Domains* section, select "Add domain" to add your company domain

![Add company domain](https://kiro.dev/images/enterprise/Kiro-profile-add-domain.png)

Selecting "Add" will add the domain and show you a verification token. Copy the verification token. The domain added will show up in the Domains list with "Pending" status. 

In your DNS Provider like Amazon Route53, create a TXT record with that verification token within **24 hours** of adding the domain. You can publish the record at **either** of two locations:

- The **exact domain you added in Kiro** (the apex — for example, `yourdomain.com`), or
- The **`_kiro-challenge` subdomain** of that domain (for example, `_kiro-challenge.yourdomain.com`). Use this if your organization's DNS policy does not allow a permanent TXT record at the apex domain.

Set the record value to the verification token shown in Kiro (for example, `kiro-site-verification=<your-token>`). Kiro checks both locations, so you only need to add the record in one of them. Do **not** use any other subdomain prefix (such as `kiro-app-1.`) — only the exact domain and the `_kiro-challenge` prefix are checked, and any other prefix will not verify. If the domain is not verified within 24 hours, it returns to an unregistered state and must be re-added (which issues a new token).

![Add DNS record](https://kiro.dev/images/enterprise/Entra-create-DNS-record.png)

If the configuration is valid, after a few minutes the status will be "Verified".

![Domain verified](https://kiro.dev/images/enterprise/Entra-Kiro-domains.png)

**⚠️ Domain verification requires a publicly resolvable domain:** Domain verification performs a **public DNS lookup** for the TXT record, so the domain you verify must be publicly resolvable. Private or internal TLDs (for example, `.local`, `.internal`, or a custom private TLD) are **not supported** — they return `NXDOMAIN` on a public DNS lookup, and the domain stays in "Pending" status indefinitely.

#### Workarounds for private or internal domains

If your organization uses a private or internal domain for its infrastructure, use one of the following approaches:

- **Verify a publicly resolvable domain or subdomain that you control.** Add the TXT record to a domain (or subdomain) that resolves on public DNS, and verify that domain instead of the private one.
- **Register the public domain your users sign in with.** If your users sign in with email addresses on a public domain, add that public domain to the Kiro profile. When a user enters their email (with the public domain) and selects login, Kiro redirects them to the Entra ID login page — regardless of your internal infrastructure domain.

**ℹ️ Privacy consideration:** Kiro does not allow a domain to be associated with more than one profile, regardless of verification status. This means a third party could attempt to add your domain to their own profile and, based on the rejection, infer that the domain is already associated with another Kiro profile. This does not grant them any access, but it does reveal that the domain has been onboarded to Kiro.

**ℹ️ Domain configuration notes:** A Kiro profile supports at most **10 domains**. The domain you configure here exists solely to identify your Kiro profile. When a user enters an email on the Kiro sign-in page, the backend looks at the domain portion of that email and uses it to look up the associated Kiro profile and its Microsoft Entra ID application. The email address itself does not need to exist in your Entra directory, and it does not need to match the identity the user ultimately authenticates with in Entra. It is only used for profile lookup.

## Step 4: Provision Kiro application

In this step, you will provision the Kiro application and verify that Kiro can sync identities from your Entra ID identity store.

### Set up provisioning

**In the Kiro console** — Navigate to *Settings → Identity Management*. In the Access Tokens section, select **Generate Token** and copy the token value, then copy the **SCIM Endpoint** URL from the same page.

**⚠️ SCIM token security:** The access token is shown only once. Copy it immediately — it cannot be recovered later, though you can generate a new one at any time. A Kiro profile supports a maximum of **2 access tokens**; if you reach the limit, revoke one before generating another. Treat the token as a password: it's a long-lived credential. Tokens are not automatically rotated — rotate them per your organization's policy. If compromised, revoke it immediately at *Settings → Identity Management → Access Tokens* and regenerate.

![Generate access token for provisioning](https://kiro.dev/images/enterprise/Entra-Kiro-Profile-access-token.png)

**In the Entra admin center** — Navigate to *Enterprise Apps → Kiro-Entra → Provisioning*. Select the **Provisioning** link from the sidebar, then set **Provisioning Mode** to **Automatic**.

- Paste the SCIM endpoint into the **Tenant URL** field
- Paste the access token into the **Secret Token** field

![Application provisioning](https://kiro.dev/images/enterprise/Entra-provisioning-config.png)

Select **Test Connection** to validate. If successful, select **Save**. If a **Provisioning Status** toggle is present, set it to **On**.

![Application provisioning success](https://kiro.dev/images/enterprise/Entra-provisioning-success.png)

![Application provisioning success](https://kiro.dev/images/enterprise/Kiro-profile-token-list.png)

After saving, **refresh the Entra ID application page** — the attribute mapping links will not appear until you do.

### Add attribute mapping

With the sidebar links enabled, open the "Attribute mapping (Preview)" section. Both Provision Groups and Provision Users should be enabled.

![Provisioning attribute mapping](https://kiro.dev/images/enterprise/Entra-attribute-mapping.png)

Select the "Provision Microsoft Entra ID Users" link to open the "Attribute Mapping" page. Select the "Edit" button for the "externalId" attribute to open the "Edit Attribute" page. Set the Source attribute value to "objectId" and save the configuration. "objectId" uniquely identifies a user or group and doesn't change, making it easy for Kiro to identify and synchronize users/groups.   

![Edit external Id attribute mapping](https://kiro.dev/images/enterprise/Entra-edit-attribute.png)

### Remove unsupported attributes

Entra auto-populates several attributes Kiro's SCIM endpoint does not support. **If left in place, provisioning will fail.** Delete the following from the attribute mapping table:

**Enterprise User Extension attributes (delete these):**
- `urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:employeeNumber`
- `urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:department`
- `urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:manager`

**Phone number attributes (delete these):**
- `phoneNumbers[type eq "work"].value`
- `phoneNumbers[type eq "mobile"].value`
- `phoneNumbers[type eq "fax"].value`

Select each attribute row and choose **Delete**. Save the mapping when done.

**ℹ️ Minimum required attributes:** If provisioning errors persist, check *Entra → Enterprise Apps → Kiro-Entra → Provisioning → Provisioning logs* for attribute-level failures. As a fallback, the only three mappings Kiro requires are `userName`, `externalId`, and `active` — all other attribute mappings can be deleted to isolate the issue.

## Step 5: Add users and groups 

**⚠️ Avoid direct user assignment:** Add users to Kiro by assigning them to a **group** that is then assigned to the application — do not assign individual users directly to the Entra application. After configuring subscriptions, review the Subscriptions tab in the Kiro console to confirm no unintended users received a seat.

Choose which users and groups to synchronize from the Entra application to Kiro. The selected users and groups become available to associate with a Kiro subscription in the Kiro profile.

In the Entra admin center, navigate to your Kiro application → **Users and groups** → select **+ Add user/group**. Assign the groups (or individual users) that should have access to Kiro.

To view users and groups automatically provisioned, navigate to the "Users and groups" section in the Entra ID application. It may take some time for users and groups to appear on their own. Refer to [Entra documentation](https://learn.microsoft.com/en-us/entra/identity/app-provisioning/check-status-user-account-provisioning#provisioning-progress-bar) for tracking the progress of the provisioning process.

To manually provision, navigate to "Provisioning" page and select "Provision On Demand" under "Quick Actions" section.

![Add users/group](https://kiro.dev/images/enterprise/Entra-on-demand-provisioning.png)

If you are provisioning a group, make sure you select all the users in the group. After you have successfully configured the group and the users in the group, you will see a success screen.

![Add users/group success](https://kiro.dev/images/enterprise/Entra-manual-provisioning-success.png)

Repeat the steps to add all the users and groups you want to synchronize with Kiro. 

**ℹ️ Info:** Sometimes provisioning might fail on first attempt, but retries are usually successful.

You have completed all configuration steps for Microsoft Entra ID.

**ℹ️ When will users appear?:** After assignment, allow up to 6 hours 40 minutes before users are available in your Kiro console: Entra pushes user data within ~40 minutes, then Kiro's provisioning cycle (which runs every 6 hours) creates the subscription.

When users appear in your Kiro console, follow the [subscription guide](https://kiro.dev/docs/enterprise/subscribe.md) to activate them.

## Security considerations

**Session management**

- Kiro uses OIDC refresh tokens to maintain user sessions. When a session expires, the refresh token keeps the Kiro session alive independently until the refresh token itself expires.
- You cannot force-revoke active user sessions from the Kiro console. To remove access, you have to remove the user from the Entra application — access will be revoked at the next token refresh attempt.
- Go to *Enterprise apps > your application > Users and Groups*. Select the user, then remove assignment

**Redirect URI security**

- Add only the redirect URIs specified in this guide. 

**Profile deletion warning**

If you delete a Kiro profile after provisioning and create a new profile with the same Entra application, group membership will not be synced. You must re-provision the application completely.

**Preventing unauthorized access**

- Do not add any user to the Kiro application in Entra.
- Verify the user is not a member of any group that is assigned to the Kiro application.
- After creating a group-based subscription, review the Subscriptions tab in the Kiro console to confirm that no unintended users received a subscription.

**Removing a user and deprovisioning behavior**

- Remove the user's assignment from your Kiro application in Entra. This blocks all future login attempts.
- Existing sessions remain active until the next token refresh is attempted, at which point access is revoked. Active sessions are not immediately terminated.
- Subscription removal is not automatic. After removing a user from the Entra application, you must also manually delete the user's subscription in the Kiro console to release the seat.

**Group membership sync behavior**

- Kiro relies entirely on push-based SCIM sync from Entra. Kiro cannot request a pull from Entra.
- Group membership changes are pushed approximately every 40 minutes. Admins can trigger an immediate sync by using "Provision on Demand" in the Entra console.
- SCIM provisioning triggers on any user or group update in Entra — not just new additions. Edits to existing users or groups will also push a sync.

## Troubleshooting

| Missed step | How will this manifest | How to fix | Notes |
|--|--|--|--|
| Did not set access token version to 2 in manifest	| After login, API calls will fail with authorization errors	| In App registrations, edit the Manifest and set api.requestedAccessTokenVersion to 2 |	Entra defaults to v1 access tokens; Kiro requires v2 |
|	Did not set scopes in Expose an API	| Login screen will show an error	| Add codewhisperer:completions and codewhisperer:conversations scopes in Expose an API |	Both scopes are required |
|	Did not set attribute mapping in provisioning	| After login, user would not have a subscription (API calls fail) |	In Attribute Mapping, set externalId source attribute to objectId. Delete ALL subscriptions and re-provision.	| objectId is the stable unique identifier |
|	Did not set redirect URIs	| Login attempts show an error screen	| Add the required localhost redirect URIs in Authentication settings	| See the setup guide for the full list of ports |
|	Did not provision on demand	| Users/groups do not appear in the Kiro console |	Navigate to Provisioning and select "Provision on Demand" |	Automatic sync can take up to 40 minutes |
|	Deleted profile after provisioning, created new profile with same app |	Group membership is not synced |	Re-provision the application from scratch with a new SCIM token |	See Profile deletion warning above |
|	Used a private or internal TLD for domain verification |	Domain stays in "Pending" status and never verifies |	Verify a publicly resolvable domain or subdomain instead, or register the public email domain your users sign in with |	Verification performs a public DNS lookup; private TLDs return NXDOMAIN |

## Related resources

- [Subscribe team members](https://kiro.dev/docs/enterprise/subscribe.md) — Activate users after provisioning
- [IAM permissions](https://kiro.dev/docs/privacy-and-security/iam-permissions.md) — Required AWS permissions for profile management
- [Microsoft Entra provisioning documentation](https://learn.microsoft.com/en-us/entra/identity/app-provisioning/check-status-user-account-provisioning) — Track provisioning progress
