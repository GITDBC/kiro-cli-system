> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Export user activity with OpenTelemetry

> Configure daily OpenTelemetry exports to monitor per-user Kiro activity in your observability platform

You can send the same daily aggregate user activity metrics to your OpenTelemetry-compatible collector. Kiro pushes credits, overage credits, messages, conversations, and per-model message counts once a day at 02:00 UTC. The export is configured by an administrator and can't be configured by individual users.

Kiro supports `OTLP/gRPC` and `OTLP/HTTP` with protobuf encoding. gRPC is the default. In the Kiro console, the HTTP option is labeled **HTTP/protobuf**.

The OpenTelemetry export and the [CSV report in Amazon S3](https://kiro.dev/docs/enterprise/monitor-and-track/user-activity.md) are independent. You can enable either format or both. Kiro stores only the ARN of your AWS Secrets Manager secret and reads the collector endpoint and authentication header from the secret at export time.

## Plan your destination configuration

Choose the protocol, endpoint, and single authentication header that your destination accepts before you create the secret. Use the following destination configurations:

| Destination | Protocol | Endpoint | Authentication header |
| --- | --- | --- | --- |
| Honeycomb | gRPC | `https://api.honeycomb.io:443` | `X-Honeycomb-Team=<ingest-key>` |
| Elastic | gRPC | `https://<deployment>.ingest.<region>.gcp.elastic-cloud.com:443` | `Authorization=ApiKey <base64-credential>` |
| OpenSearch through an OTLP receiver such as Data Prepper | gRPC | `https://<collector-host>:21891` | `Authorization=Basic <credential>` |
| Self-hosted OTLP collector | gRPC or HTTP/protobuf | `https://<collector-host>:<port>` | Authentication header required by your collector |
| Datadog | HTTP/protobuf | `https://otlp.datadoghq.com/v1/metrics` | `dd-api-key=<api-key>` |
| Amazon CloudWatch | HTTP/protobuf | `https://monitoring.<region>.amazonaws.com/v1/metrics` | `Authorization=Bearer <api-key>` |
| Dynatrace | HTTP/protobuf | `https://<environment>.live.dynatrace.com/api/v2/otlp` | `Authorization=Api-Token <access-token>` |

Replace `<deployment>`, `<region>`, `<collector-host>`, and `<environment>` with values from your destination. Replace the credential placeholder in the header with your ingestion credential.

Use an ingestion credential rather than an administrative credential. For Honeycomb, use the combined ingest key ID and secret, not the key ID alone. For Elastic, base64-encode `id:api_key`. For Datadog, use an API key, not an application key. For Dynatrace, use an access token with `metrics.ingest` permission. Amazon CloudWatch requires a bearer API key because Kiro can't sign the export with AWS Signature Version 4 (SigV4). To create the key, see [Setting up bearer token authentication for Metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OTLP-MetricsBearerTokenAuth.html) in the *Amazon CloudWatch User Guide*.

**⚠️ Protect user activity data:** OpenTelemetry datapoints can contain IAM Identity Center user IDs and, when resolvable, email addresses. Restrict access to the destination and its dashboards, choose a retention period appropriate for your organization, use a dedicated secret and KMS key for this export, and limit the collector credential to metric ingestion.

## Create a customer managed KMS key

Create a symmetric customer managed AWS KMS key for encryption and decryption. The default `aws/secretsmanager` key can't be used because Kiro reads the secret from another AWS account. The KMS key, Secrets Manager secret, and Kiro profile must be in the same AWS Region.

Add the following statement to the KMS key policy. Replace `<region>` with the Region of your Kiro profile. This grants the `q.amazonaws.com` service principal permission to decrypt the secret through Secrets Manager in that Region.

```json
{
  "Sid": "AllowKiroDecryptViaSecretsManager",
  "Effect": "Allow",
  "Principal": {
    "Service": "q.amazonaws.com"
  },
  "Action": [
    "kms:Decrypt",
    "kms:DescribeKey"
  ],
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "kms:ViaService": "secretsmanager.<region>.amazonaws.com"
    }
  }
}
```

Save the policy. You select this key as the encryption key when you create the secret.

## Create the Secrets Manager secret

In the same Region as your Kiro profile, create an **Other type of secret** in AWS Secrets Manager. On the **Plaintext** tab, enter a JSON object with exactly these keys:

```json
{
  "OTEL_EXPORTER_OTLP_ENDPOINT": "https://<collector-host>:443",
  "OTEL_EXPORTER_OTLP_HEADERS": "<Header-Name>=<token>"
}
```

- `OTEL_EXPORTER_OTLP_ENDPOINT` is your collector's OTLP endpoint.
- `OTEL_EXPORTER_OTLP_HEADERS` is one authentication header in `Name=value` format. Kiro splits the string on the first `=`, so base64 padding such as `==` in the value is preserved.

Your collector endpoint must be reachable from the public internet and use a publicly trusted TLS certificate. Kiro rejects self-signed certificates. Use a hostname rather than an IP address because Kiro verifies the certificate hostname.

For **Encryption key**, select the customer managed KMS key that you created. Don't select `aws/secretsmanager`. Add the following resource policy to the secret so Kiro can read its value:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowKiroGetSecretValue",
      "Effect": "Allow",
      "Principal": {
        "Service": "q.amazonaws.com"
      },
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "*"
    }
  ]
}
```

Store the secret and copy its secret ARN, which has the format `arn:aws:secretsmanager:<region>:<accountId>:secret:<secretName>-<randomSuffix>`.

**ℹ️ Info:** To change your endpoint or rotate your token, update the value of the secret with the same ARN. Kiro reads the current value at each export, so you don't need to update the Kiro console configuration.

## Enable the OpenTelemetry export

1. Sign in to the AWS console.

2. Switch to the Kiro console. You must have the permissions in [Policy: Allow administrators to configure Kiro and subscribe users](https://kiro.dev/docs/enterprise/iam.md#policy-allow-administrators-to-configure-kiro-and-subscribe-users).

3. Choose **Settings**.

4. Under **Kiro user activity reports**, choose **Edit**.

5. Choose the **OpenTelemetry (OTel)** export format.

6. Enter the Secrets Manager secret ARN.

7. Select the protocol that your collector accepts: **gRPC** or **HTTP/protobuf**.

8. Choose **Enable**.

The first export runs during the next 02:00 UTC cycle. Metrics for an activity date are sent the following day, and Kiro doesn't send data to your collector when you save the configuration.

## Confirm the export

Kiro doesn't send success or failure notifications. Confirm delivery in your destination by querying `kiro.daily.credits` or another exported metric and filtering on the resource attribute `service.name = kiro-enterprise`.

A successful export has these characteristics:

- `kiro.daily.credits` and `kiro.daily.messages` are present.
- For each exported metric, expect one daily datapoint per active user and client type. `kiro.daily.model_messages` has one datapoint per model.
- The `date` attribute identifies the activity date, which is the day before the export ran.
- Each datapoint includes at least `kiro.user.id`, `kiro.client.type`, and `kiro.user.new`.

Prometheus-based backends can replace periods in metric names with underscores. For example, `kiro.daily.credits` can appear as `kiro_daily_credits`.

Check the destination because Kiro treats a request accepted by the collector as successful even if the collector later rejects its datapoints.

| Destination | Where to verify |
| --- | --- |
| Honeycomb | Open the `kiro-enterprise` dataset and visualize `SUM(kiro.daily.credits)`. |
| Elastic | In Kibana, use Discover or Metrics Explorer and filter on `service.name : "kiro-enterprise"`. |
| OpenSearch | Query the configured index for `serviceName:kiro-enterprise`. For example: `curl -u <user>:<password> "https://<opensearch-host>:9200/<index-prefix>-*/_search?q=serviceName:kiro-enterprise&pretty"`. |
| Datadog | In Metrics Explorer, open `kiro.daily.credits` and filter on the `service` tag. |
| Amazon CloudWatch | Run a PromQL range query against `https://monitoring.<region>.amazonaws.com/api/v1/query_range`. Metrics don't appear in the classic metrics console or through `ListMetrics`. |
| Dynatrace | In Notebooks, run a DQL query such as `timeseries mm = sum(kiro.daily.model_messages), by:, from: -2h`. |

