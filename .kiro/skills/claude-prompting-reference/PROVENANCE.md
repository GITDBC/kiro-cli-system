# Provenance of the vendored Anthropic prompting documentation

`references/` is a **vendored mirror** of Anthropic's official prompting documentation.
It exists so that prompt, steering and skill work in this repository can cite current
upstream guidance without a network round trip.

## Do not hand-edit these files

Every `.md` file under `references/` is fetched verbatim. A local edit is lost on the
next sync and, worse, makes the mirror silently disagree with the guidance it is
supposed to reproduce.

- To bring an upstream change in, run `make sync-anthropic` from the repository root.
- To see whether the mirror has fallen behind, run `make sync-anthropic-check`; it exits
  non-zero when an update is pending.
- To also delete pages the upstream catalogue no longer advertises, run
  `uv run --project tools/docsync docsync anthropic --prune`.

`SKILL.md` and this file are the hand-maintained files of the skill, and the sync never
touches either. Both sit at the skill root rather than inside `references/`, because
pruning walks that directory for every `.md` file and would report a companion file
there as an orphan.

## Upstream source

| Property        | Value                                   |
| --------------- | --------------------------------------- |
| Documentation   | https://platform.claude.com/docs/       |
| Catalogue       | https://platform.claude.com/llms.txt    |
| Page URL prefix | `https://platform.claude.com/docs/en/`  |
| Fetch date      | 2026-11-16                              |
| Sync tool       | `tools/docsync` (`make sync-anthropic`) |
| Sync marker     | `.last-sync.json` at the skill root     |
| Page count      | 15 after the scope change of 2026-11-16 |

Each mirrored file keeps the upstream YAML frontmatter, whose `url` field records the
canonical page it was fetched from. That makes every file self-attributing regardless of
where it is read.

### Selection rules

The mirror is a subset of a much larger documentation set. Two rules, both encoded in
`tools/docsync/docsync/sources/anthropic.py`, decide what enters it:

- **By prefix**: the general pages under `build-with-claude/prompt-engineering/` (the
  overview and the best-practices guide). Per-model guides (`prompting-claude-<model>`)
  are skipped by this rule, so an upstream release never widens the mirror.
- **By exact slug**: the pages listed in `TRACKED_PAGES`: the Opus 5.5, Sonnet 5.5 and
  Haiku 5.5 prompting guides, plus prompting guidance whose section siblings are not, so
  a prefix rule would drag in unrelated material. A tracked slug that leaves the
  catalogue aborts the sync with an error instead of disappearing quietly.

The release-notes pages below sit under `models/`, whose other pages are not prompting
guidance:

| Tracked slug                             | Why it is tracked                                                                                                                          |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `models/haiku-5-5/whats-new-haiku-5-5`   | Adaptive thinking and `effort` control for Haiku 5.5, which the session effort policy depends on                                           |
| `models/opus-5-5/whats-new-opus-5-5`     | Breaking API changes and the `medium` default effort for Opus 5.5, which the session effort policy and `.kiro/settings/cli.json` depend on |
| `models/sonnet-5-5/whats-new-sonnet-5-5` | Breaking API changes and the `high` default effort for Sonnet 5.5, which the session effort policy and `.kiro/settings/cli.json` depend on |

Scope is limited to the models the agents run (Opus 5.5, Sonnet 5.5 and Haiku 5.5).
Their sibling overview and migration-guide pages are excluded because nothing in this
repository consumes them. The prompting guides for earlier generations (Opus 5, Sonnet
5, Opus 4.8) and for models no agent runs (Fable 5, 5.1, 5.2) are not mirrored;
`--prune` removes a local copy. Moving the agents to a new model means adding its slugs
to `TRACKED_PAGES`. The evaluation guide `test-and-evaluate/develop-tests` is not
tracked: nothing in this repository cites it.

Deliberately out of scope: the API reference, the SDK and deployment guides, the
use-case cookbooks, and the released system prompts. None is prompting guidance, and the
mirror is read as guidance.

## Licence and redistribution

Anthropic publishes this documentation on platform.claude.com without an accompanying
open-content licence grant, unlike the CC-BY-4.0 Agent Skills mirror vendored elsewhere
in this repository. The pages are therefore treated as third-party copyrighted material
held as a local verbatim cache for internal reference:

- The content is reproduced unmodified, with no summarising, rewriting or re-branding.
- It is not presented as this repository's own documentation.
- Making this repository public, or redistributing it outside the organisation, requires
  re-checking the terms before shipping the mirror with it.

### Modifications applied

None. The sync writes the upstream bytes unchanged, which is also what the content-hash
comparison relies on: the mirror is reformatted by no tool, and
`.kiro/skills/claude-prompting-reference/references/` is listed in `.prettierignore` so
that the repository formatter leaves it alone.
