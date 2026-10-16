# Ctxbudget

Approximate context-token budgeting for the Kiro CLI agent system in this repository.
Measures what every agent pays on every request, what activating each skill costs, and
which always-on files are worth compressing first, so that a change to `.kiro/` can have
a metric attached and a gate that catches a regression.

`ctxbudget` measures quantities; `driftcheck` validates structure. This tool reports
rather than asserts: an unresolvable resource is counted as zero and named in the
report, not failed. The `file://` and `skill://` glob resolution in `resolve.py`
deliberately duplicates `driftcheck/checks/agents.py`, because tools share no runtime
code, so the two can disagree about glob semantics. `driftcheck` owns the verdict.

## Relative versus absolute: read this before quoting a number

The backend is `tiktoken` with the `o200k_base` encoding. That is **not** the tokenizer
Anthropic bills on, and no exact backend exists here (no API key, so no ground truth).

| Figure                                | Trustworthy?                                           |
| ------------------------------------- | ------------------------------------------------------ |
| Before/after **delta** on a file      | Yes. tiktoken is deterministic.                        |
| **Ranking** of files by weighted cost | Yes, within the approximation error.                   |
| **Absolute** baseline of an agent     | No. Indicative even once calibrated (see Calibration). |
| Percentage of a real context window   | No. The unmeasurable remainder is excluded.            |

Delta tracking is the primary job: prove a compression removed tokens, and gate against
a regression. Never use an absolute total to claim a share of the context window.
`bytes / 4` is not an acceptable shortcut either: bytes-per-token across the always-on
files ranges from 3.94 to 5.81 and reorders the ranking.

## Requirements

Python 3.13 and [uv](https://docs.astral.sh/uv/). `tiktoken` is pinned exactly and
downloads its BPE table on first use, so the first run needs network access; later runs
are offline. Development targets are in [`tools/tool.mk`](../tool.mk) and the root
[`Makefile`](../../Makefile).

## Usage

```bash
# Measure and write the Markdown report (default: tmp/context-budget-report.md)
uv run --project tools/ctxbudget ctxbudget report
make context-budget

# Same figures as JSON, to stdout
uv run --project tools/ctxbudget ctxbudget report --format json --output -

# Gate against the recorded budget (exits 1 while none is recorded)
make context-budget-check

# Re-record the budget deliberately, after an intended change
uv run --project tools/ctxbudget ctxbudget check --write-budget
```

`report` writes to a file by default so that a report does not flood an agent's context.

| Subcommand  | Purpose                                                      |
| ----------- | ------------------------------------------------------------ |
| `report`    | Measure the tree and write the report.                       |
| `check`     | Compare against `.kiro/context-budget.json`, exit 1 if over. |
| `calibrate` | Record a correction factor from a `/context show` reading.   |

Run `ctxbudget <subcommand> --help` for the options. Shared: `--root`, `--verbose`,
`--budget` (default `.kiro/context-budget.json`).

## Cost model

| Class                                                | Loaded when          | Counted as                                                      |
| ---------------------------------------------------- | -------------------- | --------------------------------------------------------------- |
| `prompt: file://…`                                   | always, that agent   | full file, resolved against the config's directory              |
| `file://` resource                                   | always, that agent   | full file, root-relative, glob-expanded, deduplicated           |
| `.kiro/steering/*.md`                                | always, every agent  | full file, once, by workspace auto-load                         |
| `skill://` resource                                  | startup              | YAML frontmatter only (`name` + `description`)                  |
| `SKILL.md` body                                      | on activation        | body with frontmatter removed                                   |
| `references/**`                                      | only when read       | upper bound, separate, behind `--with-references`, never summed |
| `knowledgeBase` entry                                | only when searched   | name + description only                                         |
| agent JSON `permissions` / `tools` / `toolsSettings` | never as prompt text | excluded                                                        |

- **`baseline(agent)`** is prompt + deduplicated `file://` resources + auto-loaded
  steering + skill frontmatter + knowledge-base metadata: the floor paid on every
  request of every session with that agent, and the figure a reduction programme moves.
- **`activation(skill)`** is the one-off cost of the SKILL.md body. The reference upper
  bound is reported beside it and never added: references are read selectively.
- The per-file table ranks by weighted total (tokens × agents loading the file), the
  order in which a reduction backlog should be worked.

Two resolution rules were observed rather than assumed. Steering reaches every session,
subagents included, by workspace auto-load, so no agent declares it in `resources` (a
declaration would risk counting it twice). A `resources` entry resolves against the
workspace root; only `prompt` resolves against the config file's directory. One
observation is deliberately not modelled: that every skill description in the repository
is injected, not only the declared ones. If true, the `skill_fm` column understates
every floor; the report footer says so.

## Calibration

No calibration is recorded in this repository, so reports print `uncalibrated`.
`calibrate` makes no network call; the ground truth is a figure read by hand from Kiro
CLI's `/context show`, which reports each resource group as a percentage of the window.

```bash
# One observation; the window comes from the agent's declared model
uv run --project tools/ctxbudget ctxbudget calibrate \
    --agent orchestrator --context-files-pct 2.1

# Several, from a file: {"observations": [{"agent": "...", "context_files_pct": 1.4}]}
uv run --project tools/ctxbudget ctxbudget calibrate --observations obs.json

# Print the derived factor without writing it
uv run --project tools/ctxbudget ctxbudget calibrate --agent orchestrator \
    --context-files-pct 2.1 --dry-run
```

What the factor means and where it stops being valid:

- **Pass the `Agent files` percentage only.** That group covers what `resources`
  declares (`file://` resources, skill frontmatter, knowledge-base metadata), not the
  prompt or the auto-loaded steering. The factor is `observed / Σ declared resources`,
  not `observed / baseline`; dividing by the full baseline gives a wrong factor, and can
  flip the direction.
- **The window is a property of the model.** `--window` defaults to the window of the
  observed agent's `model`, from `MODEL_WINDOWS` in `windows.py`. A model missing from
  the table is an error demanding `--window`, never a default, because a wrong window
  scales the factor by the same error and nothing downstream can detect it.
- **A reading is a band, not a point.** `/context show` prints one decimal, which at a
  1M window is worth 1,000 tokens, so the factor is stored with `factor_low` and
  `factor_high` and never quoted more precisely than the reading.
- **Aggregate only.** The per-file figures do not reconcile with any single factor (a
  spread far wider than rounding explains, and not explained by per-file overhead), so
  no per-file correction is supportable. Applying the factor to the full baseline
  extrapolates it to the prompt and steering, which no observation reaches.

The factor is stored with its date, agents, window, basis, caveats and tiktoken version
in `.kiro/context-budget.json` under `calibration:*` keys, next to the figures it
corrects, and every report footer repeats it with its caveats.

## The recorded budget

`.kiro/context-budget.json` is not committed, and `check` exits 1 without it; that is
why `make context-budget-check` is outside `make all` and CI. Recording one with
`check --write-budget` and adding the target back enables a context-growth gate. The
file is flat, sorted JSON so that a one-figure change is a one-line diff:

```json
{
  "agent:senior-developer": 7994,
  "skill:reviewing-code": 2387,
  "meta:backend": "tiktoken/o200k_base",
  "meta:tiktoken_version": "0.13.0"
}
```

`check` exits 1 when a recorded figure is exceeded by more than `--tolerance-pct`
(default 2, absorbing whitespace reformatting or a tokenizer patch release). It warns,
without failing, when the budget was recorded under a different backend or tokenizer
version, or when a measured agent or skill is absent from it.