Each resulting time series receives one daily datapoint. If a range query returns no data, use a narrow window around the export time and a fine step, such as 60 seconds. A metric name can remain in an index or autocomplete after its datapoints fall outside the selected time window, so confirm that the query returns datapoints rather than only a metric name.

## Exported OpenTelemetry metrics

All exported metrics are monotonic OTLP `Sum` counters in the `kiro.daily.*` namespace.

| Metric | Description | Corresponding CSV column |
| --- | --- | --- |
| `kiro.daily.credits` | Credits used | `Credits_Used` |
| `kiro.daily.overage_credits` | Overage credits used | `Overage_Credits_Used` |
| `kiro.daily.messages` | Total messages | `Total_Messages` |
| `kiro.daily.conversations` | Chat conversations | `Chat_Conversations` |
| `kiro.daily.model_messages` | Messages per model | `*model_name*_messages` |

Each `kiro.daily.model_messages` datapoint includes `kiro.model.name`, which identifies the model represented by the corresponding dynamic CSV column.

**ℹ️ Amazon CloudWatch requirements:** Kiro can't use AWS Signature Version 4 (SigV4) to sign the export, so use a CloudWatch bearer API key. Metrics are written to the AWS account that issued the API key and appear in the Metrics V2 store. They don't appear in the classic CloudWatch metrics console or through `ListMetrics`; query them with PromQL.

