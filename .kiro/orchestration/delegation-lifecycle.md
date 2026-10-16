# Delegation lifecycle

Single source for the orchestrator side of delegation: how work is planned, dispatched,
parallelised, verified, and escalated. Only the orchestrator acts on it, and it reaches
the session solely through the `file://.kiro/orchestration/delegation-lifecycle.md`
entry in `.kiro/agents/orchestrator.json`. Keep this file and `routing.md` in
`.kiro/orchestration/` and keep that entry: do not move either into `.kiro/steering/`.
`preflight-report-format.md` sits there too, because the orchestrator enforces the
preflight contract and names that path when it dispatches a separate preflight turn.
Where a rule below carries no argument, the argument — and the placement decision itself
— is in `.kiro/orchestration/orchestration-rationale.md`; read it when a settled
decision is being challenged.

The specialist side of the contract lives in `COMMON.md`: the **Preflight Report**
obligations and the per-agent verification duties; the **Autonomous Mode** resolution
table is in `preflight-report-format.md`. Anything an agent must produce is specified
there; anything the orchestrator must decide is specified here.

## Preflight-first delegation

Every delegation carries a preflight; what varies is whether it gets its own turn (see
`Delegation modes`). When a separate preflight turn is dispatched, the orchestrator
never authorizes execution without reviewing that report first.

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

**Combined**: the first dispatch carries the complete task specification — scope,
constraints, file boundaries, success criteria — and is itself the authorization to
implement, so no second confirmation round is required.

**A separate preflight turn is reserved for:**

- High complexity — architecture change, new subsystem, cross-cutting redesign.
- Ambiguous or architecturally significant work, whatever its file count.
- Any task where a blocker would change **which agent** should run.

A separate preflight dispatch MUST name
`.kiro/orchestration/preflight-report-format.md`, as the Preflight row does: the
template is not always-on, and without it an agent improvises a shape that passes
structural validation while being wrong.

**Autonomous mode**: for non-interactive workflows (Ralph Loop, CI), include
`mode: autonomous` in context; the preflight still happens, but the agent resolves
uncertainty internally per `## Autonomous Mode` in `preflight-report-format.md`.

### Depth calibration

The orchestrator sets the expected depth when it delegates.

| Task complexity | Preflight depth        | Delivery                     | Examples                                             |
| --------------- | ---------------------- | ---------------------------- | ---------------------------------------------------- |
| Trivial         | 2-3 lines              | Combined with implementation | Rename a variable, fix a typo, update a config value |
| Low             | 1 paragraph            | Combined with implementation | Single-file bug fix, add a test, update docs         |
| Medium          | Structured analysis    | Combined with implementation | Multi-file change, new function, refactoring         |
| High            | Full feasibility study | Separate preflight turn      | Architecture change, new subsystem                   |

The reserved cases above override the table. File count is not a criterion at any row;
lines and ambiguity are.

### Handling preflight feedback

1. **Blockers with agent suggestion**: Validate against routing.md; add the suggested
   agent or select a better one.
2. **Blockers without suggestion**: Identify the right agent; delegate a new preflight
   for that sub-problem.
3. **Ambiguities**: Consolidate into a single structured question to the user — never
   ask multiple times.
4. **Risks**: Elevate if flagged by multiple agents; inform the user if risks conflict
   with the approved plan.
5. **Plan adjustments**: Skip, add, or reorder steps if preflight reveals different
   complexity.

### Re-planning after preflight

Re-plan when an agent cannot do part of its work, new dependencies between subtasks
appear, complexity differs significantly from the estimate, or parallel agents conflict
over file ownership. Re-planning does NOT require user approval unless "Will do" / "Will
NOT do" scope changes.

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

`<section-id>` is the agent's module path with `/` replaced by `-`
(`pipeline-transforms`, `api-handlers`). One producer agent owns exactly one file and
never writes to a sibling's.

The fourth shape is the one exception: `spec-to-dev` keeps one file per run holding a
`## Subtask status` table the orchestrator owns plus an `## Implementation notes`
section every implementing dispatch appends to, never rewriting a sibling's line.
`_<feature>` separates several runs of one skill on the same day.

