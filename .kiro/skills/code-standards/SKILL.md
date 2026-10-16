---
name: code-standards
description: >
  Full Python code standards reference. Use when writing, reviewing, or refactoring code
  and you need detailed conventions for formatting, imports, type hints, docstrings,
  naming, testing, error handling, logging, classes, dataclasses, data processing, or
  CI/CD configuration. Loaded on demand — the summary in steering/ covers essentials.
---

# Code Standards

On-demand detail behind the always-on `.kiro/steering/code-standards-summary.md`, whose
threshold table is the single copy of every numeric limit cited below. This body covers
the most frequently violated rules; for complete code examples, the full prohibited-code
list, and less-common categories, load `references/full-standards.md`.

## Language and Version

- **Python 3.13** exclusively (version pin in the threshold table)
- Package manager: **uv** (build and dependency resolution)
- Dependencies pinned to exact versions (no open ranges)

## Formatting and Style (Ruff)

- Line length and indentation per the threshold table · Quotes: **double** (`"`)
- Line ending: **auto** · Magic trailing comma: not skipped
- Active rule categories: E (pycodestyle errors), F (pyflakes), W (warnings), PL
  (pylint), UP (pyupgrade), N (pep8-naming), B (bugbear), I (isort). Ignored: `PLC0415`
  (non-top-level imports), `N802` (non-lowercase function names), `PLR0913` (too many
  arguments), `PLR2004` (magic values).
- Required additions in any new or refreshed project config: `G` (flake8-logging-format,
  catches f-strings in logger calls) and `D100`/`D104` (module docstrings). Both enforce
  rules already mandatory below and are the only mechanical coverage available for them.

## Prohibited Code (most common)

- `datetime.utcnow()` (deprecated since 3.12) → use `datetime.now(tz=UTC)` with
  `from datetime import UTC, datetime`
- `from __future__ import annotations`
- `logging.warn()` → use `logging.warning()`
- `distutils` → use `setuptools` or `build`
- Invalid escape sequences (`"\d"`) → use raw strings `r"\d"`

The remaining removed/deprecated modules and APIs (Python 3.13 removals, `imp`,
`asynchat`, etc.) are listed in `references/full-standards.md`.

## Import Organization

Strict ordering with mandatory section headers (`# Standard libraries`, `# 3pps`,
`# Own modules`). isort: `known-first-party`: `["src"]`; section order future → stdlib →
third-party → first-party → local-folder; `combine-as-imports` and
`split-on-trailing-comma` true. Full example in `references/full-standards.md`.

## Type Hints

- Mandatory on all function signatures (parameters and return type)
- Modern types: `list[str]`, `dict[str, Any]`, `tuple[...]` · unions: `str | None`
- `Final` for constants · `Literal` for restricted values: `Literal["DL", "UL"]`
- mypy enabled with `check_untyped_defs = true`

## Docstrings

Full guide: `.kiro/skills/reviewing-code/references/python-docstrings.md`. Full worked
example in `references/full-standards.md`.

- Format: **Google Docstring** exclusively
- Content starts on the line after `"""` · docstring line limit per the threshold table
- **Module docstring mandatory** in every `.py` file, including `__init__.py`: one
  paragraph stating the module purpose, placed after the copyright header and before
  `# Standard libraries`. Ruff `D100`/`D104` catch this.
- `Returns` section mandatory, even for `None`
- No types or default values in descriptive text · examples only when usage is not
  obvious
- Identical parameters must have identical descriptions across the codebase

## Logging

- Levels: `info` main operations · `debug` details · `warning`/`error` problems
- Messages end with `.` · use lazy `%` formatting, never f-strings in logger calls (ruff
  `G004` enforces this — prose alone has not)
- **Bracketed severity tag must match the logger method**: no `[WARNING]`/`[ERROR]` text
  emitted through `logger.debug()`. Promote the call to the matching level instead of
  compensating with a tag.
- NEVER remove or modify existing logging statements; new logs may be added
- Logger configured via JSON with `RotatingFileHandler`; each pipeline defines its own
  `LOGGER_NAME`; module tags when applicable: `[INFO][MODULE] Message`

## Error Handling

- Assign message to `error_message: str`, log with `logger.error`, then
  `raise ExceptionType(error_message)`
- `ValueError` for data and configuration validations
- Specific exceptions in `except` blocks (never generic `except Exception`)
- `raise ... from error` to preserve exception chains

## Constants and Configuration

- `Final` with explicit type, `UPPER_SNAKE_CASE`; class constants as `Final` attributes
- Immutable tuples preferred over lists for constant collections

## Dataclasses

