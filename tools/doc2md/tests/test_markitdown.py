# Standard libraries
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# Own modules
from doc2md.converters.markitdown import (
    _apply_image_replacements,
    _convert_single,
    _process_shape,
)


def test_convert_single_no_converter() -> None:
    """
    Verify _convert_single fails when the converter
    is not initialised.
    """

    src, dest, err = _convert_single(Path("x.pdf"), Path("out"))
    assert dest is None
    assert err is not None and "not initialised" in err


def test_convert_single_success(tmp_path: Path) -> None:
    """
    Verify _convert_single writes converted markdown
    to the output directory.
    """

    src = tmp_path / "doc.pdf"
    src.write_bytes(b"%PDF")
    out = tmp_path / "out"
    mock_conv = MagicMock()
    mock_conv.convert.return_value = SimpleNamespace(
        text_content="# Title\nBody",
    )
    with patch("doc2md.converters.markitdown._converter", mock_conv):
        _, dest, err = _convert_single(src, out, tmp_path)
    assert err is None
    assert dest is not None and dest.exists()
    assert "Title" in dest.read_text()


def test_convert_single_image_copy(tmp_path: Path) -> None:
    """
    Verify _convert_single copies image files instead
    of converting them.
    """

    src = tmp_path / "pic.png"
    src.write_bytes(b"\x89PNG")
    out = tmp_path / "out"
    mock_conv = MagicMock()
    mock_conv.convert.return_value = SimpleNamespace(text_content="")
    with patch("doc2md.converters.markitdown._converter", mock_conv):
        _, dest, err = _convert_single(src, out, tmp_path)
    assert err is None
    assert dest is not None and dest.name == "pic.png"


def test_convert_single_empty_non_image(tmp_path: Path) -> None:
    """
    Verify _convert_single reports an error for empty
    non-image conversions.
    """

    src = tmp_path / "doc.pdf"
    src.write_bytes(b"%PDF")
    out = tmp_path / "out"
    mock_conv = MagicMock()
    mock_conv.convert.return_value = SimpleNamespace(text_content="")
    with patch("doc2md.converters.markitdown._converter", mock_conv):
        _, dest, err = _convert_single(src, out, tmp_path)
    assert dest is None
    assert err is not None and "empty" in err


def test_convert_single_path_escape(tmp_path: Path) -> None:
    """
    Verify _convert_single rejects paths that escape
    the output directory.
    """

    src = tmp_path / "doc.pdf"
    src.write_bytes(b"%PDF")
    out = tmp_path / "out"
    bad_rel = tmp_path / "other"
    bad_rel.mkdir()
    mock_conv = MagicMock()
    mock_conv.convert.return_value = SimpleNamespace(text_content="content")
    with patch("doc2md.converters.markitdown._converter", mock_conv):
        _, dest, err = _convert_single(src, out, bad_rel)
    assert dest is None
    assert err is not None


def test_process_shape_no_image() -> None:
    """
    Verify _process_shape skips shapes without an
    image attribute.
    """

    shape = SimpleNamespace(name="s1")
    replacements: dict[str, list[str]] = {}
    _process_shape(shape, 0, Path("/tmp"), "f", replacements)
    assert replacements == {}


def test_process_shape_oversized(tmp_path: Path) -> None:
    """
    Verify _process_shape skips images exceeding
    MAX_IMAGE_BLOB_SIZE.
    """

    shape = SimpleNamespace(
        name="big",
        image=SimpleNamespace(blob=b"x" * 100, filename="big.png"),
    )
    replacements: dict[str, list[str]] = {}
    with patch("doc2md.converters.markitdown.MAX_IMAGE_BLOB_SIZE", 10):
        _process_shape(shape, 0, tmp_path, "f", replacements)
    assert replacements == {}


def test_process_shape_png_fallback(tmp_path: Path) -> None:
    """
    Verify _process_shape falls back to .png for
    unsupported extensions.
    """

    shape = SimpleNamespace(
        name="img1",
        image=SimpleNamespace(blob=b"data", filename="img.xyz"),
    )
    replacements: dict[str, list[str]] = defaultdict(list)
    _process_shape(shape, 0, tmp_path, "f", replacements)
    written = list(tmp_path.glob("*.png"))
    assert len(written) == 1


def test_apply_image_replacements() -> None:
    """
    Verify _apply_image_replacements substitutes
    image paths in content.
    """

    content = "![alt](img1jpg.jpg) text ![alt](img1jpg.jpg)"
    replacements: dict[str, list[str]] = {
        "img1jpg.jpg": ["real1.png", "real2.png"],
    }
    result = _apply_image_replacements(content, replacements)
    assert "real1.png" in result
    assert "real2.png" in result


def test_apply_image_replacements_duplicates() -> None:
    """
    Verify _apply_image_replacements handles multiple
    occurrences of the same fake name correctly.
    """

    content = "![a](foo.jpg) ![b](foo.jpg)"
    replacements: dict[str, list[str]] = {
        "foo.jpg": ["r1.png", "r2.png"],
    }
    result = _apply_image_replacements(content, replacements)
    assert "r1.png" in result
    assert "r2.png" in result
    assert "foo.jpg" not in result
