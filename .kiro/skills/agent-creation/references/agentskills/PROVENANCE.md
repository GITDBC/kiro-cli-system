# Provenance of the vendored Agent Skills documentation

This directory is a **vendored mirror** of the official Agent Skills standard
documentation. It exists so that the `agent-creation` skill can cite the upstream
specification and its skill-authoring guides without a network round trip.

## Do not hand-edit these files

Every `.md` file in this directory is generated. A local edit is lost on the next sync
and, worse, makes the mirror silently disagree with the standard it is supposed to
reproduce.

- To correct the content, open a pull request against the upstream repository.
- To bring an upstream change in, run `make sync-agentskills` from the repository root.
- To see whether the mirror has fallen behind, run `make sync-agentskills-check`; it
  exits non-zero when an update is pending.

`PROVENANCE.md` is the one hand-maintained file here, and the sync never touches it.

## Upstream source

| Property              | Value                                                             |
| --------------------- | ----------------------------------------------------------------- |
| Repository            | https://github.com/agentskills/agentskills                        |
| Branch                | `main`                                                            |
| Raw URL prefix        | `https://raw.githubusercontent.com/agentskills/agentskills/main/` |
| Fetch date            | 2026-09-04                                                        |
| Documentation licence | CC-BY-4.0 (Creative Commons Attribution 4.0 International)        |
| Sync tool             | `tools/docsync` (`make sync-agentskills`)                         |
| Sync marker           | `.last-sync.json` in this directory                               |

### Vendored pages

| Local file                   | Upstream source path                              |
| ---------------------------- | ------------------------------------------------- |
| `specification.md`           | `docs/specification.mdx`                          |
| `quickstart.md`              | `docs/skill-creation/quickstart.mdx`              |
| `best-practices.md`          | `docs/skill-creation/best-practices.mdx`          |
| `optimizing-descriptions.md` | `docs/skill-creation/optimizing-descriptions.mdx` |
| `evaluating-skills.md`       | `docs/skill-creation/evaluating-skills.mdx`       |
| `using-scripts.md`           | `docs/skill-creation/using-scripts.mdx`           |


The rest of the upstream documentation set is deliberately out of scope: the client
implementation guide targets authors of skill-loading clients rather than skill authors,
and the landing, client-listing and navigation pages carry no reusable guidance.

## Attribution

The vendored pages are documentation from the **Agent Skills** project by the
agentskills authors, retrieved from
<https://github.com/agentskills/agentskills> and licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/). Attribution 4.0
International permits redistribution and adaptation, including commercially, provided
credit is given and modifications are indicated. It carries no share-alike obligation,
so the surrounding repository keeps its own licence.

Upstream source code is licensed Apache-2.0. No upstream code is vendored here.

### Modifications applied

The pages are reproduced faithfully — prose is copied verbatim, never rewritten or
summarised. These mechanical presentation changes are applied by the sync tool so that
the pages read correctly as plain Markdown:

- YAML frontmatter is replaced by an `H1` title and the description as a lead paragraph.
- Callout components (`Tip`, `Note`) become labelled blockquotes.
- Tab groups (`Tabs` / `Tab`) become bold labels followed by their dedented bodies.
- Layout-only wrappers (`Card`) are dropped; their content is kept in place.
- Cross-references between the vendored pages point at the local files, since the mirror
  is flat (`/skill-creation/evaluating-skills` becomes `evaluating-skills.md`).

Links to upstream routes that are not vendored keep their original site-relative form.
