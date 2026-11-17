"""Fixtures shared by the depschecker test suite."""

# Standard libraries
import json
from pathlib import Path
from typing import Any

# 3pps
import pytest

_FIXTURES: Path = Path(__file__).parent / "fixtures"


@pytest.fixture
def urllib3_versioned_response() -> dict[str, Any]:
    """
    Recorded PyPI response for ``urllib3==2.6.3``.

    Captured verbatim from
    ``https://pypi.org/pypi/urllib3/2.6.3/json``, trimmed
    to the keys depschecker reads. Serves as the offline
    negative control: this version is known to carry
    advisories, so a scanner that reports it clean is
    broken.

    Returns:
        Decoded PyPI JSON payload.
    """

    path: Path = _FIXTURES / "pypi-urllib3-2.6.3.json"
    return dict(json.loads(path.read_text(encoding="utf-8")))


@pytest.fixture
def urllib3_unversioned_response() -> dict[str, Any]:
    """
    Recorded shape of the *unversioned* PyPI endpoint.

    ``https://pypi.org/pypi/urllib3/json`` reports an
    empty ``vulnerabilities`` array no matter how many
    advisories the installed version has. This fixture
    pins that behaviour so the original defect cannot
    return unnoticed.

    Returns:
        Decoded PyPI JSON payload.
    """

    return {
        "info": {
            "name": "urllib3",
            "version": "2.8.0",
            "project_urls": {"Changelog": "https://example.com/changelog"},
        },
        "releases": {"2.6.3": [], "2.7.0": [], "2.8.0": []},
        "vulnerabilities": [],
    }
