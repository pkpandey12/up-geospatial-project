# UP Factory Siting Tool

Ranks Uttar Pradesh's **75 districts** by the estimated **variable overhead (₹ per tonne of
output)** of building a factory for a chosen product. The overhead has five parts: raw
material, market access, land, electricity (including solar) and water. Hard filters run first;
risk flags and confidence ratings sit beside the ranking; every ranking is rerun with ±20%
on the key assumptions.

Status: **Phase 0 (setup) built; Phase 1 (EDA) started.** Plan and rules: [`docs/BRIEF.md`](docs/BRIEF.md).

## Quick start (Linux)

Prerequisites: git, Docker Engine + Compose v2, uv, make. Install steps: [`docs/SETUP.md`](docs/SETUP.md).

```bash
make setup    # tools check, .env, Python 3.12 + packages (uv), git hooks
make test     # unit + notebook tests
make lint     # ruff + product-profile validation
make db-up    # PostGIS in Docker, waits until healthy, runs the smoke test
make          # list every target
```

## Layout

```
docs/            BRIEF.md (plan), SETUP.md, TODO-sage.md, data-sources.md,
                 learn/ (one page per tool), eda/ (write-ups + data-quality log), sessions/
notebooks/eda/   01_spine.ipynb (worked example), 02_coverage.ipynb (TODO), ...
config/product_profiles/   <product>.yaml + profile.schema.json
src/up_siting/   common/ (paths, units, names, db), extract/ (LGD PDF parser),
                 load/ (Phase 2), profiles/ (schema, validator, derived quantities)
dbt/seeds/       district spine, name map, aliases, lineage (dbt project itself: Phase 3)
airflow/dags/    Phase 2
db/              PostGIS init + smoke test SQL
data/            raw/ and interim/ downloads and outputs (git-ignored)
tests/           pytest suite + fixtures
```

## Architecture (decided)

PostgreSQL + PostGIS (Docker locally, managed when hosted) · DuckDB + pandas for EDA ·
Airflow (Phase 2) running dbt Core via Cosmos (Phase 3) · layers raw → staging → intermediate
→ marts · portability rules for a possible later Snowflake warehouse
([`docs/learn/portability.md`](docs/learn/portability.md)).

## Data

Every source, with its licence, is listed in [`docs/data-sources.md`](docs/data-sources.md).
Downloaded files are never committed (except small test fixtures).
