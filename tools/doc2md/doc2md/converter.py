# Standard libraries
import logging
import os
from pathlib import Path

# Own modules
from doc2md.converters.markitdown import convert_documents
from doc2md.converters.whisper import transcribe_audio
from doc2md.types import AUDIO_EXTS, DEFAULT_WHISPER_ARGS, WhisperArgs

logger: logging.Logger = logging.getLogger(__name__)


def _log_result(
    src: Path,
    dest: Path | None,
    err: str | None,
) -> bool:
    """
    Log a single conversion result.

    Logs a warning for failures and an info message for
    successes.

    Args:
        src: Source file that was converted.
        dest: Destination file produced, or None on failure.
        err: Error message if conversion failed, or None
            on success.

    Returns:
        True if the conversion succeeded, False otherwise.
    """

    if err:
        logger.warning("Skipped '%s': %s", src, err)
        return False

    logger.info("%s -> %s.", src, dest)
    return True


def convert_files(
    files: list[Path],
    output_dir: Path,
    whisper_args: WhisperArgs | None = None,
) -> int:
    """
    Convert a list of files to Markdown.

    Routes audio files through faster-whisper and all
    remaining files through MarkItDown. Audio is processed
    sequentially in the main process; documents are
    converted in parallel via a process pool.

    Args:
        files: Files to convert.
        output_dir: Root directory for generated Markdown.
        whisper_args: Whisper model configuration. Falls
            back to sensible defaults when omitted.

    Returns:
        Number of files successfully converted.
    """

    if not files:
        return 0

    try:
        rel_to: Path | None = Path(os.path.commonpath(f.parent for f in files))
    except ValueError:
        rel_to = None

    audio: list[Path] = []
    other: list[Path] = []
    for f in files:
        (audio if f.suffix.lower() in AUDIO_EXTS else other).append(f)

    converted: int = 0

    if audio:
        wa: WhisperArgs = whisper_args or DEFAULT_WHISPER_ARGS

        converted += transcribe_audio(
            audio,
            output_dir,
            rel_to,
            wa,
            _log_result,
        )

    if other:
        converted += convert_documents(
            other,
            output_dir,
            rel_to,
            _log_result,
        )

    return converted
