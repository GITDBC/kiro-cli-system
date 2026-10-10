"""
Tests for the MDX to Markdown conversion.

Every case is an in-memory string: the converter performs no I/O, so the
suite is offline by construction.
"""

# 3pps
import pytest

# Own modules
from docsync.sources.agentskills.convert import (
    convert_mdx,
    rewrite_internal_links,
    split_frontmatter,
)

PAGE = """---
title: "Using scripts in skills"
sidebarTitle: "Using scripts"
description: "How to bundle executable scripts."
---

Intro paragraph.

<Tip>
Read agent execution traces.
</Tip>

<Card>
**Minimal example:**

```yaml
name: skill-name
```
</Card>

<Tabs sync={false}>
  <Tab title="uvx">
    Runs Python packages.

    ```bash
    uvx ruff check .
    ```
  </Tab>
</Tabs>

See [Evaluating skills](/skill-creation/evaluating-skills).
"""


def test_frontmatter_becomes_a_title_and_a_lead_paragraph() -> None:
    """The title heads the page and the description follows it."""
    markdown = convert_mdx(PAGE)
    assert markdown.startswith(
        "# Using scripts in skills\n\nHow to bundle executable scripts.\n"
    )
    assert "sidebarTitle" not in markdown


def test_callouts_become_labelled_blockquotes() -> None:
    """A Tip renders as a blockquote a plain reader can follow."""
    markdown = convert_mdx(PAGE)
    assert "> **Tip**\n>\n> Read agent execution traces." in markdown
    assert "<Tip>" not in markdown


def test_layout_wrappers_disappear_and_keep_their_content() -> None:
    """A Card contributes styling only, so only the tags are dropped."""
    markdown = convert_mdx(PAGE)
    assert "**Minimal example:**" in markdown
    assert "name: skill-name" in markdown
    assert "Card" not in markdown


def test_tabs_become_labelled_dedented_blocks() -> None:
    """Tab bodies are dedented so that fenced blocks stay fenced."""
    markdown = convert_mdx(PAGE)
    assert "**uvx**\n\nRuns Python packages." in markdown
    assert "\n```bash\nuvx ruff check .\n```" in markdown
    assert "Tabs" not in markdown


def test_links_to_mirrored_pages_become_relative_files() -> None:
    """Cross-references stay navigable inside the flat mirror."""
    assert "](evaluating-skills.md)" in convert_mdx(PAGE)


def test_links_to_unmirrored_routes_are_left_alone() -> None:
    """A route with no local file keeps its upstream form."""
    assert rewrite_internal_links("[Clients](/clients)") == "[Clients](/clients)"


def test_fragments_survive_the_link_rewrite() -> None:
    """An anchor still points inside the mirrored page."""
    rewritten = rewrite_internal_links("[Spec](/specification#description-field)")
    assert rewritten == "[Spec](specification.md#description-field)"


def test_inline_angle_brackets_are_preserved() -> None:
    """Prose such as `iteration-<N+1>/` is not mistaken for a tag."""
    markdown = convert_mdx("Rerun into `iteration-<N+1>/` next.\n")
    assert "`iteration-<N+1>/`" in markdown


def test_unknown_components_are_passed_through() -> None:
    """An unrecognised component is preserved instead of dropped."""
    markdown = convert_mdx("<Mermaid>\ngraph TD\n</Mermaid>\n")
    assert "<Mermaid>" in markdown
    assert "graph TD" in markdown


def test_a_page_without_frontmatter_is_converted_verbatim() -> None:
    """Absent frontmatter leaves the body as the whole document."""
    front, body = split_frontmatter("# Title\n\nBody.\n")
    assert front == {}
    assert body == "# Title\n\nBody.\n"


def test_unclosed_frontmatter_is_rejected() -> None:
    """A malformed page fails loudly rather than silently truncating."""
    with pytest.raises(ValueError, match="malformed frontmatter"):
        convert_mdx('---\ntitle: "Broken"\n\nBody.\n')


def test_conversion_ends_in_exactly_one_newline() -> None:
    """Trailing whitespace churn is normalized away."""
    markdown = convert_mdx(PAGE)
    assert markdown.endswith(".\n")
    assert "\n\n\n" not in markdown
