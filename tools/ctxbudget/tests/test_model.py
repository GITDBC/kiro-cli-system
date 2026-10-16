"""Tests for the cost model, the weighted aggregation and the budget gate."""

# Standard libraries
from pathlib import Path

# 3pps
import pytest

# Own modules
from ctxbudget.model import (
    agent_baseline,
    compare_budget,
    derive_calibration,
    file_loads,
    measure,
    measured_figures,
    skill_activation,
)
from ctxbudget.resolve import load_agent_configs, resolve_agent
from ctxbudget.types import (
    ArtifactKind,
    Measurement,
    Observation,
)
from tests.helpers import FakeCounter, write, write_agent


def _baseline(measurement: Measurement, agent: str) -> int:
    """
    Read one agent's baseline out of a measurement.

    Args:
        measurement: Measurement snapshot.
        agent: Agent name.

    Returns:
        The agent's baseline figure.
    """
    return next(item.total for item in measurement.baselines if item.agent == agent)


def _agent_files(measurement: Measurement, agent: str) -> int:
    """
    Read one agent's declared-resource subtotal out of a measurement.

    Args:
        measurement: Measurement snapshot.
        agent: Agent name.

    Returns:
        The subtotal `/context show` reports as "Agent files".
    """
    return next(
        item.agent_files_total for item in measurement.baselines if item.agent == agent
    )


def test_baseline_splits_by_artifact_class(tree: Path, counter: FakeCounter) -> None:
    """
    Attribute every counted artifact to its cost class.

    ``alpha`` pays its prompt (7 words), the COMMON.md it declares (6),
    the frontmatter of two skills (4 each) and the one steering file it
    does not declare (5), auto-injected.
    """
    config = next(item for item in load_agent_configs(tree) if item.slug == "alpha")
    baseline = agent_baseline(resolve_agent(config, tree), counter)
    assert baseline.tokens_for(ArtifactKind.PROMPT) == 7
    assert baseline.tokens_for(ArtifactKind.FILE) == 6
    assert baseline.tokens_for(ArtifactKind.SKILL_FRONTMATTER) == 8
    assert baseline.tokens_for(ArtifactKind.KNOWLEDGE_BASE) == 0
    assert baseline.tokens_for(ArtifactKind.STEERING_AUTO) == 5
    assert baseline.total == 26


def test_baseline_counts_a_knowledge_base_as_metadata(
    tree: Path, counter: FakeCounter
) -> None:
    """Charge a knowledge base its name and description only."""
    config = next(item for item in load_agent_configs(tree) if item.slug == "beta")
    baseline = agent_baseline(resolve_agent(config, tree), counter)
    assert baseline.tokens_for(ArtifactKind.KNOWLEDGE_BASE) == 4


def test_unresolved_resource_is_carried_into_the_baseline(
    tree: Path, counter: FakeCounter
) -> None:
    """Surface an unresolvable declaration without counting it."""
    write(tree / ".kiro" / "prompts" / "gamma.md", "one two three")
    write_agent(tree, "gamma", resources=["file://.kiro/steering/absent.md"])
    config = next(item for item in load_agent_configs(tree) if item.slug == "gamma")
    baseline = agent_baseline(resolve_agent(config, tree), counter)
    assert baseline.unresolved == ("file://.kiro/steering/absent.md",)
    assert baseline.tokens_for(ArtifactKind.FILE) == 0
    assert baseline.tokens_for(ArtifactKind.PROMPT) == 3


def test_auto_loaded_steering_reaches_every_baseline(
    tree: Path, counter: FakeCounter
) -> None:
    """
    Charge every agent for steering whether it declares it or not.

    ``beta`` declares both files through a glob and ``alpha`` declares
    one, so both end up paying for both exactly once.
    """
    measurement = measure(tree, counter, False, None)
    assert _baseline(measurement, "alpha") == 26
    steering = {
        artifact.label
        for baseline in measurement.baselines
        for artifact in baseline.artifacts
        if artifact.label.startswith(".kiro/steering/")
    }
    assert steering == {".kiro/steering/COMMON.md", ".kiro/steering/extra.md"}


def test_activation_excludes_frontmatter_and_references(
    tree: Path, counter: FakeCounter
) -> None:
    """Count the body alone, with the reference bound reported apart."""
    activation = skill_activation(
        tree / ".kiro" / "skills" / "one", counter, with_references=True
    )
    assert activation.body_tokens == 7
    assert activation.frontmatter_tokens == 4
    assert activation.refs_upper_bound == 9
    assert activation.reference_files == 1


