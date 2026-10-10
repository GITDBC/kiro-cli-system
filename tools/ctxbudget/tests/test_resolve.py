"""Tests for resource resolution and repository-root discovery."""

# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from ctxbudget.resolve import (
    find_repo_root,
    frontmatter_summary,
    is_repo_root,
    load_agent_configs,
    reference_files,
    relative_label,
    resolve_agent,
    skill_dirs,
    split_frontmatter,
    steering_files,
)
from ctxbudget.types import AgentConfig, ArtifactKind
from tests.helpers import write, write_agent


def _config(tree: Path, name: str) -> AgentConfig:
    """
    Fetch one parsed config from a tree by slug.

    Args:
        tree: Repository root.
        name: Agent slug.

    Returns:
        The parsed config.
    """
    return next(config for config in load_agent_configs(tree) if config.slug == name)


def test_is_repo_root_requires_both_markers(tmp_path: Path) -> None:
    """Report a directory as the root only when both markers exist."""
    (tmp_path / ".kiro").mkdir()
    assert not is_repo_root(tmp_path)
    (tmp_path / "tools").mkdir()
    assert is_repo_root(tmp_path)


def test_find_repo_root_walks_upward(tree: Path) -> None:
    """Find the root from a nested starting point."""
    assert find_repo_root(tree / ".kiro" / "skills" / "one") == tree


def test_find_repo_root_raises_without_markers(tmp_path: Path) -> None:
    """Raise a ValueError naming --root when discovery fails."""
    with pytest.raises(ValueError, match="--root"):
        find_repo_root(tmp_path)


def test_load_agent_configs_skips_unusable_files(tree: Path) -> None:
    """Skip malformed JSON and non-object configs without failing."""
    write(tree / ".kiro" / "agents" / "broken.json", "{not json")
    write(tree / ".kiro" / "agents" / "list.json", "[]")
    slugs = [config.slug for config in load_agent_configs(tree)]
    assert slugs == ["alpha", "beta"]


def test_load_agent_configs_without_directory(tmp_path: Path) -> None:
    """Return nothing when the agent directory is absent."""
    assert load_agent_configs(tmp_path) == ()


def test_agent_name_falls_back_to_stem(tree: Path) -> None:
    """Use the filename when the config declares no usable name."""
    write(tree / ".kiro" / "agents" / "gamma.json", '{"model": "claude-opus-5"}')
    assert _config(tree, "gamma").name == "gamma"


def test_prompt_is_resolved_relative_to_the_config(tree: Path) -> None:
    """Resolve the prompt against the config directory, not the root."""
    resolved = resolve_agent(_config(tree, "alpha"), tree)
    prompts = [entry for entry in resolved.entries if entry.kind is ArtifactKind.PROMPT]
    assert [entry.label for entry in prompts] == [".kiro/prompts/alpha.md"]


def test_missing_prompt_is_recorded_as_unresolved(tree: Path) -> None:
    """Record a prompt that resolves to nothing instead of failing."""
    write_agent(tree, "gamma", prompt="file://../prompts/absent.md")
    resolved = resolve_agent(_config(tree, "gamma"), tree)
    assert resolved.unresolved == ("file://../prompts/absent.md",)
    assert not [
        entry for entry in resolved.entries if entry.kind is ArtifactKind.PROMPT
    ]


def test_file_glob_expands_and_deduplicates(tree: Path) -> None:
    """Expand a file:// glob once, even when a member is also listed."""
    resolved = resolve_agent(_config(tree, "beta"), tree)
    files = [
        entry.label for entry in resolved.entries if entry.kind is ArtifactKind.FILE
    ]
    assert files == [".kiro/steering/COMMON.md", ".kiro/steering/extra.md"]


def test_skill_glob_yields_frontmatter_entries(tree: Path) -> None:
    """Count a skill:// resource as its frontmatter, not its body."""
    resolved = resolve_agent(_config(tree, "alpha"), tree)
    skills = [
        entry
        for entry in resolved.entries
        if entry.kind is ArtifactKind.SKILL_FRONTMATTER
    ]
    assert [entry.label for entry in skills] == [
        ".kiro/skills/one/SKILL.md#frontmatter",
        ".kiro/skills/two/SKILL.md#frontmatter",
    ]
    assert skills[0].text == "one\nFirst fixture skill."


def test_non_path_skill_resources_are_skipped(tree: Path) -> None:
    """Leave home-directory and bare-name skill:// forms alone."""
    write_agent(
        tree,
        "gamma",
        resources=["skill://bare-name", "skill://~/.kiro/skills/x/SKILL.md"],
    )
    resolved = resolve_agent(_config(tree, "gamma"), tree)
    assert not [
        entry
        for entry in resolved.entries
        if entry.kind is ArtifactKind.SKILL_FRONTMATTER
    ]


def test_unmatched_resource_is_recorded(tree: Path) -> None:
    """Record a resource that matches nothing as unresolved."""
    write_agent(tree, "gamma", resources=["file://.kiro/steering/absent.md"])
    resolved = resolve_agent(_config(tree, "gamma"), tree)
    assert "file://.kiro/steering/absent.md" in resolved.unresolved


def test_file_resources_resolve_against_the_workspace_root(tree: Path) -> None:
    """
    Refuse to credit the config-relative form Kiro does not honour.

    The regression this locks in: ``file://../steering/COMMON.md`` names
    a real file when based on ``.kiro/agents/``, so a config-relative
    base counted it as a cost while Kiro resolved it outside the
    workspace and loaded nothing.
    """
    write(tree / ".kiro" / "prompts" / "gamma.md", "g")
    write_agent(tree, "gamma", resources=["file://../steering/COMMON.md"])
    resolved = resolve_agent(_config(tree, "gamma"), tree)
    assert resolved.unresolved == ("file://../steering/COMMON.md",)
    assert not [entry for entry in resolved.entries if entry.kind is ArtifactKind.FILE]


