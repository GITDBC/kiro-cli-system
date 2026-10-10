# Delegation lifecycle

Single source for the orchestrator side of delegation: how work is planned, dispatched,
parallelised, verified, and escalated. Only the orchestrator acts on it, and it reaches
the session solely through the `file://../orchestration/delegation-lifecycle.md` entry
in `.kiro/agents/orchestrator.json`. Keep this file and `routing.md` in
`.kiro/orchestration/` and keep that entry: do not move either into `.kiro/steering/`.
`.kiro/orchestration/` holds material the orchestration layer owns, which is why
`preflight-report-format.md` sits there rather than beside the specialist contract: the
orchestrator is what enforces the preflight contract and names that path when it
dispatches a separate preflight turn. Where a rule below carries no argument, the
argument — and the placement decision itself — is in
`.kiro/orchestration/orchestration-rationale.md`; read it when a settled decision is
being challenged.

The specialist side of the contract lives in `COMMON.md`: the **Preflight Report**
format an agent must emit, the **Autonomous Mode** resolution table, and the per-agent
verification duties. Anything an agent must produce is specified there; anything the
orchestrator must decide is specified here.

## Preflight-first delegation

Every delegation carries a preflight; what varies is whether it gets its own turn.
Through Medium complexity the agent delivers it in the same turn as the implementation
(see `Delegation modes` below). When a separate preflight turn is warranted, the
orchestrator never authorizes execution without reviewing that report first.

### Cycle

Applies when a separate preflight turn was dispatched:

```
Orchestrator delegates (mode: preflight)
        ↓
Agent produces Preflight Report (read-only)
        ↓
Orchestrator evaluates:
  - All ✅ → authorize execution
  - Any ❌ (blockers) → reroute to suggested agent or add agent to plan
  - Any ❓ (ambiguities) → ask user for clarification
  - Risks acceptable? → proceed or adjust plan
        ↓
Orchestrator re-delegates (mode: execute + any plan adjustments)
```

### Delegation modes

| Mode      | Instruction                                                                                                                   | When                                                             |
| --------- | ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Combined  | "Brief preflight (2-3 lines), then implement directly."                                                                       | Default through Medium complexity — any file count               |
| Preflight | "Read `.kiro/orchestration/preflight-report-format.md`, then produce a Preflight Report in that shape. Do NOT implement yet." | High complexity, architecturally significant, or routing at risk |
| Execute   | "Proceed with implementation based on your preflight plan."                                                                   | After a separate preflight was approved                          |

**Combined mode is the default up to and including Medium complexity.** The orchestrator
sends the complete task specification in the first dispatch — scope, constraints, file
boundaries, success criteria — and the agent opens with a brief preflight then
implements in the same turn. File count is not a criterion. Delegating in combined mode
is itself the authorization to implement, so no second confirmation round is required.
The Anthropic guidance behind this is in
`.kiro/orchestration/orchestration-rationale.md`.

**A separate preflight turn is reserved for three cases:**

- High complexity — architecture change, new subsystem, cross-cutting redesign.
- Architecturally significant work, whatever its file count.
- Any task where a blocker would change **which agent** should run.

A separate preflight dispatch MUST name
`.kiro/orchestration/preflight-report-format.md`, as the Preflight row above does: the
template is not always-on, and an agent without it improvises a report shape that passes
structural validation while being wrong.

**Autonomous mode**: For non-interactive workflows (Ralph Loop, CI), the preflight still
happens but the agent resolves uncertainty internally. Include `mode: autonomous` in
context. The resolution rules are in COMMON.md.

### Depth calibration

Preflight depth scales with complexity, and so does whether the preflight gets its own
turn. The orchestrator sets the expectation when it delegates.

| Task complexity | Preflight depth        | Delivery                     | Examples                                             |
| --------------- | ---------------------- | ---------------------------- | ---------------------------------------------------- |
| Trivial         | 2-3 lines              | Combined with implementation | Rename a variable, fix a typo, update a config value |
| Low             | 1 paragraph            | Combined with implementation | Single-file bug fix, add a test, update docs         |
| Medium          | Structured analysis    | Combined with implementation | Multi-file change, new function, refactoring         |
| High            | Full feasibility study | Separate preflight turn      | Architecture change, new subsystem                   |

Ambiguous or architecturally significant work gets a separate preflight turn regardless
of where it otherwise lands in the table, as does any task whose blockers could reroute
it to a different agent. File count is not a criterion at any row; lines and ambiguity
are.

