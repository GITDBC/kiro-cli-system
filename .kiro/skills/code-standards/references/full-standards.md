# Full Python Code Standards Reference

Detail for the `code-standards` skill: worked examples, the full prohibited-code list,
and less-common categories. Rules stated in `../SKILL.md` are not repeated here; numeric
limits live only in the threshold table of `.kiro/steering/code-standards-summary.md`.

## Prohibited Code (deprecated or removed) — remainder of the list

In addition to the items in `../SKILL.md`:

- `datetime.utcfromtimestamp()` → use `datetime.fromtimestamp(ts, tz=UTC)`
- Modules removed in 3.13: `cgi`, `cgitb`, `aifc`, `audioop`, `chunk`, `crypt`,
  `imghdr`, `mailcap`, `msilib`, `nis`, `nntplib`, `ossaudiodev`, `pipes`, `sndhdr`,
  `spwd`, `sunau`, `telnetlib`, `uu`, `xdrlib` (PEP 594), plus `lib2to3` and `2to3`
- `imp` → use `importlib`
- `asynchat`, `asyncore` → use `asyncio`
- `locale.resetlocale()` → use `locale.setlocale(locale.LC_ALL, "")`
- `typing.io`, `typing.re` (removed in 3.13)
- `pkgutil.find_loader()` → use `importlib.util.find_spec()`
- `unittest.makeSuite()`, `unittest.findTestCases()`, `unittest.getTestCaseNames()` →
  use `TestLoader`
- `shutil.rmtree(onerror=...)` → use `onexc` instead
- `calendar.January`/`February` → use `calendar.JANUARY`/`FEBRUARY`

## Import Organization — full example

```python
# Standard libraries
from pathlib import Path
from typing import Final

# 3pps
import polars as pl
import numpy as np

# Own modules
from core.configs import config as cg_proto
from src.configs import config
```

## Docstrings — full example

A copyright header alone does not satisfy the module-docstring rule, since it is a
comment block and not a docstring.

Before — copyright header, then straight into imports:

```python
# Copyright (c) 2026 ...

# Standard libraries
from pathlib import Path
```

After:

```python
# Copyright (c) 2026 ...
"""
Growth-factor computation per store.

Derives per-store growth factors from historical sales records and
exposes them for downstream demand planning.
"""

# Standard libraries
from pathlib import Path
```

```python
def load_config_data(
    date: str, logger: logging.Logger
) -> tuple[pl.DataFrame, dict[str, Any], dict[str, Any]]:
    """
    Load config data and extract partition and region info.

    Retrieves configuration data for the target date from S3 storage
    and extracts relevant partition and region mapping information.

    Args:
        date: Target date in YYYYMMDD format.
        logger: Logger instance for operation tracking.

    Returns:
        Tuple containing config DataFrame, partition info dict, and
        region info dict.
    """
```

## Logging — tag/level example

A `[WARNING]` string passed to `logger.debug()` is invisible at the default level, so
the problem it describes never reaches an operator:

```python
# Before — warning text hidden at debug level
logger.debug("[WARNING][GF] %s stores lack a growth factor.", n_missing)

# After — level matches the tag
logger.warning("[WARNING][GF] %s stores lack a growth factor.", n_missing)
```

The tag/level match needs either a regex pre-commit hook
(`logger\.debug\(.*\[(WARNING|ERROR)\]`) or the reviewer checklist.

## Dataclasses — full example

```python
@dataclass(frozen=True)
class SaveConfig:
    """
    Configuration for data persistence operations.

    Attributes:
        save_files_locally: Whether to save files to local disk.
        save_files_s3: Whether to upload files to S3.
        bucket: S3 bucket instance, required when
            save_files_s3 is True.
    """

    save_files_locally: bool
    save_files_s3: bool
    bucket: Bucket | None
```

## `__init__.py` Modules

- Explicit relative imports · `__all__: list[str]` mandatory and alphabetically sorted
- `# Own modules` section header required

## Classes — full example

```python
class SalesDataCombinerConfig:
    """Configuration constants."""
    JOIN_KEYS: Final[tuple[str, ...]] = (...)

class SalesDataCombiner(SalesDataCombinerConfig):
    """Combines online and in-store predictions."""
    def __init__(
        self,
        df_online: pl.DataFrame,
        df_store: pl.DataFrame,
        logger: logging.Logger | None = None,
    ) -> None:
        ...
```

