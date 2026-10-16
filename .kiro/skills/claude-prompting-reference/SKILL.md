---
name: claude-prompting-reference
description: >
  Anthropic's official prompting documentation for current Claude models, vendored
  locally. Use when writing or revising a prompt, an agent definition, a steering file
  or a skill, when deciding how much effort or thinking a task warrants, when a model
  behaves differently from a previous version, or when hardening a prompt against
  untrusted input. Triggers: 'prompting best practices', 'Opus 5.5', 'Sonnet 5.5',
  'effort parameter', 'prompt injection'. Not for Kiro CLI configuration questions,
  which the kiro-cli-reference skill covers.
---

# Claude Prompting Reference

Official Anthropic prompting documentation, synced verbatim from
<https://platform.claude.com/docs/>. The mirror exists so that prompt and steering work
in this repository cites current upstream guidance instead of recalled guidance.

Never hand-edit `references/`; scope, sync and editing rules are in
[PROVENANCE.md](PROVENANCE.md). Check freshness with `make sync-anthropic-check`.

## Reference Index

### Core Prompting Guidance

| File                                                                                                                                        | Topic                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [prompt-engineering/overview.md](references/build-with-claude/prompt-engineering/overview.md)                                               | When prompt engineering is the right solution, and where the technique guides and tutorials live                   |
| [prompt-engineering/claude-prompting-best-practices.md](references/build-with-claude/prompt-engineering/claude-prompting-best-practices.md) | The reference guide: clarity, examples, XML structuring, thinking, and agentic-system prompting for current models |

### Per-Model Behaviour

The 5.5 guides describe differences from the corresponding 5.0 model and defer to the
5.0 guide as a baseline, so both generations stay indexed. Upstream still publishes the
5.0 guides.

| File                                                                                                                                | Topic                                                                                                                               |
| ----------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| [prompt-engineering/prompting-claude-opus-5-5.md](references/build-with-claude/prompt-engineering/prompting-claude-opus-5-5.md)     | Opus 5.5: effort calibration, prompts written for thinking disabled, unattended runs, progress updates, multiagent time signals     |
| [prompt-engineering/prompting-claude-sonnet-5-5.md](references/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5.md) | Sonnet 5.5: effort, initiative and scope, running without up-front thinking, JSON output, verification, tolerant tool-call handling |
| [prompt-engineering/prompting-claude-opus-5.md](references/build-with-claude/prompt-engineering/prompting-claude-opus-5.md)         | Opus 5: response verbosity, agentic narration, task scoping, subagent delegation, self-correction                                   |
| [prompt-engineering/prompting-claude-sonnet-5.md](references/build-with-claude/prompt-engineering/prompting-claude-sonnet-5.md)     | Sonnet 5: effort, adaptive thinking defaults, tool use, migration from Sonnet 4.6                                                   |
| [prompt-engineering/prompting-claude-opus-4-8.md](references/build-with-claude/prompt-engineering/prompting-claude-opus-4-8.md)     | Opus 4.8: verbosity, effort calibration, tool use, subagents, frontend defaults                                                     |

### Model Release Notes

Tracked only for the two models the agents run (Opus 5.5 and Sonnet 5.5). They carry the
breaking API changes and the per-model effort defaults that the session effort policy
and `.kiro/settings/cli.json` depend on.

| File                                                                                              | Topic                                                                                                                 |
| ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| [models/opus-5-5/whats-new-opus-5-5.md](references/models/opus-5-5/whats-new-opus-5-5.md)         | Opus 5.5: thinking always on, forced tool use rejected, thinking-block binding, `medium` default effort               |
| [models/sonnet-5-5/whats-new-sonnet-5-5.md](references/models/sonnet-5-5/whats-new-sonnet-5-5.md) | Sonnet 5.5: `between_tools` thinking control, forced tool use rejected, thinking-block binding, `high` default effort |

### Effort, Thinking and Context

| File                                                                  | Topic                                                                                                        |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [effort.md](references/build-with-claude/effort.md)                   | The effort parameter: trading response thoroughness against token efficiency                                 |
| [thinking.md](references/build-with-claude/thinking.md)               | Turning thinking on, reading its output, steering its depth, and combining it with tools, caching, streaming |
| [context-windows.md](references/build-with-claude/context-windows.md) | How the context window is consumed by thinking and tool use, and how to manage it as a session grows         |

### Guardrails

| File                                                                                                    | Topic                                                                                           |
| ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [increase-consistency.md](references/test-and-evaluate/strengthen-guardrails/increase-consistency.md)   | Exact output formats, prefilling, constraining with examples, grounding answers in retrieval    |
| [mitigate-jailbreaks.md](references/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks.md)     | Input screening, hardened system prompts, and safe handling of untrusted tool content           |
| [reduce-hallucinations.md](references/test-and-evaluate/strengthen-guardrails/reduce-hallucinations.md) | Allowing uncertainty, grounding in direct quotes, verifying claims with citations               |
| [reduce-prompt-leak.md](references/test-and-evaluate/strengthen-guardrails/reduce-prompt-leak.md)       | Separating context from user queries, output filtering, auditing prompts without losing quality |

## Reading Guidance

Start from `claude-prompting-best-practices.md` for anything general — it is the current
reference and supersedes technique-by-technique advice found elsewhere. Consult the
per-model page only for behaviour that differs between versions, which is where
migration surprises come from. Pair it with the matching release-notes page when the
question concerns API behaviour (thinking, `tool_choice`, effort defaults) rather than
prompt wording. The guardrail pages are the right citation when a prompt must resist
untrusted input.