Each datapoint can include the following attributes:

| Attribute | Type | Presence | Description |
| --- | --- | --- | --- |
| `kiro.user.id` | string | Always | The user's IAM Identity Center user ID |
| `kiro.client.type` | string | Always | Client type, such as `KIRO_IDE`, `KIRO_CLI`, or `PLUGIN` |
| `kiro.user.new` | boolean | Always | Whether the user activated their subscription on the activity date |
| `date` | string | When set | Activity date in UTC |
| `kiro.user.email` | string | When resolvable | The user's email address; omitted if the directory lookup can't resolve it |
| `kiro.subscription.tier` | string | When set | Subscription tier |
| `kiro.usage.limit` | integer | When set | The user's usage limit |
| `kiro.overage.enabled` | boolean | When set | Whether overage is enabled for the user |
| `kiro.overage.cap` | double | When set | The user's overage cap, with the same decimal precision as the CSV report |
| `kiro.model.name` | string | Only on `kiro.daily.model_messages` | Model name; hidden models are excluded |

Each export also includes these resource attributes:

| Resource attribute | Value | Description |
| --- | --- | --- |
| `service.name` | `kiro-enterprise` | Constant value for filtering Kiro metrics |
| `kiro.profile.arn` | `arn:aws:codewhisperer:<region>:<accountId>:profile/<profileId>` | ARN of the Kiro profile that produced the metrics |
| `kiro.profile.id` | Profile ID | ID of the Kiro profile |
| `kiro.account.id` | AWS account ID | Account that contains the Kiro profile |

## Export behavior and limits

- Kiro retries transient failures automatically, with up to three attempts for an activity date.
- If all attempts fail, Kiro doesn't resend or automatically backfill that date. The destination has a gap for that day.
- If a date is exported again, Kiro doesn't deduplicate the datapoints at your collector. The collector receives them a second time.
- A request accepted by your collector counts as successful even if the collector later rejects some or all datapoints. Verify the metrics at the destination.
- Configuration errors repeat until you correct them. After you update the secret, Kiro uses the new value during the next 02:00 UTC cycle.
- Selecting gRPC for an HTTP-only endpoint, or HTTP/protobuf for a gRPC-only endpoint, prevents delivery. Kiro doesn't notify you of the failure.

If no metrics arrive, verify that the secret and KMS key are in the Kiro profile's Region. Confirm that `q.amazonaws.com` has `secretsmanager:GetSecretValue` on the secret and `kms:Decrypt` and `kms:DescribeKey` on the KMS key. Then verify the protocol, endpoint reachability, TLS certificate, and authentication header required by your destination.
