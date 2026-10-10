# Standard libraries
from collections.abc import Callable
from pathlib import Path
from typing import TypeAlias, TypedDict

ConvertResult: TypeAlias = tuple[Path, Path | None, str | None]

ResultCallback: TypeAlias = Callable[[Path, Path | None, str | None], bool]

AUDIO_EXTS: frozenset[str] = frozenset(
    {".wav", ".mp3", ".flac", ".ogg", ".m4a"},
)
IMAGE_EXTS: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif", ".webp", ".svg"},
)
PPTX_EXTS: frozenset[str] = frozenset({".pptx"})
ALLOWED_IMG_EXTS: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".emf", ".wmf"},
)
MAX_IMAGE_BLOB_SIZE: int = 50 * 1024 * 1024  # 50 MB
MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500 MB


class WhisperArgs(TypedDict):
    """
    Configuration dictionary for faster-whisper
    transcription settings.
    """

    model: str
    language: str | None
    beam_size: int
    device: str
    cpu_threads: int


DEFAULT_WHISPER_ARGS: WhisperArgs = WhisperArgs(
    model="Systran/faster-whisper-small",
    language=None,
    beam_size=1,
    device="auto",
    cpu_threads=4,
)
