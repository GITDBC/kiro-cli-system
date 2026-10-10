# Senior Developer — Implementation Patterns

Reference patterns for the senior-developer agent. Load when implementing features or
refactoring code that needs these specific patterns.

## Clean Function Design

```python
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def process_data_file(
    file_path: Path,
    encoding: str = "utf-8",
    *,
    skip_header: bool = False,
) -> list[dict[str, str]]:
    """
    Process a data file and return parsed records.

    Args:
        file_path: Path to the input data file.
        encoding: File encoding.
        skip_header: Whether to skip the first line.

    Returns:
        List of parsed records as dictionaries.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains invalid data.
    """

    if not file_path.exists():
        error_message = f"[ERROR] File not found: {file_path}."
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    logger.info("[INFO] Processing file: %s.", file_path)
    records: list[dict[str, str]] = []

    with file_path.open(encoding=encoding) as fh:
        lines = fh.readlines()
        if skip_header:
            lines = lines[1:]

        for line_number, line in enumerate(lines, start=1):
            record = _parse_line(line.strip(), line_number)
            if record is not None:
                records.append(record)

    logger.info("[INFO] Processed %d records.", len(records))
    return records


def _parse_line(line: str, line_number: int) -> dict[str, str] | None:
    """
    Parse a single line into a record.

    Args:
        line: Raw line content.
        line_number: Line number for error reporting.

    Returns:
        Parsed record or None if the line is empty.
    """

    if not line:
        return None

    parts = line.split(",")
    if len(parts) < 2:
        logger.warning(
            "[WARNING] Skipping malformed line %d.", line_number
        )
        return None

    return {"key": parts[0].strip(), "value": parts[1].strip()}
```

## Error Handling Pattern

The `error_message` / `logger.error` / `raise ExceptionType(error_message)` triad is the
project-wide convention owned by
`.kiro/skills/code-standards/references/full-standards.md:173-177` ("Error Handling —
full detail"). See the `Clean Function Design` example above for the triad applied in
context (`process_data_file`'s `FileNotFoundError` branch); no separate generic
restatement is kept here.

## Async Pattern

```python
import asyncio
import logging
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


async def sync_resources(
    resource_ids: list[str],
    *,
    concurrency: int = 5,
) -> list[dict[str, str]]:
    """
    Synchronize resources concurrently.

    Args:
        resource_ids: Identifiers of resources to sync.
        concurrency: Maximum concurrent operations.

    Returns:
        List of sync results per resource.
    """

    semaphore = asyncio.Semaphore(concurrency)
    started_at = datetime.now(tz=UTC)

    async def _sync_one(rid: str) -> dict[str, str]:
        async with semaphore:
            logger.info("[INFO] Syncing resource %s.", rid)
            result = await _do_sync(rid)
            return {"id": rid, "status": result}

    results = await asyncio.gather(
        *[_sync_one(rid) for rid in resource_ids]
    )
    elapsed = (datetime.now(tz=UTC) - started_at).total_seconds()
    logger.info("[INFO] Synced %d resources in %.2fs.", len(results), elapsed)
    return list(results)
```

## Dataclass Pattern

```python
from dataclasses import dataclass, field
from datetime import datetime, UTC


@dataclass(slots=True, kw_only=True)
class PipelineResult:
    """
    Result of a pipeline execution.

    Attributes:
        name: Pipeline name.
        status: Execution status.
        records_processed: Number of records processed.
        errors: List of error messages.
        started_at: Execution start timestamp.
        finished_at: Execution end timestamp.
    """

    name: str
    status: str
    records_processed: int = 0
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(
        default_factory=lambda: datetime.now(tz=UTC)
    )
    finished_at: datetime | None = None

    @property
    def is_success(self) -> bool:
        """
        Check whether the pipeline succeeded.

        Returns:
            True if status is success and no errors occurred.
        """

        return self.status == "success" and not self.errors
```
