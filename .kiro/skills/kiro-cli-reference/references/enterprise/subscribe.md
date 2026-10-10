> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Subscribing your team to Kiro

> Step-by-step guide to creating a Kiro profile and subscribing users through AWS IAM Identity Center.

## Prerequisites

Before you begin, make sure you have the following:

- **An AWS account** - You can [create an AWS account](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-creating.html) if you do not have one already.

- **AWS permissions** - As a Kiro admin, you must have the permissions to access the Kiro console in AWS in order to subscribe and manage Kiro users. The minimum permissions you'll need are described in [Policy: Allow administrators to configure Kiro and subscribe users](https://kiro.dev/docs/enterprise/iam.md#policy-allow-administrators-to-configure-kiro-and-subscribe-users). 
- **Identity Provider for users/groups** - You can either connect to IAM Identity Center, Okta or Microsoft Entra ID, with the identities of the users you want to subscribe to Kiro. It is recommended to use AWS Organizations when setting up AWS IAM Identity Center, as this enables an organization instance that provides centralized identity management across multiple AWS accounts. Note that individual account instances cannot be upgraded to organization instances and would require deletion and recreation.
- **Users and groups** - You can add users and groups from your Identity Provider's built-in directory, or to an external identity provider (IdP) that is connected to IAM Identity Center. 

## Create the Kiro profile

1. Sign in to the AWS Management Console.
2. Switch to the Kiro console.
3. Make sure you are in your preferred [supported AWS Region](https://kiro.dev/docs/enterprise/supported-regions.md) to create the [Kiro profile](https://kiro.dev/docs/enterprise/concepts.md#kiro-profile) and store user data. 
4. Choose the **Sign up for Kiro** button.
5. Review the contents of the **Create Kiro profile** dialog box then choose **Enable**. The Kiro profile is created.
6. _(Optional) Edit the profile with a different name or description as needed in the **Settings** page._

[Video](https://kiro.dev/videos/docs/enterprise/subscribe-create-kiro-profile.mp4)

## Subscribe your team to Kiro

1. Switch to the Kiro console if you're not there yet.
2. Make sure you're in the AWS Region where you created the [Kiro profile](https://kiro.dev/docs/enterprise/concepts.md#kiro-profile).
3. In the **Users & Groups** page, choose the **Users** or **Groups** tab.
4. Choose the **Add user** or **Add group** button. A dialog box appears where you can select the [Kiro subscription tier](https://kiro.dev/docs/enterprise/concepts.md#kiro-subscription-tier) (Pro, Pro+, Pro Max, Power) with details about each tier. 
5. Choose the desired subscription tier and choose **Continue**.
6. In the search bar, search for a group or a user you want to subscribe to the selected tier, or select one from the drop down. 
7. The group or user will auto-populate with what is available in your Identity provider. 
8. Select them and choose **Assign**. Users or groups are now subscribed.

[Video](https://kiro.dev/videos/docs/enterprise/subscribe-add-user.mp4)
