# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from jirafetcher.config import Config, _load_global_config


def test_from_file_json(tmp_path: Path) -> None:
    """
    Verify Config.from_file loads a valid JSON config.
    """

    cfg = tmp_path / "config.json"
    cfg.write_text('{"token": "abc123"}', encoding="utf-8")
    config = Config.from_file(cfg)
    assert config.token == "abc123"
    assert config.statuses == ["In Review", "On Hold"]


def test_from_file_missing_token(tmp_path: Path) -> None:
    """
    Verify Config.from_file raises ValueError when
    token is missing.
    """

    cfg = tmp_path / "config.json"
    cfg.write_text('{"statuses": ["Done"]}', encoding="utf-8")
    with pytest.raises(ValueError, match="token"):
        Config.from_file(cfg)


def test_from_file_malformed_json(tmp_path: Path) -> None:
    """
    Verify Config.from_file raises ValueError for
    malformed JSON.
    """

    cfg = tmp_path / "config.json"
    cfg.write_text("{bad json", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed"):
        Config.from_file(cfg)


def test_from_file_global_toml_fallback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify Config.from_file falls back to global TOML
    when JSON does not exist.
    """

    toml = tmp_path / "config.toml"
    toml.write_text(
        '[jirafetcher]\ntoken = "toml-token"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("WORK_AGENTS_CONFIG", str(toml))
    config = Config.from_file(tmp_path / "nope.json")
    assert config.token == "toml-token"


def test_from_file_no_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify Config.from_file raises FileNotFoundError
    when no config source is available.
    """

    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    with pytest.raises(FileNotFoundError):
        Config.from_file(tmp_path / "nope.json")


def test_load_global_config_no_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify _load_global_config returns empty dict
    when WORK_AGENTS_CONFIG is not set.
    """

    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    assert _load_global_config() == {}


def test_default_statuses() -> None:
    """
    Verify default statuses are In Review and On Hold.
    """

    config = Config(token="x")
    assert config.statuses == ["In Review", "On Hold"]
