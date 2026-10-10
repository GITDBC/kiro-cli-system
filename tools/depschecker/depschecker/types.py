# Standard libraries
from dataclasses import dataclass, field
from typing import Any, TypeAlias

PyPIResponse: TypeAlias = dict[str, Any]


@dataclass(frozen=True)
class Advisory:
    """
    A single vulnerability advisory for a package
    version.

    Attributes:
        id: Advisory identifier (GHSA, PYSEC or CVE).
        aliases: Comma-joined alias identifiers.
        summary: Advisory summary, or empty when PyPI
            does not supply one.
        fixed_in: Comma-joined versions containing the
            fix, or empty when unfixed.
        link: Upstream advisory URL.
        withdrawn: Whether the advisory was retracted.
    """

    id: str
    aliases: str = ""
    summary: str = ""
    fixed_in: str = ""
    link: str = ""
    withdrawn: bool = False


@dataclass
class DepStatus:
    """
    Freshness status of one declared dependency.

    Freshness is a property of the *declared* direct
    dependencies, since those are what a maintainer can
    bump. ``resolved`` is carried alongside so the report
    can state which version each figure refers to.

    Attributes:
        name: Normalised package name.
        declared: Lower bound of the constraint declared
            in ``pyproject.toml``. Empty if unpinned.
        resolved: Version pinned by ``uv.lock``. Empty
            when no lockfile was available.
        latest: Latest stable version on PyPI.
        update_type: Semver distance from the effective
            version to ``latest``, or "up-to-date".
        changelog_url: Project changelog URL if known.
        error: Error message if the check failed.
    """

    name: str
    declared: str
    resolved: str = ""
    latest: str = ""
    update_type: str = "unknown"
    changelog_url: str = ""
    error: str = ""

    @property
    def effective(self) -> str:
        """
        Version the freshness comparison is based on.

        Returns:
            The resolved version when known, else the
            declared lower bound.
        """

        return self.resolved or self.declared


@dataclass
class VulnStatus:
    """
    Advisories affecting one resolved package version.

    Vulnerabilities are a property of the *resolved*
    version, which is what actually gets installed, so
    this is keyed on ``uv.lock`` rather than on the
    declared constraint.

    Attributes:
        name: Normalised package name.
        resolved: Version pinned by ``uv.lock``.
        direct: Whether the package is a declared direct
            dependency rather than transitive.
        advisories: Deduplicated advisories for the
            resolved version.
        error: Error message if the query failed.
    """

    name: str
    resolved: str
    direct: bool = False
    advisories: list[Advisory] = field(default_factory=list)
    error: str = ""
