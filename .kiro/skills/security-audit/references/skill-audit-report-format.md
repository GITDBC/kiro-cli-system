# Skill Security Audit Report Format

Output contract for an audit of a skill, agent prompt, bundled script, or MCP server
configuration. Load it when producing that report; the threat categories, audit
checklist, and PASS/WARN/FAIL severity definitions stay in the `security-engineer`
prompt.

```markdown
# Skill Security Audit Report

## Skill Metadata

- **Skill**: [skill name]
- **Path**: [path to SKILL.md]
- **Agents involved**: [list of agents in the workflow]
- **Date**: [audit date]

## Threat Analysis

[Summary of attack surface: what commands are run, what data flows externally, what
permissions are requested.]

## Findings

| #   | Severity | Finding                    | Remediation    |
| --- | -------- | -------------------------- | -------------- |
| 1   | FAIL     | [description of the issue] | [concrete fix] |
| 2   | WARN     | [description of the issue] | [concrete fix] |

## Verdict: [PASS / WARN / FAIL]

[One-line justification.]
```
