<p align="center">
  <img src="assets/imgs/kiro_logo.png" alt="Work Agents logo">
</p>

# Work Agents

A [Kiro CLI](https://kiro.dev/docs/cli/) v3 agent system made up of twelve specialised
engineering agents and an orchestrator that routes each task to the right one.

## Requirements

To use this project you need Kiro CLI v3 and [uv](https://docs.astral.sh/uv/) (Python
3.13), which manages the Python environment of every available tool. If you want to
develop your own version of the project, you also need `make` to run the Makefile
targets and Node.js with `npx` to run Prettier.

## Usage

All configuration is managed through the `config.toml` file, which you must fill in with
the appropriate credentials. Once it is ready, you can start the Kiro system with the
following steps:

```bash
cp config.toml.example config.toml   # gitignored; may hold secrets
kiro-cli chat --agent orchestrator --v3
```

Routing rules: [routing.md](.kiro/orchestration/routing.md). Permissions are set per
agent in `.kiro/agents/`.

## Ralph Loop

Autonomous, time-budgeted development: implement first, then verify with the time left.

```bash
.kiro/skills/ralph-loop/ralph.sh --time 3h "Implement user auth with JWT and tests"
```

For short interactive tasks, `.kiro/skills/ralph-loop/ralph-session.sh start "<prompt>"`
keeps the current session iterating through a Stop hook instead.