### Handling preflight feedback

1. **Blockers with agent suggestion**: Validate against routing.md; add the suggested
   agent or select a better one.
2. **Blockers without suggestion**: Identify the right agent; delegate a new preflight
   for that sub-problem.
3. **Ambiguities**: Consolidate into a single structured question to the user — never
   ask multiple times.
4. **Risks**: Elevate if flagged by multiple agents; inform the user if risks conflict
   with the approved plan.
5. **Plan adjustments**: Adjust the execution plan if preflight reveals different
   complexity (skip, add, or reorder steps).

### Re-planning after preflight

Re-plan when:

- An agent cannot do part of its assigned work.
- New dependencies between subtasks are discovered.
- Complexity differs significantly from the original estimate.
- File ownership conflicts exist between parallel agents.

Re-planning does NOT require user approval unless "Will do" / "Will NOT do" scope
changes.

### Sequential workflow reflection (3+ steps)

After each agent completes, assess:

1. Did the output meet the step's intent? If not, re-delegate.
2. Did it change the remaining plan? Adapt if yes.
3. Should the next step's instructions be rewritten?

Skip for simple 2-step workflows.

## Structured handoff format

```
## Handoff to [agent-name]

**Context:** [1-2 sentences — what happened before and why this agent is next]
**Your role:** [Specific role in this workflow]

**Input artifacts:**
- [file or data to read/use]

**Expected output:**
- Format: [Markdown report / code files / structured list]
- Must include: [specific sections or data points]

**Constraints:**
- [What NOT to do — scope boundaries]

**Success criteria:**
- [How to judge if output is good enough]

**Key decisions from previous steps:**
- [Decisions this agent must respect]
```

### Learnings propagation

In sequential workflows (3+ steps), add a `**Learnings from previous steps:**` section
to the handoff for cross-cutting discoveries that affect downstream work (e.g., API
constraints, required import ordering). Do not propagate general observations.

## Context management (workflows >3 steps)

- Pass only the structured handoff via `relevant_context`, not full outputs.
- Maintain per-step notes with: agent, decisions, artifacts.

### Notes layout

| Workflow shape                       | Path                                                 |
| ------------------------------------ | ---------------------------------------------------- |
| Single producer agent, sequential    | `notes/<skill>_<YYYY-MM-DD>.md`                      |
| Two or more parallel producer agents | `notes/<skill>_<YYYY-MM-DD>/<section-id>.md`         |
| Consolidation of a parallel run      | `notes/<skill>_<YYYY-MM-DD>/IMPROVEMENT_ANALYSIS.md` |
| Single run artifact, mixed writers   | `notes/<skill>_<feature>_<YYYY-MM-DD>.md`            |

`<section-id>` is the agent's scope expressed as its module path with `/` replaced by
`-` (`pipeline-transforms`, `api-handlers`, `data-ingestion`). One producer agent owns
exactly one file and never writes to a sibling's, so parallel agents cannot collide.

The fourth shape is the one exception: `spec-to-dev` keeps one file per run holding a
`## Subtask status` table the orchestrator owns plus an `## Implementation notes`
section every implementing dispatch appends to, never rewriting a sibling's line.
`_<feature>` sits between skill and date because several runs of one skill can target
different features on the same day. Why a directory in every other case, and why this
exception holds: `.kiro/orchestration/orchestration-rationale.md`.

## Delegation batching rules

- **Max batch**: 15 files per invocation; **preferred**: 7–12.
- **Estimation**: plan `ceil(N / 10)` batches for N files.
- **Secondary split trigger**: split when a batch exceeds roughly 3,000 lines of logic
  even if its file count is compliant. Lines, not files, are the closer proxy for
  context pressure.
- Split larger tasks into sequential batches with non-overlapping file sets.
- After throttling or failure: retry with half the file count.
- A marginal overshoot of the 15-file cap is not by itself a reason to re-plan; the LOC
  trigger is the sharper signal. Measurements behind both thresholds:
  `.kiro/orchestration/orchestration-rationale.md`.

## Parallelization safety

- **Concurrency cap: four subagents at once.** Work that needs more than four agents is
  queued into successive waves of at most four, not launched at once. Provenance of the
  number: `.kiro/orchestration/orchestration-rationale.md`.
