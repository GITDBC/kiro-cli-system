"""
Orphan detection shared by the sources that can recognise a deletion.

A source whose discovery enumerates the upstream — a sitemap crawl, a
catalogue listing — can tell that a local file is no longer published,
and the rule for acting on that is identical for all of them: walk the
mirror, treat every path absent from the discovered set as an orphan,
and either report it or delete it. The rule lives here rather than in
one source so that a second enumerating source inherits it instead of
copying it.

The reporting strings are part of the tool's observable output, so they
are kept exactly as the first source emitted them.
"""

# Own modules
from docsync.types import MirrorPaths, Slug


def prune_orphans(paths: MirrorPaths, known_slugs: set[Slug], dry_run: bool) -> int:
    """
    Remove local reference files the source no longer publishes.

    Args:
        paths: Mirror locations.
        known_slugs: Slugs the current run discovered upstream.
        dry_run: If True, only report orphans without deleting.

    Returns:
        Number of orphan files detected.
    """
    if not paths.refs_dir.is_dir():
        return 0
    orphan_count = 0
    for local_file in sorted(paths.refs_dir.rglob("*.md")):
        slug = local_file.relative_to(paths.refs_dir).with_suffix("").as_posix()
        if slug not in known_slugs:
            orphan_count += 1
            if dry_run:
                print(f"  - ORPHAN: {slug}.md (would remove with --prune)")
            else:
                local_file.unlink()
                print(f"  - PRUNED: {slug}.md")
    return orphan_count
