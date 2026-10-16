"""Tests for the PyPI queries."""

# Standard libraries
import os
from typing import Any
from unittest.mock import MagicMock, patch

# 3pps
import pytest
import requests

# Own modules
from depschecker.pypi import (
    _classify_update,
    _extract_vulns,
    _find_changelog,
    _latest_stable,
    _version_tuple,
    check_freshness,
    check_vulnerabilities,
    scan_vulnerabilities,
)

_LIVE: bool = bool(os.environ.get("DEPSCHECKER_LIVE_NETWORK"))
_KNOWN_ADVISORY: str = "GHSA-mf9v-mfxr-j63j"


def _response(payload: dict[str, Any]) -> MagicMock:
    """
    Build a mock ``requests.Response`` for a payload.

    Args:
        payload: JSON body the mock should return.

    Returns:
        Mock response object.
    """

    resp = MagicMock()
    resp.json.return_value = payload
    return resp


def test_version_tuple_simple() -> None:
    """
    Verify _version_tuple parses a standard version.
    """

    assert _version_tuple("2.32.3") == (2, 32, 3)


def test_version_tuple_non_numeric() -> None:
    """
    Verify _version_tuple treats non-numeric segments
    as zero.
    """

    assert _version_tuple("1.0b2") == (1, 0)


def test_classify_update_up_to_date() -> None:
    """
    Verify _classify_update returns up-to-date for
    equal versions.
    """

    assert _classify_update("1.0.0", "1.0.0") == "up-to-date"


def test_classify_update_patch() -> None:
    """
    Verify _classify_update detects patch updates.
    """

    assert _classify_update("1.0.0", "1.0.1") == "patch"


def test_classify_update_minor() -> None:
    """
    Verify _classify_update detects minor updates.
    """

    assert _classify_update("1.0.0", "1.1.0") == "minor"


def test_classify_update_major() -> None:
    """
    Verify _classify_update detects major updates.
    """

    assert _classify_update("1.0.0", "2.0.0") == "major"


def test_classify_update_empty() -> None:
    """
    Verify _classify_update returns unknown for empty
    versions.
    """

    assert _classify_update("", "1.0.0") == "unknown"
    assert _classify_update("1.0.0", "") == "unknown"


def test_latest_stable_skips_prerelease() -> None:
    """
    Verify _latest_stable falls back to scanning
    releases when info.version is a pre-release.
    """

    data = {
        "info": {"version": "2.0.0rc1"},
        "releases": {"1.9.0": [], "2.0.0rc1": []},
    }
    assert _latest_stable(data) == "1.9.0"


def test_latest_stable_no_stable() -> None:
    """
    Verify _latest_stable returns the pre-release
    when no stable exists.
    """

    data = {
        "info": {"version": "1.0.0a1"},
        "releases": {"1.0.0a1": []},
    }
    assert _latest_stable(data) == "1.0.0a1"


def test_latest_stable_stable_version() -> None:
    """
    Verify _latest_stable returns info.version when
    it is stable.
    """

    data = {"info": {"version": "3.0.0"}, "releases": {}}
    assert _latest_stable(data) == "3.0.0"


def test_find_changelog_direct_key() -> None:
    """
    Verify _find_changelog finds a direct Changelog
    key.
    """

    data = {
        "info": {
            "project_urls": {"Changelog": "https://example.com/changes"},
        },
    }
    assert _find_changelog(data) == "https://example.com/changes"


def test_find_changelog_fallback() -> None:
    """
    Verify _find_changelog falls back to URL
    containing 'changelog'.
    """

    data = {
        "info": {
            "project_urls": {"Docs": "https://example.com/changelog"},
        },
    }
    assert _find_changelog(data) == "https://example.com/changelog"


def test_find_changelog_none() -> None:
    """
    Verify _find_changelog returns empty string when
    no changelog URL exists.
    """

    data = {"info": {"project_urls": {"Home": "https://example.com"}}}
    assert _find_changelog(data) == ""


def test_extract_vulns_empty() -> None:
    """
    Verify _extract_vulns returns empty list when
    no vulnerabilities exist.
    """

    assert _extract_vulns({}) == []


def test_extract_vulns_null_key() -> None:
    """
    Verify _extract_vulns tolerates an explicit null
    vulnerabilities value.
    """

    assert _extract_vulns({"vulnerabilities": None}) == []