def test_knowledge_base_counts_metadata_only(tree: Path) -> None:
    """Charge a knowledge base its name and description, nothing else."""
    resolved = resolve_agent(_config(tree, "beta"), tree)
    bases = [
        entry for entry in resolved.entries if entry.kind is ArtifactKind.KNOWLEDGE_BASE
    ]
    assert [entry.label for entry in bases] == ["knowledgeBase://FixtureDocs"]
    assert bases[0].text == "FixtureDocs\nfixture knowledge base"
    assert bases[0].path is None


def test_knowledge_base_without_name_is_ignored(tree: Path) -> None:
    """Ignore a knowledge-base object carrying no usable name."""
    write_agent(tree, "gamma", resources=[{"type": "knowledgeBase"}, {"type": "x"}, 7])
    resolved = resolve_agent(_config(tree, "gamma"), tree)
    assert not [
        entry for entry in resolved.entries if entry.kind is ArtifactKind.KNOWLEDGE_BASE
    ]


def test_resources_field_of_wrong_shape_is_ignored(tree: Path) -> None:
    """Treat a non-list resources field as an empty one."""
    write(tree / ".kiro" / "prompts" / "gamma.md", "g")
    write_agent(tree, "gamma", resources="file://.kiro/steering/COMMON.md")
    resolved = resolve_agent(_config(tree, "gamma"), tree)
    kinds = [
        entry.kind
        for entry in resolved.entries
        if entry.kind is not ArtifactKind.STEERING_AUTO
    ]
    assert kinds == [ArtifactKind.PROMPT]


def test_steering_is_injected_and_deduped_against_declarations(tree: Path) -> None:
    """
    Inject every steering file, skipping one the agent already declares.

    Steering reaches a session by workspace auto-load rather than by
    declaration. ``alpha`` declares one of the two files, so only the
    other arrives as an auto-injection and neither is charged twice.
    """
    resolved = resolve_agent(_config(tree, "alpha"), tree)
    auto = [
        entry for entry in resolved.entries if entry.kind is ArtifactKind.STEERING_AUTO
    ]
    assert [entry.label for entry in auto] == [".kiro/steering/extra.md"]


def test_a_file_is_never_charged_twice_to_one_agent(tree: Path) -> None:
    """Keep a declared steering file to a single entry."""
    resolved = resolve_agent(_config(tree, "alpha"), tree)
    labels = [entry.label for entry in resolved.entries]
    assert labels.count(".kiro/steering/COMMON.md") == 1


def test_steering_and_skill_listings_are_sorted(tree: Path) -> None:
    """List steering files and skill directories in a stable order."""
    assert [path.name for path in steering_files(tree)] == ["COMMON.md", "extra.md"]
    assert [path.name for path in skill_dirs(tree)] == ["one", "two"]


def test_listings_tolerate_absent_directories(tmp_path: Path) -> None:
    """Return nothing rather than raising when a directory is absent."""
    assert steering_files(tmp_path) == ()
    assert skill_dirs(tmp_path) == ()
    assert reference_files(tmp_path) == ()


def test_skill_dirs_ignores_directories_without_a_skill_file(tree: Path) -> None:
    """Skip a skill directory that carries no SKILL.md."""
    (tree / ".kiro" / "skills" / "empty").mkdir()
    assert [path.name for path in skill_dirs(tree)] == ["one", "two"]


def test_reference_files_are_listed_recursively(tree: Path) -> None:
    """Find reference files at any depth under references/."""
    write(tree / ".kiro" / "skills" / "one" / "references" / "sub" / "x.md", "x")
    found = reference_files(tree / ".kiro" / "skills" / "one")
    assert [path.name for path in found] == ["deep.md", "x.md"]


def test_relative_label_falls_back_outside_the_tree(tree: Path, tmp_path: Path) -> None:
    """Label a path outside the tree with its absolute form."""
    outside = write(tmp_path / "outside.md", "x")
    assert relative_label(outside, tree) == str(outside)


def test_split_frontmatter_separates_block_and_body() -> None:
    """Return the block without fences and the body without leading gap."""
    front, body = split_frontmatter("---\nname: x\n---\n\n# Title\n\nbody\n")
    assert front == "name: x"
    assert body == "# Title\n\nbody"


def test_split_frontmatter_without_a_block() -> None:
    """Report no frontmatter and an untouched body."""
    assert split_frontmatter("# Title\n") == ("", "# Title\n")


def test_split_frontmatter_with_an_unterminated_block() -> None:
    """Treat an unclosed block as absent rather than swallowing the file."""
    assert split_frontmatter("---\nname: x\n") == ("", "---\nname: x\n")


def test_frontmatter_summary_takes_name_and_description() -> None:
    """Count only the two fields Kiro injects at startup."""
    text = "---\nname: x\ndescription: A skill.\ncolor: green\n---\n\nbody\n"
    assert frontmatter_summary(text) == "x\nA skill."


def test_frontmatter_summary_falls_back_on_bad_yaml() -> None:
    """Count the raw block when it cannot be parsed."""
    text = "---\nname: [unclosed\n---\n\nbody\n"
    assert frontmatter_summary(text) == "name: [unclosed"


def test_frontmatter_summary_falls_back_on_a_scalar_block() -> None:
    """Count the raw block when it is not a mapping."""
    assert frontmatter_summary("---\njust a string\n---\n\nbody\n") == "just a string"


def test_frontmatter_summary_without_a_block() -> None:
    """Charge nothing when a document has no frontmatter."""
    assert frontmatter_summary("# Title\n") == ""
