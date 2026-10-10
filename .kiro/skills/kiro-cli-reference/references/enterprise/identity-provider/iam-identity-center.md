> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Connect your IAM Identity Center

> How to connect IAM Identity Center (IdC) with Kiro

## Prerequisites

1. You must have an instance of IAM Identity Center (IdC) set up in your AWS account, with the identities of the users you want to subscribe to Kiro. 
2. Your IAM Identity Center instance must be in a supported AWS Region.
3. Administrator permission in both AWS and the IdP (if you have connected IdC to an external provider).

## How to connect IAM Identity Center 

Enable AWS IAM Identity Center in your AWS account. Add users to its directory, or connect it to an external identity provider (IdP). If this is your first time setting up an IAM Identity Center instance, see [Getting started with IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/getting-started.html).

**ℹ️ Group sync delay:** If you add users to a group that already has a Kiro subscription, allow up to 24 hours for the new group membership to propagate. There may be a delay between the time a user is added to the group and the time their subscription becomes active in the Kiro subscription console.

If your IAM Identity Center instance uses a customer managed KMS key for encryption, you must add the following statements to your key policy to allow Kiro to access Identity Center data.

Allow Kiro to decrypt data via IAM Identity Center:

```json
{
    "Sid": "Allow Kiro to use key via IDC",
    "Effect": "Allow",
    "Principal": { "Service": "q.amazonaws.com" },
    "Action": "kms:Decrypt",
    "Resource": "*",
    "Condition": {
        "StringEquals": {
            "kms:EncryptionContext:aws:sso:instance-arn": "arn:aws:sso:::instance/<your-idc-instance-id>",
            "kms:ViaService": "sso.<identity-center-region>.amazonaws.com"
        }
    }
}
```

Allow Kiro to decrypt data via Identity Store:

```json
{
    "Sid": "Allow Kiro to use key via IdentityStore",
    "Effect": "Allow",
    "Principal": { "Service": "q.amazonaws.com" },
    "Action": "kms:Decrypt",
    "Resource": "*",
    "Condition": {
        "StringEquals": {
            "kms:EncryptionContext:aws:identitystore:identitystore-arn": "arn:aws:identitystore::<identity-center-account-id>:identitystore/<your-identity-store-id>",
            "kms:ViaService": "identitystore.<identity-center-region>.amazonaws.com"
        }
    }
}
```

Replace the placeholders as follows:

- `<identity-center-account-id>` — the ID of the AWS account that owns your IAM Identity Center instance.
- `<your-idc-instance-id>` — your IAM Identity Center instance ID.
- `<your-identity-store-id>` — your Identity Store ID.
- `<identity-center-region>` — the AWS Region of your IAM Identity Center instance.

These policies can be relaxed by using `StringLike` with wildcards (`*`) instead of `StringEquals`. For more details, see [Advanced KMS key policy statements](https://docs.aws.amazon.com/singlesignon/latest/userguide/advanced-kms-policy.html) in the IAM Identity Center User Guide.

If you use group-based subscriptions, you must also grant the **`AWSServiceRoleForUserSubscriptions`** service-linked role permission to use your key. Kiro uses this role to resolve IAM Identity Center group memberships and keep group subscriptions active. If the role cannot decrypt the key, group memberships cannot be resolved and group subscriptions will not remain active.

Add the following statement to your key policy:

```json
{
    "Sid": "Allow User Subscriptions SLR to use key",
    "Effect": "Allow",
    "Principal": {
        "AWS": "arn:aws:iam::<kiro-profile-account-id>:role/aws-service-role/user-subscriptions.amazonaws.com/AWSServiceRoleForUserSubscriptions"
    },
    "Action": [
        "kms:Decrypt",
        "kms:DescribeKey"
    ],
    "Resource": "*",
    "Condition": {
        "StringEquals": {
            "kms:ViaService": [
                "sso.<identity-center-region>.amazonaws.com",
                "identitystore.<identity-center-region>.amazonaws.com"
            ]
        }
    }
}
```

The `kms:ViaService` condition must include both `sso.<identity-center-region>.amazonaws.com` and `identitystore.<identity-center-region>.amazonaws.com`.

Replace the placeholders as follows:

- `<kiro-profile-account-id>` — the ID of the AWS account that owns the **Kiro profile** (the account where the profile was created). This is not necessarily the account that owns the KMS key or the IAM Identity Center instance.
- `<identity-center-region>` — the AWS Region of your **IAM Identity Center instance**.

**ℹ️ Cross-account (delegated administrator / member account) setups:** If your Kiro profile is in a different AWS account from your IAM Identity Center instance and KMS key (for example, the Kiro profile is in a member account while Identity Center and the key are in the management account), the `AWSServiceRoleForUserSubscriptions` role lives in the account that owns the **Kiro profile**. Use that account's ID in the role ARN above — not the account that owns the key.
