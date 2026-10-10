"""Tests for the docsync command-line entry point."""

# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from docsync import cli
from docsync.cli import main
from docsync.sources import SOURCES
from docsync.sources.base import DocSource
from docsync.types import MirrorPaths, SyncCounts

KIRO: DocSource = SOURCES["kiro"]
AGENTSKILLS: DocSource = SOURCES["agentskills"]
ANTHROPIC: DocSource = SOURCES["anthropic"]


@pytest.fixture()
def recorded(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """
    Replace the sync engine with a recorder.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        Dictionary receiving the arguments the CLI passed through.
    """
    calls: dict[str, object] = {}

    def fake_sync(
        source: DocSource,
        paths: MirrorPaths,
        dry_run: bool = False,
        prune: bool = False,
    ) -> SyncCounts:
        calls["source"] = source
        calls["paths"] = paths
        calls["dry_run"] = dry_run
        calls["prune"] = prune
        return SyncCounts(pages=2, unchanged=2)

    monkeypatch.setattr(cli, "sync", fake_sync)
    return calls


def test_main_passes_kiro_flags_through(
    recorded: dict[str, object], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Flags reach the sync engine and the summary is printed."""
    assert main(["kiro", "--dry-run", "--prune", "--root", str(tmp_path)]) == 0
    assert recorded["source"] is KIRO
    assert recorded["dry_run"] is True
    assert recorded["prune"] is True
    assert recorded["paths"] == KIRO.mirror_paths(tmp_path)
    output = capsys.readouterr().out
    assert "[DRY RUN] New: 0, Updated: 0, Unchanged: 2" in output
    assert "Orphans: 0" in output


def test_main_passes_agentskills_flags_through(
    recorded: dict[str, object], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The second source reaches the engine with its own paths."""
    assert main(["agentskills", "--dry-run", "--root", str(tmp_path)]) == 0
    assert recorded["source"] is AGENTSKILLS
    assert recorded["dry_run"] is True
    assert recorded["paths"] == AGENTSKILLS.mirror_paths(tmp_path)
    output = capsys.readouterr().out
    assert "[DRY RUN] New: 0, Updated: 0, Unchanged: 2, Failed: 0" in output
    assert "Orphans" not in output


def test_main_passes_anthropic_flags_through(
    recorded: dict[str, object], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The prompting mirror prunes and reports its orphan tally."""
    assert main(["anthropic", "--dry-run", "--prune", "--root", str(tmp_path)]) == 0
    assert recorded["source"] is ANTHROPIC
    assert recorded["prune"] is True
    assert recorded["paths"] == ANTHROPIC.mirror_paths(tmp_path)
    assert "Orphans: 0" in capsys.readouterr().out


def test_main_reports_a_rejected_catalogue(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A source refusing the upstream catalogue exits 1, not a traceback."""

    def explode(
        source: DocSource,
        paths: MirrorPaths,
        dry_run: bool = False,
        prune: bool = False,
    ) -> SyncCounts:
        message = "tracked page(s) no longer advertised"
        raise ValueError(message)

    monkeypatch.setattr(cli, "sync", explode)
    assert main(["anthropic", "--root", str(tmp_path)]) == 1
    assert "tracked page(s) no longer advertised" in capsys.readouterr().err


def test_main_rejects_prune_for_a_fixed_catalogue(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--prune is refused rather than silently ignored."""
    assert main(["agentskills", "--prune", "--root", str(tmp_path)]) == 1
    assert "--prune does not apply" in capsys.readouterr().err


def test_main_rejects_an_unknown_source(tmp_path: Path) -> None:
    """Argparse restricts the source to the registry."""
    with pytest.raises(SystemExit):
        main(["nonesuch", "--root", str(tmp_path)])


def test_main_fails_when_a_dry_run_finds_updates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A dry run with pending work exits 1, as CI expects."""
    monkeypatch.setattr(
        cli,
        "sync",
        lambda source, paths, dry_run=False, prune=False: SyncCounts(
            pages=1, updated=1
        ),
    )
    assert main(["kiro", "--dry-run", "--root", str(tmp_path)]) == 1
    assert "Run without --dry-run to apply updates." in capsys.readouterr().out


def test_main_fails_when_a_page_could_not_be_fetched(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A fetch failure exits non-zero for a strict source."""
    monkeypatch.setattr(
        cli,
        "sync",
        lambda source, paths, dry_run=False, prune=False: SyncCounts(pages=6, failed=2),
    )
    assert main(["agentskills", "--root", str(tmp_path)]) == 1
    assert "2 page(s) could not be vendored." in capsys.readouterr().err


def test_main_tolerates_a_failed_page_on_a_tolerant_source(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The kiro mirror keeps its historical exit code on a gap."""
    monkeypatch.setattr(
        cli,
        "sync",
        lambda source, paths, dry_run=False, prune=False: SyncCounts(
            pages=6, failed=2, unchanged=4
        ),
    )
    assert main(["kiro", "--root", str(tmp_path)]) == 0


def test_main_discovers_the_root_when_not_given(
    recorded: dict[str, object], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Without --root the enclosing repository is used."""
    monkeypatch.setattr(cli, "find_repo_root", lambda: tmp_path)
    assert main(["kiro"]) == 0
    assert recorded["paths"] == KIRO.mirror_paths(tmp_path)


def test_main_reports_an_undiscoverable_root(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A failed discovery exits 1 with an explanation."""

    def explode() -> Path:
        message = "cannot locate the repository root"
        raise ValueError(message)

    monkeypatch.setattr(cli, "find_repo_root", explode)
    assert main(["agentskills"]) == 1
    assert "cannot locate the repository root" in capsys.readouterr().err
