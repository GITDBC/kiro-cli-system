# Provenance of the vendored Kiro CLI documentation

`references/` is a **vendored mirror** of the official Kiro CLI documentation. It exists
so that agents can answer Kiro CLI questions from current upstream documentation without
a network round trip, and it backs the `KiroCLIDocs` knowledge base.

## Do not hand-edit these files

Every `.md` file under `references/` is fetched verbatim. A local edit is lost on the
next sync and, worse, makes the mirror silently disagree with the documentation it is
supposed to reproduce.

- To bring an upstream change in, run `make sync-docs` from the repository root. This
  also refreshes the `.last-sync.json` marker, which records the page total.
- To see whether the mirror has fallen behind, run `make sync-docs-check`; it is a
  network dry run that exits non-zero when an update is pending.
- To also delete pages the sitemap no longer advertises, or that the source now
  excludes, run `uv run --project tools/docsync docsync kiro --prune`. Nothing is
  removed without `--prune`.

A startup hook performs a cheap local age check by reading `.last-sync.json`; it never
touches the network. The `KiroCLIDocs` knowledge base is indexed with
`autoUpdate: false`, so a sync that changes files leaves it stale until it is re-indexed
by hand.

`SKILL.md` and this file are the hand-maintained files of the skill, and the sync never
touches either. Both sit at the skill root rather than inside `references/`, because
pruning walks that directory for every `.md` file and would report a companion file
there as an orphan.

## Upstream source

| Property      | Value                                        |
| ------------- | -------------------------------------------- |
| Documentation | https://kiro.dev/docs/                       |
| Discovery     | https://kiro.dev/sitemap.xml                 |
| Page form     | `https://kiro.dev/docs/<slug>.md` (Markdown) |
| Fetch date    | 2026-10-16                                   |
| Sync tool     | `tools/docsync` (`make sync-docs`)           |
| Sync marker   | `.last-sync.json` at the skill root          |
| Page count    | 84 after the scope reduction of 2026-10-16   |

### Layout

Upstream moved the sections shared by every Kiro product from `/docs/cli/<section>/` to
top-level `/docs/<section>/`. A page below `/docs/cli/` keeps its position with the
section stripped; a top-level section keeps its own name:

| Upstream URL              | Local path                   |
| ------------------------- | ---------------------------- |
| `/docs/cli/chat/context/` | `references/chat/context.md` |
| `/docs/mcp/usage/`        | `references/mcp/usage.md`    |
| `/docs/hooks/`            | `references/hooks.md`        |

A relocated page still answers HTTP 200 at its old `/docs/cli/` URL with a `# Moved`
stub, so only the sitemap can tell a live page from a relocated one; discovery is
therefore sitemap-driven and the canonical URL wins when both forms are advertised.

### Selection rules

Both rules are encoded in `tools/docsync/docsync/sources/kiro.py`:

- **Sections**: everything below `/docs/cli/`, plus the top-level sections listed in
  `CLI_SECTIONS`. The sections of the other Kiro products (`crew`, `ide`, `web`,
  `mobile`) and the cross-product `guides` tutorials are out of scope.
- **Exclusions**: mirror paths listed in `EXCLUDED_PATHS`, each excluding its page and
  everything below it, whichever URL form advertised it. They drop what an agent system
  for Python engineering work does not consult: billing, enterprise administration,
  upgrade guides from other products, powers, cloud sessions, the ACP, voice,
  autocomplete, full-screen and terminal-UI interfaces, GovCloud models, the enterprise
  MCP registry, installation and sign-in pages, the 2.x reference and the 2.x-to-3.0
  migration guides. The 3.0 pages on agent config, permissions, new features and tangent
  conversations are kept.

## Licence and redistribution

The documentation is published on kiro.dev without an accompanying open-content licence
grant in the mirrored pages. It is treated as third-party material held as a local
verbatim cache for internal reference: reproduced unmodified, not presented as this
repository's own documentation, and subject to re-checking the terms before this
repository is made public or redistributed.

### Modifications applied

None. The sync writes the upstream bytes unchanged, which the content-hash comparison
relies on, and `.kiro/skills/kiro-cli-reference/references/` is listed in
`.prettierignore` so that the repository formatter leaves it alone.
