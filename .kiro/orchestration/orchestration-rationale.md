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
`file://../orchestration/delegation-lifecycle.md` entry in
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
model the project runs: Opus 5 "performs best when given the complete task specification
up front and left to run", and the same page names "legacy harness scaffolding that adds
separate verification steps" as something to remove. For Sonnet 5, which backs most of
the specialist pool, "it is important to specify the task, intent, and relevant
constraints upfront in the first human turn", because specifications delivered
progressively across turns reduce token efficiency and sometimes quality.

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
several, and keep spawn counts low."

The Conductor's minimum viable pool (typically 2–4) is the governing rule; the floor
states its intent for dispatches that do not go through the Conductor.

A reviewing stage that checks a **different** agent's output against stated criteria is
the endorsed writer-verifier pattern — Opus 5 "coordinates teams of subagents well, with
effective writer-verifier patterns", and the prohibition Anthropic states is scoped to
"your own work". That is why a review stage is allowed while re-verifying the
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

## Session effort: sources, the step-down argument, and current state

Source: `delegation-lifecycle.md`, `### Session effort policy`.

Sources for the recommendation table: Kiro's `effort.md` ("Use `max` for security
reviews, complex debugging sessions") and Anthropic's `xhigh` recommendation for the
hardest coding and agentic tasks. Effort is orthogonal to the credit-multiplier Cost
column in `routing.md` — it changes reasoning depth within a model, not which model
runs, so the two levers are set independently.

Stepping down is the primary lever rather than an exception: Anthropic's `effort.md`
directs using `low` and `medium` "liberally as your primary control for token cost and
response time wherever your evals show quality holds", and Kiro's `effort.md` says to
bump down when quick answers are wanted. The step-down rows read against the committed
baselines in `.kiro/settings/cli.json` — `claude-opus-5` at `high`, `claude-sonnet-5` at
`medium` — not against an imagined default. Anthropic also instructs re-running an
effort sweep rather than reusing levels carried over from an earlier model; that sweep
is currently unmeasurable here, as the project has no eval harness.

Current state, recorded so it is not re-derived: `claude-sonnet-5` runs at `medium` in
this workspace while Anthropic documents `high` as that model's default, a deliberate
cost choice a future operator can revisit with that comparison in hand. Settled, so it
is not reopened: `claude-haiku-4.5` runs with `thinking: {type: disabled}` and
`max_tokens: 16000` in workspace scope, and Anthropic's `effort.md` front matter omits
that model from `supportedModels` — effort is not an available lever for it, so no
`effort` value belongs in its defaults.

## Routing: why step five of the decision procedure reads the Cost column

Source: `routing.md`, `## Routing Decision Procedure`.

Step 5 uses the Cost column (`high (2.2x)`, `medium (1.3x)`, `low (0.4x)`), not a
qualitative guess. In practice this means: reach for a `medium (1.3x)` agent before
software-architect, senior-developer, or security-engineer when either would produce an
acceptable result. It does NOT mean routing implementation work away from
senior-developer — capability match comes first, and cost only breaks ties between
agents that both genuinely qualify.

## Routing: the two disambiguation rules most often applied backwards

Source: `routing.md`, `### Critical disambiguation`.

- **Data modelling**: `data-engineer.never_when` excludes high-level data modelling
  decisions, and the `Database design` pattern is explicitly
  `software-architect → data-engineer`. Conceptual model first, physical schema second.
- **Polars**: `code-standards` mandates Polars for all production data processing, so
  the library name alone carries no routing signal. Route on whether the work is a data
  pipeline or data-quality task.

## Debugging pattern: why qa-engineer also declares the skill

Source: `routing.md`, `### Pattern details`.

The Debugging row names only the executor, not every agent wired to the skill.
`qa-engineer.json` also declares `debugging`, deliberately: qa-engineer consumes the
same root-cause material for test-failure analysis under its own
`identifying failure patterns or flaky tests` trigger, without participating in that
workflow as a second executor. `check_pattern_resource_wiring` does not flag this
because it only verifies agents named in a pattern row, never the converse (see that
check's docstring for the reasoning).

## Security audit: why one security-engineer dispatch and not three

Source: `routing.md`, `### Pattern details`.

One high-cost (2.2x) invocation plus one medium (1.3x), so roughly 3.5x against the
roughly 7.9x the four-invocation form cost. The three perspectives collapsed into one
dispatch for two reasons: Opus 5 finds real bugs at a high rate per pass with its extra
findings mostly real rather than false positives, which removes the single-pass-recall
premise multi-perspective voting was built on; and three passes over the same codebase
are not the genuinely independent tracks the delegation guidance endorses for a fan-out.
