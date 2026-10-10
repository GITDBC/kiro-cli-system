# Standard libraries
import json
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Self

DEFAULT_CONFIG_PATH: Path = Path("config.json")
DEFAULT_STATUSES: list[str] = ["In Review", "On Hold"]

GLOBAL_CONFIG_ENV: str = "WORK_AGENTS_CONFIG"
TOOL_SECTION: str = "jirafetcher"


def _load_global_config() -> dict[str, Any]:
    """
    Read the jirafetcher section from the global config.

    Looks for the TOML file path in the
    ``WORK_AGENTS_CONFIG`` environment variable.

    Returns:
        Dictionary with tool settings, or empty dict
        if the variable is unset or the section is
        missing.
    """

    path_str: str | None = os.environ.get(GLOBAL_CONFIG_ENV)
    if not path_str:
        return {}
    path: Path = Path(path_str)
    if not path.is_file():
        return {}
    with path.open("rb") as fh:
        data: dict[str, Any] = tomllib.load(fh)
    result: dict[str, Any] = data.get(TOOL_SECTION, {})
    return result


@dataclass
class Config:
    """
    Application configuration loaded from a JSON file
    or the global TOML config.

    Holds the authentication token, status filters, and
    an optional title filter used to narrow down issues.
    """

    token: str = field(repr=False)
    statuses: list[str] = field(default_factory=lambda: list(DEFAULT_STATUSES))
    title_filter: str | None = None

    @classmethod
    def from_file(cls, path: Path = DEFAULT_CONFIG_PATH) -> Self:
        """
        Read and validate configuration.

        Resolution order (first match wins):

        1. Local JSON file at *path*.
        2. Global TOML via ``WORK_AGENTS_CONFIG`` env var.

        Args:
            path: Path to the JSON configuration file.

        Returns:
            A fully initialised configuration instance.

        Raises:
            FileNotFoundError: If no config source is
                available.
            ValueError: If required fields are missing or
                the file contains malformed JSON.
        """

        if path.is_file():
            return cls._from_json(path)

        global_cfg: dict[str, Any] = _load_global_config()
        if global_cfg:
            return cls._from_dict(global_cfg, source=GLOBAL_CONFIG_ENV)

        raise FileNotFoundError(
            f"No config found: {path} does not exist and "
            f"{GLOBAL_CONFIG_ENV} is not set."
        )

    @classmethod
    def _from_json(cls, path: Path) -> Self:
        """
        Parse a local JSON configuration file.

        Args:
            path: Path to the JSON file.

        Returns:
            A fully initialised configuration instance.

        Raises:
            ValueError: If JSON is malformed or token is
                missing.
        """

        try:
            raw: dict[str, Any] = json.loads(
                path.read_text(encoding="utf-8"),
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Malformed JSON in {path}: {exc}",
            ) from exc
        return cls._from_dict(raw, source=str(path))

    @classmethod
    def _from_dict(
        cls,
        raw: dict[str, Any],
        source: str,
    ) -> Self:
        """
        Build a Config from a raw dictionary.

        Args:
            raw: Key-value pairs with config fields.
            source: Label for error messages.

        Returns:
            A fully initialised configuration instance.

        Raises:
            ValueError: If the token is missing.
        """

        token: str | None = raw.get("token")
        if not token:
            raise ValueError(f"Missing 'token' in {source}.")
        return cls(
            token=token,
            statuses=raw.get(
                "statuses",
                list(DEFAULT_STATUSES),
            ),
            title_filter=raw.get("title_filter"),
        )
