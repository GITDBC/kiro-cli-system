"""
Tests for per-model context-window resolution.

The window multiplies every calibration, so a wrong one is wrong by the
ratio of two windows: the 200K default this module replaced understated a
1M observation fivefold. These tests exist to make that failure mode
unreachable again, and they assert the documented figures rather than
the tool's own arithmetic.
"""

# Standard libraries
from pathlib import Path

# Own modules
from ctxbudget.windows import MODEL_WINDOWS, agent_windows, window_for_model
from tests.helpers import write, write_agent


def test_opus_five_is_a_one_million_token_window() -> None:
    """
    Hold the figure the vendored docs state for this project's model.

    ``models.md`` lists Claude Opus 5 at 1M in its quick comparison, and
    both agents that run it would have their observations divided by five
    if this regressed to the 200K it once defaulted to.
    """
    assert window_for_model("claude-opus-5") == 1_000_000
    assert window_for_model("claude-sonnet-5") == 1_000_000


def test_two_hundred_thousand_token_models_are_not_inflated() -> None:
    """Keep the smaller windows small: the table is not a single value."""
    assert window_for_model("claude-haiku-4.5") == 200_000
    assert window_for_model("glm-5") == 200_000
    assert window_for_model("claude-opus-4.5") == 200_000


def test_every_documented_window_is_a_plausible_token_count() -> None:
    """Guard the table against a typo that would skew a whole factor."""
    assert MODEL_WINDOWS
    assert all(
        window in {200_000, 256_000, 1_000_000} for window in MODEL_WINDOWS.values()
    )


def test_an_unknown_model_resolves_to_nothing() -> None:
    """Refuse to guess: an absent id must not fall back to a default."""
    assert window_for_model("claude-opus-9") is None
    assert window_for_model("auto") is None
    assert window_for_model(None) is None
    assert window_for_model(200_000) is None


def test_agent_windows_read_the_declared_model(tree: Path) -> None:
    """Resolve the window per agent, from the config's own model field."""
    assert agent_windows(tree) == {"alpha": 1_000_000, "beta": 1_000_000}


def test_agent_windows_omit_an_undocumented_model(tree: Path) -> None:
    """Leave an unresolvable agent out instead of defaulting it."""
    write(tree / ".kiro" / "prompts" / "gamma.md", "one two three")
    write_agent(tree, "gamma", resources=[], model="some-future-model")
    write(tree / ".kiro" / "prompts" / "delta.md", "one two three")
    write_agent(tree, "delta", resources=[], model="claude-haiku-4.5")
    windows = agent_windows(tree)
    assert "gamma" not in windows
    assert windows["delta"] == 200_000
