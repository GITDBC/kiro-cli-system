"""
Convert Mintlify-flavoured MDX into plain Markdown.

The mirror is faithful: prose is copied verbatim. Only the presentation
components that a plain Markdown reader would render as noise are
translated. Frontmatter becomes a title and a lead paragraph, callouts
become blockquotes, tab groups become labelled blocks, layout-only
wrappers disappear, and cross-references between mirrored pages become
relative file links. A component outside the known set is passed through
untouched so that nothing is lost silently.
"""

# Standard libraries
import re
import textwrap
from typing import Final

# Own modules
from docsync.sources.agentskills.pages import ROUTE_TO_FILENAME

FRONTMATTER_FENCE: Final[str] = "---"

# Callouts carry meaning, so they survive as labelled blockquotes.
CALLOUT_TAGS: Final[frozenset[str]] = frozenset(
    {"Tip", "Note", "Warning", "Info", "Check", "Danger"}
)

# Layout wrappers carry styling only, so the tags are dropped and their
# content is promoted to the surrounding flow.
LAYOUT_TAGS: Final[frozenset[str]] = frozenset(
    {
        "Accordion",
        "AccordionGroup",
        "Card",
        "CardGroup",
        "Columns",
        "Frame",
        "Steps",
        "Tabs",
    }
)

OPEN_TAG: Final[re.Pattern[str]] = re.compile(
    r"^\s*<(?P<tag>[A-Z][A-Za-z]*)(?P<attrs>[^>]*)>\s*$"
)
CLOSE_TAG: Final[re.Pattern[str]] = re.compile(r"^\s*</(?P<tag>[A-Z][A-Za-z]*)>\s*$")
TITLE_ATTR: Final[re.Pattern[str]] = re.compile(r'title="(?P<title>[^"]*)"')
FRONTMATTER_ENTRY: Final[re.Pattern[str]] = re.compile(
    r"^(?P<key>[A-Za-z][A-Za-z0-9_-]*):\s*(?P<value>.*)$"
)
INTERNAL_LINK: Final[re.Pattern[str]] = re.compile(
    r"\]\((?P<route>/[A-Za-z0-9._/-]*)(?P<fragment>#[^)\s]*)?\)"
)
BLANK_RUN: Final[re.Pattern[str]] = re.compile(r"\n{3,}")


