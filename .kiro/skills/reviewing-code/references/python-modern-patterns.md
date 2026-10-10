# Python 3.11+ — Modern Patterns Reference

Reference for all code-writing agents. Use these patterns instead of their deprecated or
legacy alternatives. Target version: Python 3.11+.

## Official Documentation

- [Python 3.11 — What's New](https://docs.python.org/3.11/whatsnew/3.11.html)
- [Python 3.11 — Standard Library](https://docs.python.org/3.11/library/index.html)
- [Python 3.11 — Language Reference](https://docs.python.org/3.11/reference/index.html)

## Type Hints — Use Built-in Generics (PEP 585)

```python
# WRONG — deprecated since 3.9, removed in future
from typing import Dict, List, Optional, Tuple, Set

def process(items: List[Dict[str, Any]]) -> Optional[Tuple[str, ...]]:
    ...

# CORRECT — built-in generics
def process(items: list[dict[str, Any]]) -> tuple[str, ...] | None:
    ...
```

## Union Types — Use `X | Y` Syntax (PEP 604)

```python
# WRONG — verbose
from typing import Union, Optional

def fetch(url: str) -> Union[str, None]:
    ...

value: Optional[int] = None

# CORRECT — pipe syntax
def fetch(url: str) -> str | None:
    ...

value: int | None = None
```

## Exception Groups and `except*` (PEP 654, 3.11+)

```python
# Available for handling multiple concurrent exceptions
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(op_a())
        tg.create_task(op_b())
except* ValueError as eg:
    for exc in eg.exceptions:
        logger.error("Validation: %s", exc)
except* OSError as eg:
    for exc in eg.exceptions:
        logger.error("IO: %s", exc)
```

## `tomllib` — Built-in TOML Parsing (3.11+)

```python
# WRONG — third-party for reading TOML
import toml  # or tomli

# CORRECT — stdlib since 3.11
import tomllib

with open("config.toml", "rb") as f:
    config = tomllib.load(f)
```

## `StrEnum` (3.11+)

```python
# WRONG — manual string enum
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# CORRECT — StrEnum
from enum import StrEnum

class Status(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
```

## `Self` Type (PEP 673, 3.11+)

```python
# WRONG
from __future__ import annotations

class Builder:
    def set_name(self, name: str) -> "Builder":
        ...

# CORRECT
from typing import Self

class Builder:
    def set_name(self, name: str) -> Self:
        ...
```

## `TaskGroup` for Structured Concurrency (3.11+)

```python
# WRONG — manual gather with error handling
results = await asyncio.gather(task_a(), task_b(), return_exceptions=True)

# CORRECT — structured concurrency
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(task_a())
    t2 = tg.create_task(task_b())
# Both complete or all cancelled on first exception
```

## Dataclasses — Use `slots=True` and `kw_only=True` (3.10+)

```python
# WRONG — no slots (wastes memory, allows typos in attribute names)
@dataclass
class Config:
    host: str
    port: int = 8080

# CORRECT — slots for performance, kw_only for clarity
@dataclass(slots=True, kw_only=True)
class Config:
    host: str
    port: int = 8080
```

## `match` Statement (3.10+)

```python
# WRONG — chain of if/elif
if status == 200:
    handle_ok()
elif status == 404:
    handle_not_found()
elif status >= 500:
    handle_server_error()

# CORRECT — structural pattern matching
match status:
    case 200:
        handle_ok()
    case 404:
        handle_not_found()
    case s if s >= 500:
        handle_server_error()
```

## `pathlib` Over `os.path`

```python
# WRONG — string-based path manipulation
import os
path = os.path.join(base_dir, "data", "output.csv")
if os.path.exists(path):
    with open(path) as f:
        ...

# CORRECT — pathlib
from pathlib import Path
path = Path(base_dir) / "data" / "output.csv"
if path.exists():
    content = path.read_text(encoding="utf-8")
```

## F-strings Over `format()` and `%`

```python
# WRONG
msg = "Hello, %s! You have %d items." % (name, count)
msg = "Hello, {}! You have {} items.".format(name, count)

# CORRECT
msg = f"Hello, {name}! You have {count} items."
```

## Logging — Never Use F-strings in Log Calls

```python
# WRONG — f-string evaluated even if log level is disabled
logger.debug(f"Processing {len(items)} items for {user_id}")

# CORRECT — lazy formatting, only evaluated if level is active
logger.debug("Processing %d items for %s.", len(items), user_id)
```

## `from __future__ import annotations` — Avoid

```python
# WRONG — unnecessary on 3.11+, can cause runtime issues with isinstance
from __future__ import annotations

# CORRECT — use built-in generics and X | Y directly
def process(items: list[str]) -> dict[str, int] | None:
    ...
```

## Walrus Operator `:=` (3.8+)

```python
# WRONG — redundant variable assignment
match = pattern.search(text)
if match:
    process(match)

# CORRECT — assign and test in one expression
if match := pattern.search(text):
    process(match)
```

## `zip` with `strict=True` (3.10+)

```python
# WRONG — silently truncates if lengths differ
for name, score in zip(names, scores):
    ...

# CORRECT — raises ValueError on length mismatch
for name, score in zip(names, scores, strict=True):
    ...
```
