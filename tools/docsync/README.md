# Docsync

Sync the vendored documentation mirrors of this repository. One engine drives every
mirror; each upstream is a source adapter under `docsync/sources/`.

| Source        | Mirror                                                | Upstream                                        |
| ------------- | ----------------------------------------------------- | ----------------------------------------------- |
| `kiro`        | `.kiro/skills/kiro-cli-reference/references/`         | [kiro.dev](https://kiro.dev/docs/) sitemap      |
| `agentskills` | `.kiro/skills/agent-creation/references/agentskills/` | Agent Skills docs (6-page catalogue, CC-BY-4.0) |
| `anthropic`   | `.kiro/skills/claude-prompting-reference/references/` | Anthropic prompting docs (`llms.txt` catalogue) |

## Requirements

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) (package manager)

No third-party dependencies — the fetch uses `urllib` from the standard library.

## Setup

```bash
cd tools/docsync
make setup
```

## Usage

```bash
# Check for updates without writing (exit 1 when updates are pending)
make sync-docs-check
make sync-agentskills-check
make sync-anthropic-check

# Download updates and refresh the sync marker
make sync-docs
make sync-agentskills
make sync-anthropic

# Direct invocation
uv run --project tools/docsync docsync kiro --dry-run
uv run --project tools/docsync docsync kiro --prune
uv run --project tools/docsync docsync agentskills
uv run --project tools/docsync docsync anthropic --prune
```

### CLI options

| Option      | Description                                                           |
| ----------- | --------------------------------------------------------------------- |
| `source`    | `kiro`, `agentskills` or `anthropic` (required)                       |
| `--dry-run` | Report changes without writing; exits 1 when updates are pending      |
| `--prune`   | Delete local pages the source no longer publishes (not `agentskills`) |
| `--root`    | Repository root holding the mirror (default: auto-discovered)         |

## Sources

### kiro

The sitemap is the source of truth: pages are only added or updated. Local files are
never deleted unless `--prune` is passed. Upstream serves Markdown, so the content is
mirrored verbatim.

Upstream moved the sections shared by every Kiro product out of `/docs/cli/` and up to
`/docs/<section>/`, so the mirror tracks two shapes: `/docs/cli/<rest>/` is mirrored as
`<rest>.md`, and `/docs/<section>/<rest>/` as `<section>/<rest>.md`. A relocated page
therefore keeps the local path it already had. `CLI_SECTIONS` in `sources/kiro.py` is
the only place the in-scope sections are listed; the other Kiro products (`crew`, `ide`,
`web`, `mobile`) and the cross-product `guides` tutorials are excluded.

A relocated page keeps answering HTTP 200 at its old `/docs/cli/` URL with a `# Moved`
stub in place of the documentation, so a page advertised under both forms is fetched
from the canonical top-level URL and written once.

### agentskills

The catalogue in `sources/agentskills/pages.py` is the only place a page enters or
leaves the mirror — there is no sitemap crawl and no tree listing, because the set is
stable and small. Upstream `.mdx` is converted to plain Markdown: prose is copied
verbatim, while frontmatter becomes a title, callouts become blockquotes, tab groups
become labelled blocks, and layout-only wrappers are dropped. Cross-references between
mirrored pages become relative file links.

The upstream documentation is licensed CC-BY-4.0; attribution lives in
`references/agentskills/PROVENANCE.md`. A page that cannot be fetched or converted exits
1 and suppresses the marker write, so a partial mirror is never recorded as a successful
sync.

### anthropic

Discovery reads the published `llms.txt` catalogue, which lists every documentation page
as a Markdown link to its `.md` form — the same kind of enumeration the kiro sitemap
provides, so `--prune` applies here too. Two selection rules keep the mirror to the part
this repository needs: everything under `build-with-claude/prompt-engineering/` is taken
by prefix, so a per-model guide added with a new model release is picked up without a
code change, and the pages listed in `TRACKED_PAGES` are taken by exact slug because
their section siblings are irrelevant to prompting.

A tracked slug that leaves the catalogue raises `ValueError`, which the CLI reports as
an error exit rather than a traceback: the page was chosen deliberately, so its removal
is a decision to re-take rather than a diff to mirror. Upstream serves Markdown with a
YAML frontmatter block naming the canonical URL, so the identity transform applies and
every mirrored file is self-attributing. A page that fails to download invalidates the
run and suppresses the marker, so a partial mirror is never recorded as a success.

The marker and the hand-maintained `PROVENANCE.md` sit at the skill root rather than
inside the mirror directory, because pruning walks that directory for every `.md` file
and would report a companion file there as an orphan.

## Adding a source

Implement `DocSource` (`docsync/sources/base.py`) and register it in
`docsync/sources/__init__.py`. The contract is four methods and two policy flags:

| Member            | Purpose                                                        |
| ----------------- | -------------------------------------------------------------- |
| `mirror_paths`    | Where the pages and the sync marker live                       |
| `discover`        | Which pages exist upstream, as `Page(url, relative_path)`      |
| `provenance`      | Marker entries recording the upstream identity                 |
| `transform`       | Optional content rewrite; defaults to mirroring bytes verbatim |
| `supports_prune`  | Whether local files can be recognised as no longer published   |
| `strict_failures` | Whether one unmirrorable page invalidates the whole run        |

Page content is bytes from the fetch to the write, so the hash that classifies a page as
new, updated or unchanged is taken over exactly the bytes that land on disk. A source
that needs text decodes inside its own `transform` and hands bytes back.

A source whose discovery enumerates the upstream sets `supports_prune = True` and
delegates `prune` to `prune_orphans` in `docsync/orphans.py`, which walks the mirror and
reports or deletes every path the run did not discover. The default `prune` on
`DocSource` reports no orphans, which is the honest answer for a fixed catalogue.

## Output

```
  + NEW: chat/subagents.md
  ~ UPDATED: hooks.md
  - ORPHAN: chat/old-page.md (would remove with --prune)

[DRY RUN] New: 1, Updated: 1, Unchanged: 96, Failed: 0, Orphans: 1
```

A successful non-dry run rewrites `.last-sync.json`, which the
`driftcheck-hook-refs-freshness` hook reads to warn when a mirror goes stale.

## Development

```bash
make lint        # ruff format + ruff check --fix + isort
make code-check  # complexipy + mypy (strict)
make test        # pytest
make all         # setup + clean + lint + code-check + test
```
