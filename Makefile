TOOLS := jirafetcher depschecker doc2md driftcheck docsync ctxbudget

.PHONY: fmt fmt-check drift-check hook-test lint-all test-all \
	clean all sync-docs sync-docs-check sync-agentskills sync-agentskills-check \
	sync-anthropic sync-anthropic-check context-budget context-budget-check print-tools

fmt:
	npx prettier --write "**/*.{md,json,yml,yaml}"

fmt-check:
	npx prettier --check "**/*.{md,json,yml,yaml}"

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
	uv run --project tools/docsync docsync anthropic

sync-anthropic-check:
	uv run --project tools/docsync docsync anthropic --dry-run

drift-check:
	uv run --project tools/driftcheck driftcheck

context-budget:
	uv run --project tools/ctxbudget ctxbudget report

context-budget-check:
	uv run --project tools/ctxbudget ctxbudget check

hook-test:
	.kiro/hooks/git-safety.test.sh
	.kiro/hooks/ralph-stop.test.sh

lint-%:
	@echo "=== Linting tools/$* ==="
	@( cd tools/$* && uv run ruff check . && uv run ruff format --check . && uv run isort --check-only . && uv run mypy $* && uv run complexipy -f . )

lint-all: $(TOOLS:%=lint-%)

test-%:
	@echo "=== Testing tools/$* ==="
	@$(MAKE) --no-print-directory -C tools/$* test

test-all: $(TOOLS:%=test-%)

clean:
	@for t in $(TOOLS); do \
		echo "=== Cleaning tools/$$t ==="; \
		$(MAKE) -C tools/$$t clean; \
	done
	@echo "=== Cleaning coverage and root caches ==="
	@find . \( -type d \( -name .pytest_cache -o -name .ruff_cache -o -name .mypy_cache -o -name htmlcov \) \
		-o -type f \( -name .coverage -o -name '.coverage.*' -o -name coverage.xml \) \) \
		-not -path "*/.venv/*" -exec rm -rf {} + 2>/dev/null || true

print-tools:
	@echo $(TOOLS)

all: fmt-check drift-check lint-all test-all hook-test
