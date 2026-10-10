# Standard libraries
import logging

# Own modules
from depschecker.types import DepStatus, VulnStatus

logger: logging.Logger = logging.getLogger(__name__)

_FRESHNESS_NOTE: str = (
    "Declared is the lower bound of the constraint in `pyproject.toml`; "
    "Resolved is the version pinned in `uv.lock`. Update compares the "
    "resolved version against Latest, falling back to Declared when no "
    "lockfile was read."
)

# PyPI's JSON API exposes no severity or CVSS field at all, and returns an
# explicit null summary for PYSEC-family advisories. Stating that in the report
# keeps a blank cell from reading as "low severity".
_VULN_NOTE: str = (
    "Advisories are queried per resolved version from `uv.lock`, covering "
    "direct and transitive dependencies. PyPI's JSON API supplies no "
    "severity or CVSS field, and leaves the summary empty for "
    "PYSEC-family advisories: follow the link for severity and detail."
)


def render_freshness(statuses: list[DepStatus]) -> str:
    """
    Render a Markdown freshness report table.

    Args:
        statuses: Freshness results for declared direct
            dependencies.

    Returns:
        Markdown string with the freshness table.
    """

    lines: list[str] = [
        "# Dependency Freshness Report\n",
        f"{_FRESHNESS_NOTE}\n",
        "| Package | Declared | Resolved | Latest | Update | Changelog |",
        "|---------|----------|----------|--------|--------|-----------|",
    ]

    for s in statuses:
        declared: str = s.declared or "unpinned"
        resolved: str = s.resolved or "—"
        if s.error:
            lines.append(
                f"| {s.name} | {declared} | {resolved} | ⚠ error | — | — |",
            )
            continue
        icon: str = _update_icon(s.update_type)
        changelog: str = f"[link]({s.changelog_url})" if s.changelog_url else "—"
        lines.append(
            f"| {s.name} | {declared} | {resolved} | {s.latest} "
            f"| {icon} {s.update_type} | {changelog} |"
        )

    return "\n".join(lines) + "\n"


def render_vulnerabilities(statuses: list[VulnStatus]) -> str:
    """
    Render a Markdown vulnerability report table.

    Only includes packages with known advisories. Query
    failures are listed separately so a network error is
    never mistaken for a clean result.

    Args:
        statuses: Vulnerability results for resolved
            package versions.

    Returns:
        Markdown string with the vulnerability table.
    """

    rows: list[str] = []
    for s in statuses:
        scope: str = "direct" if s.direct else "transitive"
        for a in s.advisories:
            flag: str = " ⚠ withdrawn" if a.withdrawn else ""
            rows.append(
                f"| {s.name} | {s.resolved} | {scope} | {a.id}{flag} "
                f"| {a.aliases or '—'} | {a.summary or '—'} "
                f"| {a.fixed_in or 'none'} | {a.link or '—'} |"
            )

    lines: list[str] = ["# Vulnerability Report\n", f"{_VULN_NOTE}\n"]

    if rows:
        lines += [
            "| Package | Resolved | Scope | Advisory | Aliases | Summary "
            "| Fixed in | Link |",
            "|---------|----------|-------|----------|---------|---------"
            "|----------|------|",
            *rows,
        ]
    else:
        count: int = len(statuses)
        lines.append(f"No known vulnerabilities found in {count} resolved packages.")

    failures: list[VulnStatus] = [s for s in statuses if s.error]
    if failures:
        lines += [
            "\n## Packages not audited\n",
            "These queries failed, so their advisory status is unknown.\n",
            "| Package | Resolved | Error |",
            "|---------|----------|-------|",
            *(f"| {s.name} | {s.resolved} | {s.error} |" for s in failures),
        ]

    return "\n".join(lines) + "\n"


def render_full(
    freshness: list[DepStatus],
    vulnerabilities: list[VulnStatus],
) -> str:
    """
    Render the combined freshness and vulnerability
    report.

    Args:
        freshness: Freshness results for declared direct
            dependencies.
        vulnerabilities: Vulnerability results for
            resolved package versions.

    Returns:
        Full Markdown report string.
    """

    return render_freshness(freshness) + "\n" + render_vulnerabilities(vulnerabilities)


def _update_icon(update_type: str) -> str:
    """
    Return an emoji icon for the update type.

    Args:
        update_type: Semver distance classification.

    Returns:
        Emoji string.
    """

    icons: dict[str, str] = {
        "up-to-date": "✅",
        "patch": "🟡",
        "minor": "🟠",
        "major": "🔴",
        "unknown": "❓",
    }
    return icons.get(update_type, "❓")