## Defect-Class Rules — numerical safety, observability, I/O boundaries

Summary table in `../SKILL.md` (sections "Numerical Safety and Data Integrity" and "I/O
and Configuration Boundaries"). These rules exist because the same defect appeared in
many isolated reviewer contexts during a large-scale, multi-section parallel review of a
production codebase. Convergence across independent contexts is evidence the rule was
missing from the shared standards, not that one author was careless.

| Rule                         | Independent evidence                                            | Ruff                     | Enforced by              |
| ---------------------------- | --------------------------------------------------------------- | ------------------------ | ------------------------ |
| Zero-guard before division   | 16+ findings across 7 modules, in 7 independent review contexts | No                       | Review checklist item C1 |
| Explicit `None` over falsy   | 3 findings across 2 modules                                     | No                       | Review checklist item C2 |
| Row-count telemetry on joins | 12+ unguarded join sites across 4 modules                       | No                       | Review checklist item C3 |
| Sentinel dtype cast          | 2 findings in 1 module                                          | No                       | Review checklist item C4 |
| Module docstring             | No file in the primary package had one                          | Yes (`D100`/`D104`)      | Lint                     |
| Log tag matches log level    | 14+ sites across 6 modules                                      | No (regex hook feasible) | Review checklist item C5 |
| No f-strings in logger calls | Flagged in every review section; existing rule, unenforced      | Yes (`G004`)             | Lint                     |
| External key → `ValueError`  | 1 finding at the config-loading boundary                        | No                       | Review checklist item C6 |
| Remote I/O retry + log       | 2 findings at the remote-fetch boundary                         | No                       | Review checklist item C7 |
| No I/O at import time        | 1 finding at module scope                                       | No                       | Review checklist item C8 |

Finding identifiers and file paths from the source review are deliberately omitted: the
counts are what justify each rule, while the paths would embed one project's module
structure into a reusable standard.

### Zero-guard before division

`x / 0` produces `inf`, not `NaN`, so `.fill_nan()` does not catch it. An unguarded
ratio feeding a report metric, SLA threshold, or scheduling weight corrupts the output
silently: no exception, no log line, no way to notice without a debugger.

```python
# Before — inf when the denominator is zero
df_metrics = df_usage.with_columns(
    (pl.col("data_volume_mb") / pl.col("active_users")).alias("mb_per_user")
)

# After — explicit null for the undefined case
df_metrics = df_usage.with_columns(
    pl.when(pl.col("active_users") > 0)
    .then(pl.col("data_volume_mb") / pl.col("active_users"))
    .otherwise(None)
    .alias("mb_per_user")
)
```

NumPy equivalent: `np.where(denom > 0, numerator / denom, default)`, computed with
`np.errstate(divide="ignore", invalid="ignore")` when the raw division is evaluated
eagerly. A shared `_safe_divide` helper is preferable to repeating the guard.

### Explicit `None` over falsy fallback

`or` treats every falsy value as "unset", so a configured `0`, `0.0`, `""`, or `False`
is silently replaced by the default. This is a correctness bug wherever zero is a
legitimate configuration value, such as a priority weight or a growth factor.

```python
# Before — a configured priority of 0 becomes DEFAULT_PRIORITY
priority = config.get("priority") or DEFAULT_PRIORITY

# After — only an absent value falls back
raw_priority = config.get("priority")
priority = DEFAULT_PRIORITY if raw_priority is None else raw_priority
```

### Row-count telemetry on joins and row-dropping filters

An `inner` join on a mismatched key drops rows without raising. On a path feeding a
report metric, SLA evaluation, or ML training set, the loss is invisible in production
logs.

```python
# Before — silent loss
df_merged = df_usage.join(df_config, on=JOIN_KEYS, how="inner")

# After — observable loss
rows_before = df_usage.height
df_merged = df_usage.join(df_config, on=JOIN_KEYS, how="inner")
logger.debug(
    "[DEBUG][MERGE] usage/config join on %s: %d -> %d rows.",
    JOIN_KEYS,
    rows_before,
    df_merged.height,
)
```

Prefer one shared helper, e.g. `log_join_delta(rows_before, df_after, logger, context)`,
over repeating the two lines at every call site. With `LazyFrame`, place the counts
around the `collect()` boundary rather than forcing an extra materialisation.

### Sentinel values carry an explicit dtype

A sentinel written without a dtype makes the column's type depend on concat relaxation
rules, which silently changes dtype between runs when the sentinel branch is the only
one populated.

```python
# Before — dtype depends on vertical_relaxed upcasting
df_missing = pl.DataFrame({"conversion_rate": [MISSING_SENTINEL]})

# After — dtype is stated, not inferred
df_missing = pl.DataFrame(
    {"conversion_rate": pl.Series([MISSING_SENTINEL], dtype=pl.Float64)}
)
```

Inside an expression chain, the equivalent is
`pl.lit(MISSING_SENTINEL, dtype=pl.Float64)`. Prefer a real `null` over a numeric
sentinel whenever the consumer can handle nulls.

### External key access raises `ValueError`

A bare `KeyError` from a config parser tells the operator nothing about which file or
key is wrong, and it bypasses the project's "`ValueError` for configuration validation"
rule.

```python
# Before — bare KeyError escapes to the caller
day_zero = raw_config["day_zero"]["start_date"]

# After — validated, attributed, chained
try:
    day_zero = raw_config["day_zero"]["start_date"]
except KeyError as error:
    error_message = f"Missing key {error} in day_zero section of {config_path}."
    logger.error(error_message)
    raise ValueError(error_message) from error
```

### Remote I/O retries and logs before raising

S3, HTTP, and subprocess calls fail transiently. Without a capped-backoff retry the
whole pipeline aborts on a blip; without a `logger.error` before the raise the failure
reason is absent from the log file that operators actually read.

```python
# Before — one attempt, no diagnostic
def load_object(bucket: Bucket, key: str) -> bytes:
    return bucket.Object(key).get()["Body"].read()


# After — bounded retries, logged, chained
@retry(stop=stop_after_attempt(3), wait=wait_exponential(max=10), reraise=True)
def load_object(bucket: Bucket, key: str, logger: logging.Logger) -> bytes:
    try:
        return bucket.Object(key).get()["Body"].read()
    except ClientError as error:
        error_message = f"Failed to read s3 object {key}."
        logger.error(error_message)
        raise OSError(error_message) from error
```

`tenacity` is the preferred helper when it is already an installed dependency; a small
hand-rolled bounded loop is acceptable rather than adding a dependency for one call
site.

### No I/O at import time

Creating directories, opening files, or contacting a network service from module scope
makes the package impossible to import in a test or a lint run without side effects.
Move the work into an explicit `initialise_layout()` (or equivalent) that the pipeline
entry point calls.

## Pipeline Structure

1. Imports organized by section
2. `LOGGER_NAME: Final[str]` constant
3. Helper functions with complete docstrings
4. `main()` entry point
5. `if __name__ == "__main__":` block

## API Design (for libraries)

- Inject config and logger as parameters to high-level functions
- Minimize caller steps; design for library consumption, not just scripts

## Quality Gates

- **Complexipy**: cognitive complexity · **Deadcode**: unused code (exclusions in
  `pyproject.toml`)
- **SonarQube**: coverage floor per the threshold table

## Commit Messages

Follow the `commit-message` skill. One logical change per commit.

## Documentation

- Backticks for filenames and symbols · **MkDocs Material** with `mkdocstrings[python]`
- Versioning with **mike** · admonitions with 4-space indentation

## Change Comments

Each modification: `# Changed: [what] - Reason: [why]`

## CI/CD

- Jenkins and GitLab CI/CD · CI stages: `lint` → `test` → `docs`
- Pre-commit runs `make pipeline` (format + lint + code_check + security)
- Commits signed with GPG · notebooks cleaned with `nbstripout` before commit

## Editor Rules

- Visual rulers at the docstring and source line limits of the threshold table
- Format on type enabled for Python · Prettier `printWidth: 88` for JSON

## Reproducibility

- `set_random_seeds(seed=42)` at import time for deterministic results
- Pin all dependency versions in `pyproject.toml` · commit `uv.lock`
- Document hardware requirements when results depend on compute

## Notebooks

- Exploration only — production logic lives in modules
- Strip outputs before commit (`nbstripout`) · CI strips via `make clean_notebooks`
- Never import from notebooks; extract reusable code into proper modules
