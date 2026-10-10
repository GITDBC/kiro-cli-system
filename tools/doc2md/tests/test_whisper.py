# Standard libraries
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# Own modules
from doc2md.converters.whisper import _has_nvidia_gpu, _transcribe_single
from doc2md.types import WhisperArgs


def _wa() -> WhisperArgs:
    """Build a minimal WhisperArgs for testing."""

    return WhisperArgs(
        model="m",
        language=None,
        beam_size=1,
        device="cpu",
        cpu_threads=1,
    )


def test_has_nvidia_gpu_not_found() -> None:
    """
    Verify _has_nvidia_gpu returns False when
    nvidia-smi is not found.
    """

    _has_nvidia_gpu.cache_clear()
    with patch(
        "doc2md.converters.whisper.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        assert _has_nvidia_gpu() is False
    _has_nvidia_gpu.cache_clear()


def test_has_nvidia_gpu_success() -> None:
    """
    Verify _has_nvidia_gpu returns True when
    nvidia-smi succeeds.
    """

    _has_nvidia_gpu.cache_clear()
    mock_result = MagicMock(returncode=0)
    with patch(
        "doc2md.converters.whisper.subprocess.run",
        return_value=mock_result,
    ):
        assert _has_nvidia_gpu() is True
    _has_nvidia_gpu.cache_clear()


def test_transcribe_single_success(tmp_path: Path) -> None:
    """
    Verify _transcribe_single writes transcription
    to a markdown file.
    """

    src = tmp_path / "audio.wav"
    src.write_bytes(b"\x00")
    out = tmp_path / "out"

    seg = SimpleNamespace(text=" hello world ")
    model = MagicMock()
    model.transcribe.return_value = ([seg], None)

    _, dest, err = _transcribe_single(src, out, tmp_path, model, _wa())
    assert err is None
    assert dest is not None and dest.exists()
    assert "hello world" in dest.read_text()


def test_transcribe_single_empty(tmp_path: Path) -> None:
    """
    Verify _transcribe_single reports an error for
    empty transcription.
    """

    src = tmp_path / "audio.wav"
    src.write_bytes(b"\x00")
    out = tmp_path / "out"

    model = MagicMock()
    model.transcribe.return_value = ([], None)

    _, dest, err = _transcribe_single(src, out, tmp_path, model, _wa())
    assert dest is None
    assert err is not None and "empty" in err


def test_transcribe_single_path_escape(tmp_path: Path) -> None:
    """
    Verify _transcribe_single rejects paths that
    escape the output directory.
    """

    src = tmp_path / "audio.wav"
    src.write_bytes(b"\x00")
    out = tmp_path / "out"
    bad_rel = tmp_path / "other"
    bad_rel.mkdir()

    model = MagicMock()
    model.transcribe.return_value = ([SimpleNamespace(text="hi")], None)

    _, dest, err = _transcribe_single(src, out, bad_rel, model, _wa())
    assert dest is None
    assert err is not None
