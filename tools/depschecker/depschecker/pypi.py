"""Query PyPI for package freshness and vulnerability data.

Two endpoints, deliberately, because neither one answers both questions:

* ``/pypi/<name>/json`` carries ``info.version`` and ``releases``, which is what
  freshness needs, but its ``vulnerabilities`` key is **always empty**.
* ``/pypi/<name>/<version>/json`` is the only endpoint that populates
  ``vulnerabilities``, but it omits ``releases`` entirely and reports the
  *queried* version as ``info.version``, so it cannot answer freshness.

Querying only the unversioned endpoint is why vulnerability scanning silently
reported clean for every package.
"""

# Standard libraries
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Final

# 3pps
import requests

# Own modules
from depschecker.types import Advisory, DepStatus, PyPIResponse, VulnStatus

logger: logging.Logger = logging.getLogger(__name__)

PYPI_PACKAGE_URL: str = "https://pypi.org/pypi/{name}/json"
PYPI_VERSION_URL: str = "https://pypi.org/pypi/{name}/{version}/json"

DEFAULT_TIMEOUT: Final[int] = 15
"""HTTP timeout per PyPI request in seconds."""

_MAX_WORKERS: int = 8
_PRE_RE: re.Pattern[str] = re.compile(r"[\d.\-](a|b|rc|dev|alpha|beta|preview)\d*")


def check_freshness(
    name: str,
    declared: str,
    resolved: str = "",
    timeout: int = DEFAULT_TIMEOUT,
) -> DepStatus:
    """
    Query PyPI for the latest version of a package.

    Uses the unversioned endpoint, the only one exposing
    ``releases`` and the true latest version.

    Args:
        name: Normalised package name.
        declared: Declared constraint lower bound.
        resolved: Version pinned by ``uv.lock``, if known.
        timeout: HTTP request timeout in seconds.

    Returns:
        Populated freshness status.
    """

    status: DepStatus = DepStatus(name=name, declared=declared, resolved=resolved)

    data, error = _fetch_json(PYPI_PACKAGE_URL.format(name=name), timeout)
    if data is None:
        status.error = error
        return status

    status.latest = _latest_stable(data)
    status.update_type = _classify_update(status.effective, status.latest)
    status.changelog_url = _find_changelog(data)

    return status


def check_vulnerabilities(
    name: str,
    version: str,
    direct: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
) -> VulnStatus:
    """
    Query PyPI for advisories against one exact version.

    The version segment is mandatory: the unversioned
    endpoint never reports advisories.

    Args:
        name: Normalised package name.
        version: Exact resolved version to audit.
        direct: Whether this is a declared direct
            dependency.
        timeout: HTTP request timeout in seconds.

    Returns:
        Populated vulnerability status.

    Raises:
        ValueError: If ``version`` is empty, since an
            unversioned query cannot detect advisories.
    """

    if not version:
        message: str = f"Cannot audit {name} without a resolved version."
        logger.error("%s", message)
        raise ValueError(message)

    status: VulnStatus = VulnStatus(name=name, resolved=version, direct=direct)

    url: str = PYPI_VERSION_URL.format(name=name, version=version)
    data, error = _fetch_json(url, timeout)
    if data is None:
        status.error = error
        return status

    status.advisories = _extract_vulns(data)

    return status


def scan_vulnerabilities(
    packages: list[tuple[str, str, bool]],
    timeout: int = DEFAULT_TIMEOUT,
) -> list[VulnStatus]:
    """
    Audit many resolved package versions concurrently.

    Args:
        packages: Tuples of name, resolved version and
            direct-dependency flag.
        timeout: HTTP request timeout in seconds.

    Returns:
        Vulnerability statuses in input order.
    """

    if not packages:
        return []

    def _audit(item: tuple[str, str, bool]) -> VulnStatus:
        name, version, direct = item
        return check_vulnerabilities(name, version, direct=direct, timeout=timeout)

    workers: int = min(_MAX_WORKERS, len(packages))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_audit, packages))


