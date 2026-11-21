# Portability rules (PostGIS today, maybe Snowflake later)

Snowflake may be added after Phase 4 as an analytics warehouse, with PostGIS still serving
the app. These four rules keep that move cheap. They apply from day one, because retrofitting
portability into 100 models is the expensive version.

| # | Rule | Why |
|---|---|---|
| 1 | **Spatial logic in one place**: `ST_*` only in `dbt/models/intermediate/spatial/` and `dbt/macros/spatial/`; everything else uses their outputs (district codes, distances). | Snowflake's spatial functions differ in names, types (GEOGRAPHY vs GEOMETRY) and behaviour, so isolating them means rewriting one folder, not every model. |
| 2 | **Cross-database macros**: `dbt.dateadd`, `dbt.datediff`, `dbt.safe_cast`, `dbt.type_string()`…; `cast(x as …)` not `x::type`. | dbt's macros compile to the right dialect for each adapter; `::` is Postgres syntax that Snowflake mostly accepts but other engines don't, and date functions differ everywhere. |
| 3 | **Raw lands as Parquet** with the original file beside it. | Snowflake (and DuckDB, BigQuery, Spark) can stage and load Parquet as-is, with types; keeping the original makes every load re-playable and auditable. |
| 4 | **No Postgres-only features in models**: no arrays, JSONB operators or `DISTINCT ON`; dedupe with `row_number()` in a CTE. | These have no direct equivalent (or a different one: `VARIANT`, `QUALIFY`) in Snowflake; `row_number()` over a window is standard SQL that every warehouse runs. |

## The standard dedupe pattern (rule 4)

```sql
with ranked as (
    select
        *,
        row_number() over (
            partition by lgd_district_code
            order by _ingested_at desc
        ) as rn
    from {{ ref('stg_something') }}
)
select lgd_district_code, value, _ingested_at   -- list columns: `* exclude (rn)` isn't Postgres
from ranked
where rn = 1
```

(Snowflake would let you write `qualify row_number() over (...) = 1`, but that's exactly the
kind of dialect feature rule 4 keeps out of models.)

## Where you already see the rules

- `db/smoke_test.sql` and `tests/test_db_smoke.py` use `cast(... as geography)`, not `::geography`.
- `notebooks/eda/01_spine.ipynb` writes Parquet next to the CSV seeds.
- The LGD PDF stays untouched in `data/raw/lgd/ingest_date=…/`.

## Interview question

- *You're told "we might move to Snowflake next year". What do you do differently today, and what
  do you deliberately not do?* (Isolate dialect-specific code, keep raw in open formats, use
  the adapter's macros. Don't build an abstraction layer for a move that may never happen.)
