# Commit Convention Lookup

Type-to-emoji mapping and worked messages. Load this when the project uses gitemojis, or
when the type choice for a change is not obvious from the type list in `SKILL.md`.

## Type and Emoji

| Type       | Purpose                                | Emoji                      |
| ---------- | -------------------------------------- | -------------------------- |
| `feat`     | New feature (MINOR in SemVer)          | ✨ `:sparkles:`            |
| `fix`      | Bug fix (PATCH in SemVer)              | 🐛 `:bug:`                 |
| `docs`     | Documentation only                     | 📝 `:memo:`                |
| `style`    | Formatting, no logic change            | 🎨 `:art:`                 |
| `refactor` | Code restructuring, no behavior change | ♻️ `:recycle:`             |
| `test`     | Adding or updating tests               | 🧪 `:test_tube:`           |
| `chore`    | Build, tooling, dependencies           | 🔧 `:wrench:`              |
| `perf`     | Performance improvement                | ⚡ `:zap:`                 |
| `ci`       | CI/CD configuration                    | 👷 `:construction_worker:` |
| `build`    | Build system or dependency changes     | 📦 `:package:`             |
| `revert`   | Revert a previous commit               | ⏪ `:rewind:`              |

## Worked Examples

A feature with a scope, a body explaining what and why, and traceability metadata:

```
✨ feat(etl): add S3 data loader for PM counters

Implement parallel download and schema filtering for parquet files
stored in S3. Supports column selection and suffix-based filtering.

Tracking-Id: GEN:HIGH JIRA-ID: PROJECT-92210
```

A fix with a scope and a body, no traceability footer:

```
🐛 fix(pipeline): handle empty DataFrame in ETL orchestrator

Return early when all source files produce empty frames instead of
raising an unhandled exception downstream.
```

A documentation change small enough to need no scope and no body:

```
📝 docs: update API reference for config loader
```
