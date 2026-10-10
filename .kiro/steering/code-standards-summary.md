# Code Standards (Summary)

Critical conventions loaded always-on. For full details, read
`.kiro/skills/code-standards/SKILL.md`.

## Numeric thresholds

This table is the single always-on copy. No other steering file restates these values —
they reference this table by name instead.

| Threshold           | Value                                        |
| ------------------- | -------------------------------------------- |
| Python version pin  | `==3.11.*` — 3.11 exclusively, managed by uv |
| Test coverage floor | 80% minimum, enforced by the SonarQube gate  |
| Max source line     | 88 characters (Ruff)                         |
| Max docstring line  | 73 characters                                |
| Indentation         | 4 spaces                                     |

## Essentials

- **Type hints** mandatory on all public function signatures (PEP 585/604)
- **Docstrings**: Google format, content starts after `"""`
- **Formatting**: Ruff, double quotes
- **Imports**: ordered (stdlib → 3pps → own modules), section headers required
- **Logging**: lazy `%` formatting, never f-strings in logger calls, messages end with
  `.`
- **Error handling**: `ValueError` for validation, specific exceptions, `raise from`
- **Testing**: pytest, `test_*` naming
- **Security**: bandit, no credentials in source, licensecheck
- **Naming**: snake*case functions/vars, PascalCase classes, UPPER_SNAKE constants,
  `df*`prefix for DataFrames,`Config` suffix for config classes
- **Polars** for data processing (not Pandas), NumPy for numerical computation
- **No deprecated code**: no `datetime.utcnow()`, no
  `from __future__ import annotations`

## Engineering Principles

- **DRY** · **KISS** · **YAGNI** (stdlib/platform/installed dep before custom code)
- **Single Responsibility** · **Low coupling** · **Defensive programming**
