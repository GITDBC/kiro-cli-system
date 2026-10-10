> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Available models

> Detailed descriptions of every AI model available in Kiro, including capabilities, behavior differences, and lifecycle status.

Every model in Kiro is described below with its strengths, ideal use cases, and lifecycle status. For a quick comparison table and guidance on choosing, see the [Models overview](https://kiro.dev/docs/models.md).

## GPT-5.6 Sol

Choose Sol for your hardest multi-step work, especially long-horizon refactors and complex terminal tasks. It is OpenAI's flagship GPT-5.6 tier for frontier reasoning, coding, long-horizon planning, and workflows that require iteration and tool coordination. Sol scores 80 on the Coding Agent Index and 88.8% on Terminal-Bench 2.1, above Claude Fable 5 on both while using less than half the output tokens and taking less than half the time. Sol has a 4.4x Kiro credit multiplier for requests up to 272K tokens.

## GPT-5.6 Terra

Choose Terra for routine multi-step development when you want a middle ground between Sol's maximum capability and Luna's speed and Kiro credit efficiency. Terra scores 77.4 on the Coding Agent Index, compared with Claude Fable 5's 77.2. OpenAI separately describes Terra as GPT-5.5-competitive at half the API cost. That API comparison does not determine Kiro credit use; Terra has a 2.2x Kiro credit multiplier for requests up to 272K tokens.

## GPT-5.6 Luna

Choose Luna for high-frequency agentic tasks where speed, throughput, and Kiro credit efficiency matter more than maximum capability. OpenAI describes Luna as its fastest and lowest-cost GPT-5.6 API tier. Luna scores 74.6 on the Coding Agent Index, compared with Claude Opus 4.8's 72.5. Luna has a 1.1x Kiro credit multiplier for requests up to 272K tokens, the lowest of the three GPT-5.6 tiers.

All three GPT-5.6 tiers have a 1M token context window in the IDE, CLI, and Web. You can include longer codebases, documents, and multi-turn agent histories in a request.

Experimental support is rolling out to Pro, Pro+, Pro Max, and Power in us-east-1 and eu-central-1 with cross-region inference.

GPT-5.6 pricing follows the two-tier context model used by OpenAI and Amazon Bedrock: requests up to 272K tokens are billed at the short context rate listed above, and requests over 272K tokens are billed at double that rate (Sol 8.8x, Terra 4.4x, Luna 2.2x). [Learn more](https://openai.com/index/previewing-gpt-5-6-sol/).

## Claude Fable 5.1 (Preview)

Anthropic's most capable agentic coding model for long-running, context-heavy work. Fable 5.1 traces problems to root causes, maintains context and intent across complex tasks, and improves reliability for multi-file refactors, long autonomous runs, and security or systems work. It has a 1M context window and a 6x credit multiplier. Inference runs only in US East (N. Virginia) (`us-east-1`).

### Security tasks and safeguards

Fable 5.1 can help discover software vulnerabilities with safeguards tuned to reduce interruptions during legitimate defensive security work. Requests for exploit generation, binary-based vulnerability scanning, and penetration testing continue to use Opus-class models in Kiro.

Fable 5.1 is rolling out gradually to Kiro Enterprise organizations with [model governance](https://kiro.dev/docs/enterprise/governance/model.md) enabled. Availability is limited during Preview. Organizations with access can add Fable 5.1 from **Manage approved list** and make it available to their users. Users must restart the IDE or CLI, or refresh Kiro Web, before it appears in the model selector.

All Fable 5.1 traffic is retained for up to 30 days (unless otherwise required by law) for automated offline abuse detection. Classifier-flagged traffic will be subject to potential human review performed by AWS, and we may review flagged traffic for abuse. See [Data protection](https://kiro.dev/docs/privacy-and-security/data-protection.md#kiro-abuse-detection).

## Auto (recommended)

Kiro's model router. Auto routes your requests to frontier models with automatic fallback capabilities, so you get reliable top-tier quality without having to pick a model yourself. Free tier users get Claude Sonnet-class quality or better, while paid tiers get Claude Opus-class quality or better. Auto maintains a high quality bar to ensure results compare to or exceed the individual models available to you.

Auto is treated as its own selectable option under model governance: administrators can allow or block Auto for their users. However, when Auto is enabled, it does not restrict its internal routing to the models an administrator has approved; it may route requests to any generally available model in Kiro in that region. Auto does not route to [experimental](https://kiro.dev/docs/privacy-and-security/data-protection.md#global-cross-region-inference-for-experimental-features) models. Customers who need to guarantee that only approved models process their requests should block Auto and set an approved model as the default.

## Claude Opus 5

Anthropic's strongest agentic coding model. Sets new state-of-the-art results on leading coding benchmarks, more than doubling Opus 4.8's performance while approaching Fable 5 at half the cost. Excels at multi-file features, large refactors, and end-to-end feature work - completing full tasks rather than leaving stubs or placeholders. Opus 5 verifies its own work, iterates carefully until it succeeds, and introduces meaningful gains in multi-agent coordination with fewer conflicts between parallel agents. Ships with 1M context window and a 2.2x credit multiplier. Available in us-east-1 and eu-central-1 with cross-region inference. [Learn more](https://www.anthropic.com/news/claude-opus-5).

## Claude Opus 4.8

Anthropic's most honest Opus model. Around 4x less likely than its predecessor to let flaws in generated code pass unremarked - it flags uncertainties and pushes back when evidence is thin rather than confidently claiming progress. Tool calling is meaningfully more efficient, using fewer steps for the same intelligence. Early testers report stronger judgment on when to act vs. when to ask, and better follow-through on long-running agentic tasks. Ships with 1M context window and 128K max output. Available in us-east-1 and eu-central-1 with cross-region inference. [Learn more](https://www.anthropic.com/news/claude-opus-4-8).

## Claude Opus 4.7

Introduces adaptive thinking: the model automatically scales its internal reasoning based on task complexity. Simple questions get fast responses; complex architectural problems get deeper analysis, without you configuring anything. Beyond that, Opus 4.7 follows instructions more precisely, verifies its own outputs before reporting back, and supports 3x higher resolution vision for working with dense screenshots and diagrams. Available in us-east-1 and eu-central-1 with cross-region inference. [Learn more](https://www.anthropic.com/news/claude-opus-4-7).

## Claude Opus 4.6

Top scores on Terminal-Bench 2.0 and SWE-bench Verified for agentic coding. Stays productive over longer sessions without context drift and handles multi-million-line codebases, planning upfront and adapting as needed. Strong debugging and code review capabilities let it catch its own mistakes through careful planning and self-correction. [Learn more](https://www.anthropic.com/research/claude-opus-4-6).

## Claude Opus 4.5

Handles tradeoffs and ambiguity well when working across multiple systems. Strong single-shot accuracy on complex problems where you need a correct answer on the first attempt, without iterative back-and-forth. Well suited for sophisticated software development challenges that span service boundaries. [Learn more](https://www.anthropic.com/news/claude-opus-4-5).

## Claude Sonnet 5

Anthropic's most agentic Sonnet model. Performance approaches Opus 4.8 on reasoning, tool use, coding, and knowledge work, at Sonnet-class pricing. Plans before it edits, runs longer without supervision, and checks its own output without being asked. Early testers consistently describe it as finishing complex tasks where prior Sonnet models would stop short. Well suited for spec-driven workflows where you need higher-fidelity implementation across broad changes, and for multi-step agentic tasks in the CLI and Web that run to completion with less supervision. [Learn more](https://www.anthropic.com/news/claude-sonnet-5).

## Claude Sonnet 4.6

A full upgrade from Sonnet 4.5 that approaches Opus 4.6 intelligence while being more token efficient. Excels at iterative development workflows and maintains context across long sessions. Handles both lead agent and subagent roles in multi-model pipelines, making it well-suited for teams using Kiro powers and custom subagents. [Learn more](https://www.anthropic.com/news/claude-sonnet-4-6).

## Claude Sonnet 4.5

Strong agentic coding with extended autonomous operation - can work independently for hours with effective tool usage. Improved planning, system design, and security engineering compared to Sonnet 4.0. [Learn more](https://www.anthropic.com/news/claude-sonnet-4-5).

## Claude Sonnet 4.0

Direct access to Anthropic's Claude Sonnet 4.0 for users who prefer consistent model selection. Same model for all interactions with no routing or optimization layers. Full control and complete transparency, with predictable behavior for workflows that depend on specific model characteristics. [Learn more](https://www.anthropic.com/news/claude-4).

## Claude Haiku 4.5

Anthropic's fastest model with near-frontier performance. Matches Sonnet 4 performance across reasoning and coding at more than twice the speed. Near-frontier intelligence at one-third the cost, and the first Haiku model with extended thinking capabilities. [Learn more](https://www.anthropic.com/news/claude-haiku-4-5).

## MiniMax M2.5

Open weight model that matches frontier-class coding performance at a fraction of the cost. Trained with reinforcement learning across hundreds of thousands of real-world environments, delivering strong results across the full development lifecycle from system design to code review. 0.25x credit multiplier with inference running in US East (N. Virginia) and EU (Frankfurt). [Learn more](https://www.minimax.io/news/minimax-m25).

## GLM-5

Open weight sparse mixture-of-experts model with a 200K context window, designed for complex systems engineering and long-horizon agentic tasks. Excels at processing repository-scale context and maintaining coherence during multi-step tool use across large codebases. Well suited for cross-file migrations, full-stack feature development, and legacy refactoring where the model needs to hold the full picture. 0.5x credit multiplier with inference running in US East (N. Virginia). [Learn more](https://z.ai/blog/glm-5).

## DeepSeek 3.2

Open weight model best suited for agentic workflows and code generation. Handles long tool-calling chains, stateful sessions, and multi-step reasoning well. 0.25x credit multiplier with inference running in US East (N. Virginia). [Learn more](https://api-docs.deepseek.com/news/news250325).

## MiniMax M2.1

Open weight model best suited for multilingual programming and UI generation. Delivers strong results across Rust, Go, C++, Kotlin, TypeScript, and others. 0.15x credit multiplier with inference running in US East (N. Virginia) and EU (Frankfurt). [Learn more](https://minimax.io/news/minimax-m21).

## Qwen3 Coder Next

Open weight model purpose-built for coding agents with 256K context and strong error recovery. Works especially well for long agentic coding sessions. 0.05x credit multiplier, the most cost-effective option available, with inference running in US East (N. Virginia) and EU (Frankfurt). [Learn more](https://qwenlm.github.io/blog/qwen3-coder/).

## How models behave differently

Each model family brings a distinct working style. Understanding these differences helps you pick the right one for the task.

### GPT-5.6 (OpenAI)

GPT-5.6 models can write lightweight programs that coordinate tools and process intermediate results instead of making separate round-trips for each step. This reduces token use and dead ends, especially for spec implementation, terminal workflows, and multi-file refactors. All three tiers support longer unsupervised execution and use hidden chain-of-thought, so you see the final output rather than internal reasoning steps. Choose Sol for the hardest long-horizon work, Terra for balanced routine development, and Luna when speed and Kiro credit efficiency matter most.

### Claude Opus (Anthropic)

Opus models plan thoroughly before acting, considering multi-step approaches and edge cases upfront. They catch their own mistakes through careful review and flag uncertainty rather than confidently claiming progress. Starting with Opus 4.7, reasoning depth scales automatically based on task complexity - simpler prompts get fast responses while harder problems receive deeper analysis without you configuring anything. Opus 5 adds state-of-the-art multi-agent coordination and completes full tasks rather than leaving stubs or placeholders. Opus excels at sustained multi-file work, complex debugging, and architecture decisions where self-verification matters.

### Claude Sonnet (Anthropic)

Sonnet models balance strong agentic performance with lower Kiro credit use (1.3x versus 2.2x for Opus). Sonnet 5 plans before editing, runs longer without supervision, and checks its own output - approaching Opus-class results for spec-driven workflows and multi-step CLI and Web tasks. Earlier Sonnet models are more conservative and stick closer to what you asked for, making them predictable choices for focused, well-scoped work.

### Open weight models (DeepSeek, MiniMax, GLM, Qwen)

Open weight models offer frontier-competitive coding at the lowest Kiro credit multipliers (0.05x–0.5x). They are well suited for long sessions, high-throughput agentic work, and tasks where credit efficiency matters more than peak single-turn capability. MiniMax M2.5 delivers near-Opus results across the development lifecycle. GLM-5 handles repository-scale context for cross-file migrations and full-stack work. DeepSeek 3.2 handles long tool-calling chains and multi-step reasoning. Qwen3 Coder Next is the most cost-effective option with strong error recovery for extended CLI sessions.

## Model lifecycle

Models in Kiro go through two stages. Each stage reflects the model's maturity and the level of support you can expect.

| Stage | Description |
|-------|-------------|
| Experimental | Available for early testing and may change based on feedback. Marked in the model selector with limited region availability. |
| Active | Fully supported and recommended for production use. Available in all supported regions. |

**ℹ️ Info:** Inference requests for experimental models may be processed across multiple AWS Regions globally to optimize availability and performance. See [data protection](https://kiro.dev/docs/privacy-and-security/data-protection.md#global-cross-region-inference-for-experimental-features) for details on cross-region inference.

### Launch dates

| Model | Launched | Status |
|-------|----------|--------|
| Claude Opus 5 | July 24, 2026 | Active |
| GPT-5.6 Sol | July 13, 2026 | Experimental |
| GPT-5.6 Terra | July 13, 2026 | Experimental |
| GPT-5.6 Luna | July 13, 2026 | Experimental |
| Claude Sonnet 5 | June 30, 2026 | Active |
| Claude Opus 4.8 | May 28, 2026 | Active |
| Claude Opus 4.7 | April 16, 2026 | Active |
| GLM-5 | March 31, 2026 | Active |
| MiniMax M2.5 | March 18, 2026 | Active |
| Claude Sonnet 4.6 | February 17, 2026 | Active |
| DeepSeek 3.2 | February 10, 2026 | Experimental |
| MiniMax M2.1 | February 10, 2026 | Experimental |
| Qwen3 Coder Next | February 10, 2026 | Experimental |
| Claude Opus 4.6 | February 5, 2026 | Active |
| Claude Opus 4.5 | November 24, 2025 | Active |
| Claude Sonnet 4.5 | September 29, 2025 | Active |
| Auto | September 17, 2025 | Active |
| Claude Sonnet 4.0 | September 4, 2025 | Active |
| Claude Haiku 4.5 | September 4, 2025 | Active |
