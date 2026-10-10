> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Connect your Okta IdP

> How to connect Okta with Kiro.

To connect Okta with your Kiro Profile, you need to:

1. Create the OIDC Okta application  
2. Set up custom scopes for OIDC application
3. Set up Kiro Profile
4. Create the SCIM provisioning application

**⚠️ Important configuration requirement:** To connect your Okta with Kiro, you have to verify ownership of your company domain by adding a TXT record in your DNS provider. This ensures that no unauthorized party can associate your domain with their own Kiro profile and intercept user sign-ins.

## Why two applications
When using Okta, you need to create two applications: one OIDC application for user login, and one SCIM provisioning application (using the AWS IAM Identity Center integration from the Okta App Catalog) for synchronizing users and groups to Kiro.

## Step 1: Create OIDC application

### Create new app integration

In the Okta Admin Console, navigate to the *Applications -> Applications* section and select "Create App integration". Select "OIDC - OpenID Connect" for "Sign-in method", and "Native Application" as the Application type.  

![create app integration](https://kiro.dev/images/enterprise/Okta-create-app-integration.png)

Provide a descriptive name, example **Kiro-OIDC**, for your application and check the "Refresh Token" checkbox in the "Grant type" field. Leave the default values for all other fields. 

First, add `kiro://kiro.oauth/callback` as a Sign-in redirect URI. This is one of the URIs that Kiro clients will listen to when Okta returns the user after they successfully sign in with Okta.

Next, add 10 additional entries as Sign-in redirect URIs in the following format: `http://localhost:/oauth/callback`, where the **port-number** is one of the following port numbers - 3128, 4649, 6588, 8008, 9091, 49153, 50153, 51153, 52153 and 53153.

Add `https://app.kiro.dev/signin/oauth` as another Sign-in redirect URI to support Kiro Web.

**ℹ️ Existing Kiro OIDC applications:** If you already configured Kiro with Okta, go to **Applications > Kiro-OIDC > Edit General Settings > Login > Sign-in redirect URIs**, add `https://app.kiro.dev/signin/oauth`, and select **Save**.

Example:

![set application name](https://kiro.dev/images/enterprise/Okta-OIDC-app-details.png)

Ensure that "Skip group assignment for now" is selected and select "Save" to complete creating the application. This will show the details of the newly created application.

![OIDC application details](https://kiro.dev/images/enterprise/Okta-OIDC-application.png)

### Add users and groups
Next, you will add the users and groups that will be part of the application. Select the "Assignments" tab. Select the "Assign" button and follow the instructions to add users and groups that should have access to Kiro.

![OIDC application assignments](https://kiro.dev/images/enterprise/Okta-OIDC-app-assignments.png)

You have completed creating the OIDC application.

## Step 2: Set up custom scopes

### Create Kiro specific scopes

Now that the OIDC application has been created, you have to set up the scopes to allow user identities to present the right authorization to access Kiro. You will set up two scopes - completions and conversations.

#### Scope authorization

- **codewhisperer:completions** — Authorizes the user to access the inline code completion feature in Kiro.
- **codewhisperer:conversations** — Authorizes the user to access the chat and conversation feature in Kiro.

Only grant the scopes that your organization requires. You should understand the impact of each scope when configuring access policies.

In the Okta Admin console, navigate to the *Security -> API* section. In the "Authorization Servers" tab, select "Add Authorization Server" button.

![Okta API Security](https://kiro.dev/images/enterprise/Okta-security-api.png)

Enter a name and description for the Authorization Server. 

![Okta add authorization server](https://kiro.dev/images/enterprise/Okta-add-authorization-server.png)

Select "Save" to complete adding the server.
![Okta add authorization server](https://kiro.dev/images/enterprise/Okta-auth-server-settings.png)

Select the "Scopes" tab and select the "Add Scope" button to add a scope that authorizes user identities to access a Kiro feature. 

First, add a scope for **codewhisperer:completions** with "User content" value set to "Implicit". Leave all other fields as default. Select "Create" to add the scope.

![Okta add completions scope](https://kiro.dev/images/enterprise/Okta-add-scope-completions.png)

Follow the same steps to add a scope for **codewhisperer:conversations**.

### Add access policies 

Next, you have to add access policies and rules to the Authorization Server to control what Kiro can access through the Kiro OIDC application.

Select the "Access Policies" tab and select the "Add Policy" button.

![Okta access policies](https://kiro.dev/images/enterprise/Okta-access-policies.png)

Set a descriptive name for the policy and assign the policy to the Kiro OIDC application you created - Kiro-OIDC.

![Okta add policy](https://kiro.dev/images/enterprise/Okta-add-policy-general.png)

After the policy is created, select "Add rule" for the newly created policy.

![Okta policy rules](https://kiro.dev/images/enterprise/Okta-policy-rules.png)

Leave the default values for all the fields except for "Scopes requested". Select "The following scopes:" option and add the "codewhisperer:completions", "codewhisperer:conversations" and "offline_access" scopes. Select "Create rule" to complete adding the rule. 

**ℹ️ About offline_access:** The `offline_access` scope allows Kiro to use refresh tokens to maintain user sessions without requiring users to re-authenticate each time their access token expires.

![Okta policy add rule](https://kiro.dev/images/enterprise/Okta-policy-edit-rule.png)

Lastly, test the configuration. To test, select the "Token Preview" tab. Select the OIDC application you created for Kiro (ex: Kiro-OIDC) in the "OAuth/OIDC client" field, select "Authorization Code" as the "Grant type", and select the two codewhisperer scopes, and "offline_access" in the "Scopes" field. Select the "Preview Token" button and if the configuration is valid, the Payload section in the "Preview" panel will contain a "iss" attribute with value, and the "scp" attribute will contain the three scopes you selected.

![Okta token preview](https://kiro.dev/images/enterprise/Okta-token-preview.png)

You have completed all the steps required to configure the applications in Okta. Now you can create the Kiro Profile and subscribe your users and groups.

## Step 3: Set up Kiro Profile

### Create Kiro Profile

In the Kiro console, select "Sign up for Kiro" and select "Set up application as Admin". Select the "Connect an existing external Identity provider" option.

![Kiro Profile configuration](https://kiro.dev/images/enterprise/Okta-IdP-selection.png)

From the Okta Admin Console, navigate to *Security -> API* section and select the Authorization Server that you created for Kiro.

![Okta authorization server URI](https://kiro.dev/images/enterprise/Okta-API-auth-servers.png)

Copy the Issuer URI value for the application you just set up and paste it in the **Issuer URI** field of the Kiro Profile. 

In the Okta Admin Console, navigate to the Applications section, and open the OIDC application that you created for Kiro integration, for example Kiro-OIDC. Copy the Client ID value and paste it in the **Client ID** field of the Kiro Profile.

![Okta OIDC application details](https://kiro.dev/images/enterprise/Okta-OIDC-application.png)

Select "Enable" to complete creating the Kiro Profile. 

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

In the Kiro console, select the "Settings" button and in the *Identity management -> Domains* section, select "Add domain" to add your company domain.

![Add company domain](https://kiro.dev/images/enterprise/Kiro-profile-add-domain.png)

Selecting "Add" will add the domain and show you a verification token. Copy the verification token. The domain added will show up in the Domains list with "Pending" status. 

In your DNS Provider like Amazon Route53, create a TXT record with that verification token within **24 hours** of adding the domain. You can publish the record at **either** of two locations:

- The **exact domain you added in Kiro** (the apex — for example, `yourdomain.com`), or
- The **`_kiro-challenge` subdomain** of that domain (for example, `_kiro-challenge.yourdomain.com`). Use this if your organization's DNS policy does not allow a permanent TXT record at the apex domain.

Set the record value to the verification token shown in Kiro (for example, `kiro-site-verification=<your-token>`). Kiro checks both locations, so you only need to add the record in one of them. Do **not** use any other subdomain prefix (such as `kiro-app-1.`) — only the exact domain and the `_kiro-challenge` prefix are checked, and any other prefix will not verify. If the domain is not verified within 24 hours, it returns to an unregistered state and must be re-added (which issues a new token).

![Add DNS record](https://kiro.dev/images/enterprise/Kiro-domain-verification-DNS.png)

If the configuration is valid, after a few minutes the status will be "Verified".

![Domain verified](https://kiro.dev/images/enterprise/Entra-Kiro-domains.png)

**⚠️ Domain verification requires a publicly resolvable domain:** Domain verification performs a **public DNS lookup** for the TXT record, so the domain you verify must be publicly resolvable. Private or internal TLDs (for example, `.local`, `.internal`, or a custom private TLD) are **not supported** — they return `NXDOMAIN` on a public DNS lookup, and the domain stays in "Pending" status indefinitely.

#### Workarounds for private or internal domains

If your organization uses a private or internal domain for its infrastructure, use one of the following approaches:

- **Verify a publicly resolvable domain or subdomain that you control.** Add the TXT record to a domain (or subdomain) that resolves on public DNS, and verify that domain instead of the private one.
- **Register the public domain your users sign in with.** If your users sign in with email addresses on a public domain, add that public domain to the Kiro profile. When a user enters their email (with the public domain) and selects login, Kiro redirects them to the Okta login page — regardless of your internal infrastructure domain.

**ℹ️ Privacy consideration:** Kiro does not allow a domain to be associated with more than one profile, regardless of verification status. This means a third party could attempt to add your domain to their own profile and, based on the rejection, infer that the domain is already associated with another Kiro profile. This does not grant them any access, but it does reveal that the domain has been onboarded to Kiro.

**ℹ️ Domain configuration notes:** A Kiro profile supports at most **10 domains**. The domain you configure here exists solely to identify your Kiro profile. When a user enters an email on the Kiro sign-in page, the backend looks at the domain portion of that email and uses it to look up the associated Kiro profile and its Okta application. The email address itself does not need to exist in your Okta directory, and it does not need to match the identity the user ultimately authenticates with in Okta. It is only used for profile lookup.

### Add SCIM access token

In the Kiro console, navigate to *Settings → Identity Management → Access Tokens* and select "Generate Token" to create an access token for SCIM provisioning. Copy this token — you will need it when configuring the SCIM provisioning application in Step 4.

**⚠️ SCIM token security:** - The access token generated for SCIM provisioning is a long-lived credential. Treat it with the same care as a password.
- SCIM tokens are not automatically rotated. You must manually rotate them according to your organization's credential rotation policy.
- If a token is compromised, revoke it immediately using the revoke button in the Kiro admin console (*Settings → Identity Management → Access Tokens*), then generate a new token and update it in Okta's provisioning configuration.

![Application provisioning success](https://kiro.dev/images/enterprise/Kiro-profile-token-list.png)

## Step 4: Create SCIM provisioning application

### Create app integration

Next, you have to create the SCIM provisioning application and configure users and groups. 

In the Okta Admin Console, navigate to the *Applications -> Applications* section and select "Browse App Catalog". Search for "AWS IAM Identity Center" and select "Add Integration".

![Select IAM Identity Center integration](https://kiro.dev/images/enterprise/Okta-IdC-App.png)

This will add a new application with the "General Settings" tab open having "Application label" value of "AWS IAM Identity Center". You can choose to accept the default or change the label and select "Done".

Now you will see the details of the newly created application. In the "Sign On" tab, the SAML settings (ACS URL, Issuer URL) can be left as defaults — Kiro uses the OIDC app for login, not SAML.

### Configure SCIM provisioning 

Next, you have to configure provisioning. Select the "Provisioning" tab and then the "Integration" section. You will see a message that provisioning is not enabled. Select the "Configure API integration" button to start the provisioning process. 

Check "Enable API integration". This will display additional fields to configure.

![Okta application use SCIM](https://kiro.dev/images/enterprise/Okta-IdC-App-API-Integration.png)

* Set Base URL → paste the SCIM endpoint from Kiro console (Settings → Identity Management → SCIM Endpoint)
* Set API Token → paste the access token from Kiro console (Settings → Identity Management → Access Tokens → Generate Token)
* Select Test API Credentials — should show success
* Select Save
* Under the Provisioning tab → To App → Edit, enable:
    * Create Users 
    * Update User Attributes 
* Select Save

![Okta IdC application provisioning](https://kiro.dev/images/enterprise/Okta-IdC-App-Provisioning.png)  

### Synchronizing Groups

If you want to push groups from Okta to Kiro, then follow these instructions. 

**Pre-requisite**

Before adding groups, remove the two attributes - "department" and "employeeNumber". Select the "AWS IAM Identity Center" app that you created, and in the "Provisioning" tab, select "To App". Scroll down to the AWS IAM Identity Center Attribute Mappings section and remove the two attributes.

![Okta IAM Identity Center attribute mappings with department and employeeNumber](https://kiro.dev/images/enterprise/Okta-Attribute-mappings-list-2.png)

![Okta Attributes list](https://kiro.dev/images/enterprise/Okta-Attribute-mappings-list-1.png)

First, assign the groups to be synchronized. Select the "Assignments" tab and select the "Assign" button and choose "Assign to Groups" option. From the list of available groups, select "Assign" on each group you want synchronized and follow the steps. 

![Okta Assign groups 1](https://kiro.dev/images/enterprise/Okta-SCIM-assign-groups-1.png)

![Okta Assign groups 2](https://kiro.dev/images/enterprise/Okta-SCIM-assign-groups-2.png)

Next, set up the synchronization of groups. 

* Select the Push Groups tab. Select the Push Groups button and choose the Find groups by name option.
* Select the group(s) to push, and select Save.
* Group status should show Active, if the configuration is correct.

![Okta IdC application push groups](https://kiro.dev/images/enterprise/Okta-IdC-App-Push-Groups.png)

**ℹ️ Sync delay:** If you add users to a group that already has a Kiro subscription, allow up to 24 hours for the new group membership to propagate. There may be a delay between the time a user is added to the group and the time their subscription becomes active in the Kiro subscription console.

You have now completed all the steps required to configure an application in Okta, connect the application with a Kiro Profile, and add users/groups to the Profile.

**⚠️ Subscribe your team to Kiro:** Users can sign in after completing the steps above, but they will not be able to use Kiro models until you subscribe them. Follow the [Subscribe your team to Kiro](https://kiro.dev/docs/enterprise/subscribe.md#subscribe-your-team-to-kiro) guide to activate subscriptions for your team members.

## Security considerations

**Session management**

- Kiro uses OIDC refresh tokens to maintain user sessions. When a session expires, the refresh token keeps the Kiro session alive independently until the refresh token itself expires.
- You cannot force-revoke active user sessions from the Kiro console. To remove access, you have to remove the user from the Okta application — access will be revoked at the next token refresh attempt.
- Removing users from the Kiro OIDC application will prevent users from logging in (*Applications → Kiro OIDC application → Assignments*) → Select x next to user

**Redirect URI security**

- Add only the redirect URIs specified in this guide. 

**Profile deletion warning**

If you delete a Kiro profile after provisioning and create a new profile with the same Okta application, group membership will not be synced. You must re-provision the application completely.

**Preventing unauthorized access**

- Do not add any user to the Kiro application in Okta.
- Verify the user is not a member of any group that is assigned to the Kiro application.
- After creating a group-based subscription, review the Subscriptions tab in the Kiro console to confirm that no unintended users received a subscription.

**Removing a user and deprovisioning behavior**

- Remove the user's assignment from your Kiro application in Okta. This blocks all future login attempts.
- Existing sessions remain active until the next token refresh is attempted, at which point access is revoked. Active sessions are not immediately terminated.
- Subscription removal is not automatic. After removing a user from the Okta application, you must also manually delete the user's subscription in the Kiro console to release the seat.

**Group membership sync behavior**

- Kiro relies entirely on push-based SCIM sync from Okta. Kiro cannot request a pull from Okta.
- Group membership changes are pushed to Kiro as they occur.

## Troubleshooting

| Missed step | How will this manifest | How to fix | Notes |
|--|--|--|--|
| User was not added to the OIDC app | User will not be able to log in | Add the user to the OIDC application's Assignments tab	| User must be in both OIDC and SCIM provisioning applications |
| Did not enable provisioning to create users	| Users are not synced to Kiro |	In the SCIM provisioning app, go to *Provisioning > To App* and enable "Create Users" |	Also enable "Update User Attributes" |
| Used a private or internal TLD for domain verification | Domain stays in "Pending" status and never verifies | Verify a publicly resolvable domain or subdomain instead, or register the public email domain your users sign in with | Verification performs a public DNS lookup; private TLDs return NXDOMAIN |
