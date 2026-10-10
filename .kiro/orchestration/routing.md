# Agent Routing Schema

This file defines the agent selection logic for LLMs. Given a task description, match it
against the routing rules below to determine which agent(s) to activate. Where a rule
here carries no argument, the argument is in
`.kiro/orchestration/orchestration-rationale.md`; read it when a settled decision is
being challenged.

**IMPORTANT**: All agents MUST apply the directives from `COMMON.md` (Python 3.11, PEP
style, Jenkins/GitLab CI/CD, SonarQube coverage gate, no deprecated code). Numeric
thresholds are stated once, in `code-standards-summary.md`.

## Quick Lookup

<!-- Compact reference for fast routing. Details in sections below. -->

| Agent              | When to pick                  | Cost          | Fallback         |
| ------------------ | ----------------------------- | ------------- | ---------------- |
| software-architect | design, DDD, ADRs, trade-offs | high (2.2x)   | senior-developer |
| ai-engineer        | ML, MLOps, prompt engineering | medium (1.3x) | data-engineer    |
| data-engineer      | ETL, Spark, dbt, schemas      | medium (1.3x) | senior-developer |
| senior-developer   | implement, refactor, fix      | high (2.2x)   | code-reviewer    |
| security-engineer  | threats, OWASP, secure review | high (2.2x)   | code-reviewer    |
| code-reviewer      | review, anti-patterns, debt   | medium (1.3x) | senior-developer |
| qa-engineer        | test analysis, tool eval, TCO | medium (1.3x) | code-reviewer    |
| platform-engineer  | CI/CD, IaC, K8s, SLOs         | medium (1.3x) | senior-developer |
| technical-writer   | docs, READMEs, tutorials      | medium (1.3x) | senior-developer |
| telecom-engineer   | wireless, signal processing   | medium (1.3x) | senior-developer |
| kpi-analyst        | KPI frameworks, counters      | medium (1.3x) | data-engineer    |
| engagement-manager | client strategy, roadmaps     | low (0.4x)    | kpi-analyst      |

Cost is the credit multiplier of the model backing each agent: `claude-opus-5` = 2.2x,
`claude-sonnet-5` = 1.3x, `claude-haiku-4.5` = 0.4x.

**Routing shortcut**: implementation → senior-developer · review → code-reviewer ·
security → security-engineer · infra → platform-engineer · docs → technical-writer ·
design → software-architect · data → data-engineer · ML → ai-engineer · wireless →
telecom-engineer · KPIs → kpi-analyst · client → engagement-manager

## Agent Capabilities Matrix

For **adaptive pool selection** (see the Conductor section of
`delegation-lifecycle.md`): match a task to agents by strengths, cost, complementarity
(`pairs with`), and typical workflow position. Cost mirrors the Quick Lookup table.

| Agent              | Strengths                                                                             | Cost          | Pairs with                                              | Position                                         |
| ------------------ | ------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------- | ------------------------------------------------ |
| software-architect | system design, trade-off analysis, abstraction, DDD, ADRs                             | high (2.2x)   | senior-developer, data-engineer, code-reviewer          | early                                            |
| ai-engineer        | ML pipelines, model integration, prompt engineering, MLOps                            | medium (1.3x) | data-engineer, senior-developer, qa-engineer            | middle                                           |
| data-engineer      | ETL/ELT, data quality, Spark, dbt, schema design, migrations, EDA                     | medium (1.3x) | software-architect, ai-engineer, platform-engineer      | middle                                           |
| senior-developer   | implementation, refactoring, testing, full-stack, performance, debugging              | high (2.2x)   | code-reviewer, software-architect, technical-writer     | middle-to-late                                   |
| security-engineer  | threat modeling, OWASP, vulnerability analysis, secure design                         | high (2.2x)   | code-reviewer, platform-engineer, senior-developer      | late                                             |
| code-reviewer      | quality analysis, anti-patterns, maintainability, tech debt, review fixes             | medium (1.3x) | senior-developer, software-architect, security-engineer | late                                             |
| qa-engineer        | test analysis, coverage gaps, failure patterns, TCO/ROI, tool comparison              | medium (1.3x) | platform-engineer, senior-developer, ai-engineer        | early (tool/tech evaluation) or late (readiness) |
| platform-engineer  | CI/CD, IaC, containers, SLOs, observability, toil reduction                           | medium (1.3x) | senior-developer, security-engineer, code-reviewer      | late                                             |
| technical-writer   | documentation, clarity, structure, API references, tutorials                          | medium (1.3x) | senior-developer, software-architect                    | last                                             |
| telecom-engineer   | network protocols, mobile comms, signal processing, dimensioning, wireless algorithms | medium (1.3x) | kpi-analyst, code-reviewer                              | middle                                           |
| kpi-analyst        | KPI frameworks, counter engineering, gap analysis, percentiles, statistical tests     | medium (1.3x) | telecom-engineer, engagement-manager, data-engineer     | early-to-middle                                  |
| engagement-manager | client strategy, phased deliverables, stakeholder mapping, risk                       | low (0.4x)    | kpi-analyst, software-architect                         | early                                            |

