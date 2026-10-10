# Python Environment

- The project uses **uv** as its Python environment and dependency manager.
- All agents and skills MUST use the same virtual environment as the user (`uv run`).
- If the environment does not exist or dependencies are missing, inform the user and
  stop. Do NOT create environments or install packages automatically.
- The dependency group `kiro_tools` in `pyproject.toml` defines packages available to
  agents and skills (e.g. markitdown, jira). To install them:

  ```bash
  uv sync --group kiro_tools
  ```

- Every Python or CLI invocation from an agent must be prefixed with `uv run`.
