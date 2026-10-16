> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Models

> Choose the right AI model for your development tasks in Kiro.

Kiro gives you access to frontier and open weight AI models from OpenAI, Anthropic, and other providers. GPT-5.6 brings OpenAI models to Kiro for the first time, with three tiers that balance agentic performance and cost. Pick the right model for the job, or select Auto to let Kiro route each task to the optimal model automatically.

**ℹ️ Info:** Model selection is only available for chat experience - interactive and non-interactive.

## Quick comparison

| Model | Context | Cost | Regions | Free | Pro | Pro+ | Pro Max | Power |
|-------|:-------:|:----:|:-------:|:----:|:---:|:----:|:-------:|:-----:|
| **GPT-5.6 Sol** | 1M | 4.4x* | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **GPT-5.6 Terra** | 1M | 2.2x* | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **GPT-5.6 Luna** | 1M | 0.6x* | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **Claude Fable 5.1**<sup>†</sup> | 1M | 6x | US East only | | | | | |
| **Claude Opus 5.5** | 1M | 2.0x | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **Claude Sonnet 5.5** | 1M | 1.3x | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **Claude Opus 5** | 1M | 2.2x | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **Claude Opus 4.8** | 1M | 2.2x | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **Claude Opus 4.7** | 1M | 2.2x | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **Claude Opus 4.6** | 1M | 2.2x | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **Claude Opus 4.5** | 200K | 2.2x | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **Claude Sonnet 5** | 1M | 1.3x | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **Claude Sonnet 4.6** | 1M | 1.3x | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **Claude Sonnet 4.5** | 200K | 1.3x | US, EU | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Claude Sonnet 4.0** | 200K | 1.3x | US, EU | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Auto** | — | 1.0x | US, EU | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Claude Haiku 4.5** | 200K | 0.4x | US, EU | | ✓ | ✓ | ✓ | ✓ |
| **Kimi K3** | 1M | 2.4x | US | | ✓ | ✓ | ✓ | ✓ |
| **DeepSeek 3.2** | 128K | 0.25x | US, EU | ✓ | ✓ | ✓ | ✓ | ✓ |
| **MiniMax M2.5** | 200K | 0.25x | US, EU | ✓ | ✓ | ✓ | ✓ | ✓ |
| **GLM-5** | 200K | 0.5x | US, EU | ✓ | ✓ | ✓ | ✓ | ✓ |
| **MiniMax M2.1** | 200K | 0.15x | US, EU | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Qwen3 Coder Next** | 256K | 0.05x | US, EU | ✓ | ✓ | ✓ | ✓ | ✓ |

† Claude Fable 5.1 is rolling out in a limited Preview for Kiro Enterprise customers. Administrators enable access through model governance.

### Enterprise Preview rollout