- Agents must work on **non-overlapping files/modules**.
- Specify file boundaries explicitly in the `query`.
- If overlap is unavoidable, sequentialize.
- Run the Coordination Protocol before parallelizing implementation tasks.
- Parallelize only as far as genuinely independent work extends, and never past the cap
  of four; queue the remainder.
- For parallel review or assessment fan-outs, paste the calibration anchors from
  `.kiro/skills/reviewing-code/references/finding-calibration.md` verbatim into every
  agent's `relevant_context`. Isolated agents cannot converge on severity or effort from
  a prose rubric alone.

### Delegation floor

The cap of four is a ceiling, not a target.

- One agent over several whenever one covers the work. The Conductor's minimum viable
  pool (typically 2–4, see Phase 1 below) is the governing rule; this floor states its
  intent for dispatches that do not go through the Conductor.
- No subagent to re-verify work the orchestrator produced itself, and none whose sole
  job is restating another agent's output. A reviewing stage that checks a **different**
  agent's output against stated criteria is allowed and endorsed; express it as a native
  review loop rather than one extra dispatch per artifact.
- No subagent for a lookup a direct `read`, `grep`, or `code` call answers.

The Anthropic guidance behind the floor and the writer-verifier exception is in
`.kiro/orchestration/orchestration-rationale.md`.

### Context overflow sharding

If parallel calls fail due to context size: shard work across multiple instances of the
same agent type with smaller scopes, launch up to four shards per wave, queue any
remainder into the following wave, then synthesize outputs.

## Coordination Protocol (pre-parallelization)

Applies to IMPLEMENTATION tasks only (not analysis, reviews, research).

**Step 1 — File ownership**: List files each subtask will modify:

```yaml
subtask_files:
  - task: "description"
    files: [path/file1.py, path/file2.py]
```

**Step 2 — Overlap detection**:

- No overlap → parallelize with explicit boundaries.
- Overlap → sequentialize conflicting tasks; parallelize the rest.

**Step 3 — Shared Context Contract** (pass to all parallel agents):

```markdown
## Shared Context Contract

### Active conventions

- [Relevant conventions from code-standards-summary.md]

### Interfaces between modules

- [Shared types, schemas, function signatures]

### Active decisions

- [From state registry and architect's design]

### File boundaries (DO NOT MODIFY outside your scope)

- Your scope: [exact list of assigned files]
```

**Step 4 — Delegation**: Each agent's `relevant_context` must include its task, the
Shared Context Contract, and the explicit file list it MAY modify.

**Rules**: Execute automatically (no user confirmation). Sequentialize by default if
file analysis is ambiguous. Parallelize genuinely independent subtasks only, treating
the four-subagent cap as a ceiling; additional independent subtasks are queued into the
next wave rather than launched alongside.

## Native review loops

Iterative review is expressed as a **native subagent loop**, not a hand-rolled A→B→A
re-invocation chain. Three fields define it (see
`.kiro/skills/kiro-cli-reference/references/custom-agents/subagents.md`):

| Field            | Meaning                                                              |
| ---------------- | -------------------------------------------------------------------- |
| `target`         | Name of the stage to re-run when the loop fires                      |
| `trigger`        | Text in a stage's output that fires the loop (e.g. `NEEDS_CHANGES`)  |
| `max_iterations` | Safety cap on re-runs; must be ≥1 and is capped at 10 by the runtime |

The reviewing stage emits the trigger when revisions are needed; the runtime re-runs the
target stage with that feedback as context. When the output no longer contains the
trigger, the pipeline advances. The trigger must be at least four characters, so use a
distinctive marker such as `NEEDS_CHANGES` rather than a common word.

Prefer a native loop whenever a producing stage and a checking stage alternate. It costs
fewer orchestrator turns than manual re-delegation and the iteration count is enforced
by the runtime instead of by orchestrator bookkeeping. `reviewing-code`,
`kpi-assessment`, and `engagement-plan` all use this mechanism.

## Direct pass-through

Present a subagent's final, complete response directly without paraphrasing — especially
code, structured reports, step-by-step instructions, and technical analysis.

Synthesize when: merging multiple outputs, adding missing context, summarizing verbose
output, or highlighting key decisions/risks.

## Planning phases

For complex tasks (multi-agent, multi-file changes, or anything involving
implementation), follow this collaborative planning workflow. For simple single-agent
tasks, skip planning and delegate directly.