def test_reference_bound_is_absent_when_not_requested(
    tree: Path, counter: FakeCounter
) -> None:
    """Report None rather than zero, so the two cannot be confused."""
    activation = skill_activation(
        tree / ".kiro" / "skills" / "one", counter, with_references=False
    )
    assert activation.refs_upper_bound is None
    assert activation.reference_files == 0


def test_activation_is_never_added_to_a_baseline(measurement: Measurement) -> None:
    """Keep skill bodies out of every agent floor."""
    bodies = sum(item.body_tokens for item in measurement.activations)
    labels = {
        artifact.label
        for baseline in measurement.baselines
        for artifact in baseline.artifacts
    }
    assert bodies > 0
    assert not any(label.endswith("SKILL.md") for label in labels), (
        "a SKILL.md body reached an agent baseline"
    )


def test_file_loads_weight_by_the_number_of_loads(measurement: Measurement) -> None:
    """
    Multiply an artifact by how often it is actually paid.

    COMMON.md reaches both agents, so it is paid twice and its weighted
    column is twice its size. That multiplier, not the raw size, is what
    a removed token is subject to.
    """
    common = next(
        load for load in measurement.files if load.label == ".kiro/steering/COMMON.md"
    )
    assert common.agents == ("alpha", "beta")
    assert common.loads == 2
    assert common.weighted == common.tokens * 2


def test_file_loads_are_sorted_by_weighted_total(measurement: Measurement) -> None:
    """Rank rows the way a reduction backlog should be worked."""
    weights = [load.weighted for load in measurement.files]
    assert weights == sorted(weights, reverse=True)


def test_file_loads_over_no_baselines() -> None:
    """Produce no rows rather than failing on an empty tree."""
    assert file_loads(()) == ()


def test_measured_figures_use_the_budget_key_space(measurement: Measurement) -> None:
    """Flatten a measurement into prefixed, flat budget keys."""
    figures = measured_figures(measurement)
    assert figures["agent:alpha"] == _baseline(measurement, "alpha")
    assert figures["skill:one"] == 7


def test_calibration_divides_observed_by_the_declared_resources(
    measurement: Measurement,
) -> None:
    """
    Compare the observation against what `/context show` reports.

    The "Agent files" figure covers the declared resources and covers
    neither the agent prompt nor the auto-loaded steering, so dividing by
    the full baseline would compare the reading against a strict superset
    of what it measures and understate the factor.
    """
    declared = _agent_files(measurement, "alpha")
    observation = Observation(agent="alpha", context_files_pct=10.0, window=580)
    calibration = derive_calibration((observation,), measurement)
    assert declared < _baseline(measurement, "alpha")
    assert observation.observed_tokens == 58
    assert calibration.factor == pytest.approx(58 / declared, abs=1e-4)
    assert calibration.factor != pytest.approx(
        58 / _baseline(measurement, "alpha"), abs=1e-4
    )
    assert calibration.agents == ("alpha",)
    assert calibration.window == 580
    assert "58 observed" in calibration.observations[0]


def test_calibration_excludes_prompt_and_steering_from_the_estimate(
    measurement: Measurement,
) -> None:
    """Prove the excluded classes are exactly the two the display omits."""
    baseline = next(item for item in measurement.baselines if item.agent == "alpha")
    excluded = baseline.tokens_for(ArtifactKind.PROMPT) + baseline.tokens_for(
        ArtifactKind.STEERING_AUTO
    )
    assert excluded > 0
    assert baseline.agent_files_total == baseline.total - excluded


def test_calibration_reports_a_band_not_a_point(measurement: Measurement) -> None:
    """
    Bound the factor by the precision the observation was read to.

    One displayed decimal against a 1M window is a thousand tokens, so a
    bare point value would claim precision the reading does not have.
    """
    calibration = derive_calibration(
        (Observation(agent="alpha", context_files_pct=2.1, window=1_000_000),),
        measurement,
    )
    declared = _agent_files(measurement, "alpha")
    assert calibration.factor_low == pytest.approx(20_500 / declared, abs=1e-4)
    assert calibration.factor_high == pytest.approx(21_500 / declared, abs=1e-4)
    assert calibration.factor_low < calibration.factor < calibration.factor_high


def test_exact_token_observation_carries_no_display_band(
    measurement: Measurement,
) -> None:
    """Collapse the band when the figure came in as exact tokens."""
    calibration = derive_calibration(
        (
            Observation(
                agent="alpha",
                context_files_pct=2.1,
                window=1_000_000,
                display_step_pct=0.0,
            ),
        ),
        measurement,
    )
    assert calibration.factor_low == calibration.factor == calibration.factor_high
    assert any("exact token counts" in caveat for caveat in calibration.caveats)