def convert_mdx(text: str) -> str:
    """
    Convert one MDX page into plain Markdown.

    Args:
        text: Raw contents of the upstream .mdx file.

    Returns:
        Markdown document ending in a single newline.

    Raises:
        ValueError: If the frontmatter block is left unclosed.
    """
    front, body = split_frontmatter(text)
    converted = convert_components(body.splitlines())
    document = rewrite_internal_links("\n".join(converted))
    return assemble(front, document)


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """
    Separate the YAML frontmatter from the document body.

    Only the flat scalar entries the upstream pages use are parsed;
    surrounding double quotes are stripped from the values.

    Args:
        text: Raw contents of the upstream .mdx file.

    Returns:
        Tuple of the frontmatter entries and the remaining body.

    Raises:
        ValueError: If the opening fence has no closing fence.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_FENCE:
        return {}, text
    front: dict[str, str] = {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONTMATTER_FENCE:
            return front, "\n".join(lines[index + 1 :])
        entry = FRONTMATTER_ENTRY.match(line)
        if entry is not None:
            front[entry.group("key")] = entry.group("value").strip().strip('"')
    message = "malformed frontmatter: the opening fence has no closing fence."
    raise ValueError(message)


def convert_components(lines: list[str]) -> list[str]:
    """
    Translate the MDX components of a document body.

    Args:
        lines: Body lines of the upstream page.

    Returns:
        Body lines in plain Markdown.
    """
    state = _ConversionState()
    for line in lines:
        state.feed(line)
    return state.finish()


def rewrite_internal_links(text: str) -> str:
    """
    Point cross-references at the local mirror files.

    Routes outside the mirrored set keep their upstream form, since no
    local file could serve them.

    Args:
        text: Markdown document.

    Returns:
        Document whose links to mirrored pages are relative filenames.
    """

    def replace(match: re.Match[str]) -> str:
        filename = ROUTE_TO_FILENAME.get(match.group("route"))
        if filename is None:
            return match.group(0)
        return f"]({filename}{match.group('fragment') or ''})"

    return INTERNAL_LINK.sub(replace, text)


def assemble(front: dict[str, str], document: str) -> str:
    """
    Join the frontmatter heading and the converted body.

    Args:
        front: Frontmatter entries of the upstream page.
        document: Converted body.

    Returns:
        Markdown document ending in a single newline.
    """
    sections: list[str] = []
    title = front.get("title")
    if title:
        sections.append(f"# {title}")
    description = front.get("description")
    if description:
        sections.append(description)
    body = document.strip()
    if body:
        sections.append(body)
    return BLANK_RUN.sub("\n\n", "\n\n".join(sections)).strip() + "\n"


class _ConversionState:
    """
    Line-by-line component conversion of one document body.

    A tab body is buffered so that it can be dedented as a block once
    its closing tag arrives; a callout body is quoted as it streams.

    Attributes:
        lines: Converted output collected so far.
    """

    def __init__(self) -> None:
        """Start with an empty document and no open component."""
        self.lines: list[str] = []
        self._callout: str | None = None
        self._tab_body: list[str] | None = None

    def feed(self, line: str) -> None:
        """
        Consume one body line.

        Args:
            line: Body line of the upstream page.
        """
        if self._closes_a_component(line):
            return
        if self._tab_body is not None:
            self._tab_body.append(line)
            return
        if self._callout is not None:
            self.lines.append(f"> {line}".rstrip())
            return
        self._open_or_copy(line)

    def finish(self) -> list[str]:
        """
        Return the converted body.

        Returns:
            Converted body lines.
        """
        if self._tab_body is not None:
            self._flush_tab_body()
        return self.lines

    def _closes_a_component(self, line: str) -> bool:
        """
        Handle a closing tag of the component currently open.

        Args:
            line: Body line of the upstream page.

        Returns:
            True when the line was a closing tag and was consumed.
        """
        close = CLOSE_TAG.match(line)
        if close is None:
            return False
        tag = close.group("tag")
        if self._tab_body is not None and tag == "Tab":
            self._flush_tab_body()
            return True
        if self._tab_body is not None:
            return False
        if tag == self._callout:
            self._callout = None
            self.lines.append("")
            return True
        if self._callout is None and tag in LAYOUT_TAGS:
            self.lines.append("")
            return True
        return False

    def _open_or_copy(self, line: str) -> None:
        """
        Open a component, drop a wrapper, or copy the line through.

        Args:
            line: Body line of the upstream page.
        """
        opening = OPEN_TAG.match(line)
        if opening is None:
            self.lines.append(line)
            return
        tag = opening.group("tag")
        attrs = opening.group("attrs")
        if attrs.rstrip().endswith("/"):
            return
        if tag in {"Tab", "Step"}:
            self._start_tab(attrs)
            return
        if tag in CALLOUT_TAGS:
            self._callout = tag
            self.lines.extend(["", f"> **{tag}**", ">"])
            return
        if tag in LAYOUT_TAGS:
            self.lines.append("")
            return
        self.lines.append(line)

    def _start_tab(self, attrs: str) -> None:
        """
        Emit the label of a tab and start buffering its body.

        Args:
            attrs: Attribute text of the opening tag.
        """
        title = TITLE_ATTR.search(attrs)
        self.lines.append("")
        if title is not None:
            self.lines.extend([f"**{title.group('title')}**", ""])
        self._tab_body = []

    def _flush_tab_body(self) -> None:
        """Dedent the buffered tab body and append it to the output."""
        body = textwrap.dedent("\n".join(self._tab_body or []))
        self.lines.extend([*body.splitlines(), ""])
        self._tab_body = None