Output types follow from each role (e.g. software-architect → design docs/ADRs/interface
specs; senior-developer → code/tests/fixes; code-reviewer → review reports/scorecards;
data-engineer → pipeline code/schema DDL/contracts; technical-writer → READMEs/API
docs).

## Routing Rules

```yaml
routing:
  - group: core
    agents:
      - id: software-architect
        trigger_when:
          - system design or architecture decisions
          - choosing between architectural patterns (monolith, microservices,
            event-driven)
          - domain modeling, bounded contexts, DDD
          - trade-off analysis between technical approaches
          - writing ADRs (Architecture Decision Records)
          - evaluating scalability or maintainability of a system
          - data modeling and entity-relationship design
        never_when:
          - writing implementation code
          - reviewing existing code

      - id: ai-engineer
        trigger_when:
          - building or training ML models
          - designing data pipelines for AI/ML
          - integrating AI features into applications
          - MLOps, model deployment, inference APIs
          - NLP, computer vision, recommendation systems
          - prompt engineering or LLM integration
        never_when:
          - general data pipelines without ML component

      - id: data-engineer
        trigger_when:
          - ETL/ELT pipeline design or implementation
          - data warehouse or lakehouse architecture
          - data quality, schema validation, data contracts
          - Apache Spark, dbt, streaming systems (Kafka, Flink)
          - medallion architecture (bronze/silver/gold)
          - data migration or CDC pipelines
          - database schema design, normalization, index strategy
          - migration planning (expand-contract, zero-downtime)
          - exploratory data analysis, data profiling, dataset summarization
        never_when:
          - ML model training (use ai-engineer)
          - high-level data modeling decisions (use software-architect first)

      - id: senior-developer
        trigger_when:
          - implementing features or writing application code
          - full-stack development tasks
          - frontend/backend integration
          - performance optimization of application code
          - refactoring or improving existing code
          - debugging, root-cause analysis of defects, fixing failing tests
          - JIRA ticket enhancement, grooming, or technical breakdown
        never_when:
          - infrastructure or deployment tasks
          - high-level architecture decisions (use software-architect)

      - id: security-engineer
        trigger_when:
          - threat modeling or security architecture
          - vulnerability assessment or secure code review
          - OWASP Top 10, CWE Top 25 analysis
          - security in CI/CD (SAST, DAST, SCA)
          - authentication, authorization, secrets management
          - compliance security requirements
          - auditing AI agent skills or prompts for security risks
        never_when:
          - general code review without security focus (use code-reviewer)

      - id: code-reviewer
        trigger_when:
          - reviewing pull requests or code changes
          - evaluating code quality, maintainability, readability
          - identifying anti-patterns or code smells
          - suggesting improvements to existing code
          - applying local or mechanical fixes raised by its own review
          - mentoring through code review
          - tech debt identification and tracking
          - API design review and breaking change detection
        never_when:
          - implementing new features (use senior-developer)
          - architectural refactors spanning modules (use senior-developer)
          - security-focused audit (use security-engineer)

  - group: testing-and-evaluation
    agents:
      - id: qa-engineer
        trigger_when:
          - analyzing test execution results or reports
          - evaluating test coverage metrics
          - identifying failure patterns or flaky tests
          - release readiness assessment based on test data
          - quality risk analysis
          - comparing or selecting tools, libraries, or platforms
          - technology assessment with pros/cons
          - TCO/ROI analysis for tech decisions
          - evaluating adoption strategy for new tools
        never_when:
          - writing test code (use senior-developer)
          - implementing the chosen tool (use senior-developer)

  - group: platform
    agents:
      - id: platform-engineer
        trigger_when:
          - CI/CD pipeline design or implementation
          - Infrastructure as Code (Terraform, CDK, CloudFormation)
          - container orchestration (Docker, Kubernetes)
          - deployment strategies (blue-green, canary, rolling)
          - automating development workflows
          - defining SLOs, SLIs, or error budgets
          - observability (logs, metrics, traces)
          - incident response or post-mortems
          - chaos engineering or resilience testing
          - capacity planning
          - toil reduction analysis
        never_when:
          - application code or business logic (use senior-developer)
          - architectural design without infra (use software-architect)

  - group: domain
    agents:
      - id: telecom-engineer
        trigger_when:
          - telecommunications network design or architecture
          - signal processing, modulation, multiplexing (FDM, TDM, CDM)
          - network protocols (OSI, TCP/IP), routing, switching
          - mobile communications (GSM, LTE, handover, roaming)
          - network dimensioning, queuing theory, traffic engineering
          - channel capacity, BER, spectral efficiency
          - medium access control (Aloha, CSMA, CSMA/CD, CSMA/CA)
          - designing or optimizing wireless communication algorithms
          - channel estimation, MIMO detection, LDPC decoding
          - link adaptation, MCS selection, spectral efficiency optimization
          - iterative algorithm optimization with evaluation metrics
          - physical-layer algorithm benchmarking (NVE, BLER, BER)
        never_when:
          - general software architecture (use software-architect)
          - CI/CD or deployment tasks (use platform-engineer)
          - ML model training without wireless domain (use ai-engineer)

      - id: kpi-analyst
        trigger_when:
          - KPI definition, selection, or cataloging
          - performance counter engineering and formula validation
          - distribution and percentile analysis (P50, P95, P99)
          - measurement mapping and gap analysis
          - KPI framework design or review
          - statistical test selection, hypothesis testing, effect sizes
          - regression and correlation analysis, power analysis
        never_when:
          - general data pipelines (use data-engineer)
          - ML model metrics (use ai-engineer)

      - id: engagement-manager
        trigger_when:
          - client engagement planning or structuring
          - validation roadmaps and phased deliverables
          - data governance constraints for engagements
          - stakeholder mapping and communication strategy
          - risk registers for technical engagements
        never_when:
          - technical implementation (use senior-developer)
          - project management tooling (use platform-engineer)

  - group: docs
    agents:
      - id: technical-writer
        trigger_when:
          - writing or improving documentation
          - README files, API references, tutorials
          - docs-as-code setup (Docusaurus, MkDocs, etc.)
          - explaining complex concepts clearly
          - changelog or release notes
          - generating technical reports, specs, or structured deliverables
        never_when:
          - writing application code
```