def test_calibration_carries_its_basis_and_caveats(measurement: Measurement) -> None:
    """Record why the factor is indicative, next to the factor itself."""
    calibration = derive_calibration(
        (Observation(agent="alpha", context_files_pct=2.1, window=1_000_000),),
        measurement,
    )
    assert "Agent files" in calibration.basis
    assert "auto-loaded steering" in calibration.basis
    assert len(calibration.caveats) == 2
    assert any("1,000 tokens" in caveat for caveat in calibration.caveats)
    assert any("0.89" in caveat and "1.41" in caveat for caveat in calibration.caveats)


def test_calibration_averages_several_observations(measurement: Measurement) -> None:
    """Average the factors when more than one agent was observed."""
    calibration = derive_calibration(
        (
            Observation(agent="alpha", context_files_pct=10.0, window=580),
            Observation(agent="beta", context_files_pct=10.0, window=580),
        ),
        measurement,
    )
    assert len(calibration.observations) == 2
    assert calibration.agents == ("alpha", "beta")


def test_calibration_ignores_an_unknown_agent(measurement: Measurement) -> None:
    """Skip an observation naming an agent this tree does not have."""
    calibration = derive_calibration(
        (
            Observation(agent="absent", context_files_pct=10.0, window=580),
            Observation(agent="alpha", context_files_pct=10.0, window=580),
        ),
        measurement,
    )
    assert calibration.agents == ("alpha",)


def test_calibration_without_a_usable_observation(measurement: Measurement) -> None:
    """Refuse to invent a factor when nothing matched."""
    with pytest.raises(ValueError, match="nothing to calibrate"):
        derive_calibration(
            (Observation(agent="absent", context_files_pct=1.0, window=100),),
            measurement,
        )


def test_calibration_against_a_zero_estimate(tree: Path, counter: FakeCounter) -> None:
    """
    Refuse to divide by an agent that declares no resources.

    ``gamma`` still pays a prompt and the auto-loaded steering, so its
    baseline is non-zero; the comparison basis is not, which is the
    quantity the division needs.
    """
    write(tree / ".kiro" / "prompts" / "gamma.md", "one two three")
    write_agent(tree, "gamma", resources=[])
    measurement = measure(tree, counter, False, None)
    assert _baseline(measurement, "gamma") > 0
    assert _agent_files(measurement, "gamma") == 0
    with pytest.raises(ValueError, match="cannot calibrate"):
        derive_calibration(
            (Observation(agent="gamma", context_files_pct=1.0, window=100),),
            measurement,
        )


def test_budget_within_tolerance_passes(measurement: Measurement) -> None:
    """Absorb jitter: a 2% overshoot is not a regression at tolerance 2."""
    budget: dict[str, object] = {"agent:alpha": 100}
    measured = measured_figures(measurement)["agent:alpha"]
    budget["agent:alpha"] = int(measured / 1.02) + 1
    violations, _ = compare_budget(measurement, budget, 2.0)
    assert violations == ()


def test_budget_beyond_tolerance_fails(measurement: Measurement) -> None:
    """Fail once the overshoot exceeds the tolerance."""
    measured = measured_figures(measurement)["agent:alpha"]
    violations, _ = compare_budget(measurement, {"agent:alpha": measured - 10}, 2.0)
    assert [item.subject for item in violations] == ["agent:alpha"]
    assert violations[0].excess_pct > 2.0


def test_zero_budget_reports_a_full_overshoot(measurement: Measurement) -> None:
    """Avoid dividing by zero when a recorded figure is zero."""
    violations, _ = compare_budget(measurement, {"agent:alpha": 0}, 2.0)
    assert violations[0].excess_pct == 100.0


def test_non_integer_budget_entries_are_not_compared(
    measurement: Measurement,
) -> None:
    """Compare only the numeric figures, never the provenance strings."""
    violations, _ = compare_budget(measurement, {"meta:backend": "other"}, 2.0)
    assert violations == ()


def test_provenance_mismatch_warns_without_failing(
    measurement: Measurement,
) -> None:
    """Warn when a comparison crosses backends or tokenizer versions."""
    budget: dict[str, object] = {
        "meta:backend": "tiktoken/o200k_base",
        "meta:tiktoken_version": "0.0.1",
    }
    violations, warnings = compare_budget(measurement, budget, 2.0)
    assert violations == ()
    meta = [warning for warning in warnings if warning.startswith("meta:")]
    assert len(meta) == 2
    assert any("backend" in warning for warning in meta)


def test_unrecorded_and_removed_subjects_warn(measurement: Measurement) -> None:
    """Name both a new subject and a recorded one that vanished."""
    _, warnings = compare_budget(measurement, {"agent:ghost": 10}, 2.0)
    assert any("agent:alpha is not recorded" in warning for warning in warnings)
    assert any("agent:ghost is recorded" in warning for warning in warnings)
