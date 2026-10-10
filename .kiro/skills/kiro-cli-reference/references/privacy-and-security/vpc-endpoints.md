> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Kiro and interface endpoints (AWS PrivateLink)

> Understand how to establish a private connection between your VPC (Virtual Private Cloud) and Kiro.

You can establish a private connection between your VPC and Kiro by creating an interface VPC endpoint. Interface endpoints are powered by [AWS PrivateLink](https://aws.amazon.com/privatelink/), a technology that enables you to privately access Kiro APIs without an internet gateway, NAT device, VPN connection, or AWS Direct Connect connection. Instances in your VPC don't need public IP addresses to communicate with Kiro APIs. Traffic between your VPC and Kiro does not leave the Amazon network.

Each interface endpoint is represented by one or more [Elastic Network Interfaces](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html) in your subnets.

For more information, see [Interface VPC endpoints (AWS PrivateLink)](https://docs.aws.amazon.com/vpc/latest/privatelink/create-interface-endpoint.html) in the Amazon VPC User Guide.

## Considerations for Kiro VPC endpoints

Before you set up an interface VPC endpoint for Kiro, ensure that you review [Interface endpoint properties and limitations](https://docs.aws.amazon.com/vpc/latest/privatelink/create-interface-endpoint.html#vpce-interface-limitations) in the Amazon VPC User Guide.

Kiro supports making calls to all of its API actions from your VPC, in the context of services that are configured to work with Kiro.

## Prerequisites

Before you begin any of the procedures below, ensure that you have the following:

- An AWS account with appropriate permissions to create and configure resources.
- A VPC already created in your AWS account.
- Familiarity with AWS services, especially Amazon VPC and Kiro.

## Creating an interface VPC endpoint for Kiro

You can create a VPC endpoint for Kiro using either the Amazon VPC console or the AWS Command Line Interface (AWS CLI). For more information, see [Creating an interface endpoint](https://docs.aws.amazon.com/vpc/latest/privatelink/create-interface-endpoint.html#create-interface-endpoint) in the Amazon VPC User Guide.

Create a VPC endpoint for Kiro using one of the following service names:

- com.amazonaws.us-east-1.q
- com.amazonaws.us-east-1.codewhisperer
- com.amazonaws.eu-central-1.q
- com.amazonaws.us-gov-west-1.q
- com.amazonaws.us-gov-east-1.q

**ℹ️ Info:** Kiro supports Amazon Q Developer profiles in the US East (N. Virginia) and Europe (Frankfurt) regions. Also, the Amazon CodeWhisperer endpoint (com.amazonaws.us-east-1.codewhisperer) is only supported in the US East (N. Virginia) Region.

If you enable private DNS for the endpoint, you can make API requests to Kiro using its default DNS name for the region, for example, `q.us-east-1.amazonaws.com`, `runtime.us-east-1.kiro.dev`.

**⚠️ AWS GovCloud (US):** GovCloud regions (`us-gov-east-1`, `us-gov-west-1`) do not support `kiro.dev` DNS names. If you enable private DNS for a GovCloud VPC endpoint, you can only make API requests using the `q.<region>.amazonaws.com` DNS names (for example, `q.us-gov-east-1.amazonaws.com`).

The following private DNS names also resolve through the existing VPC endpoint automatically. No additional endpoints or configuration changes are required:

- `runtime.<region>.kiro.dev`
- `management.<region>.kiro.dev`
- `telemetry.<region>.kiro.dev`

Where `<region>` is `us-east-1` or `eu-central-1`.

For more information, see [Accessing a service through an interface endpoint](https://docs.aws.amazon.com/vpc/latest/privatelink/create-interface-endpoint.html#access-service-though-endpoint) in the Amazon VPC User Guide.

## Using an on-premises computer to connect to a Kiro endpoint

This section describes the process of using an on-premises computer to connect to Kiro through an AWS PrivateLink endpoint in your AWS VPC.

1. [Create a VPN connection between your on-premises device and your VPC](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/client-vpn-user-what-is.html).
2. [Create an interface VPC endpoint for Kiro](#creating-an-interface-vpc-endpoint-for-kiro).
3. [Set up an inbound Amazon Route 53 endpoint](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-vpc-interface-endpoint.html). This will enable you to use the DNS name of your Kiro endpoint from your on-premises device.
