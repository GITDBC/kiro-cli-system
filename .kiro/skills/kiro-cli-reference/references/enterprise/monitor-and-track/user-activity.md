> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Viewing per-user activity

> Configure daily CSV and OpenTelemetry exports to monitor per-user Kiro activity

You can export daily per-user activity telemetry for the Kiro subscribers in your organization. Use these exports to audit usage, optimize license allocation, track credit and overage consumption, and understand how individual users interact with Kiro across clients.

## Choose an export format

Kiro offers two independent export formats. You can enable either format or both:

| Format | Choose it when |
| --- | --- |
| CSV in Amazon S3 | You want daily files for queries, dashboards, or an existing analytics pipeline. |
| [OpenTelemetry](https://kiro.dev/docs/enterprise/monitor-and-track/user-activity/opentelemetry.md) | You want Kiro to push daily aggregate metrics to your OpenTelemetry-compatible collector. |

Both formats contain the same daily aggregate usage metrics. The OpenTelemetry export transforms those metrics to OTLP.

## Export CSV reports to Amazon S3

Each day at 02:00 UTC, Kiro generates a CSV report per Kiro client type (IDE, CLI, and Plugin) and writes it to your S3 bucket.

```text
s3://bucketName/prefix/AWSLogs/accountId/KiroLogs/user_report/region/year/month/day/00/clientType_accountId_user_report_timestamp.csv
```

**ℹ️ Info:** When you enable user activity reports, Kiro collects user telemetry and stores it in the S3 bucket in your account. This is controlled at the administrator level and can't be configured by users.

### Prepare the S3 bucket

Create an Amazon S3 bucket to hold the user activity report CSV file. The bucket must:

- Be in the AWS Region where the Kiro profile was installed. This profile was installed when you subscribed IAM Identity Center workforce users to Kiro Pro for the first time. For more information about this profile and the Regions where it's supported, see [Kiro profile](https://kiro.dev/docs/enterprise/concepts.md#kiro-profile) and [Supported Regions](https://kiro.dev/docs/enterprise/supported-regions.md).

- Be in the AWS account where users are subscribed. If users are subscribed in multiple AWS accounts, then you must create buckets in each of those accounts. Cross-account buckets are not supported.

- (Optional but recommended) Be different from the bucket you might be using for [logging users' prompts](https://kiro.dev/docs/enterprise/monitor-and-track/prompt-logging.md).

- Include a prefix, also known as a subfolder, where Kiro will save the CSV file. The CSV file cannot be saved in the root of the bucket.

- Have a bucket policy like the one that follows. Replace `bucketName`, `prefix`, `region`, and `accountId` with your own information. The `region` and `accountId` in the policy's `Condition` block must match the Region where your Kiro profile was installed and the AWS account where users are subscribed.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "KiroLogsWrite",
      "Effect": "Allow",
      "Principal": {
        "Service": "q.amazonaws.com"
      },
      "Action": [
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::bucketName/prefix/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "accountId"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:codewhisperer:region:accountId:*"
        }
      }
    }
  ]
}
```

To learn about protecting the data in your Amazon S3 bucket, see [Protecting data with encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingEncryption.html) in the *Amazon Simple Storage Service User Guide*.

### Enable CSV reports

1. Sign in to the AWS console.

2. Switch to the Kiro console. To use the Kiro console, you must have the permissions defined in [Policy: Allow administrators to configure Kiro and subscribe users](https://kiro.dev/docs/enterprise/iam.md#policy-allow-administrators-to-configure-kiro-and-subscribe-users).

3. Choose **Settings**.

4. Under **Kiro user activity reports**, choose **Edit**.

5. Toggle **Collect granular metrics per user**.

6. Under **S3 location**, enter the Amazon S3 URI that you will use to hold the CSV reports. Example: `s3://amzn-s3-demo-bucket/user-activity-reports/`

### After you enable

The first CSV report is generated at the next 02:00 UTC cycle after you enable reporting, and new files are written every day afterward. Once reports are in your bucket you can query them with Amazon Athena, visualize trends in Amazon QuickSight, or pull them into your existing analytics pipeline.

