# Ctxbudget

Approximate context-token budgeting for the Kiro CLI agent system in this repository.
Measures what every agent pays on every request, what activating each skill costs, and
which always-on files are worth compressing first. It exists so that every later change
to `.kiro/` has a metric attached and a gate that catches a regression.

`ctxbudget` measures quantities. `driftcheck` validates structure. A pass/fail assertion
about the shape of the agent system belongs in `driftcheck`, and this tool reports
instead of asserting — an unresolvable resource is counted as zero and named in the
report, not failed.

## Relative versus absolute: read this before quoting a number

The backend is `tiktoken` with the `o200k_base` encoding. That is **not** the tokenizer
Anthropic bills on, and there is no exact backend: this repository has no Anthropic API
key, so no network path to ground truth exists. The consequence is the single most
important thing to understand about the output.

| Figure                                | Trustworthy?                                                 |
| ------------------------------------- | ------------------------------------------------------------ |
| Before/after **delta** on a file      | Yes. tiktoken is deterministic.                              |
| **Ranking** of files by weighted cost | Yes, within the approximation error.                         |
| **Absolute** baseline of an agent     | No. Indicative even once calibrated — see Calibration below. |
| Percentage of a real context window   | No. The unmeasurable remainder is excluded.                  |

**Delta tracking is the tool's primary job.** Use it to prove a compression actually
removed tokens and to gate against a regression. Do not use an absolute total to claim a
share of the context window, calibrated or not: the one calibration recorded so far
reconciles in aggregate and does not reconcile per file.

Two things that were measured and are therefore settled rather than open:

- `bytes / 4` is not an acceptable shortcut. Bytes-per-token across the always-on files
  in this repository ranges 3.94 to 5.81, which **reorders** the cost ranking — Markdown
  tables padded by Prettier tokenize cheaply and would flatter themselves to the top of
  a reduction backlog.
- `o200k_base` versus `cl100k_base` differ by at most 1.1% on these files, well inside
  the approximation error the reports already declare. The encoding choice is not worth
  revisiting.

## Requirements

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) (package manager)

`tiktoken` is pinned exactly. It downloads its BPE table on first use and caches it, so
the first run needs network access; every later run is offline.

## Setup

```bash
cd tools/ctxbudget
make setup
```

## Usage

```bash
# Measure and write the Markdown report (default: tmp/context-budget-report.md)
uv run --project tools/ctxbudget ctxbudget report
make context-budget

# Same figures as a JSON payload, to stdout
uv run --project tools/ctxbudget ctxbudget report --format json --output -

# Gate against the committed budget
make context-budget-check

# Re-record the budget deliberately, after an intended change
uv run --project tools/ctxbudget ctxbudget check --write-budget
```

### Subcommands

| Subcommand  | Purpose                                                      |
| ----------- | ------------------------------------------------------------ |
| `report`    | Measure the tree and write the report.                       |
| `check`     | Compare against `.kiro/context-budget.json`, exit 1 if over. |
| `calibrate` | Record a correction factor from a `/context show` reading.   |

Shared options: `--root`, `--verbose`.

| Option                | Subcommand  | Description                                                             |
| --------------------- | ----------- | ----------------------------------------------------------------------- |
| `--output`            | `report`    | Destination; `-` for stdout. Default `tmp/context-budget-report.<ext>`. |
| `--format md\|json`   | `report`    | Output format.                                                          |
| `--with-references`   | `report`    | Also measure an upper bound over each skill's `references/**`.          |
| `--budget`            | all         | Budget file. Default `.kiro/context-budget.json`.                       |
| `--tolerance-pct`     | `check`     | Overshoot allowed before failing. Default 2.                            |
| `--write-budget`      | `check`     | Re-record the budget instead of gating against it.                      |
| `--agent`             | `calibrate` | Agent that was observed.                                                |
| `--context-files-pct` | `calibrate` | Percentage of the window its `Agent files` group filled.                |
| `--observed-tokens`   | `calibrate` | Observed token count, when the figure is already in tokens.             |
| `--window`            | `calibrate` | Window the percentage refers to. Default: per declared model.           |
| `--observations`      | `calibrate` | JSON file of several observations.                                      |
| `--dry-run`           | `calibrate` | Print the derived factor without writing it.                            |

`report` writes to a file rather than stdout by default, per the cross-tool convention
that a report must not flood an agent's context window.

## Cost model

Per artifact class, and the reasoning for each:

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

Two metrics come out of it:

- **`baseline(agent)`** = prompt + Σ deduped `file://` + Σ auto-loaded steering + Σ
  skill frontmatter + Σ knowledge-base metadata. This is the floor paid on **every
  request of every session** with that agent, and it is the figure a reduction programme
  is trying to move.
- **`activation(skill)`** = SKILL.md body minus frontmatter — a one-off cost paid when
  the skill is activated. `refs_upper_bound(skill)` is reported next to it and **never
  added to it**: reference files are read selectively, so summing them would report a
  cost no session pays.

The per-file table is the one that drives the work. A token removed from a file that
thirteen agents load is worth thirteen, so rows are ranked by weighted total rather than
by size. `Loads` exceeds `Agents` only when a single agent pays for the same file twice,
which no resolution rule in force does today.

## How steering and resources actually reach a session

Both questions the earlier cost model hedged are now settled by observation, and the
model no longer offers a switch for either.

**Steering arrives by workspace auto-load.** Every `.kiro/steering/*.md` file is
injected into every session, subagent sessions included, regardless of what an agent's
`resources` array lists. Two independent observations: a live orchestrator session
received all three files as injected workspace rules while its `resources` entries for
them resolved to nothing, and a `software-architect` subagent session received all three
while its config declared two. Consequently no agent declares steering in `resources`
any more — a correct declaration would risk paying roughly 2,734 tokens twice per
session, and deleting it makes the cost model unambiguous. Steering is counted once per
agent, as `steering_auto`.

**A `resources` entry resolves against the workspace root.** `file://` and `skill://`
alike. Only the `prompt` field resolves against the agent config file's own directory,
which `custom-agents/configuration-reference.md` states verbatim under "File URI path
resolution". This module once resolved `file://` resources config-relative, which is the
more damaging half of the same bug: `file://../orchestration/routing.md` names a real
file when joined to `.kiro/agents/`, so 16,803 tokens were counted as always-on while
Kiro resolved them outside the repository and loaded nothing.

The related observation — that all 33 skill descriptions were injected rather than only
the declared ones — remains **unverified** and is deliberately **not** modelled. It is
reported in the footer, because if it holds, the `skill_fm` column understates every
agent's floor.

## Calibration without an API key

`calibrate` makes no network call and none is possible. The ground truth is a figure a
human reads off Kiro CLI's own `/context show`, which reports each resource group as a
percentage of the context window — computed by the real tokenizer over the real
assembled prompt.

```bash
# One observation; the window comes from the agent's declared model
uv run --project tools/ctxbudget ctxbudget calibrate \
    --agent orchestrator --context-files-pct 2.1

# Several, from a file
uv run --project tools/ctxbudget ctxbudget calibrate --observations obs.json
```

```json
{
  "observations": [
    { "agent": "orchestrator", "context_files_pct": 2.1 },
    { "agent": "senior-developer", "context_files_pct": 1.4 }
  ]
}
```

### What the percentage must cover

Pass the percentage of the **`Agent files`** group, and nothing else. That group covers
what an agent's `resources` array declares — `file://` resources, skill frontmatter and
knowledge-base metadata — and covers neither the agent prompt nor the three auto-loaded
`.kiro/steering/*.md` files, which arrive as injected workspace rules on a separate
channel and are not listed under it. The factor is therefore
`observed / Σ declared resources`, not `observed / baseline`.

That distinction is not pedantic. Dividing a 21,000-token observation by the
orchestrator's full 23,640-token baseline yields 0.888, which reads as "tiktoken
overestimates by 11%"; dividing it by the 19,635 tokens the observation actually covers
yields 1.07, and the true direction is that tiktoken **under**counts. An earlier
revision of this document instructed the opposite and was wrong.

### The window is a per-model property

`--window` defaults to the window the observed agent's `model` field implies, read from
a table transcribed from `models.md` in the vendored Kiro docs. Opus 5 and Sonnet 5 ship
1M; Haiku 4.5, GLM-5 and Opus 4.5 ship 200K. An agent declaring a model the table does
not carry is an error demanding `--window`, never a default: the percentage is
multiplied by the window, so a 200K constant applied to a 1M session produces a factor
five times too small and nothing downstream can detect it.

### Aggregate only, and a band rather than a point

`/context show` prints one decimal. At a 1M-token window that decimal is worth 1,000
tokens, so a reading pins the aggregate to ±500 tokens and pins an individual file to
nothing useful. The calibration path accepts per-agent aggregates only, and records
`calibration:factor_low` and `calibration:factor_high` alongside the midpoint so the
factor is never quoted as more precise than the reading behind it.

