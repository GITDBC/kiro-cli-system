"""Tests for the Markdown report rendering."""

# Own modules
from depschecker.report import (
    _update_icon,
    render_freshness,
    render_full,
    render_vulnerabilities,
)
from depschecker.types import Advisory, DepStatus, VulnStatus


def test_render_freshness_up_to_date() -> None:
    """
    Verify render_freshness includes up-to-date
    packages.
    """

    statuses = [
        DepStatus(
            name="pkg",
            declared="1.0.0",
            resolved="1.0.0",
            latest="1.0.0",
            update_type="up-to-date",
        )
    ]
    result = render_freshness(statuses)
    assert "pkg" in result
    assert "up-to-date" in result


def test_render_freshness_shows_both_versions() -> None:
    """
    Verify the freshness table distinguishes the declared
    constraint from the resolved version.
    """

    statuses = [
        DepStatus(
            name="requests",
            declared="2.32",
            resolved="2.33.1",
            latest="2.33.1",
            update_type="up-to-date",
        )
    ]
    result = render_freshness(statuses)
    assert "| Package | Declared | Resolved | Latest |" in result
    assert "| requests | 2.32 | 2.33.1 | 2.33.1 " in result


def test_render_freshness_states_version_semantics() -> None:
    """
    Verify the freshness report explains which version
    each column refers to.
    """

    result = render_freshness([])
    assert "pyproject.toml" in result
    assert "uv.lock" in result


def test_render_freshness_unpinned_and_unlocked() -> None:
    """
    Verify placeholders appear when a dependency is
    unpinned and no lockfile was read.
    """

    result = render_freshness([DepStatus(name="pkg", declared="")])
    assert "unpinned" in result


def test_render_freshness_with_error() -> None:
    """
    Verify render_freshness shows error marker for
    failed checks.
    """

    statuses = [DepStatus(name="bad", declared="1.0.0", error="timeout")]
    result = render_freshness(statuses)
    assert "⚠ error" in result


def test_render_freshness_with_changelog() -> None:
    """
    Verify render_freshness includes changelog link
    when available.
    """

    statuses = [
        DepStatus(
            name="pkg",
            declared="1.0.0",
            latest="2.0.0",
            update_type="major",
            changelog_url="https://example.com/changes",
        ),
    ]
    result = render_freshness(statuses)
    assert "[link](https://example.com/changes)" in result


def test_render_vulnerabilities_none() -> None:
    """
    Verify render_vulnerabilities shows no-vuln
    message when clean.
    """

    statuses = [VulnStatus(name="pkg", resolved="1.0.0")]
    result = render_vulnerabilities(statuses)
    assert "No known vulnerabilities" in result
    assert "1 resolved packages" in result


def test_render_vulnerabilities_with_data() -> None:
    """
    Verify render_vulnerabilities includes advisory
    rows against the resolved version.
    """

    statuses = [
        VulnStatus(
            name="urllib3",
            resolved="2.6.3",
            advisories=[
                Advisory(
                    id="GHSA-mf9v-mfxr-j63j",
                    aliases="CVE-2026-44432",
                    fixed_in="2.7.0",
                    link="https://osv.dev/vulnerability/GHSA-mf9v-mfxr-j63j",
                ),
            ],
        ),
    ]
    result = render_vulnerabilities(statuses)
    assert "GHSA-mf9v-mfxr-j63j" in result
    assert "2.6.3" in result
    assert "2.7.0" in result
    assert "transitive" in result


def test_render_vulnerabilities_marks_direct_scope() -> None:
    """
    Verify the scope column distinguishes direct from
    transitive dependencies.
    """

    statuses = [
        VulnStatus(
            name="requests",
            resolved="2.32.0",
            direct=True,
            advisories=[Advisory(id="GHSA-x")],
        ),
    ]
    assert "| direct |" in render_vulnerabilities(statuses)


def test_render_vulnerabilities_notes_severity_limitation() -> None:
    """
    Verify the report warns that PyPI supplies no
    severity, so a blank cell is not "low risk".
    """

    result = render_vulnerabilities([])
    assert "severity" in result.lower()
    assert "PYSEC" in result


def test_render_vulnerabilities_flags_withdrawn() -> None:
    """
    Verify retracted advisories are marked rather than
    silently dropped.
    """

    statuses = [
        VulnStatus(
            name="pkg",
            resolved="1.0.0",
            advisories=[Advisory(id="GHSA-x", withdrawn=True)],
        ),
    ]
    assert "withdrawn" in render_vulnerabilities(statuses)


def test_render_vulnerabilities_lists_failures() -> None:
    """
    Verify failed queries are reported separately so a
    network error is not read as a clean result.
    """

    statuses = [VulnStatus(name="pkg", resolved="1.0.0", error="timeout")]
    result = render_vulnerabilities(statuses)
    assert "not audited" in result
    assert "timeout" in result


def test_render_full_contains_both() -> None:
    """
    Verify render_full includes both freshness and
    vulnerability sections.
    """

    freshness = [
        DepStatus(
            name="pkg",
            declared="1.0.0",
            resolved="1.0.0",
            latest="1.0.0",
            update_type="up-to-date",
        )
    ]
    result = render_full(freshness, [VulnStatus(name="pkg", resolved="1.0.0")])
    assert "Freshness" in result
    assert "Vulnerability" in result


def test_update_icon_known() -> None:
    """
    Verify _update_icon returns correct emoji for
    known types.
    """

    assert _update_icon("up-to-date") == "✅"
    assert _update_icon("patch") == "🟡"
    assert _update_icon("minor") == "🟠"
    assert _update_icon("major") == "🔴"


def test_update_icon_unknown() -> None:
    """
    Verify _update_icon returns fallback for unknown
    types.
    """

    assert _update_icon("weird") == "❓"
