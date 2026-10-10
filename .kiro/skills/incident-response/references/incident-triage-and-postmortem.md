# Incident Response Playbook

## Severity Classification

| Severity | Criteria                                 | Response Time     | Escalation     |
| -------- | ---------------------------------------- | ----------------- | -------------- |
| SEV1     | Service down, data loss, security breach | Immediate         | All hands      |
| SEV2     | Major degradation, >10% users affected   | 15 min            | On-call + lead |
| SEV3     | Minor degradation, workaround exists     | 1 hour            | On-call        |
| SEV4     | Cosmetic, no user impact                 | Next business day | Ticket         |

## Initial Triage Checklist

1. **Confirm the incident** — Is this real or a false alarm?
   - Check monitoring dashboards for corroborating signals
   - Verify with a second source (different metric, different region)
2. **Assess blast radius** — Who/what is affected?
   - Number of users impacted
   - Which services/regions/environments
   - Revenue impact estimate
3. **Assign severity** using the table above
4. **Open communication channel** (Slack incident channel, bridge call)
5. **Designate roles**: Incident Commander, Communications Lead, Technical Lead

## Diagnosis Methodology

### Round 1: Quick Signals (5 min)

- Check recent deployments (last 24h) — `git log --since="24 hours ago" --oneline`
- Check infrastructure changes (scaling events, config changes)
- Review error rate graphs — when did it start?
- Check external dependencies (third-party APIs, DNS, CDN)

### Round 2: Deep Dive (15 min)

- Correlate timeline: what changed at the exact moment of impact?
- Examine logs for the affected service with error-level filter
- Check resource saturation: CPU, memory, disk, connections
- Review distributed traces for failing requests

### Round 3: Hypothesis Testing (15 min)

- Form top-3 hypotheses based on evidence
- For each: what would confirm it? what would rule it out?
- Execute cheapest test first
- If all hypotheses fail, widen scope (upstream/downstream services)

## Mitigation Patterns

| Pattern       | When to use                 | Command/Action                                |
| ------------- | --------------------------- | --------------------------------------------- |
| Rollback      | Bad deploy identified       | `git revert` + redeploy                       |
| Scale up      | Resource exhaustion         | Increase replicas/capacity                    |
| Circuit break | Downstream failure          | Enable circuit breaker / disable feature flag |
| Traffic shift | Regional issue              | Route traffic to healthy region               |
| Restart       | Memory leak / stuck process | Rolling restart of affected pods              |

## Communication Templates

### Status Update (every 15 min during SEV1/SEV2)

```
**Incident Update — [HH:MM UTC]**
Status: Investigating / Identified / Mitigating / Resolved
Impact: [who is affected and how]
Current action: [what we're doing right now]
Next update: [time]
```

### Resolution Notice

```
**Incident Resolved — [HH:MM UTC]**
Duration: [start to end]
Impact: [summary]
Root cause: [brief]
Follow-up: [post-mortem scheduled for DATE]
```

## Post-Mortem Template

```markdown
## Post-Mortem: [Incident Title]

**Date**: YYYY-MM-DD **Duration**: X hours Y minutes **Severity**: SEVN **Author**:
[name]

### Summary

[2-3 sentences: what happened, impact, resolution]

### Timeline

| Time (UTC) | Event                 |
| ---------- | --------------------- |
| HH:MM      | First alert fired     |
| HH:MM      | Incident declared     |
| HH:MM      | Root cause identified |
| HH:MM      | Mitigation applied    |
| HH:MM      | Incident resolved     |

### Root Cause

[Technical explanation of why it happened]

### Contributing Factors

- [Factor 1]
- [Factor 2]

### What Went Well

- [Thing 1]

### What Went Poorly

- [Thing 1]

### Action Items

| Action   | Owner | Due Date | Priority |
| -------- | ----- | -------- | -------- |
| [action] | [who] | [when]   | P1/P2/P3 |
```