**Claude Fable 5.1** is rolling out gradually to Kiro Enterprise organizations with model governance enabled. It has a 1M context window and a 6x credit multiplier. Inference runs only in US East (N. Virginia) (`us-east-1`). Organizations with access can add Fable 5.1 from **Manage approved list** and make it available to their users. See [Claude Fable 5.1](https://kiro.dev/docs/models/available-models.md#claude-fable-51-preview) for capabilities and data-handling details.

US and EU are commercial geographies, each spanning several AWS Regions rather than a single Region. For the Regions in each geography and the endpoint that serves your requests, see [Inference endpoint regions](#inference-endpoint-regions).

Cost is relative to Auto (1.0x baseline). For example, a task that costs 10 credits on Auto would cost 20 credits on Opus 5.5, 22 credits on Opus 5, 4 credits on Haiku, or 0.5 credits on Qwen3 Coder Next.

\* GPT-5.6 uses OpenAI and Amazon Bedrock's two-tier context pricing model: requests up to 272K tokens use the listed short context rate, and requests over 272K tokens are billed at double that rate (Sol 8.8x, Terra 4.4x, Luna 1.2x).

**ℹ️ Info:** Models that share the same credit multiplier won't necessarily consume the same number of credits per task. Actual consumption depends on factors like how many tokens the model generates, internal thinking depth, and tokenizer differences. For example, Opus 4.8 uses an updated tokenizer compared to Opus 4.6, so the same prompt and response can be counted as a different number of tokens - leading to different credit costs even though both carry a 2.2x multiplier.

## AWS GovCloud (US)

AWS GovCloud (US) has a separate model catalog and Region-specific availability. See [AWS GovCloud (US) models](https://kiro.dev/docs/models/govcloud.md) for the current model list, East and West availability, access requirements, and model-authorization guidance.

## Inference endpoint regions

The table below is the source of truth for model routing. **Inference scope** shows whether requests stay within the listed endpoint location or may route globally. The profile columns show the endpoint used for each Kiro profile Region. Lifecycle status and inference routing are independent.

Profile Region applies to enterprise users who sign in through IAM Identity Center or an external identity provider. Free Tier users and individual subscribers use the US endpoint.

| Model | Inference scope | Kiro profile in US East (N. Virginia) | Kiro profile in Europe (Frankfurt) |
|-------|:---------------:|:-------------------------------------:|:----------------------------------:|
| **GPT-5.6 Sol** | Global | US | US |
| **GPT-5.6 Terra** | Global | US | US |
| **GPT-5.6 Luna** | Global | US | US |
| **Claude Fable 5.1** | Geography | US | — |
| **Claude Opus 5.5** | Geography | US | EU |
| **Claude Sonnet 5.5** | Geography | US | EU |
| **Claude Opus 5** | Geography | US | EU |
| **Claude Opus 4.8** | Geography | US | EU |
| **Claude Opus 4.7** | Geography | US | EU |
| **Claude Opus 4.6** | Geography | US | EU |
| **Claude Opus 4.5** | Geography | US | EU |
| **Claude Sonnet 5** | Geography | US | EU |
| **Claude Sonnet 4.6** | Geography | US | EU |
| **Claude Sonnet 4.5** | Geography | US | EU |
| **Claude Sonnet 4.0** | Geography | US | EU |
| **Auto** | Geography | US | EU |
| **Claude Haiku 4.5** | Geography | US | EU |
| **Kimi K3** | Global | US | — |
| **DeepSeek 3.2** | Geography | US | EU |
| **MiniMax M2.5** | Geography | US | EU |
| **GLM-5** | Geography | US | EU |
| **MiniMax M2.1** | Geography | US | EU |
| **Qwen3 Coder Next** | Geography | US | EU |

**Inference scope** shows where requests may be processed:

- **Geography:** Within the endpoint geography shown in the row.
- **Global:** Across supported commercial AWS Regions worldwide, including outside the endpoint geography.

### Regions in each geography

The Regions below support inference within each geography. Individual models may use one or more listed Regions.

| Geography | Regions used for inference |
|-----------|----------------------------|
| **US** | US East (N. Virginia) `us-east-1`, US West (Oregon) `us-west-2`, US East (Ohio) `us-east-2` |
| **EU** | Europe (Frankfurt) `eu-central-1`, Europe (Ireland) `eu-west-1`, Europe (Paris) `eu-west-3`, Europe (Stockholm) `eu-north-1`, Europe (Milan) `eu-south-1`, Europe (Spain) `eu-south-2` |

Cross-region inference, including global routing, does not change where Kiro stores your data. For the full Global scope disclosure, see [Global cross-region inference](https://kiro.dev/docs/privacy-and-security/data-protection.md#global-cross-region-inference). Global routing does not apply to AWS GovCloud (US). See [Kiro in AWS GovCloud (US)](https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/govcloud-kiro.html) for GovCloud behavior and [Amazon Bedrock cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) for how inference profiles route requests.

## How to switch models

    IDE
    CLI
    Web
    Crew
    Mobile

Use the model dropdown in the chat interface to switch models. Your selection applies to all subsequent messages in the conversation.

  [Video](https://kiro.dev/videos/model-selection.mp4)

Open `/model` in the terminal UI to switch models and configure the selected model's thinking and effort. You can also set your default model from the command line. If a model from the list above does not appear in `/model`, restart Kiro CLI.

```bash
kiro-cli settings chat.defaultModel claude-opus-4.8
```

To save your current model as the default for all future sessions:

```bash
> /model set-current-as-default
```

This stores your preference in `~/.kiro/settings/cli.json`. New sessions automatically use this model.

  [Video](https://kiro.dev/videos/select-model-cli.mp4)

Use the model dropdown in the chat input area to switch models before sending a message.

Use the model picker in the chat input to switch models for the current session. To choose which model new sessions use by default, open **Settings → Chat → Models**. If a newly available model does not appear, run `kirocrew restart`.

Coming soon to Mobile.

## Model fallback notices

In a local V3 session, Kiro can move a turn to another model when the current model declines the request or is unavailable. The transcript names the model that continued and says whether the change applies to one turn or the rest of the conversation.

In Kiro IDE, a fallback inside a sub-agent appears inside that sub-agent's activity. A retry that keeps the same model appears as a temporary retry notice. In Kiro CLI, the final notice also lists the models tried and the outcome. See [Kiro CLI model fallback notices](https://kiro.dev/docs/cli/terminal-ui.md#model-fallback-notices) for terminal behavior.

## Which model should you use?

| Use case | Model | Why |
|----------|-------------------|-----|
| General development | **Auto** | Routes to the optimal model per task, balances quality and cost automatically |
| Hardest multi-step development | **GPT-5.6 Sol** | Best fit for long-horizon refactors and terminal work that requires sustained planning and tool coordination; 1M context for longer codebases, documents, and multi-turn histories |
| Routine multi-step development | **GPT-5.6 Terra** | Balanced tier for everyday agentic work; its 2.2x Kiro credit multiplier applies to requests up to 272K tokens |
| High-frequency agentic work | **GPT-5.6 Luna** | Fastest, lowest-cost GPT-5.6 tier for repeated tasks where throughput matters; its 0.6x Kiro credit multiplier applies to requests up to 272K tokens |
| Demanding agentic coding | **Opus 5.5** | Strong fit for long, complex tasks that benefit from sustained tool use, self-verification, and clear communication |
| Fast scoped coding and agents | **Sonnet 5.5** | Clear upgrade over Sonnet 5 with more than 30% faster output; strong fit for bug fixes, review, and scoped docs, slides, and spreadsheets |
| Speed or credit savings | **Haiku 4.5** | Near-frontier intelligence at a fraction of the cost, great for quick iterations and sub-agents |
| Frontier coding at low cost | **MiniMax M2.5** | Near Opus-level results at 0.25x cost, strong across the full development lifecycle |
| Repo-scale agentic work | **GLM-5** | 200K context optimized for long-horizon workflows across large codebases |
| Long coding sessions on a budget | **Qwen3 Coder Next** | 256K context with strong error recovery at 0.05x cost |

## Model availability

Model availability can vary by country or region. Kiro's model offerings align with each provider's usage and geographic requirements. For more information, see supported countries and regions: [OpenAI](https://platform.openai.com/docs/supported-countries), [Anthropic](https://www.anthropic.com/supported-countries), [MiniMax](https://www.minimax.io), [Zhipu AI](https://z.ai) (GLM), [DeepSeek](https://www.deepseek.com), and [Qwen](https://qwenlm.github.io).

## Reasoning effort

For models that support configurable reasoning effort, you can control how much reasoning the model applies to your prompts. Lower effort levels produce faster, shorter responses and use fewer credits. Higher levels spend more tokens on deeper analysis, multi-step reasoning, and thorough code generation.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Reasoning effort selection | ✓ | ✓ | ✓ | — |

In the IDE, set the level with the **Effort** slider below the model list in the **Model** panel. In Kiro CLI, open `/model` and choose **Effort**, or use the `--effort` launch flag. In Kiro Web, use the reasoning effort selector. The IDE choice applies to subsequent messages in the conversation. In CLI, effort chosen through `/model` persists for that model. Direct `/effort <level>` changes only the current session unless you then run `/effort set-current-as-default`; in V3, `--effort` is also session-only. Web choices apply to the current session. Each picker shows only levels supported by your current model. See [Reasoning effort](https://kiro.dev/docs/models/effort.md) for the full reference: per-surface mechanics, supported models, persistent per-model defaults, thinking behavior, and precedence.

**ℹ️ Info:** Higher effort levels use more tokens internally, which means more credit consumption per interaction - even at the same credit multiplier. This is one reason why two models with identical multipliers can produce different credit costs for the same task.

## Best practices

- **Start with Auto** for most work. It optimizes both quality and cost automatically.
- **Use GPT-5.6 Sol** for the hardest multi-step work - long-horizon refactors and complex terminal tasks where you need state-of-the-art agentic performance.
- **Use GPT-5.6 Terra or Luna** when you want strong agentic capability with throughput or cost as the primary concern. Terra for balanced performance, Luna for maximum efficiency.
- **Use Opus 5.5** when you hit a wall on a complex problem, need sustained multi-file work, or want stronger self-verification and clearer communication across a long task.
- **Use Sonnet 5.5** for fast, scoped coding, bug fixes, review, agent and subagent work, or focused documentation, slides, and spreadsheets.
- **Use Haiku** for quick iterations, simple fixes, or when you want to conserve credits.
- **Monitor your usage** in your [account settings](https://kiro.dev/docs/billing.md) to understand how model choice affects consumption.
- **Factor model cost into your tier:** If you primarily use Opus, consider Pro+, Pro Max, or Power for more credits. See [plans and billing](https://kiro.dev/docs/billing.md) for details.

For detailed descriptions of each model's capabilities, strengths, and lifecycle status, see [Available models](https://kiro.dev/docs/models/available-models.md).