## Routing Decision Procedure

Consult this procedure for every delegation decision.

```
1. Does the task match a Collaboration Pattern? → Use that pattern directly.
2. Extract domain keywords from the task.
3. Match them against the `trigger_when` and `never_when` entries of the routing YAML
   above; the Quick Lookup table is the one-line version of the same signal.
4. If multiple agents match → apply the disambiguation table below.
5. If still ambiguous → prefer the lower credit multiplier, then the earlier position.
6. If the selected agent fails → use the fallback chain below.
```

Step 5 reads the Cost column, not a qualitative guess, and never overrides capability
match. Provenance: `.kiro/orchestration/orchestration-rationale.md`.

### Critical disambiguation

Resolutions for the conflicts that arise most often.

| Conflict                          | Resolution                                                                               |
| --------------------------------- | ---------------------------------------------------------------------------------------- |
| refactor (any domain)             | senior-developer — the only agent with a refactoring trigger                             |
| optimize + infra context          | platform-engineer (not senior-developer)                                                 |
| test + analysis/metrics           | qa-engineer; writing the test code itself → senior-developer                             |
| high-level data model + schema    | software-architect first, then data-engineer for physical schema, DDL, and migration     |
| pipeline implementation + Polars  | data-engineer only when the task is a data pipeline, not because Polars is named         |
| security review of code           | security-engineer leads; code-reviewer runs alongside it in the `security-audit` pattern |
| review that requires new features | code-reviewer reports, senior-developer implements                                       |
| research artifact needs review    | software-architect (code-reviewer is code-scoped only)                                   |

Two rules are often applied backwards — data modelling (conceptual model before physical
schema) and Polars (no routing signal on its own). Reasoning:
`.kiro/orchestration/orchestration-rationale.md`.

### Fallback chain

Used when the selected agent fails or the task falls outside its scope.

```
software-architect → senior-developer → code-reviewer
ai-engineer → data-engineer → senior-developer
data-engineer → senior-developer
senior-developer → code-reviewer
security-engineer → code-reviewer
code-reviewer → senior-developer
platform-engineer → senior-developer
telecom-engineer → senior-developer
kpi-analyst → data-engineer
engagement-manager → kpi-analyst
qa-engineer → code-reviewer
technical-writer → senior-developer
```

