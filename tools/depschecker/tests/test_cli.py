# Standard libraries
from pathlib import Path
from unittest.mock import patch

# 3pps
import pytest

# Own modules
from depschecker.cli import (
    _build_parser,
    _load_global_defaults,
    _resolve_lock_path,
    main,
)
from depschecker.types import DepStatus, VulnStatus

MINIMAL_PYPROJECT: str = '[project]\ndependencies = ["requests>=2.32,<3"]\n'

MINIMAL_LOCK: str = """
version = 1

[[package]]
name = "requests"
version = "2.33.1"
source = { registry = "https://pypi.org/simple" }

[[package]]
name = "urllib3"
version = "2.6.3"
source = { registry = "https://pypi.org/simple" }
"""


def _project(tmp_path: Path, with_lock: bool = True) -> Path:
    """
    Create a minimal project on disk.

    Args:
        tmp_path: Pytest temporary directory.
        with_lock: Whether to write a ``uv.lock`` too.

    Returns:
        Path to the written ``pyproject.toml``.
    """

    pyproject: Path = tmp_path / "pyproject.toml"
    pyproject.write_text(MINIMAL_PYPROJECT, encoding="utf-8")
    if with_lock:
        (tmp_path / "uv.lock").write_text(MINIMAL_LOCK, encoding="utf-8")
    return pyproject


def test_parse_minimal() -> None:
    """
    Verify parser accepts no arguments and uses
    default pyproject.toml.
    """

    ns = _build_parser().parse_args([])
    assert str(ns.pyproject) == "pyproject.toml"


def test_default_output() -> None:
    """
    Verify the default output is None (stdout).
    """

    ns = _build_parser().parse_args([])
    assert ns.output is None


def test_default_lock_is_none() -> None:
    """
    Verify --lock defaults to None so it can be inferred
    from the pyproject location.
    """

    assert _build_parser().parse_args([]).lock is None


def test_lock_flag_override() -> None:
    """
    Verify --lock accepts an explicit path.
    """

    ns = _build_parser().parse_args(["--lock", "/tmp/other.lock"])
    assert str(ns.lock) == "/tmp/other.lock"


def test_resolve_lock_path_infers_sibling() -> None:
    """
    Verify the lockfile is inferred beside the given
    pyproject.toml, keeping the CLI usable per project.
    """

    result = _resolve_lock_path(Path("/repo/tools/jirafetcher/pyproject.toml"), None)
    assert result == Path("/repo/tools/jirafetcher/uv.lock")


def test_resolve_lock_path_prefers_explicit() -> None:
    """
    Verify an explicit --lock path wins over inference.
    """

    result = _resolve_lock_path(Path("/repo/pyproject.toml"), Path("/elsewhere.lock"))
    assert result == Path("/elsewhere.lock")


def test_default_timeout() -> None:
    """
    Verify the default timeout is None (resolved
    later in main).
    """

    ns = _build_parser().parse_args([])
    assert ns.timeout is None


def test_freshness_only_flag() -> None:
    """
    Verify --freshness-only sets the flag to True.
    """

    ns = _build_parser().parse_args(["--freshness-only"])
    assert ns.freshness_only is True
    assert ns.vulns_only is False


def test_vulns_only_flag() -> None:
    """
    Verify --vulns-only sets the flag to True.
    """

    ns = _build_parser().parse_args(["--vulns-only"])
    assert ns.vulns_only is True
    assert ns.freshness_only is False


def test_freshness_vulns_mutually_exclusive() -> None:
    """
    Verify --freshness-only and --vulns-only cannot
    be used together.
    """

    with pytest.raises(SystemExit):
        _build_parser().parse_args(["--freshness-only", "--vulns-only"])


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
    Verify _load_global_defaults reads the depschecker
    section from a valid TOML file.
    """

    cfg = tmp_path / "config.toml"
    cfg.write_text("[depschecker]\ntimeout = 30\n", encoding="utf-8")
    monkeypatch.setenv("WORK_AGENTS_CONFIG", str(cfg))
    result = _load_global_defaults()
    assert result["timeout"] == 30


def test_main_file_not_found(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify main exits with code 1 when the pyproject
    file does not exist.
    """

    monkeypatch.setattr("sys.argv", ["depschecker", str(tmp_path / "nope.toml")])
    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    with pytest.raises(SystemExit, match="1"):
        main()


def test_main_missing_lock_is_fatal_for_vulns(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify a missing lockfile fails loudly rather than
    silently reporting no vulnerabilities.
    """

    pyproject = _project(tmp_path, with_lock=False)
    monkeypatch.setattr("sys.argv", ["depschecker", str(pyproject)])
    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    with pytest.raises(SystemExit, match="1"):
        main()


def test_main_freshness_only_tolerates_missing_lock(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Verify --freshness-only still runs without a lockfile,
    since freshness needs only the declared constraint.
    """

    pyproject = _project(tmp_path, with_lock=False)
    monkeypatch.setattr(
        "sys.argv",
        ["depschecker", str(pyproject), "--freshness-only"],
    )
    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)

    status = DepStatus(name="requests", declared="2.32", latest="2.33.1")
    with patch("depschecker.cli.check_freshness", return_value=status):
        main()

    out = capsys.readouterr().out
    assert "requests" in out
    assert "Freshness" in out
    assert "Vulnerability" not in out


def test_main_vulns_only_audits_transitive(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Verify --vulns-only audits every locked package,
    including ones absent from pyproject.toml.
    """

    pyproject = _project(tmp_path)
    monkeypatch.setattr("sys.argv", ["depschecker", str(pyproject), "--vulns-only"])
    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)

    with patch("depschecker.cli.scan_vulnerabilities", return_value=[]) as mock_scan:
        main()

    audited = mock_scan.call_args.args[0]
    assert ("urllib3", "2.6.3", False) in audited
    assert ("requests", "2.33.1", True) in audited

    out = capsys.readouterr().out
    assert "Vulnerability" in out
    assert "Freshness" not in out


def test_main_stdout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Verify main writes the full report to stdout.
    """

    pyproject = _project(tmp_path)
    monkeypatch.setattr("sys.argv", ["depschecker", str(pyproject)])
    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)

    status = DepStatus(name="requests", declared="2.32", resolved="2.33.1")
    vulns = [VulnStatus(name="urllib3", resolved="2.6.3")]
    with (
        patch("depschecker.cli.check_freshness", return_value=status),
        patch("depschecker.cli.scan_vulnerabilities", return_value=vulns),
    ):
        main()

    out = capsys.readouterr().out
    assert "requests" in out
    assert "Freshness" in out
    assert "Vulnerability" in out


def test_main_writes_output_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify main writes the report to the given file.
    """

    pyproject = _project(tmp_path)
    report = tmp_path / "out" / "report.md"
    monkeypatch.setattr(
        "sys.argv",
        ["depschecker", str(pyproject), "-o", str(report)],
    )
    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)

    status = DepStatus(name="requests", declared="2.32", resolved="2.33.1")
    with (
        patch("depschecker.cli.check_freshness", return_value=status),
        patch("depschecker.cli.scan_vulnerabilities", return_value=[]),
    ):
        main()

    assert "Freshness" in report.read_text(encoding="utf-8")


def test_main_invalid_lock_toml(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Verify main exits with code 1 on an unparseable
    lockfile.
    """

    pyproject = _project(tmp_path)
    (tmp_path / "uv.lock").write_text("not = = toml", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["depschecker", str(pyproject)])
    monkeypatch.delenv("WORK_AGENTS_CONFIG", raising=False)
    with pytest.raises(SystemExit, match="1"):
        main()
