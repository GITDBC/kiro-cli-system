> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Deployment options

> Decide where to enable IAM Identity Center, create your Kiro profile, and subscribe users before rolling out Kiro across your organization.

## Before you begin

Before you subscribe users, decide which AWS account you'll work in. Your choice comes down to three decisions:

- **Where to enable IAM Identity Center.** For background, see [What is IAM Identity Center?](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html) in the *AWS IAM Identity Center User Guide*.
- **Where to create your Kiro profile.** For background, see [Kiro profile](https://kiro.dev/docs/enterprise/concepts.md#kiro-profile).
- **Where to subscribe your users.** For background, see [Subscribe your team](https://kiro.dev/docs/enterprise/subscribe.md).

A deployment option is a combination of these three decisions. Choose an option below before you continue to [Subscribe your team](https://kiro.dev/docs/enterprise/subscribe.md).

## Account terminology

This page uses the following terms:

- **Standalone account** — an AWS account that isn't part of an organization managed by [AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html).
- **Management account** — the AWS account that owns an organization managed by AWS Organizations. It's responsible for the charges of all accounts in the organization.
- **Member account** — any account in an organization other than the management account.

## Choose a deployment option

### Option 1: Deploy to a standalone account (simplest)

Use this option to quickly evaluate Kiro by subscribing yourself, and optionally a small team.

- **What you do:** In a standalone account, enable IAM Identity Center, create a Kiro profile, and subscribe yourself (and your team).
- **Benefits:** Good for demos and evaluation without an enterprise-wide rollout. Richer capabilities than a personal setup.
- **Drawbacks:** Fewer features. IAM Identity Center enabled in a standalone account is an [account instance](https://docs.aws.amazon.com/singlesignon/latest/userguide/account-instances-identity-center.html#about-account-instance), which supports fewer features than an [organization instance](https://docs.aws.amazon.com/singlesignon/latest/userguide/organization-instances-identity-center.html#when-to-use-organization-instance).

### Option 2: Deploy to management and member accounts

Use this option when you want distributed administration across accounts.

- **What you do:** In the management account, enable IAM Identity Center. In a member account, create a Kiro profile and subscribe users.
- **Benefits:** More features, because IAM Identity Center is an *organization instance*. Distributed administration: subscription-management tasks live in member accounts, which is the recommended best practice.
- **Drawbacks:** More complexity, since it requires coordination across accounts. Account limit: you can subscribe users in up to 20 accounts per AWS Region per organization. If a business need prevents you from choosing another option, you can request an increase by contacting AWS Support with your use case. Requests are reviewed by the Kiro service team and aren't guaranteed to be approved.

### Option 3: Deploy to a member account only

Use this option when a member-account administrator needs to deploy without an org-wide rollout.

- **What you do:** In a member account, enable IAM Identity Center, create a Kiro profile, and subscribe users.
- **Benefits:** Quick setup. A member-account administrator can deploy without waiting for an enterprise-wide implementation or approval. Flexible for complex organizations that don't have a single, unified identity provider covering everyone you want to subscribe.
- **Drawbacks:** Fewer features. IAM Identity Center enabled in a member account is an *account instance*, which supports fewer features than an *organization instance*.

### Option 4: Deploy to a management account only

Use this option when you manage everything centrally from the management account.

- **What you do:** In the management account, enable IAM Identity Center, create a Kiro profile, and subscribe users. Optionally, share the Kiro profile with member accounts.
- **Benefits:** More features, because IAM Identity Center is an *organization instance*.
- **Drawbacks:** Not aligned with best practice. Because delegated administrators aren't supported, subscription-management tasks must be handled by an administrator in the management account instead of being delegated to member accounts.

## Next step

After you choose a deployment option, continue to [Subscribe your team](https://kiro.dev/docs/enterprise/subscribe.md).
