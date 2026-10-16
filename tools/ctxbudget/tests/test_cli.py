"""
Tests for the command-line surface.

These exercise the real ``TiktokenCounter``, since the subcommands build
it themselves. The assertions are therefore about behaviour and shape,
never about a specific token figure: a tokenizer upgrade may legitimately
move a figure and must not be able to fail this suite.
"""

# Standard libraries
import json
from pathlib import Path

# 3pps
import pytest

# Own modules
from ctxbudget.cli import (
    BUDGET_RELATIVE,
    calibration_from_budget,
    load_budget,
    main,
)
from tests.helpers import write, write_agent


def _budget(tree: Path) -> dict[str, object]:
    """
    Read the committed budget of a tree.

    Args:
        tree: Repository root.

    Returns:
        The decoded budget document.
    """
    return load_budget(tree / BUDGET_RELATIVE)


def test_report_writes_a_file_rather_than_flooding_stdout(
    tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Honour the cross-tool convention on report destinations."""
    assert main(["report", "--root", str(tree)]) == 0
    assert capsys.readouterr().out == ""
    written = (tree / "tmp" / "context-budget-report.md").read_text(encoding="utf-8")
    assert written.startswith("# Context Budget Report")


def test_report_to_stdout_on_request(
    tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Allow stdout explicitly, for a human reading the output directly."""
    assert main(["report", "--root", str(tree), "--output", "-"]) == 0
    assert "## Per-agent baseline" in capsys.readouterr().out


def test_report_honours_an_explicit_destination(tree: Path, tmp_path: Path) -> None:
    """Write where asked, creating parent directories."""
    target = tmp_path / "nested" / "report.md"
    assert main(["report", "--root", str(tree), "--output", str(target)]) == 0
    assert target.is_file()


def test_json_report_is_decodable(
    tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Emit a JSON payload other tooling can consume."""
    assert (
        main(["report", "--root", str(tree), "--format", "json", "--output", "-"]) == 0
    )
    document = json.loads(capsys.readouterr().out)
    assert document["totals"]["agents"] == len(document["agents"])
    assert document["backend"] == "tiktoken/o200k_base"


def test_json_report_default_extension(tree: Path) -> None:
    """Name the default destination after the requested format."""
    assert main(["report", "--root", str(tree), "--format", "json"]) == 0
    assert (tree / "tmp" / "context-budget-report.json").is_file()


def test_with_references_adds_the_upper_bound(tree: Path) -> None:
    """Measure reference files only when asked, and never sum them."""
    main(["report", "--root", str(tree), "--format", "json", "--with-references"])
    document = json.loads(
        (tree / "tmp" / "context-budget-report.json").read_text(encoding="utf-8")
    )
    one = next(item for item in document["skills"] if item["skill"] == "one")
    assert one["refs_upper_bound"] > 0
    assert one["reference_files"] == 1


def test_check_without_a_budget_fails_loudly(tree: Path) -> None:
    """Refuse to pass a gate that has nothing to compare against."""
    assert main(["check", "--root", str(tree)]) == 1


def test_write_budget_then_check_passes(tree: Path) -> None:
    """Record a budget, then compare the same tree against it."""
    assert main(["check", "--root", str(tree), "--write-budget"]) == 0
    budget = _budget(tree)
    assert budget["meta:backend"] == "tiktoken/o200k_base"
    assert budget["agent:alpha"] > 0
    assert main(["check", "--root", str(tree)]) == 0


def test_check_fails_when_a_figure_grows_beyond_tolerance(
    tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Catch a regression in the one figure that grew."""
    main(["check", "--root", str(tree), "--write-budget"])
    budget = _budget(tree)
    budget["agent:alpha"] = int(budget["agent:alpha"]) // 2
    write(tree / BUDGET_RELATIVE, json.dumps(budget, indent=2, sort_keys=True))
    assert main(["check", "--root", str(tree)]) == 1
    assert "agent:alpha" in capsys.readouterr().out


def test_tolerance_absorbs_jitter(tree: Path) -> None:
    """Let a sub-tolerance drift pass, so the gate stays switched on."""
    main(["check", "--root", str(tree), "--write-budget"])
    budget = _budget(tree)
    measured = int(budget["agent:alpha"])
    budget["agent:alpha"] = measured - 1
    write(tree / BUDGET_RELATIVE, json.dumps(budget, indent=2, sort_keys=True))
    assert main(["check", "--root", str(tree), "--tolerance-pct", "50"]) == 0
    assert main(["check", "--root", str(tree), "--tolerance-pct", "0"]) == 1


def test_check_warns_when_the_backend_changed(
    tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Warn, without failing, when a comparison crosses measurement settings."""
    main(["check", "--root", str(tree), "--write-budget"])
    budget = _budget(tree)
    budget["meta:tiktoken_version"] = "0.0.1"
    write(tree / BUDGET_RELATIVE, json.dumps(budget, indent=2, sort_keys=True))
    assert main(["check", "--root", str(tree)]) == 0
    assert "tiktoken_version" in capsys.readouterr().out


def test_check_warns_about_an_unbudgeted_agent(
    tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Name a new agent instead of silently leaving it ungated."""
    main(["check", "--root", str(tree), "--write-budget"])
    write(tree / ".kiro" / "prompts" / "gamma.md", "a new agent prompt")
    write_agent(tree, "gamma", resources=[])
    assert main(["check", "--root", str(tree)]) == 0
    assert "agent:gamma is not recorded" in capsys.readouterr().out


def test_calibrate_stores_the_factor_and_its_provenance(tree: Path) -> None:
    """Derive a factor from a percentage and commit it with its date."""
    assert (
        main(
            [
                "calibrate",
                "--root",
                str(tree),
                "--agent",
                "alpha",
                "--context-files-pct",
                "10",
                "--window",
                "1000",
            ]
        )
        == 0
    )
    budget = _budget(tree)
    assert budget["calibration:agents"] == "alpha"
    assert budget["calibration:window"] == 1000
    assert budget["calibration:factor"] > 0
    assert budget["calibration:observation:1"]


def test_calibrate_resolves_the_window_from_the_declared_model(tree: Path) -> None:
    """
    Default the window per model rather than to one constant.

    Both fixture agents declare ``claude-opus-5.5``, a 1M-token model. The
    200K constant this replaced would have divided the percentage by a
    fifth of the real window and recorded a factor five times too small.
    """
    assert (
        main(
            [
                "calibrate",
                "--root",
                str(tree),
                "--agent",
                "alpha",
                "--context-files-pct",
                "2.1",
            ]
        )
        == 0
    )
    budget = _budget(tree)
    assert budget["calibration:window"] == 1_000_000


def test_calibrate_refuses_an_undocumented_model(tree: Path) -> None:
    """Demand --window instead of guessing one."""
    write(tree / ".kiro" / "prompts" / "gamma.md", "one two three")
    write_agent(
        tree,
        "gamma",
        resources=["file://.kiro/steering/COMMON.md"],
        model="some-future-model",
    )
    assert (
        main(
            [
                "calibrate",
                "--root",
                str(tree),
                "--agent",
                "gamma",
                "--context-files-pct",
                "2.1",
            ]
        )
        == 1
    )
    assert (
        main(
            [
                "calibrate",
                "--root",
                str(tree),
                "--agent",
                "gamma",
                "--context-files-pct",
                "2.1",
                "--window",
                "200000",
            ]
        )
        == 0
    )
    assert _budget(tree)["calibration:window"] == 200_000


def test_calibrate_rejects_a_non_positive_window(tree: Path) -> None:
    """Refuse a window that would divide by zero or invert the ratio."""
    argv = ["calibrate", "--root", str(tree), "--agent", "alpha"]
    assert main([*argv, "--context-files-pct", "2.1", "--window", "0"]) == 1
    assert main([*argv, "--context-files-pct", "2.1", "--window", "-1"]) == 1


def test_observations_file_may_omit_every_window(tree: Path, tmp_path: Path) -> None:
    """Resolve each entry's window from the agent it names."""
    observations = tmp_path / "obs.json"
    observations.write_text(
        json.dumps(
            {
                "observations": [
                    {"agent": "alpha", "context_files_pct": 2.1},
                    {"agent": "beta", "context_files_pct": 1.4},
                ]
            }
        ),
        encoding="utf-8",
    )
    assert (
        main(["calibrate", "--root", str(tree), "--observations", str(observations)])
        == 0
    )
    assert _budget(tree)["calibration:window"] == 1_000_000


def test_calibrate_records_the_band_and_its_caveats(tree: Path) -> None:
    """Commit the precision band and the residual next to the factor."""
    main(
        [
            "calibrate",
            "--root",
            str(tree),
            "--agent",
            "alpha",
            "--context-files-pct",
            "2.1",
        ]
    )
    budget = _budget(tree)
    low = budget["calibration:factor_low"]
    factor = budget["calibration:factor"]
    high = budget["calibration:factor_high"]
    assert isinstance(low, float)
    assert isinstance(factor, float)
    assert isinstance(high, float)
    assert low < factor < high
    assert "Agent files" in str(budget["calibration:basis"])
    assert "calibration:caveat:1" in budget
    assert "calibration:caveat:2" in budget
    assert "calibration:caveat:3" not in budget
    assert not any(isinstance(value, (dict, list)) for value in budget.values())


def test_calibration_round_trips_through_the_scalar_keys(tree: Path) -> None:
    """Read back what was written, despite the flat encoding."""
    main(
        [
            "calibrate",
            "--root",
            str(tree),
            "--observations",
            str(_two_agent_observations(tree)),
        ]
    )
    calibration = calibration_from_budget(_budget(tree))
    assert calibration is not None
    assert calibration.agents == ("alpha", "beta")
    assert len(calibration.caveats) == 2
    assert len(calibration.observations) == 2


def test_recalibrating_replaces_the_previous_block(tree: Path) -> None:
    """Leave no orphan entry behind when the new block is shorter."""
    budget_path = tree / BUDGET_RELATIVE
    write(
        budget_path,
        json.dumps({"calibration:observation:9": "stale", "agent:alpha": 10}),
    )
    main(
        [
            "calibrate",
            "--root",
            str(tree),
            "--agent",
            "alpha",
            "--context-files-pct",
            "2.1",
        ]
    )
    budget = _budget(tree)
    assert "calibration:observation:9" not in budget
    assert budget["calibration:observation:1"]
    assert budget["agent:alpha"] == 10


def _two_agent_observations(tree: Path) -> Path:
    """
    Write an observations file naming both fixture agents.

    Args:
        tree: Repository root, which the file is written beside.

    Returns:
        Path to the written observations file.
    """
    return write(
        tree / "tmp" / "obs.json",
        json.dumps(
            {
                "observations": [
                    {"agent": "alpha", "context_files_pct": 2.1},
                    {"agent": "beta", "context_files_pct": 1.4},
                ]
            }
        ),
    )


def test_calibrate_preserves_recorded_figures(tree: Path) -> None:
    """Update only the calibration keys of an existing budget."""
    main(["check", "--root", str(tree), "--write-budget"])
    before = _budget(tree)["agent:alpha"]
    main(
        [
            "calibrate",
            "--root",
            str(tree),
            "--agent",
            "alpha",
            "--observed-tokens",
            "500",
        ]
    )
    assert _budget(tree)["agent:alpha"] == before


def test_calibration_is_reported_back_in_the_footer(tree: Path) -> None:
    """Round-trip a stored factor into the next report's provenance."""
    main(
        [
            "calibrate",
            "--root",
            str(tree),
            "--agent",
            "alpha",
            "--observed-tokens",
            "500",
        ]
    )
    main(["report", "--root", str(tree)])
    text = (tree / "tmp" / "context-budget-report.md").read_text(encoding="utf-8")
    assert "uncalibrated" not in text
    assert "**Calibration**: factor" in text


def test_calibrate_dry_run_writes_nothing(tree: Path) -> None:
    """Let a human see the factor before committing it."""
    assert (
        main(
            [
                "calibrate",
                "--root",
                str(tree),
                "--agent",
                "alpha",
                "--observed-tokens",
                "500",
                "--dry-run",
            ]
        )
        == 0
    )
    assert not (tree / BUDGET_RELATIVE).exists()


def test_calibrate_reads_an_observations_file(tree: Path, tmp_path: Path) -> None:
    """Accept several observations from a file a human can hand-write."""
    observations = tmp_path / "obs.json"
    observations.write_text(
        json.dumps(
            {
                "window": 1000,
                "observations": [
                    {"agent": "alpha", "context_files_pct": 10},
                    {"agent": "beta", "context_files_pct": 12, "window": 2000},
                ],
            }
        ),
        encoding="utf-8",
    )
    assert (
        main(["calibrate", "--root", str(tree), "--observations", str(observations)])
        == 0
    )
    budget = _budget(tree)
    assert budget["calibration:agents"] == "alpha, beta"
    assert budget["calibration:window"] == 2000


def test_calibrate_without_any_observation_fails(tree: Path) -> None:
    """Refuse to invent ground truth."""
    assert main(["calibrate", "--root", str(tree)]) == 1


def test_calibrate_figure_without_an_agent_fails(tree: Path) -> None:
    """Refuse a figure that names no agent to attribute it to."""
    assert main(["calibrate", "--root", str(tree), "--context-files-pct", "10"]) == 1


@pytest.mark.parametrize(
    "content",
    [
        "not json",
        "[]",
        '{"observations": {}}',
        '{"observations": [7]}',
        '{"observations": [{"agent": "alpha"}]}',
    ],
)
def test_malformed_observations_file_fails_cleanly(
    tree: Path, tmp_path: Path, content: str
) -> None:
    """Report a bad observations file instead of raising."""
    observations = tmp_path / "obs.json"
    observations.write_text(content, encoding="utf-8")
    assert (
        main(["calibrate", "--root", str(tree), "--observations", str(observations)])
        == 1
    )


def test_malformed_budget_fails_cleanly(tree: Path) -> None:
    """Report an unreadable budget instead of raising."""
    write(tree / BUDGET_RELATIVE, "[]")
    assert main(["check", "--root", str(tree)]) == 1


def test_missing_budget_reads_as_empty(tmp_path: Path) -> None:
    """Treat an absent budget as empty rather than an error."""
    assert load_budget(tmp_path / "absent.json") == {}


def test_partial_calibration_block_reads_as_absent() -> None:
    """
    Prefer an honest "uncalibrated" to a factor without provenance.

    A footer claiming a correction whose origin is unknown is worse than
    one admitting none was recorded.
    """
    assert calibration_from_budget({"calibration:factor": 1.1}) is None
    assert calibration_from_budget({}) is None


def test_calibration_block_tolerates_missing_optional_fields() -> None:
    """
    Rebuild a factor whose optional provenance fields were dropped.

    A band that was never recorded collapses onto the point value rather
    than acquiring an invented width, and an unrecorded window reads as
    unknown rather than as some default that would misprint the footer.
    """
    calibration = calibration_from_budget(
        {"calibration:factor": 1.5, "calibration:observed_at": "2026-01-01"}
    )
    assert calibration is not None
    assert calibration.tiktoken_version == "unknown"
    assert calibration.agents == ()
    assert calibration.factor_low == calibration.factor_high == 1.5
    assert calibration.window == 0
    assert calibration.basis == "unrecorded"
    assert calibration.caveats == ()


def test_unknown_root_fails_cleanly(tmp_path: Path) -> None:
    """Report a tree that is not a repository instead of raising."""
    assert main(["report", "--root", str(tmp_path / "absent")]) == 1
