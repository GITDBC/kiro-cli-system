# Standard libraries
from pathlib import Path

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


def test_main_no_files_exits(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify main exits with code 1 when no files are
    found.
    """

    monkeypatch.setattr("sys.argv", ["doc2md", str(tmp_path / "nope")])
    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    with pytest.raises(SystemExit, match="1"):
        main()


def test_main_beam_size_validation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify main rejects invalid --whisper-beam-size.
    """

    f = tmp_path / "a.txt"
    f.write_text("x")
    monkeypatch.setattr(
        "sys.argv",
        ["doc2md", str(f), "--whisper-beam-size", "0"],
    )
    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    with pytest.raises(SystemExit):
        main()


def test_main_cpu_threads_validation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify main rejects invalid --whisper-cpu-threads.
    """

    f = tmp_path / "a.txt"
    f.write_text("x")
    monkeypatch.setattr(
        "sys.argv",
        ["doc2md", str(f), "--whisper-cpu-threads", "0"],
    )
    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    with pytest.raises(SystemExit):
        main()
