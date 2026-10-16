"""Tests for the converter routing."""

# Standard libraries
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

# 3pps
import pytest

# Own modules
from doc2md.converter import _log_result, convert_files
from doc2md.types import DEFAULT_WHISPER_ARGS


def test_log_result_error(caplog: pytest.LogCaptureFixture) -> None:
    """
    Verify _log_result returns False and logs a warning
    on error.
    """

    with caplog.at_level(logging.WARNING):
        assert _log_result(Path("x.txt"), None, "fail") is False
    assert "Skipped" in caplog.text


def test_log_result_success(caplog: pytest.LogCaptureFixture) -> None:
    """
    Verify _log_result returns True and logs the
    conversion path.
    """

    with caplog.at_level(logging.INFO):
        assert _log_result(Path("x.txt"), Path("x.md"), None) is True
    assert "->" in caplog.text


@patch("doc2md.converter.convert_documents", return_value=1)
@patch("doc2md.converter.transcribe_audio", return_value=2)
def test_convert_files_routes_audio(
    mock_ta: MagicMock,
    mock_cd: MagicMock,
    tmp_path: Path,
) -> None:
    """
    Verify convert_files routes audio and non-audio
    files to the correct converters.
    """

    files = [Path("/a/song.mp3"), Path("/a/doc.pdf")]
    convert_files(files, tmp_path)
    mock_ta.assert_called_once()
    assert mock_ta.call_args[0][0] == [Path("/a/song.mp3")]
    mock_cd.assert_called_once()
    assert mock_cd.call_args[0][0] == [Path("/a/doc.pdf")]


@patch("doc2md.converter.convert_documents", return_value=1)
@patch("doc2md.converter.transcribe_audio", return_value=0)
def test_convert_files_routes_nonaudio(
    mock_ta: MagicMock,
    mock_cd: MagicMock,
    tmp_path: Path,
) -> None:
    """
    Verify convert_files skips audio transcription
    when no audio files exist.
    """

    files = [Path("/a/doc.pdf")]
    convert_files(files, tmp_path)
    mock_ta.assert_not_called()
    mock_cd.assert_called_once()


@patch("doc2md.converter.convert_documents", return_value=0)
@patch("doc2md.converter.transcribe_audio", return_value=1)
def test_convert_files_default_whisper_args(
    mock_ta: MagicMock,
    mock_cd: MagicMock,
    tmp_path: Path,
) -> None:
    """
    Verify convert_files uses DEFAULT_WHISPER_ARGS
    when whisper_args is None.
    """

    files = [Path("/a/song.wav")]
    convert_files(files, tmp_path, whisper_args=None)
    wa_used = mock_ta.call_args[0][3]
    assert wa_used == DEFAULT_WHISPER_ARGS


def test_convert_files_empty_list(tmp_path: Path) -> None:
    """
    Verify convert_files returns 0 for an empty file
    list.
    """

    assert convert_files([], tmp_path) == 0
