"""Command-line interface for doc2md."""

# Standard libraries
import argparse
import logging
import os
import sys
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

# Own modules
from doc2md.converter import convert_files
from doc2md.files import collect_files
from doc2md.types import DEFAULT_WHISPER_ARGS, WhisperArgs

logger: logging.Logger = logging.getLogger(__name__)

_TOOL_SECTION: str = "doc2md"


def _load_global_defaults() -> dict[str, Any]:
    """
    Read defaults from the global TOML config.

    Returns:
        Dictionary with tool settings, or empty dict.

    Raises:
        ValueError: If the config file is not valid TOML.
    """

    path_str: str | None = os.environ.get("WORK_AGENTS_CONFIG")
    if not path_str:
        return {}
    path: Path = Path(path_str)
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as fh:
            result: dict[str, Any] = tomllib.load(fh).get(_TOOL_SECTION, {})
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid TOML in config file {path}: {exc}") from exc
    return result


def _apply_config_defaults(
    parser: argparse.ArgumentParser,
    defaults: Mapping[str, Any],
) -> None:
    """
    Seed the whisper options from the global config.

    Command-line values still win, since argparse only falls back
    to these defaults for options that were not passed.

    Args:
        parser: Parser built by ``_build_parser``.
        defaults: The ``[doc2md]`` section of the global config.
    """

    parser.set_defaults(
        **{
            f"whisper_{key}": defaults.get(f"whisper_{key}", value)
            for key, value in DEFAULT_WHISPER_ARGS.items()
        }
    )


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser with all positional
    arguments, options, and the whisper argument group.

    Returns:
        Configured argument parser.
    """

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=(
            "Convert files to Markdown using MarkItDown (and Whisper for audio)."
        ),
    )

    parser.add_argument(
        "paths",
        nargs="+",
        help="Files or directories to process.",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="Output directory (default: output).",
    )

    parser.add_argument(
        "-e",
        "--exclude",
        nargs="+",
        default=None,
        help="Glob patterns to exclude.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )

    wg: argparse._ArgumentGroup = parser.add_argument_group(
        "whisper",
        "Audio transcription via faster-whisper",
    )

    wg.add_argument(
        "--whisper-model",
        help="Model name or path.",
    )

    wg.add_argument(
        "--whisper-language",
        help="Language code (e.g. 'es'). Auto-detect if omitted.",
    )

    wg.add_argument(
        "--whisper-beam-size",
        type=int,
        help="Beam size (default: 1).",
    )

    wg.add_argument(
        "--whisper-device",
        choices=["auto", "cpu", "cuda"],
        help="Device (default: auto).",
    )

    wg.add_argument(
        "--whisper-cpu-threads",
        type=int,
        help="CPU threads (default: 4).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """
    Entry point for the doc2md CLI.

    Parses command-line arguments, collects input files,
    and runs the conversion pipeline.

    Args:
        argv: Command-line arguments, defaulting to sys.argv[1:].

    Returns:
        Process exit code: 1 when the global config is invalid, when
        no files are found or when nothing was converted; 0 otherwise.
    """

    os.umask(0o077)

    parser: argparse.ArgumentParser = _build_parser()
    try:
        defaults: dict[str, Any] = _load_global_defaults()
    except ValueError as exc:
        logger.error("%s.", exc)
        return 1
    _apply_config_defaults(parser, defaults)
    args: argparse.Namespace = parser.parse_args(argv)

    w_model: str = args.whisper_model
    w_language: str | None = args.whisper_language
    w_beam: int = args.whisper_beam_size
    w_device: str = args.whisper_device
    w_threads: int = args.whisper_cpu_threads

    if not isinstance(w_beam, int):
        parser.error("--whisper-beam-size must be an integer.")
    if not isinstance(w_threads, int):
        parser.error("--whisper-cpu-threads must be an integer.")

    if w_beam < 1 or w_beam > 20:
        parser.error("--whisper-beam-size must be between 1 and 20.")
    if w_threads < 1 or w_threads > 32:
        parser.error("--whisper-cpu-threads must be between 1 and 32.")

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    files: list[Path] = collect_files(
        args.paths,
        args.exclude,
    )

    if not files:
        logger.error("No files found to process.")
        return 1

    files = [f.resolve() for f in files]

    logger.info("Found %d file(s) to process.", len(files))

    wa: WhisperArgs = WhisperArgs(
        model=w_model,
        language=w_language,
        beam_size=w_beam,
        device=w_device,
        cpu_threads=w_threads,
    )

    converted: int = convert_files(
        files,
        Path(args.output),
        whisper_args=wa,
    )

    logger.info(
        "%d/%d file(s) converted in '%s'.",
        converted,
        len(files),
        args.output,
    )

    return 0 if converted else 1


if __name__ == "__main__":
    sys.exit(main())
