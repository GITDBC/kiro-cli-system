---
name: deps-audit
description: >
  Dependency freshness and vulnerability audit with depschecker. Triggers: 'check
  dependencies', 'audit deps', 'outdated packages', 'vulnerability scan'. Not for code
  review or security audits beyond dependencies (use security-audit).
---

# Dependency Audit

## Workflow

One **security-engineer** dispatch covers freshness and vulnerabilities:

1. Run one combined report, with absolute paths and the output written to a file so it
   does not flood the context (see `tools/TOOLS_OVERVIEW.md`):

   ```bash
   export WORK_AGENTS_CONFIG="<repo>/config.toml"
   uv run --project <repo>/tools/depschecker depschecker \
     --lock <abs-project>/uv.lock \
     -o <repo>/tmp/deps-report.md \
     <abs-project>/pyproject.toml
   ```

   Without a `uv.lock`, the scan exits 1; pass `--freshness-only` and state that
   vulnerabilities were not checked.

2. Read the report and highlight packages whose major/minor updates require migration
   effort.
3. Cross-reference each vulnerability with the freshness data and produce a prioritized
   table: Package | Current | CVE/Advisory | Severity | Fixed in | Upgrade resolves?
   State "uncertain" rather than asserting a fix when the advisory data does not clearly
   confirm the upgrade resolves the CVE; a false "resolves" claim leaves the team
   exposed.

## Success Criteria

- Freshness report produced with upgrade recommendations.
- Vulnerability report produced with severity and fix-version mapping.
- Clear prioritization: which upgrades resolve security issues vs. are optional
  freshness bumps.
