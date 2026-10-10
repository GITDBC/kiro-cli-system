"""
Context-window size per model, and the window an agent's model implies.

A calibration turns a percentage of the context window into tokens, so
the window is the multiplier the entire factor rides on: reading a 1M
observation against a 200K window understates the result fivefold and
says nothing about it. The window is a property of the model an agent
declares, not a constant of the tool, so it is looked up per agent.

The table is transcribed from the vendored Kiro documentation --
``.kiro/skills/kiro-cli-reference/references/models.md``, "Quick
comparison" -- and carries only models whose window that table states
and whose id spelling is confirmed, either by the same documentation set
(``claude-opus-4.8``, ``claude-sonnet-4``) or by an agent config in this
repository (``claude-opus-5``, ``claude-sonnet-5``, ``claude-haiku-4.5``).
The GPT-5.6 tiers and the remaining open-weight models are deliberately
absent: their windows are documented but their id spelling is not, and a
guessed key would be a silent trap the moment it matched.

An id the table does not carry resolves to no window at all, which makes
the caller demand ``--window`` explicitly. That is the point of the
module: refusing to guess is the only behaviour that cannot produce a
factor which is wrong by the ratio of two windows without saying so.
"""

# Standard libraries
import logging
from pathlib import Path
from typing import Final

# Own modules
from ctxbudget.resolve import load_agent_configs

logger = logging.getLogger(__name__)

MODEL_WINDOWS: Final[dict[str, int]] = {
    "claude-opus-5": 1_000_000,
    "claude-opus-4.8": 1_000_000,
    "claude-opus-4.7": 1_000_000,
    "claude-opus-4.6": 1_000_000,
    "claude-opus-4.5": 200_000,
    "claude-sonnet-5": 1_000_000,
    "claude-sonnet-4.6": 1_000_000,
    "claude-sonnet-4.5": 200_000,
    "claude-sonnet-4": 200_000,
    "claude-haiku-4.5": 200_000,
    "glm-5": 200_000,
}


def window_for_model(model: object) -> int | None:
    """
    Look up the context window of one model id.

    Args:
        model: Value of an agent config's ``model`` field, of any type,
            since the field is read straight out of decoded JSON.

    Returns:
        The documented window, or None when the field is absent, is not
        a string, or names a model the table does not carry.
    """
    if not isinstance(model, str):
        return None
    return MODEL_WINDOWS.get(model)


def agent_windows(root: Path) -> dict[str, int]:
    """
    Map every agent to the window the model it declares implies.

    An agent whose model is unknown is left out rather than defaulted,
    so a caller asking for it gets an error instead of a wrong figure.

    Args:
        root: Repository root.

    Returns:
        Agent name to context window, for the agents that resolve.
    """
    windows: dict[str, int] = {}
    for config in load_agent_configs(root):
        window = window_for_model(config.data.get("model"))
        if window is None:
            logger.debug(
                "Agent %s declares model %r, whose window is not documented.",
                config.name,
                config.data.get("model"),
            )
            continue
        windows[config.name] = window
    return windows
