# Every tool under tools/ is a self-contained uv project: its own
# pyproject.toml, ruff config, mypy strict run and pytest suite. The
# directory name must equal the module name, since lint-<tool> runs
# `mypy $t` inside tools/$t.
TOOLS := jirafetcher depschecker doc2md driftcheck docsync ctxbudget

# The per-tool lint-%/test-% pattern rules below are deliberately NOT
# listed here: marking a pattern-matched name .PHONY makes GNU Make
# treat it as already up to date and silently skip the recipe.
.PHONY: fmt fmt-check drift-check hook-test lint-all test-all \
	clean all sync-docs sync-docs-check sync-agentskills sync-agentskills-check \
	sync-anthropic sync-anthropic-check context-budget context-budget-check print-tools

fmt:
	npx prettier --write "**/*.{md,json,yml,yaml}"

fmt-check:
	npx prettier --check "**/*.{md,json,yml,yaml}"

# The KiroCLIDocs knowledge base indexes
# .kiro/skills/kiro-cli-reference/references with autoUpdate: false, so a
# sync that actually changes files leaves it stale until someone re-indexes
# by hand. Re-indexing on every sync was considered and rejected: it would
# pay 141-file semantic-embedding latency on every orchestrator session
# start for a rare, low-impact staleness whose authoritative copy is on
# disk and greppable anyway. The reminder below is the cheap mitigation.
sync-docs:
	@uv run --project tools/docsync docsync kiro; \
	if ! git diff --quiet -- .kiro/skills/kiro-cli-reference/references; then \
		echo "NOTE: vendored docs changed — KiroCLIDocs knowledge base is now stale; re-index it (autoUpdate is deliberately false)."; \
	fi

sync-docs-check:
	uv run --project tools/docsync docsync kiro --dry-run

sync-agentskills:
	uv run --project tools/docsync docsync agentskills

sync-agentskills-check:
	uv run --project tools/docsync docsync agentskills --dry-run

sync-anthropic:
	@uv run --project tools/docsync docsync anthropic; \
	if ! git diff --quiet -- .kiro/skills/claude-prompting-reference/references; then \
		echo "NOTE: vendored docs changed — KiroCLIDocs knowledge base is now stale; re-index it (autoUpdate is deliberately false)."; \
	fi

sync-anthropic-check:
	uv run --project tools/docsync docsync anthropic --dry-run

drift-check:
	uv run --project tools/driftcheck driftcheck

# Quantities, not structure: drift-check validates the agent system's
# shape, context-budget measures what it costs. The report lands in the
# gitignored tmp/ tree.
#
# No budget baseline is recorded in this repository, so context-budget-check
# is deliberately absent from `all` and from CI: with no baseline to compare
# against it exits 1. To gate on context growth, record one with
# `ctxbudget check --write-budget` and re-add the target to `all` and to
# .github/actions/files-checker/action.yml.
context-budget:
	uv run --project tools/ctxbudget ctxbudget report

context-budget-check:
	uv run --project tools/ctxbudget ctxbudget check

# The git-safety preToolUse hook is shell, not Python, so no per-tool
# pytest suite covers it. Without an entry point here its cases rot.
hook-test:
	.kiro/hooks/git-safety.test.sh

# Deliberately NOT delegated to tools/$*/Makefile's own `lint`: that
# target auto-fixes, so delegating would let the gate pass by rewriting
# code instead of checking it.
lint-%:
	@echo "=== Linting tools/$* ==="
	@( cd tools/$* && uv run ruff check . && uv run ruff format --check . && uv run mypy $* && uv run complexipy -f . )

lint-all: $(TOOLS:%=lint-%)

# Unlike lint-%, delegating here is safe: both sides run the same
# `uv run pytest tests/`.
test-%:
	@echo "=== Testing tools/$* ==="
	@$(MAKE) --no-print-directory -C tools/$* test

test-all: $(TOOLS:%=test-%)

# Each tool already owns a `clean` target; this delegates to them and then
# sweeps what they leave behind. The repo-wide find is deliberate: coverage
# artefacts land next to whichever tool was measured, and the per-tool clean
# targets only remove cache directories and bytecode, not coverage data.
clean:
	@for t in $(TOOLS); do \
		echo "=== Cleaning tools/$$t ==="; \
		$(MAKE) -C tools/$$t clean; \
	done
	@echo "=== Cleaning coverage and root caches ==="
	@find . \( -type d \( -name .pytest_cache -o -name .ruff_cache -o -name .mypy_cache -o -name htmlcov \) \
		-o -type f \( -name .coverage -o -name '.coverage.*' -o -name coverage.xml \) \) \
		-not -path "*/.venv/*" -exec rm -rf {} + 2>/dev/null || true

# Single source of truth for CI's test-tools matrix: `make print-tools` emits
# TOOLS space-separated so the workflow can turn it into a JSON array. Adding
# or removing a tool here is the only edit required for both `make test-all`
# and the CI matrix to pick it up.
print-tools:
	@echo $(TOOLS)

all: fmt-check drift-check lint-all test-all hook-test
