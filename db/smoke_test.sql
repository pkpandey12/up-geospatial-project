-- Phase 0 smoke test: proves the server is up, PostGIS is installed, and a spatial
-- function works. Run with `make db-smoke` (also run automatically by `make db-up`).
\set ON_ERROR_STOP on
select version() as postgres_version;
select postgis_full_version() as postgis_version;
-- Distance in metres between Lucknow and Kanpur (approx. city centres), on the spheroid.
-- Expect roughly 70-80 km. A wrong answer here usually means lon/lat were swapped.
select round(
    st_distance(
        cast(st_setsrid(st_makepoint(80.9462, 26.8467), 4326) as geography),
        cast(st_setsrid(st_makepoint(80.3319, 26.4499), 4326) as geography)
    ) / 1000.0
) as lucknow_kanpur_km;
