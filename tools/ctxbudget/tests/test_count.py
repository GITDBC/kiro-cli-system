"""
Tests for the tiktoken counting backend.

These are the only tests that load a real tokenizer. Everything else
goes through ``FakeCounter``, which is what the ``Counter`` protocol
exists to allow.
"""

# Standard libraries
from pathlib import Path

# Own modules
from ctxbudget.count import BACKEND, ENCODING_NAME, TiktokenCounter


def test_backend_and_version_are_reported() -> None:
    """Name the encoding in the backend identifier, for provenance."""
    counter = TiktokenCounter()
    assert counter.backend == BACKEND == f"tiktoken/{ENCODING_NAME}"
    assert counter.version


def test_empty_text_costs_nothing() -> None:
    """Count empty text as zero without loading the encoding."""
    assert TiktokenCounter().count("") == 0


def test_counting_is_deterministic() -> None:
    """
    Produce the same figure twice for the same text.

    This is the property the whole tool rests on: absolute totals are
    approximate, so only a deterministic backend makes a before/after
    delta meaningful.
    """
    counter = TiktokenCounter()
    assert counter.count("a measured line of prose") == counter.count(
        "a measured line of prose"
    )


def test_bytes_over_four_would_disagree() -> None:
    """
    Show that the bytes/4 shortcut misranks two same-size strings.

    Padded table markup and prose of identical byte length tokenize
    differently, which is why the shortcut was rejected: it reorders the
    cost ranking that drives reduction work.
    """
    counter = TiktokenCounter()
    table = ("| aaa | bbb | ccc |" * 6)[:100]
    prose = ("reduction of measured context prose " * 6)[:100]
    assert len(table.encode()) == len(prose.encode()) == 100
    assert counter.count(table) != counter.count(prose)


def test_special_token_markup_is_counted_not_rejected() -> None:
    """
    Count text containing tokenizer control markup literally.

    Documentation in this repository quotes such markup, and a counter
    that raised on it would fail on exactly the files it must measure.
    """
    assert TiktokenCounter().count("before <|endoftext|> after") > 0


def test_counting_a_file_is_memoized(tmp_path: Path) -> None:
    """Read a path once, however many agents declare it."""
    counter = TiktokenCounter()
    path = tmp_path / "file.md"
    path.write_text("some words to count", encoding="utf-8")
    first = counter.count_path(path)
    path.write_text("entirely different content now", encoding="utf-8")
    assert counter.count_path(path) == first


def test_missing_file_costs_nothing(tmp_path: Path) -> None:
    """Count an unreadable file as zero, leaving verdicts to driftcheck."""
    assert TiktokenCounter().count_path(tmp_path / "absent.md") == 0


def test_unreadable_path_costs_nothing(tmp_path: Path) -> None:
    """Count a directory handed in as a file as zero."""
    assert TiktokenCounter().count_path(tmp_path) == 0
