# Shared recipe body for every tool under tools/. Included by each tool's
# Makefile, which contributes only its module name via CURDIR — see the
# comment on TOOLS in the root Makefile for the directory-equals-module
# invariant this depends on.
MODULE := $(notdir $(patsubst %/,%,$(CURDIR)))

.PHONY: setup clean lint code-check test all

.DEFAULT_GOAL := all

setup:
	@uv sync --all-groups

clean:
	@find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .complexipy_cache -o -name .ruff_cache \) -exec rm -rf {} +
	@find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete

lint:
	@uv run ruff format .
	@uv run ruff check --fix .
	@uv run isort .

code-check:
	@uv run complexipy -f .
	@uv run mypy $(MODULE)

test:
	@uv run pytest tests/

all: setup clean lint code-check test
