> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Models

> Enterprise governance of models for Kiro

By default, your users can use any model supported by Kiro in their client. You have the ability to manage which models your users are allowed to use.

You can manage model access by selecting the list of models that users can access.

## Claude Fable 5.1 Preview rollout

Claude Fable 5.1 is rolling out gradually to Kiro Enterprise organizations. Availability is limited during Preview, and inference runs only in US East (N. Virginia) (`us-east-1`). Organizations with access can enable Fable 5.1 through model governance.

After model access management is enabled, administrators can add Fable 5.1 from **Manage approved list**. Fable 5.1 then appears in the model selector across the Kiro IDE, CLI, and Web after users restart or refresh their client. See [Claude Fable 5.1](https://kiro.dev/docs/models/available-models.md#claude-fable-51-preview) for pricing and complete data-handling details.

**⚠️ Warning:** All Fable 5.1 traffic is retained for up to 30 days (unless otherwise required by law) for automated offline abuse detection. Classifier-flagged traffic will be subject to potential human review performed by AWS, and we may review flagged traffic for abuse.

**⚠️ Warning:** Make sure that the Kiro clients are updated to the latest version for proper enforcement.

## Enabling model access management

To opt into managing the models list:
1. Open the Kiro console.
2. Choose **Settings**.
3. In the **Shared settings** section, toggle the **Control which models are available to users** under the **Model availability** setting.

![model availability settings](https://kiro.dev/images/enterprise/mcp-governance.png)

## Adding models to the allow list

To add models to the list of models available in Kiro clients:
1. Select the **Manage approved list** link in the **Model availability** setting.
2. A modal dialog will show the list of models that are available to manage including "Auto"
3. Each model will have a name and description.
4. Select the models that you want to make available to the clients.
5. Set a default model. The default model is automatically applied to all clients in your organization.
6. Select **Save list** to save the model list.

![model list](https://kiro.dev/images/enterprise/models-list.png)

**⚠️ Warning:** Adding models to the model list will not take effect immediately. Either clients have to restart their session or logoff / login to load the models list.

## Removing models from the allow list

To remove models from the allow list, simply uncheck the models from the allow list of models. 

Keep in mind, removing a model that was previously available will not be immediately removed from the client. Clients have to restart their session. 

## Key considerations

1. If you manage the model allow list, any new model offered by Kiro will not become available to clients unless you add them into the allow list.
2. You will receive a notification in the console when a new model becomes available.