Planning is a **conversation, not a presentation**.

### Phase 1 — Understand and clarify

Restate the understanding in 2-3 sentences, surface assumptions, and ask structured
questions with numbered multiple-choice options for unclear parts. The user can answer
any subset (e.g., "1=a, 2=b"). Typically 1-2 rounds. Do not over-ask — make reasonable
assumptions and let the user correct them.

### Phase 2 — Research (when needed)

Delegate read-only exploration to the appropriate agent. No modifications. Skip when
sufficient context is already available.

### Phase 3 — Draft plan with self-critique

Before presenting, challenge the plan: What could go wrong? Is there a simpler
alternative? Is it over- or under-engineered? Are dependencies missing?

Present as Markdown with:

- **Problem statement**: what and why.
- **Approach**: strategy and why over alternatives.
- **Will do**: tasks with objectives, assigned agents, files, demo description.
- **Will NOT do**: explicit exclusions.
- **Risks and open questions**: weak points, uncertainties.
- **Agent sequence**: parallel vs sequential.

End with **proactive questions** surfacing decisions where user input matters most.

### Phase 4 — Refine through dialogue

- Pushback → adjust and re-present changed parts only.
- Disagreement → explain why and propose an alternative.
- Approval → execute.
- After 3 rounds of significant changes → consolidate into a clean final plan.

The plan is approved when the user explicitly confirms.

### Phase 5 — Targeted agent preflight

After user approval, delegate in **preflight mode** only to those agents whose
feasibility is genuinely uncertain — an agent facing an unfamiliar subsystem, a task
whose blockers could reroute it to a different agent, or a High-complexity slice of the
plan. Everything else goes straight to Phase 6 in combined mode with the full
specification.

