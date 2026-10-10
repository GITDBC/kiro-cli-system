# Driftcheck

Structural drift detection for the Kiro CLI agent system in this repository. Validates
that agent configs, skills, steering files, prompts and hooks stay consistent with each
other.

## Requirements

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) (package manager)

## Setup

```bash
cd tools/driftcheck
make setup
```

## Usage

```bash
# Validate the enclosing repository
uv run --project tools/driftcheck driftcheck

# Same thing through the repository Makefile
make drift-check

# Validate another tree (used by the test suite)
driftcheck --root /path/to/repo
```

### CLI options

| Option   | Description                                                                      |
| -------- | -------------------------------------------------------------------------------- |
| `--root` | Repository root to validate (default: nearest ancestor with `.kiro/` + `tools/`) |

Exit code is 1 when any ERROR was reported, 0 otherwise. Warnings never fail the run.

## Checks

Twenty-seven checks run in a fixed order; the order is the console output order.

| Section                            | Module                     | Severity        |
| ---------------------------------- | -------------------------- | --------------- |
| Resource references                | `checks/agents.py`         | ERROR           |
| Resource path form                 | `checks/agents.py`         | ERROR           |
| Agent registry consistency         | `checks/agents.py`         | ERROR / WARNING |
| Legacy v2 agent config fields      | `checks/agents.py`         | ERROR           |
| permissions.rules validation       | `checks/permissions.py`    | ERROR           |
| tools tag validation               | `checks/permissions.py`    | ERROR           |
| Skill routing coverage             | `checks/skills.py`         | WARNING         |
| Pattern-to-resources wiring        | `checks/skills.py`         | ERROR / WARNING |
| State registry integrity           | `checks/state.py`          | ERROR           |
| Memory store framework boundary    | `checks/state.py`          | ERROR           |
| Prompt file references             | `checks/prompts.py`        | ERROR           |
| Hook script path references        | `checks/hooks.py`          | ERROR           |
| Git-safety hook coverage           | `checks/hooks.py`          | ERROR / WARNING |
| Steering/skill content duplication | `checks/steering.py`       | WARNING         |
| Orchestrator-only file placement   | `checks/steering.py`       | ERROR           |
| Orchestration file reachability    | `checks/steering.py`       | ERROR           |
| Orphan prompt files                | `checks/prompts.py`        | WARNING         |
| Orphaned skill reference files     | `checks/skills.py`         | WARNING         |
| Model governance (Anthropic-only)  | `checks/agents.py`         | ERROR / WARNING |
| Workspace model defaults           | `checks/agents.py`         | ERROR / WARNING |
| routing.md cost label accuracy     | `checks/agents.py`         | WARNING         |
| Numbered markdown headers          | `checks/steering.py`       | WARNING         |
| Stale agent-named reference files  | `checks/skills.py`         | WARNING         |
| Stale skill-name mentions          | `checks/skills.py`         | WARNING         |
| Review recall suppression          | `checks/prompt_quality.py` | WARNING         |
| Agent prompt scope statements      | `checks/prompt_quality.py` | WARNING         |
| Known cross-file contradictions    | `checks/prompt_quality.py` | WARNING         |

A check that raises is reported as an ERROR naming it, and the other twenty-six still
run. One malformed agent config therefore never aborts a run.

`Resource references` resolves every `resources` entry — `file://` and `skill://` alike
— against the repository root, which is how Kiro resolves them, reporting every
unresolvable entry of a config rather than only the first. A glob is satisfied by one
match, so `skill://.kiro/skills/*/SKILL.md` is valid while a wildcard matching nothing
is not. Home-directory and bare-name `skill://` forms are not paths into this tree and
are left alone.

`Resource path form` rejects a `file://` resource written relative to the config file,
such as `file://../steering/COMMON.md`. That form fails silently and is why thirteen
broken configs once passed green: it names a real file when joined to `.kiro/agents/`,
so an existence check accepts it, while Kiro joins it to the workspace root, lands
outside the repository and loads nothing. The `prompt` field is out of scope — Kiro
documents it as resolved against the config file's own directory, so the config-relative
form is correct there and only there.

