"""Tests for report rendering, the committed budget and check output."""

# Standard libraries
import json
from dataclasses import replace

# Own modules
from ctxbudget.report import (
    UNMEASURABLE,
    budget_document,
    render_budget,
    render_check,
    render_json,
    render_markdown,
)
from ctxbudget.types import (
    BudgetViolation,
    Calibration,
    Measurement,
)

CALIBRATION = Calibration(
    factor=1.1234,
    factor_low=1.0700,
    factor_high=1.1800,
    observed_at="2026-01-31",
    agents=("alpha",),
    tiktoken_version="0.13.0",
    window=200_000,
    basis='the artifact classes `/context show` groups as "Agent files"',
    caveats=("the aggregate is the only quantity a reading can calibrate",),
    observations=("alpha: 10.0% of 200000 = 20000 observed vs 17803 estimated",),
)


def test_markdown_carries_the_three_tables(measurement: Measurement) -> None:
    """Emit the per-agent, per-file and per-skill sections, in order."""
    text = render_markdown(measurement)
    positions = [
        text.index("## Per-agent baseline"),
        text.index("## Always-on artifacts, weighted"),
        text.index("## Skill activation costs"),
        text.index("## Provenance and limits"),
    ]
    assert positions == sorted(positions)


def test_markdown_splits_the_baseline_by_class(measurement: Measurement) -> None:
    """Publish the prompt / file / skill_fm split the reduction work needs."""
    header = next(
        line
        for line in render_markdown(measurement).splitlines()
        if line.startswith("| Agent |")
    )
    assert "prompt" in header
    assert "file://" in header
    assert "skill_fm" in header


def test_markdown_publishes_the_weighted_column(measurement: Measurement) -> None:
    """Report agents, loads and the weighted total per artifact."""
    text = render_markdown(measurement)
    assert "| Artifact | Tokens | Agents | Loads | Weighted |" in text
    assert "Weighted total across all agents:" in text


def test_footer_declares_backend_and_approximation(
    measurement: Measurement,
) -> None:
    """State the backend and that every figure is approximate."""
    text = render_markdown(measurement)
    assert measurement.backend in text
    assert "APPROXIMATE" in text
    assert "no Anthropic API key" in text


def test_footer_declares_the_unmeasurable_remainder(
    measurement: Measurement,
) -> None:
    """Name every excluded cost source explicitly."""
    text = render_markdown(measurement)
    for item in UNMEASURABLE:
        assert item in text


def test_footer_says_uncalibrated_when_nothing_is_recorded(
    measurement: Measurement,
) -> None:
    """Admit the absence rather than implying an absolute total is exact."""
    assert "uncalibrated" in render_markdown(measurement)


def test_footer_names_the_factor_and_its_provenance(
    measurement: Measurement,
) -> None:
    """Publish factor, band, basis, caveats, date, agent and window."""
    text = render_markdown(replace(measurement, calibration=CALIBRATION))
    assert "1.1234" in text
    assert "1.07-1.18" in text
    assert "2026-01-31" in text
    assert "alpha" in text
    assert "200,000-token window" in text
    assert "Basis: the artifact classes" in text
    assert "Caveat: the aggregate is the only quantity" in text


def test_footer_calls_a_calibrated_total_indicative(
    measurement: Measurement,
) -> None:
    """
    Keep the honest verdict attached to the factor.

    A factor reported without it reads as licence to quote an absolute
    total as a share of the window, which the residual per-file spread
    does not support.
    """
    text = render_markdown(replace(measurement, calibration=CALIBRATION))
    assert "treat the result as indicative" in text


def test_footer_warns_on_a_stale_calibration(measurement: Measurement) -> None:
    """Flag a factor derived against a different tokenizer version."""
    stale = replace(CALIBRATION, tiktoken_version="0.0.1")
    text = render_markdown(replace(measurement, calibration=stale))
    assert "derived against a different tokenizer" in text


def test_footer_states_how_steering_and_resources_resolve(
    measurement: Measurement,
) -> None:
    """
    Record the two facts a reader needs to trust a figure.

    Steering arrives by workspace auto-load, and a ``resources`` entry
    resolves against the workspace root rather than the config file.
    Both were wrong in an earlier cost model, so both are stated.
    """
    text = render_markdown(measurement)
    assert "**Steering**: every `.kiro/steering/*.md` file is injected" in text
    assert "**Resource resolution**:" in text
    assert "resolved against the workspace root" in text


