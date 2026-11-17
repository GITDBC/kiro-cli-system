<p align="center">
  <img src="assets/imgs/kiro_logo.png" alt="Work Agents logo">
</p>

<p align="center">
  <a href="https://github.com/GITDBC/kiro-cli-system/actions/workflows/ci-cd.yml"><img src="https://github.com/GITDBC/kiro-cli-system/actions/workflows/ci-cd.yml/badge.svg" alt="CI/CD pipeline status"></a>
  <a href="https://opensource.org/licenses/MIT" target="_blank">
    <img src="https://img.shields.io/badge/license-MIT-blue" alt="License MIT">
  </a>
</p>

# Work Agents

A [Kiro CLI](https://kiro.dev/docs/cli/) V3 agent system made up of nine specialised
engineering agents and an orchestrator that routes each task to the right one.

## Requirements

- Kiro CLI 3.0.0 or later (V3 harness)
- [uv](https://docs.astral.sh/uv/) with Python 3.13

## Usage

```bash
cp config.toml.example config.toml   # gitignored; may hold secrets
kiro-cli chat --agent orchestrator --trust-all-tools
```

The project is V3-only: `.kiro/settings/cli.json` pins `chat.agentEngine` to `v3`.

## Autonomous execution

For unattended work with a time budget:

```bash
.kiro/skills/ralph-loop/ralph.sh --time 3h "Implement user auth with JWT and tests"
```

For short interactive tasks, `.kiro/skills/ralph-loop/ralph-session.sh start "<prompt>"`
keeps the session iterating through a Stop hook instead.
