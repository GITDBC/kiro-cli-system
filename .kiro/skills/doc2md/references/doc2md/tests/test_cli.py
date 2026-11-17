"""Tests for the doc2md command-line interface."""

# Standard libraries
from pathlib import Path
from unittest.mock import patch

# 3pps
import pytest

# Own modules
from doc2md.cli import _build_parser, _load_global_defaults, main


def test_parse_minimal() -> None:
    """
    Verify parser accepts a single positional path
    argument.
    """

    ns = _build_parser().parse_args(["file.txt"])
    assert ns.paths == ["file.txt"]


def test_default_output() -> None:
    """
    Verify the default output directory is 'output'.
    """

    ns = _build_parser().parse_args(["f"])
    assert ns.output == "output"


def test_default_exclude() -> None:
    """
    Verify the default exclude list is None.
    """

    ns = _build_parser().parse_args(["f"])
    assert ns.exclude is None


def test_whisper_defaults() -> None:
    """
    Verify all whisper CLI args default to None
    (resolved later in main).
    """

    ns = _build_parser().parse_args(["f"])
    assert ns.whisper_model is None
    assert ns.whisper_language is None
    assert ns.whisper_beam_size is None
    assert ns.whisper_device is None
    assert ns.whisper_cpu_threads is None


def test_load_global_defaults_no_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify _load_global_defaults returns empty dict
    when WORK_AGENTS_CONFIG is not set.
    """

    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    assert _load_global_defaults() == {}


def test_load_global_defaults_valid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify _load_global_defaults reads the doc2md
    section from a valid TOML file.
    """

    cfg = tmp_path / "config.toml"
    cfg.write_text('[doc2md]\nwhisper_model = "large"\n', encoding="utf-8")
    monkeypatch.setenv("WORK_AGENTS_CONFIG", str(cfg))
    result = _load_global_defaults()
    assert result["whisper_model"] == "large"


def test_load_global_defaults_invalid_toml(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify _load_global_defaults raises ValueError
    for a malformed TOML file.
    """

    cfg = tmp_path / "config.toml"
    cfg.write_text("[doc2md\n", encoding="utf-8")
    monkeypatch.setenv("WORK_AGENTS_CONFIG", str(cfg))
    with pytest.raises(ValueError, match="Invalid TOML"):
        _load_global_defaults()


def test_main_invalid_config_returns_1(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify main returns 1 when the global config is
    not valid TOML.
    """

    cfg = tmp_path / "config.toml"
    cfg.write_text("[doc2md\n", encoding="utf-8")
    monkeypatch.setenv("WORK_AGENTS_CONFIG", str(cfg))
    assert main([str(tmp_path)]) == 1


def test_main_no_files_returns_1(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify main returns 1 when no files are found.
    """

    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    assert main([str(tmp_path / "nope")]) == 1


@pytest.mark.parametrize(
    ("flag", "value"),
    [
        ("--whisper-beam-size", "0"),
        ("--whisper-beam-size", "21"),
        ("--whisper-cpu-threads", "0"),
        ("--whisper-cpu-threads", "33"),
    ],
)
def test_main_rejects_out_of_range(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    flag: str,
    value: str,
) -> None:
    """
    Verify main rejects out-of-range whisper options
    with an argparse error.
    """

    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    with pytest.raises(SystemExit, match="2"):
        main([str(tmp_path), flag, value])


def test_main_rejects_non_integer_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify main rejects a non-integer beam size coming
    from the global config.
    """

    cfg = tmp_path / "config.toml"
    cfg.write_text("[doc2md]\nwhisper_beam_size = 1.5\n", encoding="utf-8")
    monkeypatch.setenv("WORK_AGENTS_CONFIG", str(cfg))
    with pytest.raises(SystemExit, match="2"):
        main([str(tmp_path)])


def test_main_config_defaults_and_cli_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify config values seed the whisper options,
    CLI flags override them, and success returns 0.
    """

    src = tmp_path / "a.txt"
    src.write_text("x", encoding="utf-8")
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        '[doc2md]\nwhisper_model = "large"\nwhisper_beam_size = 3\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("WORK_AGENTS_CONFIG", str(cfg))
    with patch("doc2md.cli.convert_files", return_value=1) as convert:
        code = main([str(src), "-o", str(tmp_path / "out"), "--whisper-beam-size", "5"])

    assert code == 0
    wa = convert.call_args.kwargs["whisper_args"]
    assert wa["model"] == "large"
    assert wa["beam_size"] == 5
    assert wa["device"] == "auto"


def test_main_nothing_converted_returns_1(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify main returns 1 when no file was converted.
    """

    src = tmp_path / "a.txt"
    src.write_text("x", encoding="utf-8")
    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    with patch("doc2md.cli.convert_files", return_value=0):
        assert main([str(src), "-v"]) == 1
