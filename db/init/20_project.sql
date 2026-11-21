-- Runs once, the first time the container starts with an empty data volume
-- (after the image's own 10_postgis.sh, which already creates PostGIS in $POSTGRES_DB).
-- Phase 0 only makes sure PostGIS is there. Schemas (raw, staging, ...) arrive with
-- Phase 2 loaders and Phase 3 dbt, so nothing is created here yet.
create extension if not exists postgis;
