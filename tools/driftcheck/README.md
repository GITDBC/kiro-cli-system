# Driftcheck

Structural drift detection for the Kiro CLI agent system in this repository. Validates
that agent configs, skills, steering files, prompts and hooks stay consistent with each
other. Repository maintenance tool: it validates `.kiro/` and `memory/`, not user code.

## Requirements

Python 3.13 and [uv](https://docs.astral.sh/uv/). Development targets are in
[`tools/tool.mk`](../tool.mk) and the root [`Makefile`](../../Makefile).

## Usage

```bash
# Validate the enclosing repository
uv run --project tools/driftcheck driftcheck
make drift-check                      # same, through the root Makefile

# Validate another tree
uv run --project tools/driftcheck driftcheck --root /path/to/repo
```

`--root` defaults to the nearest ancestor holding both `.kiro/` and `tools/`; discovery
walks upward from the module file, then from the working directory for a non-editable
install, and fails with `ValueError` if neither finds one.

Exit code is 1 when any ERROR was reported, 0 otherwise. Warnings never fail the run.

## Checks

The authority is `CHECKS` in [`driftcheck/registry.py`](driftcheck/registry.py): its
order is the console output order, and this table summarises it. Where the two disagree,
the registry is right. There are 27 checks.

A check that raises is reported as an ERROR naming it, and the remaining checks still
run, so one malformed agent config never aborts a run.

| Section                            | Module                     | Severity        | Purpose                                                                                                                                |
| ---------------------------------- | -------------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Resource references                | `checks/agents.py`         | ERROR           | Every `resources` entry resolves (root-relative).                                                                                      |
| Resource path form                 | `checks/agents.py`         | ERROR           | No `file://` resource written relative to the config file.                                                                             |
| Agent registry consistency         | `checks/agents.py`         | ERROR / WARNING | Every agent is listed as `subagent/<name>` in the orchestrator `tools`.                                                                |
| Legacy v2 agent config fields      | `checks/agents.py`         | ERROR           | No field shapes the v3 engine removed.                                                                                                 |
| permissions.rules validation       | `checks/permissions.py`    | ERROR           | Capabilities, effects and patterns are documented ones.                                                                                |
| tools tag validation               | `checks/permissions.py`    | ERROR           | `tools` entries are documented tags.                                                                                                   |
| Skill routing coverage             | `checks/skills.py`         | WARNING         | Each skill has a Collaboration Patterns row in `orchestrator.md`.                                                                      |
| Pattern-to-resources wiring        | `checks/skills.py`         | ERROR / WARNING | A pattern's skill is declared by the agent it names.                                                                                   |
| State registry integrity           | `checks/state.py`          | ERROR           | `memory/state.yaml` parses and respects the entry cap.                                                                                 |
| Memory store framework boundary    | `checks/state.py`          | ERROR           | `memory/` holds only an empty `state.yaml` template.                                                                                   |
| Prompt file references             | `checks/prompts.py`        | ERROR           | Every agent `prompt` file exists.                                                                                                      |
| Hook script path references        | `checks/hooks.py`          | ERROR           | Hook files: `v1` schema, valid trigger and matcher, scripts exist.                                                                     |
| Git-safety hook coverage           | `checks/hooks.py`          | ERROR / WARNING | A `PreToolUse` hook matches the shell tools of every agent.                                                                            |
| Steering/skill content duplication | `checks/steering.py`       | WARNING         | Steering does not reproduce a skill body.                                                                                              |
| Orchestrator-only file placement   | `checks/steering.py`       | ERROR           | The orchestrator prompt keeps its routing and delegation sections; nothing orchestrator-only sits in steering or dispatcher resources. |
| Docs file reachability             | `checks/steering.py`       | ERROR           | Every `docs/` file can reach a session.                                                                                                |
| Orphan prompt files                | `checks/prompts.py`        | WARNING         | No prompt file lacks an agent that uses it.                                                                                            |
| Orphaned skill reference files     | `checks/skills.py`         | WARNING         | Each `references/` file is named by its `SKILL.md`.                                                                                    |
| Mirror page count                  | `checks/mirrors.py`        | WARNING         | A mirror's `.md` count equals its marker's `pages_total`.                                                                              |
| Model governance (Anthropic-only)  | `checks/agents.py`         | ERROR / WARNING | `model` is in `ALLOWED_MODELS`; `auto` is rejected.                                                                                    |
| Workspace model defaults           | `checks/agents.py`         | ERROR / WARNING | `chat.modelDefaults` keys use approved models.                                                                                         |
| Cost label accuracy                | `checks/agents.py`         | WARNING         | Orchestrator prompt's Routing Quick Lookup costs match each model's multiplier.                                                        |
| Agent engine (v3-only)             | `checks/agents.py`         | ERROR           | `chat.agentEngine` is `v3`; `ralph.sh` passes `--agent-engine v3`.                                                                     |
| Numbered markdown headers          | `checks/steering.py`       | WARNING         | No enumerated headings (`## 1. …`).                                                                                                    |
| Stale agent-named reference files  | `checks/skills.py`         | WARNING         | No `<role>-patterns.md` naming a retired agent.                                                                                        |
| Stale skill-name mentions          | `checks/skills.py`         | WARNING         | No prose naming a skill that no longer exists.                                                                                         |
| Agent prompt scope statements      | `checks/prompt_quality.py` | WARNING         | Each routed agent's prompt has a boundaries section.                                                                                   |

### Checks that need an explanation

`Resource path form` exists because the relative form fails silently: Kiro resolves a
`file://` resource against the workspace root, so `file://../steering/COMMON.md` names a
real file when joined to `.kiro/agents/` (an existence check accepts it) but loads
nothing at runtime. The `prompt` field is the exception: it resolves against the config
file's own directory.

`Legacy v2 agent config fields` rejects `allowedTools`, an embedded `hooks` key and the
`toolsSettings` field (v3 ignores all of its blocks, `subagent` included). The runtime
ignores them, but a maintainer reads them as authorization. It is scoped to
`.kiro/agents/` because documentation legitimately names the removed fields.

`Orchestrator-only file placement` and `Docs file reachability` guard the context budget
in both directions. Kiro loads every `.kiro/steering/` file into every session,
subagents included, so the routing and delegation rules live in sections of
`.kiro/prompts/orchestrator.md` (`Routing`, `Delegation`, `Harness gates`, `Conductor`),
which only the orchestrator loads. A subagent that declares no `file://` resources also
inherits its parent's, so the orchestrator declares none. The check rejects a
`routing.md` or `delegation-lifecycle.md` back in steering, a `file://` resource on any
agent that lists `subagent/<name>` tools, and an orchestrator prompt that loses one of
the four sections; the reachability check follows pointers from steering, prompts and
declared resources through the `docs/` files themselves. None of these failures is
visible at runtime, hence ERROR.

`Memory store framework boundary` applies only when the root `.gitignore` ignores the
contents of `memory/` (`memory/`, `memory/*` or `memory/**`); that rule declares
"`memory/` is framework-empty here". Without it the check reports nothing: a consuming
project's `memory/` is legitimately populated.

`Model governance` and `Cost label accuracy` read `ALLOWED_MODELS` and
`MODEL_COST_LABELS` in `checks/agents.py`. The labels match by prefix in insertion
order, so an exact id whose multiplier departs from its family (`claude-opus-5.5`,
`claude-haiku-5.5`) must precede the family entry.

## Hooks

One lifecycle hook ships as a console script, so it is linted, type-checked and tested
like the rest of the package.

| Console script                   | Event        | Wired in                 | Purpose                               |
| -------------------------------- | ------------ | ------------------------ | ------------------------------------- |
| `driftcheck-hook-refs-freshness` | SessionStart | `.kiro/hooks/hooks.json` | Warn when the vendored docs are stale |

The hook is a workspace hook, not tied to any agent, and runs once per session as
`uv run --project tools/driftcheck driftcheck-hook-refs-freshness`. It reads
`.last-sync.json` in the kiro-cli-reference skill, warns when the mirror is older than
seven days, makes no network call and always exits 0, so a session is never blocked.

Two further hooks, validating a written agent config and `memory/state.yaml` after every
file write, were removed: the same validation runs at the `make drift-check` gate, and
on an unqualified write matcher they cost about 405 ms per write, including writes
unrelated to either file.