`Legacy v2 agent config fields` rejects the field shapes the v3 agent engine removed:
`allowedTools`, an embedded `hooks` key, and per-tool `toolsSettings` blocks together
with the settings they held (`allowedCommands`, `deniedCommands`, `allowedPaths`,
`deniedPaths`, `autoAllowReadonly`, `denyByDefault`), matched at both the block and the
setting level. It is an ERROR because this project targets v3 only: the runtime ignores
such a field, but a maintainer reads it as authorization, so a config granting shell
access through `allowedTools` looks permissioned and is not. `toolsSettings.subagent` is
permitted — it is the one sub-block v3 keeps, and `availableAgents` / `trustedAgents`
have no `permissions.rules` equivalent.

The check is scoped to `.kiro/agents/` and deliberately not extended to the JSON
templates in skill documentation. Documentation legitimately names these fields: the
vendored kiro.dev mirror documents the 2.x shape in full, and this repository's
migration record and agent-creation reference both name the removed fields in order to
forbid them. Distinguishing a forbidding mention from a teaching one needs a per-file
allowlist, which is the drift surface the check exists to remove. An agent config is the
only place where the fields carry consequence, so that is where the gate sits. A
malformed config is skipped here, since `Resource references` owns unparseable JSON.

`Pattern-to-resources wiring` asserts that a skill named in a routing.md Collaboration
Patterns row next to an agent is declared in that agent's `resources`, because a custom
agent loads no skill it is not given. `ORCHESTRATOR_ONLY_SKILLS` exempts skills whose
body is exclusively meta-content.

`Orchestrator-only file placement` guards the always-on context budget from both
directions. `routing.md` and `delegation-lifecycle.md` live in `.kiro/orchestration/`
rather than `.kiro/steering/` because Kiro CLI loads every steering file into every
session, subagent sessions included, regardless of an agent's `resources`: a probe
measured their roughly 1,118 lines filling an estimated 70-75% of a specialist's context
on every dispatch, for content no specialist acts on. The check therefore errors if
either file reappears under `.kiro/steering/`, and equally if the orchestrator stops
naming it in `resources`, which is now the only route by which it reaches any session.
Neither failure is visible at runtime, which is what the check substitutes for.

`Orchestration file reachability` covers the rest of that directory.
`.kiro/orchestration/` holds material the orchestration layer owns, and a file there
arrives in a session one of two ways: an agent declares it in `resources`, or an
always-on file names it and sends a reader there on demand. Always-on means a
`.kiro/steering/` file, which Kiro loads into every session, or any file some agent
declares as a `file://` resource. A file satisfying neither is content nothing can
arrive at, and no other check notices — `Orphaned skill reference files` walks a skill's
own `references/` directory and never looks here. So deleting one prose pointer silently
strands a whole file, which is how `orchestration-rationale.md` and
`preflight-report-format.md` are held: by pointer alone. ERROR rather than WARNING for
the same reason as the placement check above — the loss is invisible at runtime, which
is what makes it a defect rather than a smell. A file naming its own path does not vouch
for itself.

The three `checks/prompt_quality.py` sections validate the instruction artifacts against
documented Claude prompting anti-patterns; the source pages are vendored under
`.kiro/skills/claude-prompting-reference/references/`. They are deterministic, external
checks by design: the same guidance says to delete prompt-level instructions that tell a
model to re-verify its own output, and names a tool-side check as the substitute. None
of them writes to a prompt.

