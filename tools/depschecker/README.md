# Depschecker

Check Python dependency freshness and known vulnerabilities against
[PyPI](https://pypi.org/).

## Requirements

- Python 3.13 and [uv](https://docs.astral.sh/uv/)

Set up with `make setup` inside `tools/depschecker`.

## Usage

Freshness comes from the declared constraints in `pyproject.toml`; vulnerabilities come
from the resolved versions in `uv.lock`, which is also the only place transitive
dependencies appear. The lockfile is inferred as a sibling of the given
`pyproject.toml`, so the existing invocation keeps working unchanged.

The commands below assume the tool environment is active. From the repository root,
prefix each with `uv run --project tools/depschecker`.

```bash
# Full report (freshness + vulnerabilities), uv.lock inferred alongside
depschecker pyproject.toml

# Only freshness (no lockfile required)
depschecker --freshness-only pyproject.toml

# Only vulnerabilities (requires a lockfile)
depschecker --vulns-only pyproject.toml

# Explicit lockfile path
depschecker --lock /path/to/uv.lock pyproject.toml

# Write to file
depschecker -o report.md pyproject.toml

# Custom timeout per request
depschecker --timeout 30 pyproject.toml

# Verbose logging
depschecker -v pyproject.toml

# Or run as a module
python -m depschecker.cli pyproject.toml
```

### CLI Options

| Option             | Description                                                      |
| ------------------ | ---------------------------------------------------------------- |
| `pyproject`        | Path to `pyproject.toml` (positional, default: `pyproject.toml`) |
| `--lock`           | Path to `uv.lock` (default: `uv.lock` beside `pyproject`)        |
| `-o`, `--output`   | Write report to file instead of stdout                           |
| `--freshness-only` | Only check version freshness, skip vulnerabilities               |
| `--vulns-only`     | Only check vulnerabilities, skip freshness report                |
| `--timeout`        | HTTP timeout per PyPI request in seconds (default: 15)           |
| `-v`, `--verbose`  | Enable debug logging                                             |

`--vulns-only` and the default full report both require a lockfile and exit with code 1
if one cannot be found. Failing loudly is deliberate: the alternative is a scan that
reports no vulnerabilities because it audited nothing.

### Configuration

When `WORK_AGENTS_CONFIG` points to the repository `config.toml`, the `[depschecker]`
section is read (see `config.toml.example`); `--timeout` takes priority. A malformed
config file exits 1 with a message.

## Output

The tool outputs two Markdown tables: a freshness report and a vulnerability report.

### Freshness table

Covers the declared direct dependencies. `Declared` is the lower bound of the constraint
in `pyproject.toml`, `Resolved` is the version pinned in `uv.lock`, and `Update`
compares the resolved version against `Latest`, falling back to `Declared` when no
lockfile was read.

| Package  | Declared | Resolved | Latest | Update   | Changelog   |
| -------- | -------- | -------- | ------ | -------- | ----------- |
| requests | 2.32     | 2.33.1   | 2.34.2 | 🟠 minor | [link](...) |
| ruff     | 0.16.4   | 0.16.4   | 0.16.8 | 🟡 patch | [link](...) |

Update types are classified by semver distance: ✅ up-to-date, 🟡 patch, 🟠 minor, 🔴
major.

### Vulnerability table

Covers every registry package in the lock resolution, direct and transitive, at its
exact resolved version.

| Package | Resolved | Scope      | Advisory            | Aliases        | Summary | Fixed in | Link |
| ------- | -------- | ---------- | ------------------- | -------------- | ------- | -------- | ---- |
| urllib3 | 2.6.3    | transitive | GHSA-mf9v-mfxr-j63j | CVE-2026-44432 | —       | 2.7.0    | ...  |

Queries that fail are listed under a separate "Packages not audited" heading, so a
network error is never presented as a clean result. Retracted advisories are marked
`⚠ withdrawn` rather than dropped.

## Design notes

Two PyPI endpoints are used, because neither answers both questions:

- `https://pypi.org/pypi/<name>/json` carries `info.version` and `releases`, which is
  what freshness needs, but its `vulnerabilities` key is **always empty**.
- `https://pypi.org/pypi/<name>/<version>/json` is the only endpoint that populates
  `vulnerabilities`, but it omits `releases` and reports the _queried_ version as
  `info.version`, so it cannot answer freshness.

Vulnerabilities are keyed on `uv.lock` rather than on the declared constraint because a
range floor is not what gets installed: `requests>=2.32,<3` would otherwise be audited
as `requests==2.32`, a version nobody ran.

PyPI's JSON API exposes no severity or CVSS field and returns an explicit null summary
for PYSEC-family advisories, so those cells render as `—` and the report says so. The
OSV batch API (`https://api.osv.dev/v1/querybatch`) would supply severity, at the cost
of a second external dependency and a second failure mode; it was left out to keep the
tool on a single upstream.

### Testing the security control

`tests/test_pypi.py` carries a negative control: a recorded PyPI response for
`urllib3==2.6.3` (a version with four real advisories) asserted to produce findings,
plus an assertion that the requested URL contains the version segment. A live-network
equivalent is opt-in via `DEPSCHECKER_LIVE_NETWORK=1` and skipped by default so the
suite stays deterministic.

## Development

Targets (`make lint`, `make code-check`, `make test`, `make all`) come from
[`tools/tool.mk`](../tool.mk); the repository gates (`make lint-depschecker`,
`make test-depschecker`) are in the root [`Makefile`](../../Makefile). `make test`
enforces an 80% coverage floor.
