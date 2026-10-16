# Orchestration rationale and decision records

On-demand reference. It holds the arguments behind rules stated elsewhere, relocated off
the always-on path so they are not paid on every request. Read a section when a settled
decision is being challenged, re-derived, or re-argued — never to learn what to do. The
rules themselves live in `.kiro/steering/COMMON.md`,
`.kiro/orchestration/delegation-lifecycle.md`, and `.kiro/orchestration/routing.md`, and
each of them points here.

Nothing in this file is optional history: every section is a decision that was made
once, with its evidence, so that a future reader finds the reasoning instead of
repeating the debate.

## Repository layout: why orchestration material sits outside steering

Source: `.kiro/steering/COMMON.md` and the header of
`.kiro/orchestration/delegation-lifecycle.md`.

`.kiro/steering/` holds only what every agent needs: `COMMON.md`,
`code-standards-summary.md`, and `python-environment.md`. Orchestrator-only material
lives in `.kiro/orchestration/` and is loaded by the orchestrator alone, so a specialist
never pays for it and never has to decide whether it applies.

`delegation-lifecycle.md` reaches the session through an explicit
`file://.kiro/orchestration/delegation-lifecycle.md` entry in
`.kiro/agents/orchestrator.json`. That entry is load-bearing — removing it strips the
orchestrator of its delegation machinery.