## Delegation batching rules

- **Max batch**: 15 files per invocation; **preferred**: 7–12.
- **Estimation**: plan `ceil(N / 10)` batches for N files.
- **Secondary split trigger**: split when a batch exceeds roughly 3,000 lines of logic
  even if its file count is compliant; lines are the closer proxy for context pressure.
- Split larger tasks into sequential batches with non-overlapping file sets.
- After throttling or failure: retry with half the file count.
- A marginal overshoot of the 15-file cap is not by itself a reason to re-plan; the LOC
  trigger is the sharper signal.

## Parallelization safety

- **Concurrency cap: four subagents at once**, a ceiling rather than a target.
  Parallelize only genuinely independent work and queue the rest into successive waves
  of at most four.
- Agents must work on **non-overlapping files/modules**; specify file boundaries
  explicitly in the `query`. If overlap is unavoidable, sequentialize.
- Run the Coordination Protocol before parallelizing implementation tasks.
- For parallel review or assessment fan-outs, paste the calibration anchors from
  `.kiro/skills/reviewing-code/references/finding-calibration.md` verbatim into every
  agent's `relevant_context`.

### Delegation floor

- One agent over several whenever one covers the work. The Conductor's minimum viable
  pool (Phase 1 below) is the governing rule; this floor states its intent for
  dispatches that do not go through the Conductor.
- No subagent to re-verify work the orchestrator produced itself, and none whose sole
  job is restating another agent's output. A reviewing stage that checks a **different**
  agent's output against stated criteria is allowed and endorsed; express it as a native
  review loop rather than one extra dispatch per artifact.
- No subagent for a lookup a direct `read`, `grep`, or `code` call answers.

### Context overflow sharding

If parallel calls fail due to context size: shard work across instances of the same
agent type with smaller scopes, in waves within the concurrency cap, then synthesize.

## Coordination Protocol (pre-parallelization)

Applies to IMPLEMENTATION tasks only (not analysis, reviews, research).

**Step 1 — File ownership**: List files each subtask will modify:

```yaml
subtask_files:
  - task: "description"
    files: [path/file1.py, path/file2.py]
```

**Step 2 — Overlap detection**: no overlap → parallelize with explicit boundaries;
overlap → sequentialize conflicting tasks, parallelize the rest.

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
file analysis is ambiguous. Waves follow `Parallelization safety`.

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
target stage with that feedback as context, and the pipeline advances once the output no
longer contains the trigger. The trigger must be at least four characters, so use a
distinctive marker such as `NEEDS_CHANGES`.

Prefer a native loop whenever a producing stage and a checking stage alternate: it costs
fewer orchestrator turns, and the runtime enforces the iteration count. `reviewing-code`
uses it.

## Direct pass-through

Present a subagent's final, complete response directly without paraphrasing — especially
code, structured reports, step-by-step instructions, and technical analysis.

Synthesize when: merging multiple outputs, adding missing context, summarizing verbose
output, or highlighting key decisions/risks.

## Planning phases

For complex tasks (multi-agent, multi-file changes, or anything involving
implementation), follow this collaborative planning workflow; simple single-agent tasks
are delegated directly. Planning is a **conversation, not a presentation**.

### Phase 1 — Understand and clarify

Restate the understanding in 2-3 sentences, surface assumptions, and ask structured
questions with numbered multiple-choice options for unclear parts; the user can answer
any subset (e.g., "1=a, 2=b"). Typically 1-2 rounds. Do not over-ask — make reasonable
assumptions and let the user correct them.

### Phase 2 — Research (when needed)

Delegate read-only exploration to the appropriate agent. Skip when sufficient context is
already available.

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

After approval, delegate in **preflight mode** only to agents whose feasibility is
genuinely uncertain — an unfamiliar subsystem, blockers that could reroute the task, or
a High-complexity slice of the plan. Everything else goes straight to Phase 6 in
combined mode with the full specification.

Evaluate the reports per `Handling preflight feedback`. If the plan changes
significantly ("Will do" / "Will NOT do" scope affected), inform the user and get
re-approval.

### Phase 6 — Execute

