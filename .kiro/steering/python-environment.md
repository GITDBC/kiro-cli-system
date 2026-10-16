# Python Environment

- The project uses **uv**. Each tool under `tools/` has its own environment: run it with
  `uv run --project tools/<tool>`; prefix every other Python or CLI call with `uv run`.
- Agents and skills MUST use the user's existing environment. If it is missing or
  dependencies are absent, inform the user and stop — never create environments or
  install packages automatically.
