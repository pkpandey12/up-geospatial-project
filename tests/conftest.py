"""Shared pytest setup. Learn: docs/learn/pytest.md

Tests marked @pytest.mark.todo check functions Sage implements. While the function still
raises NotImplementedError the test is reported as "xfailed" (expected failure), so
`make test` stays green. Once implemented, the test runs normally: a WRONG implementation
fails red. `make todo` ignores the marker (--runxfail) to show the honest pass/fail list.
"""

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        if item.get_closest_marker("todo"):
            item.add_marker(
                pytest.mark.xfail(
                    raises=NotImplementedError, reason="TODO(sage): not implemented yet"
                )
            )


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def lgd_pdf() -> Path:
    """The real LGD export for UP, downloaded 2026-11-21 (see docs/data-sources.md)."""
    return FIXTURES / "lgd" / "Districts_of_Uttar_Pradesh_State.pdf"
