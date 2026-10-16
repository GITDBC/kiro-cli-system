"""
Token counting, behind a one-implementation seam.

``Counter`` exists so a second backend can be added later without
touching the model. Exactly one implementation ships: ``TiktokenCounter``
over ``o200k_base``. There is deliberately no Anthropic backend and no
``--exact`` flag — this repository has no API key, and an unusable code
path is worse than an absent one.

Why not ``len(bytes) / 4``: measured bytes-per-token across this
repository's always-on files ranges 3.94 to 5.81, so the shortcut
reorders the cost ranking. Prettier-padded Markdown tables tokenize
cheaply and would flatter themselves at the top of a reduction backlog.

Why ``o200k_base`` is settled rather than a choice: measured against
``cl100k_base`` on the same files the two differ by at most 1.1%, well
inside the approximation error the reports already declare.
"""

# Standard libraries
import logging
from pathlib import Path
from typing import Final, Protocol

# 3pps
import tiktoken

logger = logging.getLogger(__name__)

ENCODING_NAME: Final[str] = "o200k_base"

# Backend identifier printed in every report footer and recorded in the
# committed budget, so a figure can never be compared across backends
# without the mismatch being visible.
BACKEND: Final[str] = f"tiktoken/{ENCODING_NAME}"


class Counter(Protocol):
    """
    Anything able to approximate the token count of some text.

    The protocol is the seam an exact backend would plug into. It is
    intentionally minimal: a backend that needs a model name, a request
    budget or an event loop does not belong behind it.
    """

    @property
    def backend(self) -> str:
        """Return the backend identifier for report provenance."""
        ...

    @property
    def version(self) -> str:
        """Return the tokenizer library version."""
        ...

    def count(self, text: str) -> int:
        """
        Count the tokens of a string.

        Args:
            text: Text to tokenize.

        Returns:
            Approximate token count.
        """
        ...

    def count_path(self, path: Path) -> int:
        """
        Count the tokens of a file's contents.

        Args:
            path: File to read and tokenize.

        Returns:
            Approximate token count, 0 for a missing file.
        """
        ...


class TiktokenCounter:
    """
    Deterministic offline counter over the ``o200k_base`` encoding.

    Deterministic matters more than exact here: the tool's primary job
    is delta tracking, and a deterministic tokenizer makes a before/after
    difference trustworthy even while the absolute total carries an
    unquantified error.

    Per-path results are memoized because the always-on files are
    resolved once per agent and this repository has ten agents, so
    ``COMMON.md`` would otherwise be tokenized ten times per run.
    """

    def __init__(self) -> None:
        """Create a counter with a lazily loaded encoding."""
        self._encoding: tiktoken.Encoding | None = None
        self._path_cache: dict[Path, int] = {}

    @property
    def backend(self) -> str:
        """Return the backend identifier for report provenance."""
        return BACKEND

    @property
    def version(self) -> str:
        """Return the installed tiktoken version."""
        return str(tiktoken.__version__)

    @property
    def encoding(self) -> tiktoken.Encoding:
        """
        Return the encoding, loading it on first use.

        Returns:
            The ``o200k_base`` encoding.
        """
        if self._encoding is None:
            self._encoding = tiktoken.get_encoding(ENCODING_NAME)
        return self._encoding

    def count(self, text: str) -> int:
        """
        Count the tokens of a string.

        Args:
            text: Text to tokenize.

        Returns:
            Approximate token count, 0 for empty text.
        """
        if not text:
            return 0
        return len(self.encoding.encode(text, disallowed_special=()))

    def count_path(self, path: Path) -> int:
        """
        Count the tokens of a file's contents, memoized per path.

        A missing or unreadable file counts as 0 rather than raising:
        resource references are validated by ``driftcheck``, and this
        tool measures quantities instead of asserting structure.

        Args:
            path: File to read and tokenize.

        Returns:
            Approximate token count, 0 when the file cannot be read.
        """
        resolved = path.resolve()
        cached = self._path_cache.get(resolved)
        if cached is not None:
            return cached
        try:
            text = resolved.read_text(encoding="utf-8", errors="replace")
        except OSError as error:
            logger.warning("Cannot read %s: %s.", resolved, error)
            text = ""
        tokens = self.count(text)
        self._path_cache[resolved] = tokens
        return tokens
