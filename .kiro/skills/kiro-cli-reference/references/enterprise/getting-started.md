> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Onboarding quickstart

> Deploy Kiro to your organization with confidence. Learn how to subscribe users, manage subscriptions, and track usage.

## Audience

Read this page if you're an administrator who wants to onboard your team to Kiro and manage their subscriptions.

## To onboard your team to Kiro

1. **Create an AWS account** if you don't have one already (see [Create an AWS account](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-creating.html)).

1. **Sign in to your AWS account**. You can sign in as an AWS root user or as a user with a privileged role. Alternatively, [allow administrators to use Kiro with minimum permissions](https://kiro.dev/docs/enterprise/iam.md#policy-allow-administrators-to-configure-kiro-and-subscribe-users). 

1. **Connect to your identity provider**. Add users to its directory from AWS IAM Identity Center, or connect it to an external identity provider (IdP) such as Okta, or Microsoft Entra ID. Follow the instructions on how to connect your [identity provider](https://kiro.dev/docs/enterprise/identity-provider.md) to Kiro.

1. **Create a Kiro profile and subscribe users**. Within the AWS console, navigate to the Kiro console and use the available UI to create a profile and subscribe users. The profile is the glue that ties your user identities with their Kiro subscriptions and settings. Once your Kiro profile is created and connected, you can import your users and groups and [subscribe your team to Kiro](https://kiro.dev/docs/enterprise/subscribe.md).

1. **Share download instructions with your team**. Once users are subscribed, they can download Kiro IDE or Kiro CLI from the [Kiro downloads page](https://kiro.dev/downloads/) and sign in with their identity provider credentials.
