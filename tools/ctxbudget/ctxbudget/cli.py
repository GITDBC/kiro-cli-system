"""
Command-line entry point for context-budget measurement.

Usage:
    ctxbudget report                      # write the Markdown report
    ctxbudget report --format json        # same figures, JSON payload
    ctxbudget check                       # gate against the recorded budget
    ctxbudget check --write-budget        # re-record the budget deliberately
    ctxbudget calibrate --agent NAME --context-files-pct P

``report`` writes to a file rather than stdout by default, per the
cross-tool convention that a report must not flood an agent's context.
Pass ``--output -`` for stdout.
"""

# Standard libraries
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Final

# Own modules
from ctxbudget.count import TiktokenCounter
from ctxbudget.model import (
    AGENT_SEPARATOR,
    CALIBRATION_PREFIX,
    CAVEAT_PREFIX,
    OBSERVATION_PREFIX,
    compare_budget,
    derive_calibration,
    measure,
)
from ctxbudget.report import (
    calibration_keys,
    render_budget,
    render_check,
    render_json,
    render_markdown,
)
from ctxbudget.resolve import ROOT_MARKERS, find_repo_root, is_repo_root
from ctxbudget.types import Calibration, Measurement, Observation
from ctxbudget.windows import MODEL_WINDOWS, agent_windows

logger = logging.getLogger(__name__)

# The committed budget, and the single place calibration provenance is
# stored. One file rather than two: the factor is only meaningful next
# to the figures it corrects, and a second file invites the two to drift.
BUDGET_RELATIVE: Final[str] = ".kiro/context-budget.json"

# Reports land in the gitignored tmp/ tree: they are regenerated output,
# and the numbers worth keeping are the ones in the committed budget.
DEFAULT_REPORT_STEM: Final[str] = "tmp/context-budget-report"

DEFAULT_TOLERANCE_PCT: Final[float] = 2.0

STDOUT_TARGET: Final[str] = "-"


def _add_common(parser: argparse.ArgumentParser) -> None:
    """
    Add the arguments every subcommand accepts.

    Args:
        parser: Subcommand parser to extend.
    """
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help=(
            "Repository root to measure (default: nearest ancestor holding "
            ".kiro/ and tools/)."
        ),
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser.

    Returns:
        Configured argument parser with its three subcommands.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Approximate context-token budgeting for the Kiro CLI agent "
            "system. Figures are approximate; deltas are trustworthy."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_report_parser(subparsers)
    _add_check_parser(subparsers)
    _add_calibrate_parser(subparsers)
    return parser


def _add_report_parser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    """
    Register the ``report`` subcommand.

    Args:
        subparsers: Subparser action to register on.
    """
    report = subparsers.add_parser("report", help="Measure and write a report.")
    _add_common(report)
    report.add_argument(
        "--output",
        type=str,
        default=None,
        help=(
            f"Report destination (default: {DEFAULT_REPORT_STEM}.<ext> under "
            f"the root; '{STDOUT_TARGET}' for stdout)."
        ),
    )
    report.add_argument(
        "--format", choices=("md", "json"), default="md", help="Output format."
    )
    report.add_argument(
        "--with-references",
        action="store_true",
        help=(
            "Also measure an upper bound over each skill's references/**. "
            "Never summed into a baseline or a session estimate."
        ),
    )


def _add_check_parser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    """
    Register the ``check`` subcommand.

    Args:
        subparsers: Subparser action to register on.
    """
    check = subparsers.add_parser("check", help="Gate against the recorded budget.")
    _add_common(check)
    check.add_argument(
        "--budget",
        type=Path,
        default=None,
        help=f"Budget file (default: {BUDGET_RELATIVE} under the root).",
    )
    check.add_argument(
        "--tolerance-pct",
        type=float,
        default=DEFAULT_TOLERANCE_PCT,
        help=(
            "Percentage a figure may exceed its budget by before it fails "
            f"(default {DEFAULT_TOLERANCE_PCT:g}, absorbing jitter)."
        ),
    )
    check.add_argument(
        "--write-budget",
        action="store_true",
        help=(
            "Re-record the budget from this measurement instead of gating "
            "against it. Preserves any stored calibration provenance."
        ),
    )


