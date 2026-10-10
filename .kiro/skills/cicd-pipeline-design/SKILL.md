---
name: cicd-pipeline-design
description: >
  CI/CD pipeline design workflow. Use when designing or reviewing multi-stage deployment
  pipelines with approval gates, environment promotion, and deployment strategies
  (blue-green, canary, rolling). Assigned to platform-engineer. Not for running existing
  pipelines or debugging CI failures (use debugging skill).
---

# CI/CD Pipeline Design Workflow

## Invocation

Use when: designing a new pipeline, adding stages/environments, choosing deployment
strategies, implementing approval/quality gates, or reviewing rollback capabilities.

Do NOT use when: fixing a broken pipeline step (`debugging`), running an existing
pipeline, or writing application code.

## Workflow

Delegate to **platform-engineer**:

### Phase 1: Requirements Gathering

- Identify target environments (dev, staging, production).
- Define artifact types (images, packages, binaries).
- Determine compliance requirements (approvals, audit trails).
- Establish SLAs: max deployment time, max rollback time.

### Phase 2: Pipeline Architecture

For stage-configuration examples (Jenkinsfile/GitLab CI snippets, gate definitions),
load `references/cicd-automation-patterns.md`.

Design stages following this pattern:

```
Commit → Build → Test → Security Scan → Stage Deploy → Integration Test → Approval → Prod Deploy → Smoke Test → Monitor
```

For each stage define: trigger (auto/manual), gate (pass criteria), timeout, rollback
(auto/manual + criteria).

### Phase 3: Deployment Strategy Selection

| Strategy       | When to use                                           | Rollback speed | Risk    |
| -------------- | ----------------------------------------------------- | -------------- | ------- |
| **Rolling**    | Stateless services, low risk                          | Medium         | Low     |
| **Blue-Green** | Zero-downtime required, fast rollback critical        | Instant        | Medium  |
| **Canary**     | High-traffic services, gradual validation needed      | Fast           | Lowest  |
| **Recreate**   | Dev/staging only, or stateful with maintenance window | Slow           | Highest |

### Phase 4: Reliability Patterns

- **Rollback automation**: define failure signals that trigger automatic rollback.
- **Circuit breakers**: stop promotion if error rate exceeds threshold.
- **Deployment windows**: restrict prod deploys to safe hours.
- **Artifact immutability**: same artifact promoted through all stages.
- **Infrastructure as Code**: pipeline definition versioned alongside app code.

### Phase 5: Output

- Pipeline diagram (stages, gates, triggers).
- Configuration files (Jenkinsfile, `.gitlab-ci.yml`, GitHub Actions, etc.).
- Rollback runbook.
- Monitoring integration (deploy markers, error budget impact).

## Safety

- Never deploy directly to production without at least one prior environment validation.
- Always include a rollback mechanism.
- Approval gates for production are mandatory unless explicitly waived by the user.