`Review recall suppression` flags a reporting floor set by severity ("only report
high-severity issues", "be conservative", "don't nitpick") in a review-oriented artifact
that does not also state the bar. Claude Sonnet 5 and Opus 5 follow such a floor
literally: the model investigates just as deeply and then withholds findings it judges
below the stated bar, so measured recall falls while bug-finding ability is unchanged.
Two scoping decisions keep it quiet. The verbs are limited to `report`, `flag` and
`emit`, so a _fixing_ budget ("Fix `Critical` and `High` findings") is untouched — that
is a legitimate instruction and the one `reviewing-code` Step 2 gives. And the skill
surface is the curated `REVIEW_ORIENTED_SKILLS` allowlist, validated for staleness like
`DIRECT_INVOKE_SKILLS`, because "Be conservative with interpretation" in a statistics
reference is advice about reading a p-value, not an instruction to withhold findings.
Agent prompts need no allowlist — the patterns were calibrated against all of them. A
group carrying an explicit finding bar, a `finding-calibration.md` reference, or
Anthropic's own remedy of reporting everything and filtering downstream is exempt: the
threshold is then governed rather than hidden, which is the shape `reviewing-code`
carries.

`Agent prompt scope statements` requires a boundary section in the prompt of every agent
routing.md declares as a routing-YAML `- id:` entry. Those entries each carry a
`never_when` list, but routing lives with the orchestrator while the prompt is what the
specialist itself loads, so an agent invoked directly has nothing telling it to hand
work back. `## Boundaries` is the house heading; "When not to use" and "Do not use" are
accepted so a rename does not read as a regression. The orchestrator is deliberately out
of scope — it has no routing entry because it is not a delegation target. A prompt that
does not resolve is skipped rather than reported, since `Prompt file references` owns
missing prompts.

`Known cross-file contradictions` is a curated pair list, narrow on purpose and in the
spirit of `DIRECT_INVOKE_SKILLS`: a general-purpose contradiction detector over prose
would be wrong often enough to get switched off, and a disabled check protects nothing.
Each `ContradictionPair` names two files and one pattern per side, and fires only when
both are present — so the entry stops firing when either side is rewritten, instead of
needing to be deleted by hand. A pair naming a file that no longer exists is reported as
stale, the way a stale allowlist entry is. Entries are added only for contradictions
that were actually found; the seed pair is the orchestrator prompt authorising unbounded
subagent fan-out while `delegation-lifecycle.md` states four concurrent subagents as a
platform limit.

`Memory store framework boundary` asserts that `memory/` holds nothing but an empty
`state.yaml`. A framework tree is installed into other projects, so `memory/` is
per-consuming-project runtime state: its contents describe the project using the
framework, not the framework itself. Durable framework documentation therefore belongs
in a versioned location such as `docs/`, and a populated registry shipped from a
framework tree would hand every consuming project another project's decisions.

The invariant is framework-scoped, and the scope is determined from a marker the tree
already carries: a root `.gitignore` rule that ignores `memory/` contents. Its presence
is the declaration "`memory/` is framework-empty here"; its absence is the declaration
"`memory/` is mine". A consuming project's `memory/` is legitimately populated, and
tracking it requires dropping that rule — the same act that disables this check — so the
marker cannot disagree with the belief it encodes, which a separate flag or config field
could. When the rule is absent the check reports nothing at all: not a pass, not a
warning, simply an empty section, because an `OK` for a condition that was never
evaluated is misleading. Recognised spellings are `memory/`, `memory/*` and `memory/**`,
optionally anchored with a leading slash and tolerating surrounding whitespace;
commented-out lines, negations such as `!memory/state.yaml`, narrower globs such as
`memory/*.md` and other ignore sources are deliberately not recognised. The match is
narrow and documented rather than a reimplementation of gitignore semantics.

## Repository-root discovery

`paths.find_repo_root` walks upward from the module file and returns the first ancestor
containing both `.kiro/` and `tools/`. When the package is installed non-editably the
search is retried from the working directory. Nothing depends on a fixed parent depth,
so moving a module cannot silently point the checks at the wrong tree. Failure raises
`ValueError`; `--root` bypasses discovery entirely.

## Hooks

Three agent lifecycle hooks ship as console scripts, so they are linted, type-checked
and tested like the rest of the package.

| Console script                   | Event       | Wired? | Purpose                               |
| -------------------------------- | ----------- | ------ | ------------------------------------- |
| `driftcheck-hook-agent-config`   | postToolUse | No     | Validate a written agent JSON config  |
| `driftcheck-hook-state-yaml`     | postToolUse | No     | Validate `memory/state.yaml`          |
| `driftcheck-hook-refs-freshness` | agentSpawn  | Yes    | Warn when the vendored docs are stale |

`driftcheck-hook-refs-freshness` is wired on the orchestrator's `agentSpawn` event and
runs once per session. `driftcheck-hook-agent-config` and `driftcheck-hook-state-yaml`
are available, tested console scripts that are intentionally not wired as `postToolUse`
hooks: the same validation already runs at the `make drift-check` gate, and wiring them
on the unqualified `fs_write` matcher charged every file write by any agent that had
them wired — including writes unrelated to agent configs or `state.yaml` — a measured
combined cost of about 405 ms per write. They remain in the package so the capability
can be re-wired selectively if a future need justifies the per-write cost.

Invoked as `uv run --project tools/driftcheck <script>`. A hook that cannot run its
check (no repository root, unreadable event, missing dependency) warns on stderr and
exits 0. Only `driftcheck-hook-state-yaml` exits non-zero, and only when the check ran
and found a genuine violation.

## Development

```bash
make lint        # ruff format + ruff check --fix + isort
make code-check  # complexipy + mypy (strict)
make test        # pytest
make all         # setup + clean + lint + code-check + test
```