## Collaboration Patterns

When a task spans multiple concerns, use these predefined workflows. The orchestrator
matches the task to a pattern, then delegates following the agent sequence.

| Task                      | Skill                                                   | Agents (in order)                                                                                                                           | Topology                                                                                  |
| ------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Spec-driven development   | spec-to-dev                                             | senior-developer → software-architect → USER_VALIDATION → senior-developer (parallel) → code-reviewer → senior-developer → technical-writer | sequential + parallel impl (max 4 concurrent), code-reviewer interface gate between waves |
| Security audit            | security-audit                                          | security-engineer (one dispatch, all three perspectives) + code-reviewer                                                                    | parallel (2 invocations)                                                                  |
| Data pipeline with ML     | data-pipeline                                           | software-architect → data-engineer → ai-engineer                                                                                            | sequential                                                                                |
| Production incident       | incident-response                                       | platform-engineer                                                                                                                           | single                                                                                    |
| Technology evaluation     | tech-evaluation                                         | qa-engineer → software-architect → platform-engineer                                                                                        | sequential                                                                                |
| Release readiness         | release-readiness                                       | qa-engineer, platform-engineer, security-engineer                                                                                           | parallel                                                                                  |
| Review and fix            | reviewing-code                                          | code-reviewer                                                                                                                               | native loop (target: fix, trigger: NEEDS_CHANGES, max_iterations: 3)                      |
| Dependency audit          | deps-audit                                              | senior-developer → security-engineer                                                                                                        | sequential                                                                                |
| Tech debt assessment      | tech-debt-tracking                                      | code-reviewer, software-architect, platform-engineer                                                                                        | parallel                                                                                  |
| KPI assessment            | kpi-assessment                                          | kpi-analyst → telecom-engineer (reviewer)                                                                                                   | native loop (target: kpi-analyst, trigger: NEEDS_CHANGES, max_iterations: 2)              |
| Engagement plan           | engagement-plan                                         | engagement-manager → kpi-analyst (reviewer)                                                                                                 | native loop (target: engagement-manager, trigger: NEEDS_CHANGES, max_iterations: 2)       |
| Agent/skill creation      | agent-creation                                          | software-architect → senior-developer → code-reviewer → security-engineer                                                                   | sequential                                                                                |
| Software design review    | software-design-review                                  | software-architect, code-reviewer                                                                                                           | parallel                                                                                  |
| ML model testing          | ml-model-testing                                        | ai-engineer → qa-engineer                                                                                                                   | sequential                                                                                |
| Database design           | — (pattern only, no skill)                              | software-architect → data-engineer                                                                                                          | sequential                                                                                |
| Wireless optimization     | wireless-optimization                                   | telecom-engineer → code-reviewer                                                                                                            | sequential                                                                                |
| Debugging                 | debugging                                               | senior-developer                                                                                                                            | single (iterative, max 3)                                                                 |
| Code refactoring          | refactoring                                             | senior-developer                                                                                                                            | single                                                                                    |
| Domain research           | domain-research                                         | telecom-engineer → software-architect → technical-writer                                                                                    | sequential                                                                                |
| CI/CD pipeline design     | cicd-pipeline-design                                    | platform-engineer                                                                                                                           | single                                                                                    |
| JIRA enhancement          | jira-enhancement                                        | senior-developer                                                                                                                            | single                                                                                    |
| Autonomous loop           | ralph-loop                                              | senior-developer                                                                                                                            | single (standalone)                                                                       |
| Dynamic orchestration     | — (orchestration: `delegation-lifecycle.md`, Conductor) | —                                                                                                                                           | generated at runtime                                                                      |
| Self-improvement          | self-improvement                                        | code-reviewer → software-architect                                                                                                          | sequential                                                                                |
| Exploratory data analysis | exploratory-data-analysis                               | data-engineer                                                                                                                               | single (direct-invoke)                                                                    |
| Statistical analysis      | statistical-analysis                                    | kpi-analyst                                                                                                                                 | single (direct-invoke)                                                                    |
| Unit test generation      | unit-test-generation                                    | senior-developer                                                                                                                            | single (direct-invoke)                                                                    |

### Pattern details