def _fetch_json(url: str, timeout: int) -> tuple[PyPIResponse | None, str]:
    """
    Fetch and decode a PyPI JSON document.

    Args:
        url: Fully formed endpoint URL.
        timeout: HTTP request timeout in seconds.

    Returns:
        Tuple of decoded payload and error message. The
        payload is ``None`` exactly when the error is
        non-empty.
    """

    try:
        resp: requests.Response = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Failed to fetch %s: %s.", url, exc)
        return None, str(exc)

    try:
        data: PyPIResponse = resp.json()
    except ValueError as exc:
        logger.warning("Invalid JSON from %s: %s.", url, exc)
        return None, f"Invalid JSON response: {exc}"

    return data, ""


def _latest_stable(data: PyPIResponse) -> str:
    """
    Extract the latest stable version from PyPI response.

    Skips pre-release versions unless no stable release
    exists.

    Args:
        data: Full PyPI JSON response.

    Returns:
        Latest stable version string.
    """

    version: str = data.get("info", {}).get("version", "")
    releases: dict[str, Any] = data.get("releases", {})

    if not _PRE_RE.search(version):
        return version

    # Fall back to scanning releases for latest stable.
    stable: list[str] = [v for v in releases if not _PRE_RE.search(v)]
    if not stable:
        return version

    return sorted(stable, key=_version_tuple, reverse=True)[0]


def _version_tuple(version: str) -> tuple[int, ...]:
    """
    Convert a version string to a comparable tuple of
    integers.

    Non-numeric segments are treated as zero.

    Args:
        version: Version string (e.g. ``2.32.3``).

    Returns:
        Tuple of integers for comparison.
    """

    parts: list[int] = []
    for segment in version.split("."):
        match: re.Match[str] | None = re.match(r"(\d+)", segment)
        parts.append(int(match.group(1)) if match else 0)
    return tuple(parts)


def _classify_update(current: str, latest: str) -> str:
    """
    Classify the semver distance between two versions.

    Args:
        current: Version currently in effect.
        latest: Latest version string.

    Returns:
        One of ``up-to-date``, ``patch``, ``minor``, or
        ``major``.
    """

    if not current or not latest:
        return "unknown"

    cur: tuple[int, ...] = _version_tuple(current)
    lat: tuple[int, ...] = _version_tuple(latest)

    # Pad to at least 3 elements.
    cur = cur + (0,) * (3 - len(cur))
    lat = lat + (0,) * (3 - len(lat))

    if lat <= cur:
        return "up-to-date"
    if lat[0] != cur[0]:
        return "major"
    if lat[1] != cur[1]:
        return "minor"
    return "patch"


def _find_changelog(data: PyPIResponse) -> str:
    """
    Attempt to find a changelog URL from project URLs.

    Args:
        data: Full PyPI JSON response.

    Returns:
        Changelog URL or empty string.
    """

    urls: dict[str, str] = data.get("info", {}).get("project_urls") or {}
    for key in ("Changelog", "Changes", "History", "Release Notes", "What's New"):
        if key in urls:
            return urls[key]
    # Fallback: any URL containing "changelog" or "releases".
    for url in urls.values():
        if "changelog" in url.lower() or "releases" in url.lower():
            return url
    return ""


def _extract_vulns(data: PyPIResponse) -> list[Advisory]:
    """
    Extract advisories from a versioned PyPI response.

    PyPI lists the same vulnerability once per identifier
    namespace, so GHSA and PYSEC entries sharing a CVE
    alias are collapsed to a single advisory.

    Args:
        data: Versioned PyPI JSON response.

    Returns:
        Deduplicated advisories.
    """

    raw: list[dict[str, Any]] = data.get("vulnerabilities") or []

    advisories: list[Advisory] = []
    seen: set[str] = set()

    for vuln in raw:
        aliases: list[str] = [a for a in (vuln.get("aliases") or []) if a]
        identifier: str = vuln.get("id") or (aliases[0] if aliases else "unknown")
        key: str = next((a for a in aliases if a.startswith("CVE-")), identifier)
        if key in seen:
            continue
        seen.add(key)

        fixed: list[str] = vuln.get("fixed_in") or []
        advisories.append(
            Advisory(
                id=identifier,
                aliases=", ".join(aliases),
                # PyPI returns an explicit null summary for
                # PYSEC-family advisories, so `or` is needed
                # rather than a `get` default.
                summary=vuln.get("summary") or "",
                fixed_in=", ".join(fixed),
                link=vuln.get("link") or "",
                withdrawn=bool(vuln.get("withdrawn")),
            )
        )

    return advisories
