"""Phase 0 database smoke test. Needs the container: run via `make db-up` / `make db-smoke`."""

import psycopg
import pytest

from up_siting.common.db import DbSettings

pytestmark = pytest.mark.integration


def test_postgis_is_installed() -> None:
    with psycopg.connect(DbSettings.from_env().conninfo(), connect_timeout=5) as conn:
        version = conn.execute("select postgis_full_version()").fetchone()[0]
    assert "POSTGIS=" in version


def test_spatial_distance_is_sane() -> None:
    # Lucknow -> Kanpur, roughly 70-80 km. Swapped lon/lat would give a very different number.
    sql = """
        select st_distance(
            cast(st_setsrid(st_makepoint(80.9462, 26.8467), 4326) as geography),
            cast(st_setsrid(st_makepoint(80.3319, 26.4499), 4326) as geography)
        ) / 1000.0
    """
    with psycopg.connect(DbSettings.from_env().conninfo(), connect_timeout=5) as conn:
        km = conn.execute(sql).fetchone()[0]
    assert 60 < km < 90
