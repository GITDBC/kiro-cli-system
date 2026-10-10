> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Monitoring and tracking

> Track Kiro usage through dashboards, user activity reports, prompt logs, and AWS monitoring tools.

Monitoring is an important part of maintaining the reliability, availability, and performance of Kiro and your other AWS solutions. Kiro includes the following features to help you track and record user activity:

* *A dashboard* shows you aggregate user activity metrics of Kiro subscribers. For more information, see [Viewing Kiro usage on the dashboard](https://kiro.dev/docs/enterprise/monitor-and-track/dashboard.md).
* *User activity reports* show you what individual users are up to in Kiro. For more information, see [Viewing per-user activity](https://kiro.dev/docs/enterprise/monitor-and-track/user-activity.md).
* *Prompt logs* provide you with a record of all the prompts that users enter into Kiro chat in their IDE or the CLI. For more information, see [Logging users' prompts](https://kiro.dev/docs/enterprise/monitor-and-track/prompt-logging.md).

AWS also provides the following tools and features to monitor and record Kiro activity:

* *AWS CloudTrail* captures API calls and related events made by or on behalf of your AWS account and delivers the log files to an Amazon Simple Storage Service (Amazon S3) bucket that you specify. You can identify which users and accounts called AWS, the source IP address from which the calls were made, and when the calls occurred.
* *Amazon CloudWatch* monitors your AWS resources and the applications you run on AWS in real time. You can collect and track metrics, create customized dashboards, and set alarms that notify you or take actions when a specified metric reaches a threshold that you specify. For example, you can have CloudWatch track the number of times that Kiro has been invoked on your account, or the number of daily active users.

## Download subscription data as CSV from the Kiro Console

Administrators can export Kiro subscription data as a CSV file directly from the Kiro Console. To download the data, use the **Download CSV** button on the **Users & Groups** page's **Subscriptions** table. The exported CSV file includes the following fields:

* User name
* Subscription status
* Kiro plan
* Plan source
* Activation date

  [Video](https://kiro.dev/videos/subscriptions-download.mp4)