def _add_calibrate_parser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    """
    Register the ``calibrate`` subcommand.

    Args:
        subparsers: Subparser action to register on.
    """
    calibrate = subparsers.add_parser(
        "calibrate",
        help="Record a calibration factor from a /context show observation.",
        description=(
            "Derives a correction factor from ground truth read off Kiro "
            "CLI's own `/context show`, which reports each resource group as "
            "a percentage of the context window computed by the real "
            "tokenizer over the real assembled prompt. No API call is made "
            "and none is possible. Pass the percentage of the `Agent files` "
            "group: that group covers the resources an agent declares, and "
            "covers neither the agent prompt nor the auto-loaded steering "
            "files, so it is compared against the declared-resource subtotal "
            "rather than against a full baseline. The comparison is "
            "aggregate-only — at a 1M-token window one displayed decimal is "
            "1,000 tokens, which cannot resolve an individual file. Pass "
            "--observed-tokens instead when the figure is already in tokens."
        ),
    )
    _add_common(calibrate)
    calibrate.add_argument("--agent", default=None, help="Agent that was observed.")
    calibrate.add_argument(
        "--context-files-pct",
        type=float,
        default=None,
        help=(
            "Percentage of the window the observed agent's `Agent files` group filled."
        ),
    )
    calibrate.add_argument(
        "--observed-tokens",
        type=int,
        default=None,
        help="Observed token count, as an alternative to a percentage.",
    )
    calibrate.add_argument(
        "--window",
        type=int,
        default=None,
        help=(
            "Context window the percentage refers to. Default: the window "
            "the observed agent's `model` field implies, which is only "
            "available for the models "
            f"{', '.join(sorted(MODEL_WINDOWS))} — otherwise this flag is "
            "required, since a defaulted window scales the factor by the "
            "ratio of the two windows without saying so."
        ),
    )
    calibrate.add_argument(
        "--observations",
        type=Path,
        default=None,
        help=(
            "JSON file of several observations: "
            '{"window": 1000000, "observations": '
            '[{"agent": "orchestrator", "context_files_pct": 2.1}]}. '
            "Both `window` keys are optional and resolved per agent."
        ),
    )
    calibrate.add_argument(
        "--budget",
        type=Path,
        default=None,
        help=f"Budget file to store the factor in (default: {BUDGET_RELATIVE}).",
    )
    calibrate.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the derived factor without writing it.",
    )


def load_budget(path: Path) -> dict[str, object]:
    """
    Read a budget document.

    Args:
        path: Budget file.

    Returns:
        The decoded mapping, empty when the file does not exist.

    Raises:
        ValueError: If the file exists but is not a JSON object.
    """
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        message = f"cannot read budget {path}: {error}"
        raise ValueError(message) from error
    if not isinstance(data, dict):
        message = f"budget {path} top level is not an object"
        raise ValueError(message)
    return data