**Spec-driven development**: Full spec-driven flow: explore → design+decompose →
validate plan with user → coordinate+implement (parallel per subtask) → review → fix →
document. The architect decomposes into subtasks with file ownership. The orchestrator
applies the Coordination Protocol to parallelize implementation. MUST pause for user
approval after the design phase. When implementation spans more than one dependency
wave, a single code-reviewer dispatch sits at each wave boundary as an interface gate,
covering only the subtasks whose exposed interfaces are consumed downstream and checking
contract shape alone — signatures, schemas, error contracts. It is one dispatch per
boundary rather than per subtask, so a single-wave feature pays nothing, and the
code-reviewer step above remains the only full review.

**Review and fix**: Iterative loop implemented as a **native subagent loop**, not a
manual re-invocation chain: a review stage emits `NEEDS_CHANGES` when revisions are
required, which re-runs the fix stage with the review feedback as context
(`target: fix`, `trigger: NEEDS_CHANGES`, `max_iterations: 3`). The loop exits as soon
as the review output no longer contains the trigger. Single agent (code-reviewer)
applies local and mechanical fixes; new features or architectural refactors are handed
to senior-developer. For large codebases (>15 files), split into batches of 7-12 files.

**Debugging**: Single-agent iterative pattern (max 3 attempts) executed by
senior-developer alone; the row names only the executor, not every agent wired to the
skill. `qa-engineer.json` also declares `debugging` deliberately, for test-failure
analysis rather than as a second executor — see
`.kiro/orchestration/orchestration-rationale.md`.

**Security audit**: Two parallel invocations — one security-engineer dispatch carrying
an explicit coverage instruction that names all three perspectives (threat model, code
vulnerabilities, configuration and dependencies), plus code-reviewer for
quality-adjacent findings. A third dispatch, scoped to configuration and dependencies,
is justified only when that surface is genuinely a separate codebase — a standalone IaC
repository, a vendored dependency tree — not when config files simply sit beside the
code under audit. Cost arithmetic and the single-dispatch argument:
`.kiro/orchestration/orchestration-rationale.md`.

**Database design**: Pattern only — there is no backing skill file. The orchestrator
composes it manually: software-architect settles the high-level data model and bounded
contexts, then data-engineer produces the physical schema, DDL, indexes, and migration
plan.

**Tech debt assessment**: Parallel analysis: code-reviewer scans code debt,
software-architect assesses architectural debt, platform-engineer evaluates operational
debt. Output saved to `tech-debt/` or `suggestions/`.

**Agent/skill creation**: software-architect defines spec and boundaries,
senior-developer drafts the agent/skill, code-reviewer validates quality and
consistency, security-engineer audits for risks. Orchestrator updates routing.md at the
end.

**Dynamic orchestration**: Conductor-style workflow for tasks that don't match any
predefined skill. Governed by the Conductor section of `delegation-lifecycle.md` rather
than by a skill file. The orchestrator selects a minimal agent pool from the
Capabilities Matrix, designs an optimal topology, and delegates with structured
instructions. The plan adapts during execution based on intermediate results.

**Autonomous loop**: Time-budgeted autonomous loop via `ralph.sh --time`. Not
orchestrator-managed — runs as standalone process.

**Exploratory data analysis**: Single-agent direct-invoke utility. data-engineer
generates a structured markdown EDA report covering data quality, statistical summaries,
correlations, and downstream recommendations. Use when a user provides a data file to
explore or summarize before further processing.

**Statistical analysis**: Single-agent direct-invoke utility. kpi-analyst selects
appropriate statistical tests, checks assumptions, calculates effect sizes, and reports
results in APA format. Use when choosing statistical tests, running hypothesis tests,
regression/correlation analysis, power analysis, or Bayesian methods.

**Unit test generation**: Single-agent direct-invoke utility. senior-developer generates
pytest test suites for existing code — fixtures, parametrised cases, and edge-case
coverage targeting the 80% SonarQube threshold. Use when a user points at a module or
function that needs tests, without a broader implementation or review workflow.

**KPI assessment**: Native subagent loop rather than a manual kpi-analyst →
telecom-engineer → kpi-analyst chain. kpi-analyst produces the KPI framework;
telecom-engineer reviews it for domain correctness and emits `NEEDS_CHANGES` when the
framework needs revision, which re-runs the kpi-analyst stage with that feedback
(`target: kpi-analyst`, `trigger: NEEDS_CHANGES`, `max_iterations: 2`).

**Engagement plan**: Native subagent loop rather than a manual engagement-manager →
kpi-analyst → engagement-manager chain. engagement-manager drafts the engagement plan;
kpi-analyst reviews measurability and emits `NEEDS_CHANGES` to re-run the drafting stage
(`target: engagement-manager`, `trigger: NEEDS_CHANGES`, `max_iterations: 2`).
