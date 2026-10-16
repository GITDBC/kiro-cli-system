"""Tests for the Whisper converter."""

# Standard libraries
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# Own modules
from doc2md.converters.whisper import (
    _has_nvidia_gpu,
    _load_model,
    _transcribe_single,
    transcribe_audio,
)
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


def test_transcribe_audio_loads_model_once(tmp_path: Path) -> None:
    """
    Verify transcribe_audio loads the model once and
    counts every successful transcription.
    """

    files = [tmp_path / "a.wav", tmp_path / "b.wav"]
    model = MagicMock()
    with (
        patch(
            "doc2md.converters.whisper._load_model",
            return_value=model,
        ) as load,
        patch(
            "doc2md.converters.whisper._transcribe_single",
            side_effect=lambda f, *_: (f, f, None),
        ),
    ):
        converted = transcribe_audio(
            files, tmp_path, None, _wa(), lambda *r: r[1] is not None
        )

    assert converted == 2
    load.assert_called_once()


def test_load_model_cpu_passes_threads() -> None:
    """
    Verify _load_model uses int8 on CPU and forwards
    the configured thread count.
    """

    fake = MagicMock()
    with patch.dict(sys.modules, {"faster_whisper": fake}):
        _load_model(_wa())
    fake.WhisperModel.assert_called_once_with(
        "m", device="cpu", compute_type="int8", cpu_threads=1
    )


def test_load_model_auto_selects_cuda() -> None:
    """
    Verify _load_model resolves device "auto" to CUDA
    with float16 when a GPU is detected.
    """

    fake = MagicMock()
    args = _wa()
    args["device"] = "auto"
    with (
        patch.dict(sys.modules, {"faster_whisper": fake}),
        patch("doc2md.converters.whisper._has_nvidia_gpu", return_value=True),
    ):
        _load_model(args)
    fake.WhisperModel.assert_called_once_with(
        "m", device="cuda", compute_type="float16"
    )