- `@dataclass(frozen=True)` for immutable configurations
- Docstring with `Attributes` section; validation in `__post_init__` when needed
- Full example in `references/full-standards.md`.

## Naming Conventions

| Element       | Convention         | Example                                   |
| ------------- | ------------------ | ----------------------------------------- |
| Modules       | `snake_case`       | `etl_orchestrator.py`                     |
| Classes       | `PascalCase`       | `DemandForecastModel`                     |
| Functions     | `snake_case`       | `load_config_data`                        |
| Constants     | `UPPER_SNAKE_CASE` | `LOGGER_NAME`                             |
| Variables     | `snake_case`       | `df_config_data`                          |
| DataFrames    | `df_` prefix       | `df_input`, `df_config_data`              |
| Configuration | `Config` suffix    | `SaveConfig`, `ETLPipelineConfig`         |
| Loaders       | `Loader` suffix    | `ConfigDataLoader`, `ParquetConfigLoader` |

## Classes

Pattern: `ClassConfig` (constants) → `Class(ClassConfig)` (logic);
`logger: logging.Logger | None = None` as optional parameter; input validation at
constructor start. Full example in `references/full-standards.md`.

## Data Processing and Performance

- **Polars** for all production data processing; Pandas only when strictly necessary as
  an intermediate step
- `LazyFrame` (`scan_parquet`) for read optimization · NumPy for pure numerical
  computation
- Avoid: row-by-row operations, unnecessary format conversions, expensive objects inside
  loops, unnecessary DataFrame copies

## Numerical Safety and Data Integrity

Defect classes that recurred across independent reviews of a large production codebase.
Before/after snippets, rationale, and enforcement notes in
`references/full-standards.md`.

| Rule                                                                                                                                                                              | Ruff catches it |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| **Guard every division** whose denominator is runtime data: `pl.when(denom != 0).then(num / denom).otherwise(None)`, NumPy `np.where(denom > 0, num / denom, default)`            | No              |
| **Never `value or default`** for optional numeric/boolean fields — use `default if value is None else value`; `or` silently discards `0`, `0.0`, `""`, `False`                    | No              |
| **Log row counts around joins and row-dropping filters** on any path feeding a report metric, SLA evaluation, or model input: `logger.debug("... %d -> %d rows.", before, after)` | No              |
| **Sentinel values carry an explicit dtype**: `pl.lit(SENTINEL, dtype=pl.Float64)` — never rely on `vertical_relaxed`/`diagonal_relaxed` concat to upcast                          | No              |
| `.fill_nan()` / `.fill_null()` do **not** substitute for a zero-guard: `x / 0` yields `inf`, not `NaN`                                                                            | No              |

## I/O and Configuration Boundaries

| Rule                                                                                                                                                                                 | Ruff catches it |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| **External key access raises `ValueError`**: wrap JSON/dict config lookups in `try/except KeyError` and `raise ValueError(error_message) from error`, naming the key and source file | No              |
| **Remote I/O retries and logs before raising**: S3, HTTP, and subprocess calls use a capped-backoff retry helper and `logger.error` before any `raise` or re-raise                   | No              |
| **Never create directories or perform I/O at import time** — side effects belong in an explicit initialisation call                                                                  | No              |

None of the rules in these two tables is lint-checkable, so each is also a mandatory
item on the reviewer checklist in `.kiro/skills/reviewing-code/SKILL.md`.

## Testing

- Framework: **pytest** with `pytest-order` and `pytest-cov`
- Coverage floor per the threshold table (SonarQube gate) · reports in `coverage.xml`
- Structure: `tests/` mirroring `src/` · `test_*.py` files · `Test*` classes · `test_*`
  functions · pytest fixtures (not `setUp`/`tearDown`) · `unittest.mock` or
  `pytest-mock`
- Custom markers: `@pytest.mark.training`, `@pytest.mark.inference` · `session` scope
  for expensive fixtures · `assert_frame_equal` for DataFrames · options
  `--strict-markers`, `--tb=short`

## Security

- **Bandit**: `bandit -r src/ -ll` · **licensecheck** for license verification
- Credentials never in source code (use external JSON files or secret managers); auth
  tokens/secrets never logged, even at debug level

## Engineering Principles

The principles in `code-standards-summary.md` apply, plus **strategic over tactical**:
invest 10–20% of development time in design improvements.

## References

For `__init__.py` module rules, pipeline structure, API design guidance, quality gates
(Complexipy/Deadcode/SonarQube), commit message conventions, documentation tooling,
change-comment format, CI/CD stages, editor rulers, reproducibility (seeds, pinning),
and notebook rules, load `references/full-standards.md`. That file also holds the
before/after snippets, review evidence, and enforcement mapping for the Numerical Safety
and I/O Boundary rules above.
