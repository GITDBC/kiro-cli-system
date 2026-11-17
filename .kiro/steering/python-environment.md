# Python Environment

- The project uses **uv**. Each tool has its own environment: run it with
  `uv run --project <tool directory>` (`tools/<tool>` for maintenance tools,
  `.kiro/skills/<skill>/references/<tool>` for skill tools); prefix every other Python
  or CLI call with `uv run`.
- Agents and skills MUST use the user's existing environment. If it is missing or
  dependencies are absent, inform the user and stop — never create environments or
  install packages automatically.
