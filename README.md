<p align="center">
  <img src="assets/imgs/kiro_logo.png" alt="Work Agents logo">
</p>

# Work Agents

Specialized engineering agents orchestrated by a central agent that delegates tasks
automatically. Built for [Kiro CLI](https://kiro.dev/docs/cli/) v3.

## Configuration

```bash
cp config.toml.example config.toml
```

Tools read their section from `config.toml` when `WORK_AGENTS_CONFIG` points to it. CLI
arguments take priority. Gitignored (may contain secrets).

## Kiro CLI Quick Start

```bash
kiro-cli chat --agent orchestrator --trust-all-tools --v3
```

The orchestrator picks the right agent(s) and delegates via `use_subagent`, see
[routing.md](.kiro/orchestration/routing.md) for more details.

## Ralph Loop (Autonomous Development)

Time-budgeted autonomous loop: implements first, then verifies/tests with remaining
time.

```bash
.kiro/skills/ralph-loop/ralph.sh --time 3h "Implement user auth with JWT and tests"
```