def calibration_from_budget(budget: dict[str, object]) -> Calibration | None:
    """
    Rebuild the stored calibration from a budget document.

    A partially written calibration block is treated as absent: a report
    footer claiming a factor without its provenance would be worse than
    one honestly saying "uncalibrated". The band, basis and caveats are
    optional so that a block written before they existed still reads,
    and a missing band collapses onto the point value rather than
    inventing a width for it.

    Args:
        budget: Decoded budget document.

    Returns:
        The stored calibration, or None when none is recorded.
    """
    factor = budget.get(f"{CALIBRATION_PREFIX}factor")
    observed_at = budget.get(f"{CALIBRATION_PREFIX}observed_at")
    if not isinstance(factor, (int, float)) or not isinstance(observed_at, str):
        return None
    agents = budget.get(f"{CALIBRATION_PREFIX}agents")
    version = budget.get(f"{CALIBRATION_PREFIX}tiktoken_version")
    window = budget.get(f"{CALIBRATION_PREFIX}window")
    basis = budget.get(f"{CALIBRATION_PREFIX}basis")
    return Calibration(
        factor=float(factor),
        factor_low=_bound(budget, "factor_low", float(factor)),
        factor_high=_bound(budget, "factor_high", float(factor)),
        observed_at=observed_at,
        agents=_agents(agents),
        tiktoken_version=version if isinstance(version, str) else "unknown",
        window=int(window) if isinstance(window, int) else 0,
        basis=basis if isinstance(basis, str) else "unrecorded",
        caveats=_indexed_values(budget, CAVEAT_PREFIX),
        observations=_indexed_values(budget, OBSERVATION_PREFIX),
    )


def _agents(value: object) -> tuple[str, ...]:
    """
    Read the agents a stored factor came from.

    Args:
        value: Recorded value, a separator-joined string.

    Returns:
        The agent names, empty when nothing usable was recorded.
    """
    if not isinstance(value, str):
        return ()
    return tuple(
        item.strip() for item in value.split(AGENT_SEPARATOR.strip()) if item.strip()
    )


def _indexed_values(budget: dict[str, object], prefix: str) -> tuple[str, ...]:
    """
    Collect one of the numbered scalar sequences, back in order.

    Numeric rather than lexicographic ordering, so a tenth entry does
    not sort between the first and the second.

    Args:
        budget: Decoded budget document.
        prefix: Full key prefix the sequence uses.

    Returns:
        The recorded items, empty when the sequence is absent.
    """
    entries = [
        (int(suffix), str(value))
        for key, value in budget.items()
        if key.startswith(prefix) and (suffix := key.removeprefix(prefix)).isdigit()
    ]
    return tuple(value for _, value in sorted(entries))


def _bound(budget: dict[str, object], key: str, fallback: float) -> float:
    """
    Read one end of a stored factor band.

    Args:
        budget: Decoded budget document.
        key: Calibration key holding the bound, without its prefix.
        fallback: Value to use when the bound was never recorded.

    Returns:
        The recorded bound, or the fallback.
    """
    value = budget.get(f"{CALIBRATION_PREFIX}{key}")
    return float(value) if isinstance(value, (int, float)) else fallback


def _resolve_root(root: Path | None) -> Path:
    """
    Resolve the repository root to measure.

    An explicit root is validated rather than trusted: pointing the tool
    at a tree that holds no ``.kiro/`` would otherwise produce an empty
    report, which reads as "nothing costs anything" instead of as a
    mistake.

    Args:
        root: Explicit root, or None to discover one.

    Returns:
        Absolute repository root.

    Raises:
        ValueError: If discovery fails, or the explicit root is not one.
    """
    if root is None:
        return find_repo_root()
    resolved = root.resolve()
    if not is_repo_root(resolved):
        markers = ", ".join(f"{marker}/" for marker in ROOT_MARKERS)
        message = f"{resolved} is not a repository root: it lacks {markers}"
        raise ValueError(message)
    return resolved


