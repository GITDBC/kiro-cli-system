# Python 3.13 — Modern Patterns Reference

Reference for all code-writing agents. Use these patterns instead of their deprecated or
legacy alternatives. Target version: Python 3.13 (the repository pin is in the threshold
table of `code-standards-summary.md`). Each heading names the version that introduced
the feature; everything listed is available on the 3.13 baseline.

## Official Documentation

- [Python 3.13 — What's New](https://docs.python.org/3.13/whatsnew/3.13.html)
- [Python 3.12 — What's New](https://docs.python.org/3.13/whatsnew/3.12.html)
- [Python 3.13 — Standard Library](https://docs.python.org/3.13/library/index.html)
- [Python 3.13 — Language Reference](https://docs.python.org/3.13/reference/index.html)

## Removed Modules — PEP 594 Dead Batteries (removed in 3.13)

Importing any of these raises `ModuleNotFoundError` on 3.13: `aifc`, `audioop`, `cgi`,
`cgitb`, `chunk`, `crypt`, `imghdr`, `mailcap`, `msilib`, `nis`, `nntplib`,
`ossaudiodev`, `pipes`, `sndhdr`, `spwd`, `sunau`, `telnetlib`, `uu`, `xdrlib`. The
`lib2to3` package and the `2to3` tool were removed as well. Replacements: `shlex.quote`
for `pipes.quote`, `email.message` / `urllib.parse` for `cgi` parsing helpers, and a
maintained third-party package where no stdlib equivalent exists.

## Type Parameter Syntax (PEP 695, 3.12)

```python
# WRONG — legacy TypeVar boilerplate
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, item: T) -> None:
        self.item = item

def first(items: list[T]) -> T:
    return items[0]

# CORRECT — inline type parameters
class Box[T]:
    def __init__(self, item: T) -> None:
        self.item = item

def first[T](items: list[T]) -> T:
    return items[0]
```

Type parameters accept defaults since 3.13 (PEP 696): `class Box[T = str]: ...`.

## `type` Statement for Aliases (PEP 695, 3.12)

```python
# WRONG — TypeAlias annotation
from typing import TypeAlias

Matrix: TypeAlias = list[list[float]]

# CORRECT — lazily evaluated, can be generic
type Matrix = list[list[float]]
type Pair[T] = tuple[T, T]
```

## `typing.override` (PEP 698, 3.12)

```python
# CORRECT — the type checker flags the method if the base method is renamed
from typing import override

class JsonReport(Report):
    @override
    def render(self) -> str:
        ...
```

## `warnings.deprecated` (PEP 702, 3.13)

```python
# WRONG — manual warning, invisible to type checkers
import warnings

def old_api() -> None:
    warnings.warn("Use new_api().", DeprecationWarning, stacklevel=2)

# CORRECT — runtime DeprecationWarning plus a static type-checker diagnostic
from warnings import deprecated

@deprecated("Use new_api().")
def old_api() -> None:
    ...
```

## `typing.TypeIs` for Narrowing (PEP 742, 3.13)

```python
# CORRECT — narrows in both branches, unlike TypeGuard
from typing import TypeIs

def is_str(value: object) -> TypeIs[str]:
    return isinstance(value, str)
```

## F-string Grammar (PEP 701, 3.12)

```python
# WRONG — workarounds for quote reuse
key = "name"
msg = f"User: {user[key]}"

# CORRECT — the same quote type may be reused inside replacement fields,
# and expressions may span lines and contain backslashes
msg = f"User: {user["name"]}"
lines = f"{"\n".join(rows)}"
```

## `itertools.batched` (3.12)

```python
# WRONG — hand-rolled chunking
chunks = [items[i : i + 100] for i in range(0, len(items), 100)]

# CORRECT — works on any iterable, yields tuples
from itertools import batched

for chunk in batched(items, 100):
    ...
```

## Exception Groups and `except*` (PEP 654, 3.11)

```python
# Available for handling multiple concurrent exceptions
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(op_a())
        tg.create_task(op_b())
except* ValueError as eg:
    for exc in eg.exceptions:
        logger.error("Validation: %s.", exc)
except* OSError as eg:
    for exc in eg.exceptions:
        logger.error("IO: %s.", exc)
```

## `tomllib` — Built-in TOML Parsing (3.11)

```python
# WRONG — third-party for reading TOML
import toml  # or tomli

# CORRECT — stdlib
import tomllib

with open("config.toml", "rb") as f:
    config = tomllib.load(f)
```

## `StrEnum` (3.11)

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

## `Self` Type (PEP 673, 3.11)

```python
# WRONG
class Builder:
    def set_name(self, name: str) -> "Builder":
        ...

# CORRECT
from typing import Self

class Builder:
    def set_name(self, name: str) -> Self:
        ...
```

## `TaskGroup` for Structured Concurrency (3.11)

```python
# WRONG — manual gather with error handling
results = await asyncio.gather(task_a(), task_b(), return_exceptions=True)

# CORRECT — structured concurrency
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(task_a())
    t2 = tg.create_task(task_b())
# Both complete or all cancelled on first exception
```

## Type Hints — Use Built-in Generics (PEP 585) and `X | Y` (PEP 604)

```python
# WRONG — typing aliases, deprecated since 3.9
from typing import Dict, List, Optional, Tuple, Union

def process(items: List[Dict[str, Any]]) -> Optional[Tuple[str, ...]]:
    ...

def fetch(url: str) -> Union[str, None]:
    ...

# CORRECT — built-in generics and pipe syntax
def process(items: list[dict[str, Any]]) -> tuple[str, ...] | None:
    ...

def fetch(url: str) -> str | None:
    ...
```

## Dataclasses — Use `slots=True` and `kw_only=True` (3.10)

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

`copy.replace(config, port=9090)` (3.13) builds a modified copy of a dataclass or named
tuple; prefer it over `dataclasses.replace` in code that also handles other types.

## `match` Statement (3.10)

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

## `zip` with `strict=True` (3.10)

```python
# WRONG — silently truncates if lengths differ
for name, score in zip(names, scores):
    ...

# CORRECT — raises ValueError on length mismatch
for name, score in zip(names, scores, strict=True):
    ...
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
# WRONG — unnecessary on 3.13, can cause runtime issues with isinstance
from __future__ import annotations

# CORRECT — use built-in generics and X | Y directly
def process(items: list[str]) -> dict[str, int] | None:
    ...
```

## `datetime.UTC` Over `utcnow()`

```python
# WRONG — datetime.utcnow() is deprecated since 3.12 and returns a naive value
from datetime import datetime

now = datetime.utcnow()

# CORRECT — timezone-aware
from datetime import UTC, datetime

now = datetime.now(UTC)
```