For a higher-level view of Kiro usage without per-user detail, see [Viewing Kiro usage on the dashboard](https://kiro.dev/docs/enterprise/monitor-and-track/dashboard.md). To also capture the content of user prompts, see [Prompt logging](https://kiro.dev/docs/enterprise/monitor-and-track/prompt-logging.md).

## CSV report metrics and structure

Each CSV contains static columns and dynamic per-model message columns.

| Metric name | Description |
| --- | --- |
| Date | Date of the report activity |
| UserId | ID of the user whose activity is reported |
| Client_Type | `KIRO_IDE`, `KIRO_CLI`, or `PLUGIN` |
| Chat_Conversations | Number of conversations by the user during the day |
| Credits_Used | Credits consumed from the user's subscription plan during the day |
| Overage_Cap | Overage limit set by the administrator when `Overage_Enabled` is true. If overage is not enabled, this field shows the maximum credits included in the subscription plan as a preset value |
| Overage_Credits_Used | Total number of overage credits used by the user, if overage is enabled |
| Overage_Enabled | Whether overage is enabled for this user |
| ProfileId | Profile associated with the user activity |
| Subscription_Tier | Kiro subscription plan: Pro, ProPlus, ProMax, or Power |
| Total_Messages | Number of messages sent to and from Kiro, including user prompts, tool calls, and Kiro responses |
| New_User | Whether the user activated their Kiro subscription on the report date |
| User_Email | Email address of the user |
| *model_name*_messages | Number of messages processed by a model for a user, including Auto |

The number of `*model_name*_messages` columns depends on the models used on the report date. These columns use lowercase model names in alphabetical order, starting with Auto. A column contains `0` when a user didn't use that model during the report day.

## Legacy user activity report metrics

The legacy user activity report continues to run alongside the per-client report and contains CLI and plugin usage. Its daily CSV files are published to the same S3 bucket at this path:

```text
s3://bucketName/prefix/AWSLogs/accountId/KiroLogs/by_user_analytic/Region/year/month/day/00/accountId_by_user_analytic_timestamp.csv
```

The `00` segment is a fixed hour partition for the 02:00 UTC write cycle. In each file:

- Each row represents a user who interacted with Kiro that day.
- Each column contains one of the legacy metrics listed below, calculated from the user telemetry collected during the day.
- If more than 1,000 users interact with Kiro during the day, Kiro splits the data into files containing 1,000 users each. Files are suffixed with `part_1`, `part_2`, and so on.

The following table describes the legacy metrics that are included in the user activity reports generated by Kiro.

| Metric name | Description |
|-------------|-------------|
| Chat_AICodeLines | Lines of code suggested by Kiro and accepted by the user. This metric includes code that was generated through the Kiro chat (not inline chat) and inserted into the IDE. |
| Chat_MessagesInteracted | Number of chat messages where the user has interacted positively with Kiro. Examples of positive interactions: clicking a link, inserting a suggestion, and upvoting a response from Kiro. This metric includes messages that were generated by Kiro chat (not inline chat). |
| Chat_MessagesSent | Number of messages sent to and from Kiro. This metric includes the user prompts and Kiro responses in the Kiro chat (not inline chat). |
| CodeFix_AcceptanceEventCount | Number of code fixes suggested by Kiro and accepted by the user. This metric applies to code fixes generated through the code review feature. |
| CodeFix_AcceptedLines | Lines of code suggested by Kiro and accepted by the user. This metric applies to lines of code generated through the code review feature. |
| CodeFix_GeneratedLines | Lines of code suggested by Kiro. This metric applies to lines of code generated through the code review feature. |
| CodeFix_GenerationEventCount | Number of code fixes suggested by Kiro. This metric applies to code fixes generated through the code review feature. |
| CodeReview_FailedEventCount | Number of code issues that were found but for which Kiro could not suggest a code fix. This metric applies to code issues generated using the code review feature. |
| CodeReview_FindingsCount | Number of code issues found by Kiro. This metric applies to code issues found using the code review feature. |
| CodeReview_SucceededEventCount | Number of code issues that were found and for which Kiro was able to generate a suggested code fix. This metric applies to code issues found using the code review feature. |
| Dev_AcceptanceEventCount | Number of code features suggested by Kiro and accepted by the user. This metric applies to code features generated through the /dev command. |
| Dev_AcceptedLines | Lines of code suggested by Kiro and accepted by the user. This metric applies to lines of code generated through the /dev command. |
| Dev_GeneratedLines | Lines of code suggested by Kiro. This metric applies to lines of code generated through the /dev command. |
| Dev_GenerationEventCount | Number of code features suggested by Kiro. This metric applies to code features generated through the /dev command. |
| DocGeneration_AcceptedFileUpdates | Number of file updates suggested by Kiro and accepted by the user. This metric applies to file updates generated through the /doc command. |
| DocGeneration_AcceptedFilesCreations | Number of file creations suggested by Kiro and accepted by the user. This metric applies to file creations generated through the /doc command. |
| DocGeneration_AcceptedLineAdditions | Lines of documentation additions suggested by Kiro and accepted by the user. This metric applies to documentation generated through the /doc command. |
| DocGeneration_AcceptedLineUpdates | Lines of documentation updates suggested by Kiro and accepted by the user. This metric applies to documentation generated using the /doc command. |
| DocGeneration_EventCount | Number of times the user engaged with Kiro using the /doc command. |
| DocGeneration_RejectedFileCreations | Number of file creations suggested by Kiro and rejected by the user. This metric applies to file creations generated through the /doc command. |
| DocGeneration_RejectedFileUpdates | Number of file updates suggested by Kiro and rejected by the user. This metric applies to file updates generated through the /doc command. |
| DocGeneration_RejectedLineAdditions | Lines of documentation additions suggested by Kiro and rejected by the user. This metric applies to documentation generated through the /doc command. |
| DocGeneration_RejectedLineUpdates | Lines of documentation updates suggested by Kiro and rejected by the user. This metric applies to documentation generated using the /doc command. |
| InlineChat_AcceptedLineAdditions | Lines of code additions suggested by Kiro and accepted by the user. This metric includes code additions generated through the inline chat (not Kiro chat). |
| InlineChat_AcceptedLineDeletions | Lines of code deletions suggested by Kiro and accepted by the user. This metric includes code deletions suggested through the inline chat (not Kiro chat). |
| InlineChat_AcceptanceEventCount | Number of inline chat (not Kiro chat) suggestions that were accepted by the user. |
| InlineChat_DismissalEventCount | Number of inline chat (not Kiro chat) suggestions that were abandoned by the user. By 'abandoned', we mean that the code suggestion was displayed but the user kept typing or performing other operations in their IDE, and did not explicitly accept or reject the code suggestion. |
| InlineChat_DismissedLineAdditions | Lines of code additions suggested by Kiro and abandoned by the user. By 'abandoned', we mean that the code suggestion was displayed but the user kept typing or performing other operations in their IDE, and did not explicitly accept or reject the code suggestion. This metric includes code additions generated through the inline chat (not Kiro chat). |
| InlineChat_DismissedLineDeletions | Lines of code deletions suggested by Kiro and abandoned by the user. By 'abandoned', we mean that the code suggestion was displayed but the user kept typing or performing other operations in their IDE, and did not explicitly accept or reject the code suggestion. This metric includes code deletions suggested through the inline chat (not Kiro chat). |
| InlineChat_EventCount | Number of inline chat (not Kiro chat) sessions that the user engaged in. |
| InlineChat_RejectedLineAdditions | Lines of code additions suggested by Kiro and rejected by the user. This metric includes code additions generated through the inline chat (not Kiro chat). |
| InlineChat_RejectedLineDeletions | Lines of code deletions suggested by Kiro and rejected by the user. This metric includes code deletions suggested through the inline chat (not Kiro chat). |
| InlineChat_RejectionEventCount | Number of inline chat (not Kiro chat) suggestions that were rejected by the user. |
| Inline_AICodeLines | Lines of code suggested by Kiro and accepted by the user. This metric includes code that was accepted as inline suggestions. |
| Inline_AcceptanceCount | Number of inline suggestions accepted by the user. |
| Inline_SuggestionsCount | Number of inline suggestions displayed to the user. |
| TestGeneration_AcceptedLines | Lines of code suggested by Kiro and accepted by the user. This metric applies to lines of code generated through the /test command. |
| TestGeneration_AcceptedTests | Number of unit tests suggested by Kiro and accepted by the user. This metric applies to unit tests generated through the /test command. |
| TestGeneration_EventCount | Number of times the user engaged with Kiro through the /test command. |
| TestGeneration_GeneratedLines | Lines of code suggested by Kiro. This metric applies to lines of code generated through the /test command. |
| TestGeneration_GeneratedTests | Number of unit tests suggested by Kiro. This metric applies to unit tests generated through the /test command. |
| Transformation_EventCount | Number of times the user engaged with Kiro through the /transform command, excluding the times when the user transformed code on the command line. |
| Transformation_LinesGenerated | Lines of code suggested by Kiro. This metric applies to code generated through the /transform command, excluding code transformed on the command line. |
| Transformation_LinesIngested | Lines of code provided to Kiro for transformation. This metric applies to code that is provided through the /transform command, excluding code provided for transformation on the command line, or for an SQL conversion. |
