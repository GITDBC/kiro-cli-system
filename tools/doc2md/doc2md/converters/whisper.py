# Standard libraries
import functools
import logging
import subprocess
from pathlib import Path
from typing import Any

# Own modules
from doc2md.types import ConvertResult, ResultCallback, WhisperArgs

logger: logging.Logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def _has_nvidia_gpu() -> bool:
    """
    Detect whether an NVIDIA GPU is available by
    attempting to run ``nvidia-smi``.

    Returns:
        True if ``nvidia-smi`` exits successfully,
            False otherwise.
    """

    try:
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            timeout=5,
            check=False,
        )

    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

    else:
        return result.returncode == 0


def _load_model(args: WhisperArgs) -> Any:
    """
    Load a faster-whisper model based on the provided
    configuration.

    Automatically selects CUDA with float16 when an
    NVIDIA GPU is detected, otherwise falls back to CPU
    with int8 quantisation.

    Args:
        args: Whisper model configuration.

    Returns:
        A loaded ``WhisperModel`` instance ready for
            transcription.
    """

    # 3pps
    from faster_whisper import WhisperModel

    device: str = args["device"]

    if device == "auto":
        device = "cuda" if _has_nvidia_gpu() else "cpu"

    compute: str = "float16" if device == "cuda" else "int8"

    extra: dict[str, int] = (
        {} if device == "cuda" else {"cpu_threads": args["cpu_threads"]}
    )

    return WhisperModel(
        args["model"],
        device=device,
        compute_type=compute,
        **extra,
    )


def _transcribe_single(
    file: Path,
    output_dir: Path,
    rel_to: Path | None,
    model: Any,
    args: WhisperArgs,
) -> ConvertResult:
    """
    Transcribe a single audio file and write the result
    as a Markdown document.

    The output file contains the original filename as a
    heading followed by the transcribed text, with
    paragraphs separated by blank lines.

    Args:
        file: Audio file to transcribe.
        output_dir: Root directory for generated Markdown.
        rel_to: Common ancestor path used to preserve
            directory structure in the output.
        model: A loaded ``WhisperModel`` instance.
        args: Whisper model configuration.

    Returns:
        Tuple of (source path, destination path or None
            on failure, error message or None on success).
    """

    try:
        relative: Path = file.relative_to(rel_to) if rel_to else Path(file.name)
        dest_dir: Path = output_dir / relative.parent

        if not dest_dir.resolve().is_relative_to(output_dir.resolve()):
            return file, None, "output path escapes output directory."

        dest_dir.mkdir(parents=True, exist_ok=True)

        segments, _ = model.transcribe(
            str(file),
            language=args["language"],
            beam_size=args["beam_size"],
            vad_filter=True,
        )

        text: str = "\n\n".join(s.text.strip() for s in segments if s.text.strip())

        if not text:
            return file, None, "transcription produced empty output."

        dest: Path = dest_dir / f"{file.stem}_{file.suffix.lstrip('.')}.md"

        dest.write_text(
            f"# {file.name}\n\n{text}\n",
            encoding="utf-8",
        )

    except Exception as e:
        logger.debug("Transcription failed for '%s'.", file, exc_info=True)
        return file, None, str(e)

    else:
        return file, dest, None


def transcribe_audio(
    files: list[Path],
    output_dir: Path,
    rel_to: Path | None,
    args: WhisperArgs,
    on_result: ResultCallback,
) -> int:
    """
    Transcribe a list of audio files sequentially using
    faster-whisper.

    The model is loaded once and reused for all files.
    Results are reported through the callback as each
    file completes.

    Args:
        files: Audio files to transcribe.
        output_dir: Root directory for generated Markdown.
        rel_to: Common ancestor path used to preserve
            directory structure in the output.
        args: Whisper model configuration.
        on_result: Callback invoked with each conversion
            result as ``(source, dest, error)``. Must
            return a truthy value on success.

    Returns:
        Number of files successfully transcribed.
    """

    logger.info(
        "Transcribing %d audio file(s) with '%s'.",
        len(files),
        args["model"],
    )

    model: Any = _load_model(args)
    converted: int = 0

    for f in files:
        result: ConvertResult = _transcribe_single(
            f,
            output_dir,
            rel_to,
            model,
            args,
        )
        converted += on_result(*result)

    return converted