For the agents that do get a preflight turn, run the evaluation described in
Preflight-first delegation above: collect the reports, resolve blockers by rerouting or
adding agents, consolidate all ambiguities into ONE question to the user, and adjust the
plan for reported risks. If the plan changes significantly (scope of "Will do" / "Will
NOT do" affected), inform the user and get re-approval.

Why the phase is targeted rather than universal:
`.kiro/orchestration/orchestration-rationale.md`.

### Phase 6 — Execute

Delegate in **execute mode**. Pass the approved plan plus any adjustments from Phase 5
as `relevant_context` to each agent. Agents implement their assigned tasks following
their preflight execution plan.

## Harness gates

Guardrails, verification gates, and safety mechanisms enforced by the orchestrator
during delegation and synthesis.

### Output validation

Every agent output MUST contain the required structural elements or be rejected:

| Task mode          | Required sections                               | Rejection trigger                     |
| ------------------ | ----------------------------------------------- | ------------------------------------- |
| Preflight          | Preflight Report with feasibility assessment    | Missing feasibility or execution plan |
| Execute (code)     | See `Post-execution verification gate` below    | Stated in that section                |
| Execute (analysis) | Executive summary + structured findings         | No summary or unstructured prose dump |
| Combined           | Brief preflight + implementation + verification | Missing any of the three              |

Combined mode is the default delivery through Medium complexity, for any file count (see
Depth calibration above). A 2-3 line preflight followed by the implementation in the
same turn satisfies the table above and MUST NOT be rejected for lacking a full
Preflight Report.

**Rejection protocol** — on structurally invalid output:

1. Do NOT pass downstream.
2. Re-delegate with explicit format instructions.
3. On second failure: log as `agent_feedback` (severity: high) and fall back.

### Circuit breakers

#### Retry limits

| Scope                  | Max attempts | After exhaustion                        |
| ---------------------- | ------------ | --------------------------------------- |
| Single agent task      | 3            | Fallback to next-best agent             |
| Agent in workflow step | 2            | Reroute or skip with user notification  |
| Full workflow          | 1 restart    | Halt, present partial results, ask user |

Within a single agent task, escalate the context rather than repeating it: retry with
the same context → retry with reduced context → escalate.

#### Repetition detection

If two consecutive outputs from the same agent are substantially the same — same
findings, same structure, no new information — MUST:

1. Stop retrying.
2. Diagnose root cause (wrong agent? missing context? impossible task?).
3. Try a fundamentally different approach (different agent, reduced scope, or escalate).

#### Fallback routing

- **Scope failure**: use the fallback chain in routing.md (next-best agent by
  `trigger_when` overlap).
- **code-reviewer**: historically fails silently on large contexts — retry with half the
  files before falling back to orchestrator review. Never skip review entirely.

### Token budget awareness

Cost labels come from the Cost column in routing.md, which states the real credit
multiplier: `high (2.2x)`, `medium (1.3x)`, `low (0.4x)`.

- Trivial/Low → any agent
- Medium → prefer `medium (1.3x)` or `low (0.4x)` agents when several qualify
- High → justify selecting a `high (2.2x)` agent in the delegation log

The `high (2.2x)` agents are **software-architect, senior-developer, and
security-engineer** (all backed by `claude-opus-5`). Do NOT reach for one of those where
a `medium (1.3x)` agent suffices. ai-engineer runs at `medium (1.3x)` and is not subject
to this restriction. Capability match still comes first, per the routing rules in
routing.md.

### Session effort policy

Reasoning effort is a session-level lever held by the human, never a per-dispatch one:
`use_subagent` accepts only `agent_name`, `query`, and `relevant_context`, and subagents
inherit the session's steering, MCP, permissions, and file access. Effort resolves per
model from `chat.modelDefaults`, or per session via `--effort` / `/effort`, with
precedence session → workspace → user → built-in. The orchestrator therefore never
varies effort per delegation; at most it recommends one level once per session, before
the work starts.

| Work                                                                                                  | Recommended session effort |
| ----------------------------------------------------------------------------------------------------- | -------------------------- |
| `security-audit`                                                                                      | `max`                      |
| `debugging`, past the second failed attempt                                                           | `max`                      |
| `spec-to-dev` design phase, architecture change                                                       | `xhigh`                    |
| Direct-invoke utilities (`exploratory-data-analysis`, `statistical-analysis`, `unit-test-generation`) | `medium`                   |
| Routine mechanical work (renames, config edits, doc formatting, single-file fixes)                    | `low`                      |
| Everything else                                                                                       | session default            |

Sources for these levels, the step-down argument, and the recorded current state
(`claude-sonnet-5` at `medium`, `claude-haiku-4.5` with no `effort` lever) are in
`.kiro/orchestration/orchestration-rationale.md`. Two rules follow from them: step down
liberally — `low` and `medium` are the primary control for token cost and response time
— and never add an `effort` value to `claude-haiku-4.5`'s defaults, which do not support
one. Effort is orthogonal to the Cost column in `routing.md`: it changes reasoning depth
within a model, not which model runs.

### Post-execution verification gate

Accept a code-modifying execution when its output lists the files modified and the
validation outcome from this run. If validation was not run, or ran and failed, return
the task to the owning agent naming the missing or failing check. The orchestrator does
not re-run validation itself — the agent that made the change owns it, per `COMMON.md`'s
`## Verification First`.

### Scope creep detection

Compare the declared preflight plan against actual output:

- Files modified outside the plan → flag as scope creep.
- Planned files not modified → flag as incomplete.
- Either case → ask the agent to explain before accepting.

### Drift detection

Run `make drift-check` (or `uv run --project tools/driftcheck driftcheck`) after
modifying the agent system. Validates:

- Agent config resource references resolve to existing files.
- All agents are registered in the orchestrator's `availableAgents`.
- All skills (except direct-invoke utilities) have collaboration patterns in routing.md.
- Prompt file references are valid, and no prompt file is orphaned.
- `state.yaml` is structurally sound.
- No steering file duplicates a skill file (summary in steering, detail in the skill).
- No orphaned reference files under a skill's `references/` directory.
- `routing.md` and `delegation-lifecycle.md` stay in `.kiro/orchestration/` and remain
  referenced by the orchestrator's `resources`.

Run after: agent creation/deletion, skill addition, resource file moves, routing.md
edits.

### State protection

Before writing `state.yaml`, validate:

1. YAML is syntactically valid.
2. No section exceeds 20 entries.
3. All entries have required fields (`id`, `date`, `scope`).
4. IDs are unique within their section.
5. Dates are valid ISO format.

On failure: do NOT write. Log the error and preserve the existing file.

Backup before write:

```bash
cp memory/state.yaml memory/state.yaml.bak 2>/dev/null
# If write fails or produces invalid YAML, restore:
# cp memory/state.yaml.bak memory/state.yaml
```

### Delegation quality signals

Scores inform `agent_feedback` entries in state.yaml when patterns emerge; not stored
numerically.

| Signal                  | Measurement                                                     |
| ----------------------- | --------------------------------------------------------------- |
| First-attempt success   | Did the agent's output pass verification without re-delegation? |
| Scope adherence         | Did it stay within declared file boundaries?                    |
| Preflight accuracy      | Did the preflight correctly predict complexity and risks?       |
| Verification discipline | Did it run tests/lints without being reminded?                  |

### Escalation protocol

```
Level 1: Retry with adjusted context (orchestrator handles)
Level 2: Reroute to different agent (orchestrator handles)
Level 3: Reduce scope and attempt partial delivery (orchestrator handles)
Level 4: Present to user — what was attempted, why it failed,
         what partial results exist, recommended next step
```

Never silently drop a task. Every delegation must result in: successful output,
documented failure with partial results, or explicit escalation to user.

### Guardrail summary

Before EVERY delegation, check:

1. **Right agent?** (Quick Lookup table in routing.md)
2. **Right mode?** (preflight/execute/combined — see Delegation modes above)
3. **Sufficient context?** (relevant_context includes what the agent needs)
4. **Verification plan?** (how will I check the output?)
5. **Fallback plan?** (what if this agent fails?)
6. **Within budget?** (not using a high-cost agent for a low-complexity task)

## Conductor: ad-hoc workflow composition

When no predefined Collaboration Pattern in routing.md matches, the orchestrator
generates a custom workflow at runtime. All of these must be true: the task spans
multiple concerns · no existing skill matches well · the optimal agent sequence is not
obvious. If the task clearly matches a predefined skill, or a single agent suffices, do
not compose an ad-hoc workflow.

### Phase 1 — Pool selection

1. Score each agent against the task using the Capabilities Matrix in routing.md:
   **strong** (core), **support** (validates/enriches), **irrelevant** (discard).
2. Select the minimum viable pool from the strong and support agents (typically 2–4).

Internal output:

```
Active pool: [agent-1 (strong), agent-2 (strong), agent-3 (support)]
Discarded: [agent-4 (irrelevant because...), ...]
```

### Phase 2 — Topology design

Pick based on data dependencies:

| Topology                  | Use when                                                       |
| ------------------------- | -------------------------------------------------------------- |
| **Sequential**            | Step N needs the output of step N-1                            |
| **Parallel → Synthesize** | Subtasks are independent; the orchestrator merges              |
| **Diamond**               | Parallel analysis → single synthesis → sequential continuation |
| **Iterative**             | A quality gate requires re-delegation until criteria are met   |

Rules: default to parallel when subtasks do not share inputs · sequential only for true
data dependencies · at most 4 sequential steps before looking for parallelization ·
parallelise only where subtasks are genuinely independent and each is large enough to
warrant its own dispatch, since four is a ceiling rather than a target (see
`Delegation floor`). Iterative topologies are expressed as native review loops.

### Phase 3 — Structured delegation

```
query: [WHAT to produce — clear, measurable objective]
relevant_context:
  role: [Agent's specific role in THIS workflow]
  input: [Data/artifacts from previous steps, or "none — start from scratch"]
  output_format: [Exact structure required]
  constraints:
    - [Scope boundary — what NOT to touch]
    - [Assumptions to maintain]
  success_criteria:
    - [Criterion 1 — measurable]
    - [Criterion 2 — measurable]
  feeds_into: [Which agent/step consumes this output and what they need]
```

### Phase 4 — Execute with adaptation

After each step: evaluate the output against `success_criteria` · adapt the remaining
plan (skip, inject, or swap steps) · never forward stale context — update
`relevant_context` with what was actually produced. Rewrite the next agent's query when
the previous step changed the picture.

Present the plan to the user for approval before executing it.

### Phase 5 — Synthesis

Merge outputs into a unified response · highlight conflicts between agents · note
verified versus unverified items · suggest follow-up actions if the task is not fully
resolved.

### Anti-patterns

- **Broadcast**: delegating to all agents "just in case".
- **Rigid plan**: following the original topology when results suggest a different path.
- **Vague delegation**: free-form queries without the structured template.
- **Over-sequencing**: sequential steps that could run in parallel.
- **Context dumping**: passing full previous outputs instead of structured summaries.

### Success criteria

The workflow solves the task completely · the minimum agent pool was used · each agent
had clear scoped instructions · the plan adapted when intermediate results warranted it
· the final synthesis is coherent and actionable.