Delegate in **execute mode**, passing the approved plan plus any Phase 5 adjustments as
`relevant_context`. Agents implement following their preflight execution plan.

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

A 2-3 line combined preflight followed by the implementation satisfies the table and
MUST NOT be rejected for lacking a full Preflight Report.

**Rejection protocol** — on structurally invalid output:

1. Do NOT pass downstream.
2. Re-delegate with explicit format instructions.
3. On second failure: record an `agent_feedback` entry (`agent`, `pattern`,
   `mitigation`) in `memory/state.yaml` and fall back.

### Circuit breakers

#### Retry limits

| Scope                  | Max attempts | After exhaustion                        |
| ---------------------- | ------------ | --------------------------------------- |
| Single agent task      | 3            | Fallback to next-best agent             |
| Agent in workflow step | 2            | Reroute or skip with user notification  |
| Full workflow          | 1 restart    | Halt, present partial results, ask user |

Within a single agent task, escalate the context rather than repeating it: same context
→ reduced context → escalate.

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
- **Safeguard refusal**: a security-engineer stop with `stop_reason: "refusal"` is a
  classifier decline, not a scope failure. Retry once with the defensive framing and
  authorization made explicit (the user's own code, review rather than exploit
  development); fall back only if the retry is also declined.

### Token budget awareness

Cost (the Cost column of routing.md) only breaks ties between agents that match on
capability — `Routing Decision Procedure`, step 5.

### Session effort policy

Effort is a session-level lever held by the human: the orchestrator never varies it per
delegation and at most recommends one level once per session, before the work starts.

| Work                                                                               | Recommended session effort |
| ---------------------------------------------------------------------------------- | -------------------------- |
| `security-audit`                                                                   | `xhigh`                    |
| Debugging pattern, past the second failed attempt                                  | `xhigh`                    |
| `spec-to-dev` design phase, architecture change                                    | `high`                     |
| Routine mechanical work (renames, config edits, doc formatting, single-file fixes) | `low`                      |
| Everything else                                                                    | session default            |

Precedence, the unverified reach of `/effort` into subagents, and the step-down
argument: `orchestration-rationale.md`, `## Session effort`.

### Post-execution verification gate

Accept a code-modifying execution when its output lists the files modified and the
validation outcome from this run. If validation was not run, or ran and failed, return
the task to the owning agent naming the missing or failing check. The orchestrator does
not re-run validation itself — the agent that made the change owns it, per `COMMON.md`'s
`## Verification First`.

### Scope creep detection

Compare the declared preflight plan against actual output:

- Files modified outside the plan → flag as scope creep.
- Features, tests, files, docs, or refactors nobody asked for → flag as scope creep; the
  agent should have named them at the end instead. Tests and docstrings the code
  standards require for the change are exempt.
- Planned files not modified → flag as incomplete.
- Either case → ask the agent to explain before accepting.

### Drift detection

Run `make drift-check` after agent creation or deletion, skill addition, resource file
moves, or routing.md edits.

### State protection

Every `memory/state.yaml` entry carries `id`, `date` (ISO format), and `scope`, plus
`agent`, `pattern`, and `mitigation` in `agent_feedback`. After writing the file, run
`make drift-check`, which validates parsing, the 20-entry section cap, and unique ids;
required fields and dates are not machine-checked, so confirm them before writing. Fix
any finding before continuing.

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

## Conductor: ad-hoc workflow composition

When no predefined Collaboration Pattern in routing.md matches, the orchestrator
generates a custom workflow at runtime. All of these must be true: the task spans
multiple concerns · no existing pattern matches well · the optimal agent sequence is not
obvious. If a predefined pattern clearly matches, or a single agent suffices, do not
compose an ad-hoc workflow.

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
parallelise only subtasks that are genuinely independent and large enough to warrant
their own dispatch (see `Delegation floor`). Iterative topologies are native review
loops.

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

Present the plan to the user for approval before executing it. After each step: evaluate
the output against `success_criteria` · adapt the remaining plan (skip, inject, or swap
steps) · never forward stale context — update `relevant_context` with what was actually
produced, and rewrite the next agent's query when the previous step changed the picture.

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
