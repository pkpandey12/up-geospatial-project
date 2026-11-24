# UP Factory Siting Tool

Ranks Uttar Pradesh's **75 districts** by the estimated **variable overhead (₹ per tonne of
output)** of building a factory for a chosen product and plant size. The MVP is
district-level and non-geographic, piloted on **ethanol** (first) and **CBG**. Cost terms:
raw material, land, water, and power (a statewide constant). Hard filters run first; each
district gets a ₹/t range, a confidence rating and a rank range from ±20% sensitivity runs;
risk flags sit beside the ranking.

Status: **Phase 0 signed off (22 Nov 2026); Phase 1 (EDA) in progress, to 1 Jan 2027.**
Plan and rules: [`docs/BRIEF.md`](docs/BRIEF.md). Spec:
[`docs/design/design-doc-2026-11-24.md`](docs/design/design-doc-2026-11-24.md).

## Quick start (Windows, macOS, Linux)

Two ways in, same commands ([`docs/SETUP.md`](docs/SETUP.md) has step-by-step installs):

- **Dev Container** (identical on every OS): install Docker + VS Code, clone, *Reopen in Container*.
- **On your host**: Docker + git + make + uv on macOS/Linux, or inside WSL2 on Windows.

```bash
make setup    # tools check, .env, Python 3.12 + packages (uv), git hooks
make test     # unit + notebook tests
make lint     # ruff + product-profile validation
make db-up    # PostGIS in Docker, waits until healthy, runs the smoke test
make          # list every target
```

## Layout

```
docs/            BRIEF.md (plan), SETUP.md, TODO-sage.md, TODO-later.md, data-sources.md,
                 design/ (design doc), learn/ (one page per tool),
                 eda/ (source register, download cards, plan, write-ups, data-quality log), sessions/
notebooks/eda/   01_spine (worked example), 02_coverage, 03_district_table (Sage),
                 10_apy_crop_production, 11_hq_climate (source loaders)
config/product_profiles/   <product>.yaml + profile.schema.json
src/up_siting/   common/ (paths, units, names, db), extract/ (LGD PDF parser, raw manifest),
                 load/ (Phase 2), profiles/ (schema, validator, derived quantities)
.devcontainer/  Dev Container (Linux toolchain image + compose service)
dbt/seeds/       district spine, name map, aliases, lineage (dbt project itself: Phase 3)
airflow/dags/    Phase 2
db/              PostGIS init + smoke test SQL
data/            raw/ and interim/ downloads and outputs (git-ignored)
tests/           pytest suite + fixtures
```

## Architecture (decided)

Local first: PostgreSQL + PostGIS in Docker · DuckDB + pandas for the EDA · Airflow in
Docker (Phase 2) running dbt Core via Cosmos (Phase 3) · layers raw → staging → intermediate
→ marts. From March 2027: AWS (S3 + one EC2 running Airflow), Snowflake as the warehouse
(stretch), hence the portability rules ([`docs/learn/portability.md`](docs/learn/portability.md)).

## Data

Every source, with its licence and required attribution, is listed in
[`docs/data-sources.md`](docs/data-sources.md). Downloaded files are never committed (except
small test fixtures); each is registered in `data/raw/<source>/_manifest.jsonl`
(`make register`). Partner data lives only in git-ignored `private/` folders.