def _write(target: Path, text: str) -> None:
    """
    Write text to a path, creating parent directories.

    Args:
        target: Destination file.
        text: Content to write.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    logger.info("Written to %s.", target)


def _measure(args: argparse.Namespace, root: Path) -> Measurement:
    """
    Run a measurement under the resolved settings.

    Args:
        args: Parsed arguments.
        root: Repository root.

    Returns:
        The measurement snapshot.
    """
    budget_path = getattr(args, "budget", None) or root / BUDGET_RELATIVE
    calibration = calibration_from_budget(load_budget(budget_path))
    return measure(
        root=root,
        counter=TiktokenCounter(),
        with_references=bool(getattr(args, "with_references", False)),
        calibration=calibration,
    )


def cmd_report(args: argparse.Namespace) -> int:
    """
    Measure the tree and emit the report.

    Args:
        args: Parsed arguments.

    Returns:
        Process exit code, always 0 once the measurement succeeded.
    """
    root = _resolve_root(args.root)
    measurement = _measure(args, root)
    text = (
        render_json(measurement)
        if args.format == "json"
        else render_markdown(measurement)
    )
    if args.output == STDOUT_TARGET:
        sys.stdout.write(text)
        return 0
    if args.output is None:
        target = root / f"{DEFAULT_REPORT_STEM}.{args.format}"
    else:
        target = Path(args.output)
    _write(target, text)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    """
    Gate the measurement against the recorded budget.

    Args:
        args: Parsed arguments.

    Returns:
        1 when a figure exceeds its budget beyond tolerance, else 0.
    """
    root = _resolve_root(args.root)
    budget_path = args.budget or root / BUDGET_RELATIVE
    budget = load_budget(budget_path)
    measurement = _measure(args, root)
    if args.write_budget:
        _write(budget_path, render_budget(measurement))
        return 0
    if not budget:
        logger.error(
            "No budget at %s. Record one with `check --write-budget`.", budget_path
        )
        return 1
    violations, warnings = compare_budget(measurement, budget, args.tolerance_pct)
    sys.stdout.write(render_check(violations, warnings))
    return 1 if violations else 0


def _observations(
    args: argparse.Namespace, windows: dict[str, int]
) -> tuple[Observation, ...]:
    """
    Collect the observations a calibrate invocation supplies.

    Args:
        args: Parsed arguments.
        windows: Window each agent's declared model implies.

    Returns:
        The observations, in file order then CLI order.

    Raises:
        ValueError: If nothing was supplied, or the file is malformed.
    """
    collected = list(_file_observations(args.observations, windows))
    single = _flag_observation(args, windows)
    if single is not None:
        collected.append(single)
    if not collected:
        message = (
            "supply either --observations FILE, or --agent with "
            "--context-files-pct or --observed-tokens"
        )
        raise ValueError(message)
    return tuple(collected)


def _resolve_window(agent: str, explicit: object, windows: dict[str, int]) -> int:
    """
    Decide which context window an observation was read against.

    The window is a per-model property, so it is resolved from the
    observed agent's ``model`` field rather than defaulted. An
    undocumented model is an error, not a fallback: a percentage divided
    by the wrong window scales the derived factor by the ratio of the
    two, and nothing downstream could detect it.

    Args:
        agent: Agent the observation names.
        explicit: Window supplied on the command line or in the
            observations file, or None to resolve it.
        windows: Window each agent's declared model implies.

    Returns:
        The window in tokens.

    Raises:
        ValueError: If the explicit window is not positive, or none was
            given and the agent's model has no documented window.
    """
    if explicit is not None:
        window = int(explicit) if isinstance(explicit, (int, float)) else 0
        if window <= 0:
            message = f"window for agent {agent} must be a positive token count"
            raise ValueError(message)
        return window
    resolved = windows.get(agent)
    if resolved is None:
        message = (
            f"cannot determine the context window of agent {agent}: it declares "
            "no model, or one whose window the vendored Kiro docs do not state "
            f"(documented: {', '.join(sorted(MODEL_WINDOWS))}). Pass --window, "
            "or a 'window' key in the observations file"
        )
        raise ValueError(message)
    return resolved


def _flag_observation(
    args: argparse.Namespace, windows: dict[str, int]
) -> Observation | None:
    """
    Build the single observation the flags describe, if any.

    Args:
        args: Parsed arguments.
        windows: Window each agent's declared model implies.

    Returns:
        The observation, or None when the flags describe none.

    Raises:
        ValueError: If a figure was given without an agent, or the
            window could not be resolved.
    """
    has_figure = args.context_files_pct is not None or args.observed_tokens is not None
    if not has_figure:
        return None
    if not args.agent:
        message = "--agent is required alongside an observed figure"
        raise ValueError(message)
    window = _resolve_window(args.agent, args.window, windows)
    if args.observed_tokens is not None:
        return Observation(
            agent=args.agent,
            context_files_pct=args.observed_tokens / window * 100.0,
            window=window,
            display_step_pct=0.0,
        )
    return Observation(
        agent=args.agent,
        context_files_pct=float(args.context_files_pct),
        window=window,
    )


def _file_observations(
    path: Path | None, windows: dict[str, int]
) -> tuple[Observation, ...]:
    """
    Read observations from a JSON file.

    Args:
        path: Observations file, or None.
        windows: Window each agent's declared model implies.

    Returns:
        The parsed observations, empty when no file was given.

    Raises:
        ValueError: If the file cannot be read or has the wrong shape.
    """
    if path is None:
        return ()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        message = f"cannot read observations {path}: {error}"
        raise ValueError(message) from error
    if not isinstance(data, dict) or not isinstance(data.get("observations"), list):
        message = f"{path} must be an object with an 'observations' array"
        raise ValueError(message)
    window = data.get("window")
    observations = data["observations"]
    return tuple(_observation(item, window, windows, path) for item in observations)


def _observation(
    item: object, window: object, windows: dict[str, int], path: Path
) -> Observation:
    """
    Build one observation from a decoded file entry.

    Args:
        item: One element of the file's ``observations`` array.
        window: File-level window, or None to resolve per agent.
        windows: Window each agent's declared model implies.
        path: Observations file, for the error message.

    Returns:
        The parsed observation.

    Raises:
        ValueError: If the entry is not an object, omits a required
            field, carries a non-numeric figure, or names an agent whose
            window can be neither read nor resolved.
    """
    if not isinstance(item, dict):
        message = f"{path} holds a non-object observation"
        raise ValueError(message)
    agent = item.get("agent")
    percentage = item.get("context_files_pct")
    if not isinstance(agent, str) or not isinstance(percentage, (int, float)):
        message = (
            f"{path} holds an observation without a string 'agent' and a "
            "numeric 'context_files_pct'"
        )
        raise ValueError(message)
    return Observation(
        agent=agent,
        context_files_pct=float(percentage),
        window=_resolve_window(agent, item.get("window", window), windows),
    )


def cmd_calibrate(args: argparse.Namespace) -> int:
    """
    Derive and store a calibration factor.

    Args:
        args: Parsed arguments.

    Returns:
        Process exit code, 0 once the factor was derived.

    Raises:
        ValueError: If the observations or the tree are unusable.
    """
    root = _resolve_root(args.root)
    observations = _observations(args, agent_windows(root))
    measurement = _measure(args, root)
    calibration = derive_calibration(observations, measurement)
    logger.info(
        "Derived calibration factor %.4f (%.4f-%.4f) from %d observation(s).",
        calibration.factor,
        calibration.factor_low,
        calibration.factor_high,
        len(observations),
    )
    for line in calibration.observations:
        logger.info("  %s.", line)
    for caveat in calibration.caveats:
        logger.info("  Caveat: %s", caveat)
    if args.dry_run:
        logger.info("Dry run: nothing written.")
        return 0
    budget_path = args.budget or root / BUDGET_RELATIVE
    updated = {
        key: value
        for key, value in load_budget(budget_path).items()
        if not key.startswith(CALIBRATION_PREFIX)
    }
    updated.update(calibration_keys(calibration))
    _write(budget_path, json.dumps(dict(sorted(updated.items())), indent=2) + "\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    """
    Parse arguments and dispatch to the requested subcommand.

    Args:
        argv: Command-line arguments, defaulting to sys.argv[1:].

    Returns:
        Process exit code.
    """
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    commands = {
        "report": cmd_report,
        "check": cmd_check,
        "calibrate": cmd_calibrate,
    }
    try:
        return commands[args.command](args)
    except ValueError as error:
        logger.error("%s.", error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
