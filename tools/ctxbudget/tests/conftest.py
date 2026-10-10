"""Fixtures shared by the ctxbudget test suite."""

# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from ctxbudget.model import measure
from ctxbudget.types import Measurement
from tests.helpers import FakeCounter, build_tree


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    """
    Build the synthetic repository tree.

    Args:
        tmp_path: Pytest-provided temporary directory.

    Returns:
        Root of the synthetic repository.
    """
    return build_tree(tmp_path)


@pytest.fixture()
def counter() -> FakeCounter:
    """
    Provide the word-counting stand-in for the token backend.

    Returns:
        A fake counter.
    """
    return FakeCounter()


@pytest.fixture()
def measurement(tree: Path, counter: FakeCounter) -> Measurement:
    """
    Measure the synthetic tree.

    Args:
        tree: Root of the synthetic repository.
        counter: Word-counting backend.

    Returns:
        A measurement snapshot.
    """
    return measure(
        root=tree,
        counter=counter,
        with_references=False,
        calibration=None,
    )