def test_extract_vulns_with_data() -> None:
    """
    Verify _extract_vulns parses vulnerability
    entries correctly.
    """

    data = {
        "vulnerabilities": [
            {
                "id": "GHSA-aaaa-bbbb-cccc",
                "aliases": ["CVE-2024-0001"],
                "summary": "Bad thing.",
                "fixed_in": ["1.2.0"],
                "link": "https://cve.example.com",
            },
        ],
    }
    result = _extract_vulns(data)
    assert len(result) == 1
    assert result[0].id == "GHSA-aaaa-bbbb-cccc"
    assert result[0].fixed_in == "1.2.0"
    assert result[0].aliases == "CVE-2024-0001"


def test_extract_vulns_null_summary_becomes_empty() -> None:
    """
    Verify _extract_vulns maps an explicit null summary
    to an empty string rather than leaking None.
    """

    data = {
        "vulnerabilities": [
            {"id": "PYSEC-2026-1", "summary": None, "fixed_in": None, "link": None},
        ],
    }
    result = _extract_vulns(data)
    assert result[0].summary == ""
    assert result[0].fixed_in == ""
    assert result[0].link == ""


def test_extract_vulns_marks_withdrawn() -> None:
    """
    Verify _extract_vulns flags retracted advisories.
    """

    data = {
        "vulnerabilities": [
            {"id": "GHSA-x", "withdrawn": "2026-01-01T00:00:00Z"},
        ],
    }
    assert _extract_vulns(data)[0].withdrawn is True


# --- Negative control -------------------------------------------------------
# The defect these three tests guard: depschecker queried
# https://pypi.org/pypi/<name>/json, whose `vulnerabilities` key is always
# empty, so every scan reported clean. Nothing in the old suite asserted that a
# known-vulnerable package produces a finding, which is why it survived.


def test_check_vulnerabilities_detects_known_advisory(
    urllib3_versioned_response: dict[str, Any],
) -> None:
    """
    Verify a known-vulnerable version yields findings.

    ``urllib3==2.6.3`` carries four advisories on PyPI. A
    scanner reporting it clean is not working.
    """

    with patch(
        "depschecker.pypi.requests.get",
        return_value=_response(urllib3_versioned_response),
    ):
        status = check_vulnerabilities("urllib3", "2.6.3")

    assert status.error == ""
    assert status.advisories, "known-vulnerable version reported clean"
    assert _KNOWN_ADVISORY in {a.id for a in status.advisories}
    assert all(a.fixed_in == "2.7.0" for a in status.advisories)


def test_check_vulnerabilities_requests_versioned_url(
    urllib3_versioned_response: dict[str, Any],
) -> None:
    """
    Verify the queried URL carries the version segment.

    PyPI populates ``vulnerabilities`` only on the
    version-specific endpoint, so the version segment is
    the whole fix.
    """

    with patch(
        "depschecker.pypi.requests.get",
        return_value=_response(urllib3_versioned_response),
    ) as mock_get:
        check_vulnerabilities("urllib3", "2.6.3")

    url = mock_get.call_args.args[0]
    assert url == "https://pypi.org/pypi/urllib3/2.6.3/json"
    assert "/2.6.3/" in url


def test_unversioned_endpoint_hides_advisories(
    urllib3_unversioned_response: dict[str, Any],
) -> None:
    """
    Pin the PyPI behaviour that caused the defect.

    The unversioned payload reports no advisories even for
    a package with four, so freshness responses must never
    be used as a vulnerability source.
    """

    assert _extract_vulns(urllib3_unversioned_response) == []


def test_check_vulnerabilities_deduplicates_alias_pairs(
    urllib3_versioned_response: dict[str, Any],
) -> None:
    """
    Verify GHSA and PYSEC entries sharing a CVE collapse.

    The recorded response lists four entries covering two
    real vulnerabilities.
    """

    raw = urllib3_versioned_response["vulnerabilities"]
    assert len(raw) == 4

    with patch(
        "depschecker.pypi.requests.get",
        return_value=_response(urllib3_versioned_response),
    ):
        status = check_vulnerabilities("urllib3", "2.6.3")

    assert len(status.advisories) == 2


def test_check_vulnerabilities_rejects_empty_version() -> None:
    """
    Verify an unversioned audit is refused outright.

    Querying without a version is the original bug, so it
    fails loudly rather than returning a false clean.
    """

    with pytest.raises(ValueError, match="without a resolved version"):
        check_vulnerabilities("urllib3", "")


def test_check_vulnerabilities_network_error() -> None:
    """
    Verify check_vulnerabilities records network errors
    instead of reporting a clean result.
    """

    with patch(
        "depschecker.pypi.requests.get",
        side_effect=requests.RequestException("timeout"),
    ):
        status = check_vulnerabilities("urllib3", "2.6.3")

    assert status.error != ""
    assert status.advisories == []


