> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# IAM permissions

> AWS Identity and Access Management (IAM) permissions required for Kiro.

## Required permissions 

To create a Kiro profile and manage subscriptions, you need to ensure that the role managing it has the following IAM permissions in the AWS account.

### General

These are IAM permissions required to manage Kiro profile and users subscriptions regardless of the identity store you use. Here are the [supported identity stores](https://kiro.dev/docs/enterprise/identity-provider.md). 

```
- codewhisperer:ListProfiles
- codewhisperer:CreateProfile
- codewhisperer:DeleteProfile
- codewhisperer:UpdateProfile
- codewhisperer:TagResource
- codewhisperer:UntagResource
- codewhisperer:ListTagsForResource
- codewhisperer:AllowVendedLogDeliveryForResource
- q:ListDashboardMetrics
```

### External identity provider related

If you are connecting an external identity provider, you will also need the following permissions

```
- q:ListLoginDomains
- q:AssociateLoginDomain
- q:DisassociateLoginDomain
- q:ListScimAccessTokens
- q:CreateScimAccessToken
- q:DeleteScimAccessToken
- q:ListGroups
- q:ListUsers
- q:BatchDescribeUsers
- q:BatchDescribeGroups
```

## Additional resources

For more information about IAM and security best practices:

- [AWS Identity and Access Management documentation](https://docs.aws.amazon.com/iam/)
- [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Kiro data protection](https://kiro.dev/docs/privacy-and-security/data-protection.md)
- [Kiro infrastructure security](https://kiro.dev/docs/privacy-and-security/infrastructure-security.md)