The placement is deliberate and should not be undone. Kiro CLI loads every
`.kiro/steering/` file into every session, subagent sessions included, regardless of an
agent's `resources` list, and inclusion modes are unsupported on the CLI
(`kiro-cli-reference/references/steering.md`: "All steering files in the
`.kiro/steering/` directory are loaded automatically"). While `delegation-lifecycle.md`
and `routing.md` lived there, a probe of `engagement-manager` found their roughly 1,118
lines filling an estimated 70-75% of a specialist's context on every dispatch, for
content that specialist never acts on.

`driftcheck`'s `check_orchestration_placement` asserts both halves of the arrangement
together: the two files must not sit in `.kiro/steering/`, and the orchestrator must
still name them in its `resources`, which is now the only way they reach any session.

## Combined mode as the default delivery

Source: `delegation-lifecycle.md`, `### Delegation modes` and `### Depth calibration`.

The orchestrator sends the complete task specification in the first dispatch — scope,
constraints, file boundaries, success criteria — and the agent opens with a brief
preflight then implements in the same turn. Anthropic's guidance drives this for every
model the project runs. The Opus 5.5 guide says the Opus 5 patterns "remain a reasonable
starting point", and the Opus 5 guide states that the model "performs best when given
the complete task specification up front and left to run" and names "legacy harness
scaffolding that adds separate verification steps" as something to remove (Opus 5
guidance; the Opus 5.5 guide restates neither point). The Opus 5.5 guide adds that the
model "sustains long-running autonomous work better than Claude Opus 5", run "end to end
with parallel subagents and little oversight". For Sonnet, which backs most of the
specialist pool, the Sonnet 5 guide holds that "it's important to specify the task,
intent, and relevant constraints upfront in the first human turn", because
specifications delivered progressively across turns reduce token efficiency and
sometimes quality (Sonnet 5 guidance; the Sonnet 5.5 guide says those patterns "remain a
reasonable starting point"). The Sonnet 5.5 guide corroborates the cost of the opposite
pattern: "On agentic coding tasks at `low` and `medium` effort, the model sometimes
checks in before the work is done."

File count is not a criterion — a mechanical rename across twelve files qualifies, and
so does an unambiguous multi-file change. Lines and ambiguity are the real proxies for
difficulty, which is why a twelve-file mechanical rename is combined while one contested
design decision in a single file is not.

At Medium complexity the preflight stays structured — the analysis is not what was
removed, only the extra round trip.

Routing information is the genuine value of a separate preflight turn, and nothing in
Anthropic's guidance argues against paying one invocation to learn it — an execute
dispatch to the wrong agent costs strictly more.

## Notes layout: why a directory rather than one file

Source: `delegation-lifecycle.md`, `### Notes layout`.

Per a large parallel review that produced `notes/<project>-review-<date>/` with one
section note per reviewer plus one consolidation:

- Parallel writers need disjoint targets. A shared file forces either append-with-lock
  (which serialises the fan-out) or each agent holding the accumulated file in context
  to avoid overwriting siblings — reintroducing the context pressure batching exists to
  avoid.
- The consolidating agent reads the notes individually anyway, so a merged file would
  have to be re-split before use.
- `<section-id>/F3` is a stable, greppable finding reference. A heading anchor or line
  range into a monolith breaks whenever an earlier section is edited.
- A downstream agent that needs a handful of the sections reads only those small files
  instead of one monolithic document.

The fourth shape (single run artifact, mixed writers) is a principled exception rather
than a violation of the first bullet. `spec-to-dev` keeps one file per run holding a
`## Subtask status` table the orchestrator owns plus an `## Implementation notes`
section every implementing dispatch appends to. The context-pressure half of the
disjoint-targets argument was calibrated on 236–490-line section notes and does not
transfer to a payload of one `[st-N]`-prefixed line per discovery; the overwrite half is
handled by the append discipline, which never rewrites a section. Decisively, the
orchestrator re-reads the status table at every wave boundary, so sharding the artifact
per subtask would defeat the resumability it exists to provide and the two halves cannot
live in different files. `_<feature>` sits between skill and date because several runs
of one skill can target different features on the same day, unlike the
once-per-repository runs the other rows were written for.

## Batching: empirical validation of the file and line thresholds

Source: `delegation-lifecycle.md`, `## Delegation batching rules`.

Measured against a large-scale parallel code review split across many reviewer sections,
each covering a disjoint slice of a sizeable production codebase. The note lengths below
are measurements of what those sections needed, not targets to write toward.

| Measure                             | Value                                                                                  |
| ----------------------------------- | -------------------------------------------------------------------------------------- |
| Average batch                       | Landed inside the 7–12 preferred band, close to the `ceil(N/10)` estimate              |
| Sections showing context exhaustion | 0 — no truncated tables, no thinned detail sections                                    |
| Largest compliant batches           | 8–13 files, notes 236–291 lines                                                        |
| Batches over the 15-file cap        | 2 (19 files / 4,388 lines and 24 files / 2,814 lines)                                  |
| Quality of the over-cap batches     | 12 and 11 fully detailed findings; note lengths 291 and 236 lines, at the scope median |

Two conclusions, both grounded rather than asserted:

- The 7–12 preferred band held at scale: the run's average sat inside it and no section
  degraded. Keep it as the planning default.
- The 15-file cap is softer than previously stated. Two batches exceeded it by 27% and
  60% with no measurable penalty, so a marginal overshoot is not a reason to re-plan.
  Note length tracked finding count and complexity, not file count — the smallest
  section produced the longest note (490 lines) because it held three correctness bugs.
  This is why the LOC trigger exists: the two over-cap batches were also the two largest
  by lines, and the compliant ones clustered at 1,450–2,200 lines.

## Concurrency cap: provenance of the number four

Source: `delegation-lifecycle.md`, `## Parallelization safety`.

The 2.x subagent docs stated the cap explicitly ("up to four subagents at once"); the
current mirror at
`.kiro/skills/kiro-cli-reference/references/custom-agents/subagents.md` no longer
restates a number and only says sub-agents run in parallel. The project keeps four as
its working ceiling pending re-confirmation upstream.

## Calibration anchors: why they are pasted verbatim

Source: `delegation-lifecycle.md`, `## Parallelization safety`.

Isolated agents cannot converge on severity or effort from a prose rubric alone: in the
large multi-section run above, the same defect class landed on `High` in one section and
`Medium` in three others, which made the consolidated ranking untrustworthy.

## Delegation floor: why the cap is a ceiling and not a target

Source: `delegation-lifecycle.md`, `### Delegation floor`.

Anthropic's Opus 5 guidance: "If one subagent can complete the task, use one rather than
several, and keep spawn counts low." This is Opus 5 guidance that still applies: the
Opus 5.5 guide says the Opus 5 patterns "remain a reasonable starting point" and
restates no spawning rule of its own. The Sonnet 5.5 guide corroborates the cost of
unrequested review dispatches: telling the model to stop launching reviewer sub-agents
at `max` effort "cut session cost by about a third, with no change in quality".

The Conductor's minimum viable pool (typically 2–4) is the governing rule; the floor
states its intent for dispatches that do not go through the Conductor.

A reviewing stage that checks a **different** agent's output against stated criteria is
the endorsed writer-verifier pattern — Opus 5 "coordinates teams of subagents well, with
effective writer-verifier patterns", and the prohibition Anthropic states is scoped to
"your own work". Both quotations are Opus 5 guidance; the Opus 5.5 guide has no
equivalent statement. That is why a review stage is allowed while re-verifying the
orchestrator's own output is not, and why such a stage is expressed as a native review
loop rather than one extra dispatch per artifact.

## Targeted preflight: why Phase 5 is narrowed

Source: `delegation-lifecycle.md`, `### Phase 5 — Targeted agent preflight`.

A plan that was already self-critiqued in Phase 3 and user-approved in Phase 4 does not
need an N-agent re-validation pass; re-delegating to every assigned agent buys one round
trip per agent to re-confirm what the plan already states.

The purpose is unchanged — specialized knowledge enriching the plan before code is
written — but it is bought where it is uncertain rather than everywhere. The
orchestrator's plan is a hypothesis; a preflight validates the parts of it most likely
to be wrong.

## Session effort: sources, the step-down argument, and mechanics

Source: `delegation-lifecycle.md`, `### Session effort policy`.

Sources for the recommendation table, read against `claude-opus-5.5`, the model behind
the three `high (2.0x)` agents; the orchestrator itself runs `claude-sonnet-5.5`:

- The Opus 5.5 guide ("Calibrate effort"): "Reserve `xhigh` and `max` for work where
  you've measured a quality gain", and "At a given level, Claude Opus 5.5 tends to think
  more per turn than Claude Opus 5, especially at `xhigh` and `max`." The project has no
  measurement, and a level name now buys more thinking than before. Hence `max` is not
  recommended by any row, the two former `max` rows sit at `xhigh`, and the design row
  moved from `xhigh` to `high`.
- Anthropic's `effort.md` table describes `xhigh` as for "Long-running agentic and
  coding tasks (over 30 minutes)", which fits a full security audit and a debugging
  session that has already failed twice.
- The Opus 5.5 guide: at its default `medium` the model "matched or beat Claude Opus 5
  at `high` effort" on agentic coding, and "on several coding evaluations `low` comes
  close to it at much lower cost". This supports the `low` row for routine mechanical
  work.
- Kiro's `effort.md` ("Use `max` for security reviews, complex debugging sessions") is
  model-agnostic. The model-specific Opus 5.5 guidance is the narrower source, so it
  governs where the two differ. A measured gain at `max` is the condition for returning
  to Kiro's recommendation.

Effort is orthogonal to the credit-multiplier Cost column in `routing.md` — it changes
reasoning depth within a model, not which model runs, so the two levers are set
independently.

Stepping down is the primary lever rather than an exception. The Opus 5.5 guide: "To get
less thinking, lower the effort level first. Lowering effort reduces thinking, and with
it cost and latency, more reliably than prompt instructions do." The Sonnet 5.5 guide
agrees: "To get less thinking, lower the effort level." The stronger wording is Opus 5
guidance that still applies and has no 5.5 counterpart: Anthropic's `effort.md` directs
using `low` and `medium` "liberally as your primary control for token cost and response
time wherever your evals show quality holds". Kiro's `effort.md` says to bump down when
quick answers are wanted. The step-down rows read against the committed baselines in
`.kiro/settings/cli.json`, not against an imagined default. Both 5.5 guides instruct
running a fresh effort sweep rather than carrying settings over from the earlier model;
that sweep is currently unmeasurable here, as the project has no eval harness.

The committed values live in `.kiro/settings/cli.json` and are not restated here. The
evidence behind running both 5.5 models at `medium`: Anthropic reports that Opus 5.5 at
`medium` matched or beat Opus 5 at `high` in fewer tokens, which matters for a model
carrying a 2.0x multiplier; for Sonnet, Anthropic's agentic starting point is "start at
`medium` for well-specified tasks and move to `high` for harder or longer ones". The
documented cost is that "[a]t `low` and `medium`, on long agentic tasks, it's more
likely to stop and check in with the user before it finishes", which the carry-through
clause in `COMMON.md` addresses at the prompt level instead of by raising effort.
Neither value has been measured.

Mechanics moved here from the policy: effort resolves per model from
`chat.modelDefaults`, or per session via `--effort` / `/effort`, with precedence session
→ workspace → user → built-in. `use_subagent` accepts only `agent_name`, `query`, and
`relevant_context`, and subagents inherit the session's steering, MCP, permissions, and
file access, which is why effort cannot be a per-dispatch lever. The recommendation
table assumes the orchestrator's session model, `claude-sonnet-5.5`; whether a
session-level `/effort` reaches subagents running `claude-opus-5.5` is not verified, and
the per-model lever is `chat.modelDefaults`. The `xhigh` rows are ceilings, and `max` is
reserved for a measured quality gain.

A future operator revisiting either value needs an eval harness first; without one the
sweep both guides call for cannot be run. Settled, so it is not reopened:
`claude-haiku-4.5` runs with `thinking: {type: disabled}` in workspace scope, and
Anthropic's `effort.md` front matter omits that model from `supportedModels` — effort is
not an available lever for it, so no `effort` value belongs in its defaults.

## Routing: the two disambiguation rules most often applied backwards

Source: `routing.md`, `### Critical disambiguation`.

- **Data modelling**: `data-engineer.never_when` excludes high-level data modelling
  decisions, and the `Database design` pattern is explicitly
  `software-architect → data-engineer`. Conceptual model first, physical schema second.
- **Polars**: `code-standards` mandates Polars for all production data processing, so
  the library name alone carries no routing signal. Route on whether the work is a data
  pipeline or data-quality task.

## Security audit: why one security-engineer dispatch and not three

Source: `routing.md`, `### Pattern details`.

One high-cost (2.0x) invocation plus one medium (1.3x), so roughly 3.3x against the
roughly 7.3x the four-invocation form cost (three security-engineer invocations at 2.0x
plus one code-reviewer at 1.3x). The three perspectives collapsed into one dispatch for
two reasons: the Opus 5.5 guide reports "more bugs caught than on Claude Opus 5 and
fewer false alarms" in code review, which removes the single-pass-recall premise
multi-perspective voting was built on (Opus 5 guidance made the same point: it "finds
real bugs at a high rate per pass"); and three passes over the same codebase are not the
genuinely independent tracks the delegation guidance endorses for a fan-out.

## State registry: scope and why it ships empty

Source: the header of `memory/state.yaml` and `delegation-lifecycle.md`,
`### State protection`.

The orchestrator filters the registry by `scope` and passes only intersecting entries,
so every entry is paid for in context on the invocations it matches. An entry belongs
there only if it constrains future work and is captured nowhere else: coding rules live
in `code-standards`, review rules in `reviewing-code`, delegation conventions in
`delegation-lifecycle.md`, routing in `routing.md`, layout in `README.md` and
`tools/TOOLS_OVERVIEW.md`, and anything a check can enforce in `tools/driftcheck`. A
copy in the registry drifts from the reviewed original the moment one is edited and the
other is not. `agent_feedback` is for a recurring delegation failure pattern with no
other home — for example "code-reviewer fails silently on large contexts, retry with
half the files".

The registry was reset on 2026-08-26 because all sixteen earlier entries had been
written into one of those artefacts; git history, not the registry, is the changelog.
This repository is a framework installed into other projects, so the registry is
per-consuming-project state and ships empty here; `decisions` and `agent_feedback` are
empty by design. A full day of architectural work confirmed that steering files and
skills hold decisions with durable force, and that rejected ideas belong in an
out-of-scope register in the consuming project's own tree. In a framework tree,
`memory/` holding anything but the template is a drift-check error; the check applies
only while the root `.gitignore` ignores `memory/` contents, so a consuming project that
tracks its own `memory/` disables it by dropping that rule. `state.yaml` structure is
checked only by the driftcheck state check, run by the `make drift-check` gate; no hook
validates it.

A learned-state store that promotes entries into agent context without human review —
correction detection, episode capture, threshold-based rule promotion, lessons
auto-injection — was assessed and rejected, and the Self-improvement pattern in
`routing.md` may not propose one. None of the reference implementations placed a review
gate between detection and promotion, and the detection step is documented as
unreliable: it misses subtle corrections and drops rapid ones inside a dedup window. A
durable learned pattern belongs in a reviewed skill or steering file. The prohibition
covers automatic promotion, not persistence; a design with an explicit human gate stays
open.