Two caveats are stored with every factor and reprinted wherever it is reported:

- The basis is the declared resources, so applying the factor to a full baseline
  extrapolates it to the prompt and the steering files, which no observation has
  reached.
- The per-file figures do not reconcile with any single factor. On the orchestrator
  observation, `tools/TOOLS_OVERVIEW.md` implies 0.89, `delegation-lifecycle.md` 1.16
  and `routing.md` 1.41 — a spread far wider than the ±500-token rounding explains.

### What reconciles and what does not

Both candidate explanations for that spread were checked once, and neither closes it:

- **Per-file framing overhead.** Ruled out. No `displayed = tokens × f + c` fits all
  three rows inside display precision: `routing.md` (0.8%) and `delegation-lifecycle.md`
  (0.9%) differ by at most 2,000 displayed tokens over 2,079 estimated ones, which
  forces `f ≤ 0.96`; at that slope `TOOLS_OVERVIEW.md` needs `c ≤ 273` while
  `routing.md` needs `c ≥ 2,031`. A positive overhead would also lift the smallest file
  most, and `TOOLS_OVERVIEW.md` is the one sitting below 1.0.
- **The displayed percentage may not be a plain `tokens / window`.** Not ruled out, and
  not settleable locally. A second, weaker signal points the same way: the three file
  rows sum to 2.0% while the total reads 2.1%, leaving at most ~1,500 tokens for 36
  skill frontmatters this tool measures at 2,770.

The aggregate at 1.07 is the only quantity that reconciles, and it does so within the
reading's own ±500 tokens. Treat it as indicative: the direction — tiktoken undercounts
what Claude charges — is solid, the magnitude is plausible, and no per-file correction
is supportable.

Everything is stored in `.kiro/context-budget.json` under `calibration:*` keys, together
with the observation date, the agents it came from, the window, the basis, the caveats
and the tiktoken version that produced the estimate. Storing it next to the figures it
corrects is deliberate: a factor in a separate file would drift away from the
measurement it applies to. Every report footer then names the factor, its band, its
basis and its caveats, or says `uncalibrated`.

## The committed budget

`.kiro/context-budget.json` is a flat, sorted JSON document so that a one-figure change
is a one-line diff:

```json
{
  "agent:senior-developer": 7994,
  "skill:reviewing-code": 2387,
  "meta:backend": "tiktoken/o200k_base",
  "meta:tiktoken_version": "0.13.0"
}
```

`check` exits 1 when any recorded figure is exceeded by more than `--tolerance-pct`
(default 2, which absorbs the jitter of a whitespace reformat or a tokenizer patch
release). It warns, without failing, when the budget was recorded under a different
backend or tokenizer version, and when a measured agent or skill is absent from the
budget.

## Extension seam

There is exactly **one** seam, and it is the `MetricFamily` protocol in `types.py`
together with the `EXTRA_METRICS` tuple in `model.py`:

```python
class DuplicationSignal:
    name = "Cross-file duplication"

    def rows(self, measurement: Measurement) -> tuple[MetricRow, ...]: ...


EXTRA_METRICS = (DuplicationSignal(),)
```

A family receives a **finished** `Measurement`, so it reaches every resolved artifact
and every token count without editing `resolve.py` or `count.py`, and `report.py`
renders whatever it returns as one extra section. That is enough for the metric families
already foreseen — duplication detection, directive inventories, description-overlap
signals.

One seam only, on purpose. A family that needs more than a finished measurement is a
different tool, and a second seam would invite speculative abstraction into modules
whose figures are contractual.

## Deliberate duplication with driftcheck

The `file://` and `skill://` glob-resolution logic in `resolve.py` restates
`driftcheck/checks/agents.py` (`missing_resources`, `_skill_uri_resolves`).
`TOOLS_OVERVIEW.md` states that tools share no runtime Python, so the copy is the price
of that boundary rather than an oversight.

The consequence is recorded so it is not discovered by surprise: **the two copies can
now disagree about glob semantics** — which wildcards are recognised, how a
home-directory or bare-name `skill://` target is treated, and whether a glob matching
nothing is an error. `driftcheck` owns the pass/fail verdict on resolution; this module
only needs a set of paths to count, so it degrades to "counts nothing" where the other
errors.

## Development

```bash
make lint        # ruff format + ruff check --fix + isort
make code-check  # complexipy + mypy (strict)
make test        # pytest
make all         # setup + clean + lint + code-check + test
```
