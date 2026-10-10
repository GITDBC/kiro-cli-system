---
name: claude-prompting-reference
description: >
  Anthropic's official prompting documentation for current Claude models, vendored
  locally. Use when writing or revising a prompt, an agent definition, a steering file
  or a skill, when deciding how much effort or thinking a task warrants, when a model
  behaves differently from a previous version, or when designing evaluations and
  guardrails for prompted behaviour. Triggers: 'prompt engineering', 'prompting best
  practices', 'Opus 5', 'Sonnet 5', 'effort parameter', 'extended thinking', 'context
  window', 'prompt injection', 'jailbreak', 'hallucination', 'prompt leak', 'output
  consistency', 'evaluations', 'system prompt design'. Not for Kiro CLI configuration
  questions, which the kiro-cli-reference skill covers.
---

# Claude Prompting Reference

Official Anthropic prompting documentation, synced verbatim from
<https://platform.claude.com/docs/>. The mirror exists so that prompt and steering work
in this repository cites current upstream guidance instead of recalled guidance.

## Mirror Scope

Two selection rules decide what lands here, both encoded in
`tools/docsync/docsync/sources/anthropic.py`:

| Rule               | What it takes                                            | Why                                                                                                   |
| ------------------ | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Subtree, by prefix | Everything under `build-with-claude/prompt-engineering/` | Anthropic publishes a per-model prompting guide with each release; a prefix picks it up automatically |
| Exact slug         | Individually listed pages in `TRACKED_PAGES`             | These sit in sections whose other pages are irrelevant here, so a prefix would drag the section in    |

Local paths reproduce the upstream layout, so `build-with-claude/effort.md` is mirrored
at `references/build-with-claude/effort.md` and no two pages can collide on a shared
filename such as `overview.md`.

A tracked exact page that disappears from the upstream catalogue aborts the sync with an
error rather than being dropped quietly: the page was chosen deliberately, so its
removal is a decision to re-take. A page inside the subtree comes and goes with the
catalogue, and `--prune` removes the local file once it is gone.

## Freshness Check

The mirror records its last successful sync in `.last-sync.json` at the skill root,
beside this file rather than inside `references/`, because pruning walks that directory
and would treat any companion file there as an orphan.

```bash
make sync-anthropic-check   # network dry run; exits 1 when updates are pending
make sync-anthropic         # apply updates and refresh the marker
```

To additionally remove local pages the catalogue no longer advertises:

```bash
uv run --project tools/docsync docsync anthropic --prune
```

Never hand-edit a file under `references/` — the next sync overwrites it. See
[PROVENANCE.md](PROVENANCE.md) for the upstream identity and the editing rules.

## Reference Index

### Core Prompting Guidance

| File                                                                                                                                        | Topic                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [prompt-engineering/overview.md](references/build-with-claude/prompt-engineering/overview.md)                                               | When prompt engineering is the right solution, and where the technique guides and tutorials live                   |
| [prompt-engineering/claude-prompting-best-practices.md](references/build-with-claude/prompt-engineering/claude-prompting-best-practices.md) | The reference guide: clarity, examples, XML structuring, thinking, and agentic-system prompting for current models |

### Per-Model Behaviour

| File                                                                                                                              | Topic                                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| [prompt-engineering/prompting-claude-opus-5.md](references/build-with-claude/prompt-engineering/prompting-claude-opus-5.md)       | Opus 5: response verbosity, agentic narration, task scoping, subagent delegation, self-correction    |
| [prompt-engineering/prompting-claude-sonnet-5.md](references/build-with-claude/prompt-engineering/prompting-claude-sonnet-5.md)   | Sonnet 5: effort, adaptive thinking defaults, tool use, migration from Sonnet 4.6                    |
| [prompt-engineering/prompting-claude-opus-4-8.md](references/build-with-claude/prompt-engineering/prompting-claude-opus-4-8.md)   | Opus 4.8: verbosity, effort calibration, tool use, subagents, frontend defaults                      |
| [prompt-engineering/prompting-claude-fable-5.md](references/build-with-claude/prompt-engineering/prompting-claude-fable-5.md)     | Fable 5 and Mythos 5: effort, instruction following, long runs, memory, scaffolding changes          |
| [prompt-engineering/prompting-claude-fable-5-1.md](references/build-with-claude/prompt-engineering/prompting-claude-fable-5-1.md) | Fable 5.1 and Mythos 5.1: effort, progress updates, tool-call batching, scope, subagents, compaction |

### Effort, Thinking and Context

| File                                                                  | Topic                                                                                                        |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [effort.md](references/build-with-claude/effort.md)                   | The effort parameter: trading response thoroughness against token efficiency                                 |
| [thinking.md](references/build-with-claude/thinking.md)               | Turning thinking on, reading its output, steering its depth, and combining it with tools, caching, streaming |
| [context-windows.md](references/build-with-claude/context-windows.md) | How the context window is consumed by thinking and tool use, and how to manage it as a session grows         |

### Evaluation and Guardrails

| File                                                                                                    | Topic                                                                                           |
| ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [develop-tests.md](references/test-and-evaluate/develop-tests.md)                                       | Defining measurable success criteria and building evaluations, from exact match to LLM grading  |
| [increase-consistency.md](references/test-and-evaluate/strengthen-guardrails/increase-consistency.md)   | Exact output formats, prefilling, constraining with examples, grounding answers in retrieval    |
| [mitigate-jailbreaks.md](references/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks.md)     | Input screening, hardened system prompts, and safe handling of untrusted tool content           |
| [reduce-hallucinations.md](references/test-and-evaluate/strengthen-guardrails/reduce-hallucinations.md) | Allowing uncertainty, grounding in direct quotes, verifying claims with citations               |
| [reduce-prompt-leak.md](references/test-and-evaluate/strengthen-guardrails/reduce-prompt-leak.md)       | Separating context from user queries, output filtering, auditing prompts without losing quality |

## Reading Guidance

Start from `claude-prompting-best-practices.md` for anything general — it is the current
reference and supersedes technique-by-technique advice found elsewhere. Consult the
per-model page only for behaviour that differs between versions, which is where
migration surprises come from. The guardrail pages are the right citation when a prompt
must resist untrusted input, and `develop-tests.md` is the one to cite when a change to
prompted behaviour needs evidence rather than an opinion.
