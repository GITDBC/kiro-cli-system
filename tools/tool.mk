# Shared recipe body for every tool under tools/. Included by each tool's
# Makefile, which contributes only its module name via CURDIR. The directory
# name must equal the module name, since the root lint-<tool> target runs
# `mypy <tool>` inside tools/<tool>.
MODULE := $(notdir $(patsubst %/,%,$(CURDIR)))

.PHONY: setup clean lint code-check test all

.DEFAULT_GOAL := all

setup:
	@uv sync --all-groups

# The .venv exclusion keeps `clean` from deleting bytecode and caches that
# belong to the tool's own environment.
clean:
	@find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .complexipy_cache -o -name .ruff_cache \) -not -path "*/.venv/*" -prune -exec rm -rf {} +
	@find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -not -path "*/.venv/*" -delete

lint:
	@uv run ruff format .
	@uv run ruff check --fix .
	@uv run isort .

code-check:
	@uv run complexipy -f .
	@uv run mypy $(MODULE)

test:
	@uv run pytest tests/ --cov=$(MODULE) --cov-fail-under=80

all: setup lint code-check test