def test_check_vulnerabilities_marks_direct() -> None:
    """
    Verify the direct-dependency flag is carried through.
    """

    with patch(
        "depschecker.pypi.requests.get",
        return_value=_response({"vulnerabilities": []}),
    ):
        status = check_vulnerabilities("requests", "2.33.1", direct=True)

    assert status.direct is True


def test_scan_vulnerabilities_preserves_order() -> None:
    """
    Verify scan_vulnerabilities returns results in input
    order despite concurrent execution.
    """

    packages = [("a", "1.0", True), ("b", "2.0", False), ("c", "3.0", False)]
    with patch(
        "depschecker.pypi.requests.get",
        return_value=_response({"vulnerabilities": []}),
    ):
        results = scan_vulnerabilities(packages)

    assert [r.name for r in results] == ["a", "b", "c"]
    assert [r.resolved for r in results] == ["1.0", "2.0", "3.0"]


def test_scan_vulnerabilities_empty() -> None:
    """
    Verify scan_vulnerabilities short-circuits on an
    empty input without opening a thread pool.
    """

    assert scan_vulnerabilities([]) == []


# --- Freshness --------------------------------------------------------------


def test_check_freshness_success() -> None:
    """
    Verify check_freshness populates DepStatus from
    a mocked PyPI response.
    """

    payload = {
        "info": {"version": "2.0.0", "project_urls": None},
        "releases": {},
    }
    with patch("depschecker.pypi.requests.get", return_value=_response(payload)):
        status = check_freshness("pkg", "1.0.0")

    assert status.latest == "2.0.0"
    assert status.update_type == "major"
    assert status.error == ""


def test_check_freshness_requests_unversioned_url() -> None:
    """
    Verify freshness queries the unversioned endpoint,
    the only one exposing releases and the true latest.
    """

    payload = {"info": {"version": "2.0.0"}, "releases": {}}
    with patch(
        "depschecker.pypi.requests.get",
        return_value=_response(payload),
    ) as mock_get:
        check_freshness("pkg", "1.0.0", resolved="1.5.0")

    assert mock_get.call_args.args[0] == "https://pypi.org/pypi/pkg/json"


def test_check_freshness_compares_resolved_not_declared() -> None:
    """
    Verify the update distance is measured from the
    resolved version, not the declared constraint floor.
    """

    payload = {"info": {"version": "2.33.1"}, "releases": {}}
    with patch("depschecker.pypi.requests.get", return_value=_response(payload)):
        status = check_freshness("requests", "2.32", resolved="2.33.1")

    assert status.effective == "2.33.1"
    assert status.update_type == "up-to-date"


def test_check_freshness_falls_back_to_declared() -> None:
    """
    Verify freshness still works with no lockfile, using
    the declared constraint floor.
    """

    payload = {"info": {"version": "2.33.1"}, "releases": {}}
    with patch("depschecker.pypi.requests.get", return_value=_response(payload)):
        status = check_freshness("requests", "2.32")

    assert status.effective == "2.32"
    assert status.update_type == "minor"


def test_check_freshness_network_error() -> None:
    """
    Verify check_freshness sets error on network
    failure.
    """

    with patch(
        "depschecker.pypi.requests.get",
        side_effect=requests.RequestException("timeout"),
    ):
        status = check_freshness("pkg", "1.0.0")

    assert status.error != ""
    assert status.latest == ""


def test_check_freshness_invalid_json() -> None:
    """
    Verify check_freshness reports undecodable bodies.
    """

    resp = MagicMock()
    resp.json.side_effect = ValueError("no json")
    with patch("depschecker.pypi.requests.get", return_value=resp):
        status = check_freshness("pkg", "1.0.0")

    assert "Invalid JSON" in status.error


# --- Opt-in live check ------------------------------------------------------


@pytest.mark.skipif(
    not _LIVE,
    reason="Set DEPSCHECKER_LIVE_NETWORK=1 to run the live PyPI check.",
)
def test_live_pypi_reports_urllib3_advisory() -> None:
    """
    Verify against live PyPI that the fix still holds.

    Opt-in so the default suite stays deterministic and
    offline. Guards against PyPI changing its response
    shape under us.
    """

    status = check_vulnerabilities("urllib3", "2.6.3", timeout=30)

    assert status.error == ""
    assert _KNOWN_ADVISORY in {a.id for a in status.advisories}