def test_reference_note_depends_on_the_run(measurement: Measurement) -> None:
    """Say whether reference bounds were measured, and never sum them."""
    without = render_markdown(measurement)
    assert "Reference upper bounds were not measured" in without
    with_refs = render_markdown(replace(measurement, with_references=True))
    assert "never summed into an activation cost" in with_refs


def test_unresolved_resources_are_reported_not_asserted(
    measurement: Measurement,
) -> None:
    """Name an unresolvable declaration and defer the verdict to driftcheck."""
    baseline = replace(
        measurement.baselines[0], unresolved=("file://.kiro/steering/absent.md",)
    )
    text = render_markdown(
        replace(measurement, baselines=(baseline, *measurement.baselines[1:]))
    )
    assert "file://.kiro/steering/absent.md" in text
    assert "driftcheck` owns the verdict" in text


def test_json_report_is_valid_and_sorted(measurement: Measurement) -> None:
    """Emit a decodable payload carrying both metric families."""
    document = json.loads(render_json(replace(measurement, calibration=CALIBRATION)))
    assert document["approximate"] is True
    assert document["calibration"]["factor"] == 1.1234
    assert {item["agent"] for item in document["agents"]} == {"alpha", "beta"}
    assert {item["skill"] for item in document["skills"]} == {"one", "two"}
    assert document["unmeasurable_remainder"] == list(UNMEASURABLE)


def test_json_report_carries_the_aggregates_the_markdown_prints(
    measurement: Measurement,
) -> None:
    """Spare a consumer from re-summing a figure the report already states."""
    document = json.loads(render_json(measurement))
    totals = document["totals"]
    assert totals["agent_baselines"] == sum(
        item["baseline"] for item in document["agents"]
    )
    assert totals["agents"] == len(document["agents"])
    assert totals["files_weighted"] == sum(
        item["weighted"] for item in document["files"]
    )
    assert totals["skill_bodies"] == sum(
        item["body_tokens"] for item in document["skills"]
    )
    assert totals["skills"] == len(document["skills"])


def test_budget_document_is_flat_and_scalar(measurement: Measurement) -> None:
    """
    Keep the committed budget a single-level document of scalars.

    No arrays either, not only no objects: Prettier formats this file and
    inlines a short array while expanding a long one, so an array written
    here could not also pass `make fmt-check`.
    """
    document = budget_document(replace(measurement, calibration=CALIBRATION))
    assert list(document) == sorted(document)
    assert not any(isinstance(value, (dict, list)) for value in document.values())
    assert document["agent:alpha"] == measurement.baselines[0].total
    assert document["skill:one"] == measurement.activations[0].body_tokens
    assert document["meta:backend"] == measurement.backend
    assert "meta:steering_mode" not in document


def test_budget_records_calibration_provenance(measurement: Measurement) -> None:
    """Commit the factor, its band and its caveats next to the figures."""
    document = budget_document(replace(measurement, calibration=CALIBRATION))
    assert document["calibration:factor"] == 1.1234
    assert document["calibration:factor_low"] == 1.07
    assert document["calibration:factor_high"] == 1.18
    assert document["calibration:agents"] == "alpha"
    assert document["calibration:tiktoken_version"] == "0.13.0"
    assert document["calibration:basis"] == CALIBRATION.basis
    assert document["calibration:caveat:1"] == CALIBRATION.caveats[0]
    assert document["calibration:observation:1"] == CALIBRATION.observations[0]


def test_budget_omits_calibration_keys_when_absent(
    measurement: Measurement,
) -> None:
    """Write no calibration block rather than a placeholder one."""
    document = budget_document(measurement)
    assert not [key for key in document if key.startswith("calibration:")]


def test_rendered_budget_round_trips(measurement: Measurement) -> None:
    """Serialize to JSON that decodes back to the same document."""
    assert json.loads(render_budget(measurement)) == budget_document(measurement)


def test_check_output_passes_cleanly() -> None:
    """Report a pass in one line, with no violation noise."""
    text = render_check((), ())
    assert "PASS" in text
    assert "ERROR" not in text


def test_check_output_names_every_violation() -> None:
    """Name the subject, both figures, the overshoot and the tolerance."""
    violation = BudgetViolation(
        subject="agent:alpha", budget=100, measured=110, tolerance_pct=2.0
    )
    text = render_check((violation,), ("provenance differs",))
    assert "WARNING: provenance differs" in text
    assert "agent:alpha is 110 tokens, budget 100" in text
    assert "+10.0%" in text
    assert "FAIL: 1 figure(s) over budget" in text
